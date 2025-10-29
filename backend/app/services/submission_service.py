from sqlalchemy.orm import Session
from app.models.submission import Submission
from app.models.assignment import Assignment
from app.models.user import User


class SubmissionService:
    def __init__(self, sa_session: Session) -> None:
        self._session = sa_session

    def submit(self, assignment: Assignment, student: User, content: str) -> Submission:
        submission = (
            self._session.query(Submission)
            .filter_by(assignment_id=assignment.id, student_id=student.id)
            .first()
        )
        if submission is None:
            submission = Submission(assignment_id=assignment.id, student_id=student.id, content=content)
            self._session.add(submission)
        else:
            submission.content = content
            submission.status = "submitted"
        self._session.commit()
        return submission

    def grade(self, submission_id: int, marks: float) -> Submission:
        submission = self._session.get(Submission, submission_id)
        if not submission:
            raise ValueError("Submission not found")
        if marks < 0 or marks > submission.assignment.max_marks:
            raise ValueError("Invalid marks")
        submission.grade = float(marks)
        submission.status = "graded"
        self._session.commit()
        return submission

    def for_assignment(self, assignment: Assignment) -> list[Submission]:
        return (
            self._session.query(Submission)
            .filter_by(assignment_id=assignment.id)
            .order_by(Submission.timestamp.desc())
            .all()
        )
