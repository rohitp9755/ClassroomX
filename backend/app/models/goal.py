from datetime import datetime
from app import db
from .base import TimestampMixin


class Goal(TimestampMixin, db.Model):
    __tablename__ = "goals"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_completed = db.Column(db.Boolean, default=False, nullable=False)
    target_date = db.Column(db.DateTime, nullable=True)
    total_study_time = db.Column(db.Integer, default=0, nullable=False)  # Total seconds studied

    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    project = db.relationship("Project", back_populates="goals")
    sessions = db.relationship("StudySession", back_populates="goal", cascade="all, delete-orphan", lazy="select", order_by="StudySession.start_time.desc()")

    def mark_complete(self):
        if not self.is_completed:
            self.is_completed = True
            self.completed_at = datetime.utcnow()

    def mark_incomplete(self):
        if self.is_completed:
            self.is_completed = False
            self.completed_at = None

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "is_completed": self.is_completed,
            "target_date": self.target_date.isoformat() if self.target_date else None,
            "total_study_time": self.total_study_time,
            "sessions_count": len(self.sessions),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

