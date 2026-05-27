from __future__ import annotations

from flask import Blueprint, abort, jsonify, render_template, request
from flask_login import current_user, login_required

from . import db
from .models import Friendship, Message, Order, User


social_bp = Blueprint("social", __name__)


def _is_friend(user_id: int, other_id: int) -> bool:
    return (
        Friendship.query.filter_by(user_id=user_id, friend_id=other_id).first()
        is not None
    )


@social_bp.get("/users")
@login_required
def users_search_page():
    q = request.args.get("q", "").strip()
    users = []
    if q:
        users = (
            User.query.filter(User.username.ilike(f"%{q}%"))
            .order_by(User.username.asc())
            .limit(50)
            .all()
        )
    return render_template("social/users.html", q=q, users=users)


@social_bp.get("/api/users/search")
@login_required
def api_users_search():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"results": []})

    users = (
        User.query.filter(User.username.ilike(f"%{q}%"))
        .order_by(User.username.asc())
        .limit(20)
        .all()
    )
    results = []
    for u in users:
        if u.id == current_user.id:
            continue
        results.append(
            {
                "username": u.username,
                "email": u.email,
                "is_friend": _is_friend(current_user.id, u.id),
            }
        )
    return jsonify({"results": results})


@social_bp.get("/u/<string:username>")
@login_required
def profile(username: str):
    u = User.query.filter_by(username=username).first_or_404()
    is_me = u.id == current_user.id
    is_friend = False if is_me else _is_friend(current_user.id, u.id)

    friends = (
        User.query.join(Friendship, Friendship.friend_id == User.id)
        .filter(Friendship.user_id == u.id)
        .order_by(User.username.asc())
        .limit(200)
        .all()
    )

    inbox = []
    orders = []
    if is_me:
        inbox = (
            Message.query.filter_by(receiver_id=current_user.id)
            .order_by(Message.created_at.desc())
            .limit(50)
            .all()
        )
        orders = (
            Order.query.filter_by(user_id=current_user.id)
            .order_by(Order.created_at.desc())
            .limit(20)
            .all()
        )

    return render_template(
        "social/profile.html",
        profile_user=u,
        is_me=is_me,
        is_friend=is_friend,
        friends=friends,
        inbox=inbox,
        orders=orders,
    )


@social_bp.post("/api/friends/add")
@login_required
def api_friend_add():
    username = (request.form.get("username") or "").strip()
    if not username:
        abort(400)
    u = User.query.filter_by(username=username).first()
    if not u or u.id == current_user.id:
        abort(404)

    if not _is_friend(current_user.id, u.id):
        db.session.add(Friendship(user_id=current_user.id, friend_id=u.id))
        db.session.commit()

    return jsonify({"ok": True, "is_friend": True})


@social_bp.post("/api/friends/remove")
@login_required
def api_friend_remove():
    username = (request.form.get("username") or "").strip()
    if not username:
        abort(400)
    u = User.query.filter_by(username=username).first()
    if not u or u.id == current_user.id:
        abort(404)

    Friendship.query.filter_by(user_id=current_user.id, friend_id=u.id).delete()
    db.session.commit()
    return jsonify({"ok": True, "is_friend": False})


@social_bp.post("/messages/send")
@login_required
def send_message():
    to_username = (request.form.get("to") or "").strip()
    content = request.form.get("content", "")
    if not to_username:
        abort(400)

    receiver = User.query.filter_by(username=to_username).first()
    if not receiver:
        abort(404)

    if not content.strip():
        abort(400)

    msg = Message(sender_id=current_user.id, receiver_id=receiver.id, content=content)
    db.session.add(msg)
    db.session.commit()
    return jsonify({"ok": True})

