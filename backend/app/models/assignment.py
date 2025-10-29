from datetime import datetime
from app import db


class Assignment(db.Model):
    __tablename__ = "assignments"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    max_marks = db.Column(db.Integer, nullable=False, default=100)
    due_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    class_id = db.Column(db.Integer, db.ForeignKey("classrooms.id"), nullable=False)

    classroom = db.relationship("Classroom", back_populates="assignments")
    submissions = db.relationship("Submission", back_populates="assignment", cascade="all, delete-orphan", lazy="select")
