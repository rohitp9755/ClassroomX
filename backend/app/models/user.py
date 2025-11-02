from flask_login import UserMixin
from app import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'teacher' or 'student'

    # Relationships
    teaching_classrooms = db.relationship("Classroom", back_populates="teacher", lazy="select")
    submissions = db.relationship("Submission", back_populates="student", lazy="select")
    projects = db.relationship("Project", back_populates="student", cascade="all, delete-orphan", lazy="select")

    def get_id(self):  # type: ignore[override]
        return str(self.id)


@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))
