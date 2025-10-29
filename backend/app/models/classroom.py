from app import db
from .base import classroom_students


class Classroom(db.Model):
    __tablename__ = "classrooms"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False, index=True)

    teacher_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    teacher = db.relationship("User", back_populates="teaching_classrooms")
    students = db.relationship("User", secondary=classroom_students, lazy="select")
    assignments = db.relationship("Assignment", back_populates="classroom", cascade="all, delete-orphan", lazy="select")
