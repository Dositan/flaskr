import os

import click
from flask import Flask
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy

__version__ = (1, 0, 0, "dev")

db = SQLAlchemy()


# Application Factory
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # some deploy systems set the database url in the environ
    db_url = os.environ.get("DATABASE_URL")

    if db_url is None:
        # default to a sqlite database in the instance folder
        db_path = os.path.join(app.instance_path, "flaskr.sqlite")
        db_url = f"sqlite:///{db_path}"
        # ensure the instance folder exists
        os.makedirs(app.instance_path, exist_ok=True)

    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI=db_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # initialize Flask-SQLAlchemy and the init-db command
    db.init_app(app)
    app.cli.add_command(init_db_command)

    # apply the blueprints to the app
    from . import auth, blog

    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)

    # make "index" point at "/", which is handled by "blog.index"
    app.add_url_rule("/", endpoint="index")

    return app


def init_db():
    db.drop_all()
    db.create_all()


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")
