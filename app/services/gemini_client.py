import re
import threading
import time
from dataclasses import dataclass

import requests


class GeminiClientError(RuntimeError):
    def __init__(self, message, retryable=True):
        super().__init__(message)
        self.retryable = retryable


@dataclass
class GeminiKeyState:
    key: str
    index: int
    cooldown_until: float = 0.0
    disabled: bool = False
    requests_sent: int = 0
    errors_seen: int = 0
    last_error: str = ""

    @property
    def label(self):
        return f"key_{self.index + 1}"


@dataclass
class GeminiResponse:
    text: str
    key_index: int
    attempts: int
    model: str


class GeminiKeyManager:
    def __init__(self, keys, cooldown_seconds=60):
        if not keys:
            raise GeminiClientError("GEMINI_API_KEYS is empty.", retryable=False)
        self._states = [GeminiKeyState(key=key, index=index) for index, key in enumerate(keys)]
        self._cooldown_seconds = cooldown_seconds
        self._cursor = 0
        self._lock = threading.Lock()

    @property
    def total_keys(self):
        return len(self._states)

    def next_key(self):
        with self._lock:
            now = time.time()
            total = len(self._states)
            for _ in range(total):
                state = self._states[self._cursor]
                self._cursor = (self._cursor + 1) % total
                if not state.disabled and state.cooldown_until <= now:
                    return state
        raise GeminiClientError("No Gemini API key is currently available.", retryable=True)

    def mark_success(self, state):
        with self._lock:
            state.requests_sent += 1
            state.last_error = ""

    def cooldown(self, state, message):
        with self._lock:
            state.errors_seen += 1
            state.last_error = message
            state.cooldown_until = time.time() + self._cooldown_seconds

    def disable(self, state, message):
        with self._lock:
            state.errors_seen += 1
            state.last_error = message
            state.disabled = True

    def mark_error(self, state, message):
        with self._lock:
            state.errors_seen += 1
            state.last_error = message

    def status(self):
        now = time.time()
        with self._lock:
            keys = []
            for state in self._states:
                cooldown_remaining = max(0, int(state.cooldown_until - now))
                if state.disabled:
                    status = "disabled"
                elif cooldown_remaining:
                    status = "cooldown"
                else:
                    status = "available"
                keys.append(
                    {
                        "label": state.label,
                        "status": status,
                        "cooldown_remaining": cooldown_remaining,
                        "requests_sent": state.requests_sent,
                        "errors_seen": state.errors_seen,
                        "last_error": state.last_error,
                    }
                )
        return keys


class GeminiClient:
    _manager = None
    _manager_signature = None
    _manager_lock = threading.Lock()

    def __init__(self, key_manager, model, timeout_seconds=45):
        self.key_manager = key_manager
        self.model = model
        self.timeout_seconds = timeout_seconds

    @classmethod
    def from_app_config(cls, config):
        keys = tuple(config["GEMINI_API_KEYS"])
        signature = (keys, config["GEMINI_KEY_COOLDOWN_SECONDS"])
        with cls._manager_lock:
            if cls._manager is None or cls._manager_signature != signature:
                cls._manager = GeminiKeyManager(
                    keys=keys,
                    cooldown_seconds=config["GEMINI_KEY_COOLDOWN_SECONDS"],
                )
                cls._manager_signature = signature

        return cls(
            key_manager=cls._manager,
            model=config["GEMINI_MODEL"],
            timeout_seconds=config["GEMINI_TIMEOUT_SECONDS"],
        )

    @classmethod
    def status_from_app_config(cls, config):
        client = cls.from_app_config(config)
        return {
            "model": client.model,
            "total_keys": client.key_manager.total_keys,
            "keys": client.key_manager.status(),
        }

    def generate_text(self, prompt, max_attempts=None):
        attempts_allowed = max_attempts or self.key_manager.total_keys
        last_error = None

        for attempt in range(1, attempts_allowed + 1):
            state = self.key_manager.next_key()
            try:
                text = self._request_with_key(state, prompt)
                self.key_manager.mark_success(state)
                return GeminiResponse(
                    text=text,
                    key_index=state.index,
                    attempts=attempt,
                    model=self.model,
                )
            except GeminiClientError as exc:
                last_error = exc
                if not exc.retryable:
                    raise

        raise GeminiClientError(str(last_error or "Gemini request failed."), retryable=True)

    def _request_with_key(self, state, prompt):
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent"
        )
        params = {"key": state.key}
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "topP": 0.9,
            },
        }

        try:
            response = requests.post(
                url,
                params=params,
                json=payload,
                timeout=self.timeout_seconds,
            )
        except requests.RequestException as exc:
            message = f"Network error on {state.label}: {exc}"
            self.key_manager.mark_error(state, message)
            raise GeminiClientError(message, retryable=True) from exc

        if response.status_code == 429:
            message = self._error_message(response, f"{state.label} hit rate limit.")
            self.key_manager.cooldown(state, message)
            raise GeminiClientError(message, retryable=True)

        if response.status_code in {401, 403}:
            message = self._error_message(response, f"{state.label} is not authorized.")
            self.key_manager.disable(state, message)
            raise GeminiClientError(message, retryable=True)

        if response.status_code == 400:
            message = self._error_message(response, "Gemini rejected the request.")
            self.key_manager.mark_error(state, message)
            raise GeminiClientError(message, retryable=False)

        if 500 <= response.status_code < 600:
            message = self._error_message(response, f"Gemini server error on {state.label}.")
            self.key_manager.mark_error(state, message)
            raise GeminiClientError(message, retryable=True)

        if not response.ok:
            message = self._error_message(
                response,
                f"Gemini request failed on {state.label}: HTTP {response.status_code}.",
            )
            self.key_manager.mark_error(state, message)
            raise GeminiClientError(message, retryable=False)

        data = response.json()
        try:
            parts = data["candidates"][0]["content"]["parts"]
            return "\n".join(part.get("text", "") for part in parts).strip()
        except (KeyError, IndexError, TypeError) as exc:
            self.key_manager.mark_error(state, "Unexpected Gemini response shape.")
            raise GeminiClientError("Gemini returned an unexpected response shape.", retryable=False) from exc

    @staticmethod
    def _error_message(response, fallback):
        try:
            data = response.json()
        except ValueError:
            return fallback

        message = data.get("error", {}).get("message")
        if not message:
            return fallback
        return _redact_sensitive(message)[:280]


def _redact_sensitive(message):
    redacted = re.sub(r"api_key:[A-Za-z0-9_.-]+", "api_key:[redacted]", str(message))
    redacted = re.sub(r"key=[A-Za-z0-9_.-]+", "key=[redacted]", redacted)
    return redacted
