from datetime import datetime
from sqlalchemy.orm import Session
from app.models.assignment import Assignment
from app.models.classroom import Classroom


class AssignmentService:
    def __init__(self, sa_session: Session) -> None:
        self._session = sa_session

    def post_assignment(self, classroom: Classroom, title: str, description: str, max_marks: int, due_date: datetime) -> Assignment:
        assignment = Assignment(
            title=title,
            description=description,
            max_marks=max_marks,
            due_date=due_date,
            class_id=classroom.id,
        )
        self._session.add(assignment)
        self._session.commit()
        return assignment

    def list_assignments(self, classroom: Classroom) -> list[Assignment]:
        return (
            self._session.query(Assignment)
            .filter_by(class_id=classroom.id)
            .order_by(Assignment.created_at.desc())
            .all()
        )
