from datetime import datetime
from app import db


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


# Association table: many-to-many Classroom <-> User (students)
classroom_students = db.Table(
    "classroom_students",
    db.Column("classroom_id", db.Integer, db.ForeignKey("classrooms.id"), primary_key=True),
    db.Column("student_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
)
