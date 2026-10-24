import os
from flask import Flask

from app.config import Config


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)
    app.jinja_env.auto_reload = True
    # The checked-in bundle is used on Render. Local development and tests never
    # import it implicitly, even when a shared disk is configured.
    if app.config.get('SEED_DATA_BUNDLE') and os.environ.get('RENDER') == 'true':
        from app.services.deployment_seed import seed_runtime_data
        with app.app_context():
            seed_runtime_data(app.config['SEED_DATA_BUNDLE'])

    @app.after_request
    def add_no_cache_headers(response):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    from app.routes import main_bp

    app.register_blueprint(main_bp)
    return app


app = create_app()
