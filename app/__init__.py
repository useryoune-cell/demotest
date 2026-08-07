from flask import Flask

from app.config import Config


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    from app.services.runtime_reset import reset_non_demo_student_data_once

    reset_non_demo_student_data_once()

    from app.routes import main_bp

    app.register_blueprint(main_bp)
    return app


app = create_app()
