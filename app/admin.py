from flask import Blueprint, abort, current_app, redirect, render_template, request, url_for
from flask_login import login_required

from . import db
from .models import ChatMessage, Comment, Message, User


admin_bp = Blueprint("admin", __name__)


def _check_token() -> None:
    token = request.args.get("token") or request.form.get("token")
    expected = current_app.config.get("ADMIN_TOKEN", "admin")
    if not token or token != expected:
        abort(403)


@admin_bp.get("/admin")
@login_required
def admin_index():
    _check_token()
    stats = {
        "users": User.query.count(),
        "comments": Comment.query.count(),
        "messages": Message.query.count(),
        "chat_messages": ChatMessage.query.count(),
    }
    return render_template("admin/index.html", stats=stats)


@admin_bp.get("/admin/comments")
@login_required
def admin_comments():
    _check_token()
    comments = (
        Comment.query.order_by(Comment.created_at.desc())
        .limit(200)
        .all()
    )
    return render_template("admin/comments.html", comments=comments)


@admin_bp.post("/admin/comments/<int:comment_id>/delete")
@login_required
def admin_comment_delete(comment_id: int):
    _check_token()
    Comment.query.filter_by(id=comment_id).delete()
    db.session.commit()
    return redirect(url_for("admin.admin_comments", token=request.form.get("token")))


@admin_bp.get("/admin/chat")
@login_required
def admin_chat():
    _check_token()
    messages = (
        ChatMessage.query.order_by(ChatMessage.created_at.desc())
        .limit(200)
        .all()
    )
    return render_template("admin/chat.html", messages=messages)


@admin_bp.post("/admin/chat/<int:msg_id>/delete")
@login_required
def admin_chat_delete(msg_id: int):
    _check_token()
    ChatMessage.query.filter_by(id=msg_id).delete()
    db.session.commit()
    return redirect(url_for("admin.admin_chat", token=request.form.get("token")))

