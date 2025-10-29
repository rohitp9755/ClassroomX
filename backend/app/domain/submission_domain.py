from sqlalchemy.orm import Session
from app.models.submission import Submission


class SubmissionDomain:
    def __init__(self, sa_session: Session, submission: Submission) -> None:
        self._session = sa_session
        self._submission = submission

    def mark_graded(self, mark: float) -> Submission:
        self._submission.grade = float(mark)
        self._submission.status = "graded"
        self._session.commit()
        return self._submission

    def status_label(self) -> str:
        return "Graded" if self._submission.status == "graded" else "Submitted"
