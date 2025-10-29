from typing import Optional
from sqlalchemy.orm import Session
from flask_login import login_user
from app import bcrypt
from app.models.user import User


class AuthService:
    def __init__(self, sa_session: Session) -> None:
        self._session = sa_session

    def signup(self, name: str, email: str, password: str, role: str) -> User:
        if role not in ("teacher", "student"):
            raise ValueError("Invalid role")
        if self._session.query(User).filter_by(email=email).first():
            raise ValueError("Email already registered")
        pw_hash = bcrypt.generate_password_hash(password).decode()
        user = User(name=name, email=email, password_hash=pw_hash, role=role)
        self._session.add(user)
        self._session.commit()
        return user

    def login(self, email: str, password: str) -> Optional[User]:
        user = self._session.query(User).filter_by(email=email).first()
        if not user:
            return None
        if not bcrypt.check_password_hash(user.password_hash, password):
            return None
        login_user(user)
        return user
