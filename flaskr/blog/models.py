from flask import url_for

from flaskr import db
from flaskr.auth.models import User


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.ForeignKey(User.id), nullable=False)
    created = db.Column(
        db.DateTime, nullable=False, server_default=db.func.current_timestamp()
    )
    title = db.Column(db.String, nullable=False)
    body = db.Column(db.String, nullable=False)

    # User object backed by author_id
    # lazy="joined" means the user is returned with the post in one query
    author = db.relationship(User, lazy="joined", backref="post")
    comments = db.relationship("Comment", backref="post", lazy="dynamic")

    def __repr__(self) -> str:
        return f"Post('{self.title}', '{self.created}')"

    @property
    def update_url(self):
        return url_for("blog.update", id=self.id)

    @property
    def delete_url(self):
        return url_for("blog.delete", id=self.id)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(
        db.DateTime, nullable=False, server_default=db.func.current_timestamp()
    )
    body = db.Column(db.String(250), nullable=False)
    author_id = db.Column(db.ForeignKey(User.id), nullable=False)
    post_id = db.Column(db.ForeignKey(Post.id), nullable=False)

    def __repr__(self):
        return f"Comment('{self.body}', '{self.created}')"
