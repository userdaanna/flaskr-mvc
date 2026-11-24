import functools
import os
import uuid
from flask import Blueprint, current_app, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from .models import User, db

bp = Blueprint("auth", __name__, url_prefix="/auth")

def salvar_arquivo(file):
    if file and file.filename:
        nome_seguro = secure_filename(file.filename)
        nome_unico = f"{uuid.uuid4().hex}_{nome_seguro}"
        file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], nome_unico))
        return nome_unico
    return None

@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        avatar_file = request.files.get("avatar")
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."
        elif User.query.filter_by(username=username).first() is not None:
            error = f"User {username} is already registered."

        if error is None:
            avatar_filename = salvar_arquivo(avatar_file)
            novo_usuario = User(
                username=username,
                password=generate_password_hash(password),
                avatar=avatar_filename,
            )
            db.session.add(novo_usuario)
            db.session.commit()
            return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/register.html")

@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        error = None
        user = User.query.filter_by(username=username).first()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user.password, password):
            error = "Incorrect password."

        if error is None:
            session.clear()
            session["user_id"] = user.id
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        g.user = db.session.get(User, user_id)

@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)
    return wrapped_view
