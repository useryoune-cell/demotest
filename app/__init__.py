from flask import Flask

from app.config import Config


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)
    app.jinja_env.auto_reload = True

    @app.after_request
    def add_no_cache_headers(response):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    from app.services.runtime_reset import reset_non_demo_student_data_once

    reset_non_demo_student_data_once()

    from app.routes import main_bp

    app.register_blueprint(main_bp)
    return app


app = create_app()
