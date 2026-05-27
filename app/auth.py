from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from . import db
from .models import User


auth_bp = Blueprint("auth", __name__)


@auth_bp.get("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    return render_template("auth/login.html")


@auth_bp.post("/login")
def login_post():
    username_or_email = request.form.get("username_or_email", "").strip()
    password = request.form.get("password", "")

    user = (
        User.query.filter((User.username == username_or_email) | (User.email == username_or_email))
        .limit(1)
        .one_or_none()
    )
    if not user or not user.check_password(password):
        flash("Неверный логин или пароль.", "danger")
        return redirect(url_for("auth.login"))

    login_user(user)
    flash("Вы вошли в аккаунт.", "success")
    return redirect(url_for("main.index"))


@auth_bp.get("/register")
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    return render_template("auth/register.html")


@auth_bp.post("/register")
def register_post():
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not username or not email or not password:
        flash("Заполни все поля.", "warning")
        return redirect(url_for("auth.register"))

    if User.query.filter_by(username=username).first():
        flash("Такой username уже занят.", "warning")
        return redirect(url_for("auth.register"))
    if User.query.filter_by(email=email).first():
        flash("Email уже используется.", "warning")
        return redirect(url_for("auth.register"))

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    login_user(user)
    flash("Аккаунт создан.", "success")
    return redirect(url_for("main.index"))


@auth_bp.post("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for("main.index"))

