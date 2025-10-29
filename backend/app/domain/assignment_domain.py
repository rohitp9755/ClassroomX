from datetime import datetime
from statistics import mean
from sqlalchemy.orm import Session
from app.models.assignment import Assignment


class AssignmentDomain:
    def __init__(self, sa_session: Session, assignment: Assignment) -> None:
        self._session = sa_session
        self._assignment = assignment

    def is_open(self) -> bool:
        return datetime.utcnow() <= self._assignment.due_date

    def submission_count(self) -> int:
        return len(self._assignment.submissions)

    def average_grade(self) -> float | None:
        grades = [s.grade for s in self._assignment.submissions if s.grade is not None]
        return mean(grades) if grades else None
