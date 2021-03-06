from flask import (Blueprint, flash, g, redirect, render_template, request,
                   url_for)
from werkzeug.exceptions import abort

from flaskr import db
from flaskr.auth.views import login_required
from flaskr.blog.models import Comment, Post

bp = Blueprint("blog", __name__)


@bp.route("/")
def index():
    """Show all the posts, most recent first."""
    posts = Post.query.order_by(Post.created.desc()).all()
    return render_template("blog/index.html", posts=posts)


def get_post(id, check_author=True):
    """Get a post and its author by id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of post to get
    :param check_author: require the current user to be the author
    :return: the post with author information
    :raise 404: if a post with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    post = Post.query.get_or_404(id, f"Post id {id} doesn't exist.")

    if check_author and post.author != g.user:
        abort(403)

    return post


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new post for the current user."""
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db.session.add(Post(title=title, body=body, author=g.user))
            db.session.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


@bp.route("/<int:id>", methods=("GET",))
def post(id):
    """See a particular post by specifying its id."""
    post = get_post(id, check_author=False)
    comments = Comment.query.filter_by(post_id=id)
    return render_template("blog/post.html", post=post, comments=comments)


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            post.title = title
            post.body = body
            db.session.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a post.

    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    post = get_post(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("blog.index"))


@bp.route("/<int:id>/comment", methods=("GET", "POST"))
@login_required
def comment(id):
    """Comment a post as a current user"""
    post = Post.query.get_or_404(id)

    if request.method == "POST":
        body = request.form["body"]
        if not body:
            flash("Comment body is required.")
        else:
            db.session.add(Comment(body=body, author_id=g.user.id, post_id=post.id))
            db.session.commit()
            return redirect(url_for("blog.post", id=id))

    return render_template("blog/post.html")
