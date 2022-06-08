from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password = db.Column("password", db.String, nullable=False)
    created = db.Column(
        db.DateTime, nullable=False, server_default=db.func.current_timestamp()
    )
    posts = db.relationship("Post", backref="user")
    comments = db.relationship("Comment", backref="user")

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        """Store the password as a hash for security."""
        self._password = generate_password_hash(value)

    def check_password(self, value):
        return check_password_hash(self.password, value)
