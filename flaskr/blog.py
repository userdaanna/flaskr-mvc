import os
import uuid
from flask import Blueprint, current_app, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from .auth import login_required
from .models import Post, db

bp = Blueprint("blog", __name__)

def salvar_imagem_post(file):
    if file and file.filename:
        nome_seguro = secure_filename(file.filename)
        nome_unico = f"{uuid.uuid4().hex}_{nome_seguro}"
        file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], nome_unico))
        return nome_unico
    return None

@bp.route("/")
def index():
    posts = Post.query.order_by(Post.created.desc()).all()
    return render_template("blog/index.html", posts=posts)

@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        imagem = request.files.get("imagem_post")
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            imagem_filename = salvar_imagem_post(imagem)
            post = Post(
                title=title,
                body=body,
                author_id=g.user.id,
                imagem_post=imagem_filename,
            )
            db.session.add(post)
            db.session.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")

def get_post(id, check_author=True):
    post = db.session.get(Post, id)
    if post is None:
        abort(404, f"Post id {id} doesn't exist.")
    if check_author and post.author_id != g.user.id:
        abort(403)
    return post

@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        imagem = request.files.get("imagem_post")
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            post.title = title
            post.body = body
            nova_imagem = salvar_imagem_post(imagem)
            if nova_imagem:
                post.imagem_post = nova_imagem
            db.session.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)

@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    post = get_post(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("blog.index"))
