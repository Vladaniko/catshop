from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from . import db
from .models import ChatMessage


chat_bp = Blueprint("chat", __name__)


@chat_bp.get("/chat")
@login_required
def chat_page():
    messages = (
        ChatMessage.query.order_by(ChatMessage.created_at.desc())
        .limit(50)
        .all()
    )
    # показываем в порядке от старых к новым
    messages = list(reversed(messages))
    return render_template("chat/chat.html", messages=messages)


@chat_bp.post("/chat")
@login_required
def chat_post():
    content = request.form.get("content", "")
    if not content.strip():
        flash("Сообщение пустое.", "warning")
        return redirect(url_for("chat.chat_page"))

    msg = ChatMessage(user_id=current_user.id, content=content)
    db.session.add(msg)
    db.session.commit()
    return redirect(url_for("chat.chat_page"))

