from __future__ import annotations

from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from . import db, login_manager


class Friendship(db.Model):
    __tablename__ = "friendships"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    friend_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint("user_id", "friend_id", name="uq_friendship_pair"),
    )


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    bio = db.Column(db.Text, default="", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))


class Cat(db.Model):
    __tablename__ = "cats"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, index=True)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False, default="")
    image_url = db.Column(db.String(512), nullable=False, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    cat_id = db.Column(db.Integer, db.ForeignKey("cats.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", lazy="joined")
    cat = db.relationship("Cat", lazy="joined")


class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    sender = db.relationship("User", foreign_keys=[sender_id], lazy="joined")
    receiver = db.relationship("User", foreign_keys=[receiver_id], lazy="joined")


class ChatMessage(db.Model):
    __tablename__ = "chat_messages"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", lazy="joined")


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    items = db.relationship("OrderItem", back_populates="order", lazy="joined")


class OrderItem(db.Model):
    __tablename__ = "order_items"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False, index=True)
    cat_id = db.Column(db.Integer, db.ForeignKey("cats.id"), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price_at_moment = db.Column(db.Integer, nullable=False)

    order = db.relationship("Order", back_populates="items")
    cat = db.relationship("Cat", lazy="joined")


def seed_initial_data() -> None:
    # Cats catalog seed
    if Cat.query.count() == 0:
        cats = [
            Cat(
                name="Pixel Paws",
                price=120,
                description="Спокойный котик для уютных вечеров. Любит окна и тёплые пледы.",
                image_url="https://images.unsplash.com/photo-1518791841217-8f162f1e1131?auto=format&fit=crop&w=1200&q=80",
            ),
            Cat(
                name="Shadow Whiskers",
                price=250,
                description="Ночной охотник за лазером. Отлично подходит для тренировки реакции.",
                image_url="https://images.unsplash.com/photo-1511044568932-338cba0ad803?auto=format&fit=crop&w=1200&q=80",
            ),
            Cat(
                name="Sunny Loaf",
                price=180,
                description="Профессиональный «батон». Занимает место на клавиатуре мгновенно.",
                image_url="https://images.unsplash.com/photo-1543852786-1cf6624b9987?auto=format&fit=crop&w=1200&q=80",
            ),
            Cat(
                name="Captain Meow",
                price=420,
                description="Котик-босс. Смотрит на твой код и молча осуждает. Очень редкий.",
                image_url="https://images.unsplash.com/photo-1516972810927-80185027ca84?auto=format&fit=crop&w=1200&q=80",
            ),
        ]
        db.session.add_all(cats)
        db.session.commit()

