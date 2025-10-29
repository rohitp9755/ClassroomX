from datetime import datetime
from app import db


class Submission(db.Model):
    __tablename__ = "submissions"

    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey("assignments.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    grade = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default="submitted", nullable=False)  # submitted|graded

    assignment = db.relationship("Assignment", back_populates="submissions")
    student = db.relationship("User", back_populates="submissions")
