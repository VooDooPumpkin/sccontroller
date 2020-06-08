import os
from flask import Flask


def create_app(test_cfg=None):

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    if test_cfg is None:
        app.config.from_pyfile('config.py')
    else:
        app.config.from_mapping(test_cfg)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app