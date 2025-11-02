from datetime import datetime
from app import db
from .base import TimestampMixin


class Project(TimestampMixin, db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    color = db.Column(db.String(7), default="#3b82f6", nullable=False)  # Hex color code

    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    student = db.relationship("User", back_populates="projects")
    goals = db.relationship("Goal", back_populates="project", cascade="all, delete-orphan", lazy="select", order_by="Goal.created_at.desc()")

    def to_dict(self):
        completed_goals = sum(1 for g in self.goals if g.is_completed)
        total_goals = len(self.goals)
        total_time = sum((g.total_study_time or 0) for g in self.goals)
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "color": self.color,
            "goals_count": total_goals,
            "completed_goals": completed_goals,
            "progress": (completed_goals / total_goals * 100) if total_goals > 0 else 0,
            "total_study_time": total_time,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

