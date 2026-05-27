from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from . import db
from .models import Cat, Comment, Order, OrderItem


main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def index():
    cats = Cat.query.order_by(Cat.created_at.desc()).all()
    return render_template("index.html", cats=cats)


@main_bp.get("/cat/<int:cat_id>")
def cat_detail(cat_id: int):
    cat = Cat.query.get_or_404(cat_id)
    comments = Comment.query.filter_by(cat_id=cat_id).order_by(Comment.created_at.desc()).all()
    return render_template("cat_detail.html", cat=cat, comments=comments)


@main_bp.post("/cat/<int:cat_id>/comment")
@login_required
def add_comment(cat_id: int):
    content = request.form.get("content", "")

    # Для тренировочного сайта: рабочее поле ввода; контент хранится как есть.
    if not content.strip():
        flash("Комментарий пустой.", "warning")
        return redirect(url_for("main.cat_detail", cat_id=cat_id))

    c = Comment(cat_id=cat_id, user_id=current_user.id, content=content)
    db.session.add(c)
    db.session.commit()

    flash("Комментарий добавлен.", "success")
    return redirect(url_for("main.cat_detail", cat_id=cat_id))


@main_bp.post("/cat/<int:cat_id>/buy")
@login_required
def buy_cat(cat_id: int):
    cat = Cat.query.get_or_404(cat_id)
    order = Order(user_id=current_user.id)
    db.session.add(order)
    db.session.flush()

    item = OrderItem(
        order_id=order.id,
        cat_id=cat.id,
        quantity=1,
        price_at_moment=cat.price,
    )
    db.session.add(item)
    db.session.commit()

    flash("Псевдо-покупка оформлена. Заказ сохранён в БД.", "success")
    return redirect(url_for("social.profile", username=current_user.username))


@main_bp.get("/me")
@login_required
def me():
    return redirect(url_for("social.profile", username=current_user.username))

