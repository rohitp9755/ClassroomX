from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.classroom import Classroom
from app.models.assignment import Assignment
from app.models.submission import Submission


class UserBase(ABC):
    def __init__(self, sa_session: Session, user_record: User) -> None:
        self._session = sa_session
        self._user = user_record

    def to_safe_dict(self) -> Dict[str, Any]:
        return {"id": self._user.id, "name": self._user.name, "email": self._user.email, "role": self._user.role}

    @abstractmethod
    def role(self) -> str:  # polymorphic interface
        raise NotImplementedError

    def check_password(self, bcrypt, plaintext: str) -> bool:
        return bcrypt.check_password_hash(self._user.password_hash, plaintext)


class Teacher(UserBase):
    def role(self) -> str:
        return "teacher"

    def create_class(self, name: str, code: str) -> Classroom:
        classroom = Classroom(name=name, code=code, teacher_id=self._user.id)
        self._session.add(classroom)
        self._session.commit()
        return classroom

    def post_assignment(self, class_id: int, title: str, description: str, max_marks: int, due_date) -> Assignment:
        assignment = Assignment(title=title, description=description, max_marks=max_marks, due_date=due_date, class_id=class_id)
        self._session.add(assignment)
        self._session.commit()
        return assignment

    def grade_submission(self, submission_id: int, marks: float) -> Submission:
        submission = self._session.get(Submission, submission_id)
        if submission is None:
            raise ValueError("Submission not found")
        if marks < 0:
            raise ValueError("Marks must be non-negative")
        if marks > submission.assignment.max_marks:
            raise ValueError("Marks exceed maximum")
        submission.grade = float(marks)
        submission.status = "graded"
        self._session.commit()
        return submission


class Student(UserBase):
    def role(self) -> str:
        return "student"

    def join_class(self, code: str) -> Classroom:
        classroom = self._session.query(Classroom).filter_by(code=code).first()
        if classroom is None:
            raise ValueError("Invalid class code")
        # Append only if not already enrolled
        if self._user not in classroom.students:
            classroom.students.append(self._user)
            self._session.commit()
        return classroom

    def submit_assignment(self, assignment_id: int, content: str) -> Submission:
        assignment = self._session.get(Assignment, assignment_id)
        if assignment is None:
            raise ValueError("Assignment not found")
        submission = (
            self._session.query(Submission)
            .filter_by(assignment_id=assignment_id, student_id=self._user.id)
            .first()
        )
        if submission is None:
            submission = Submission(assignment_id=assignment_id, student_id=self._user.id, content=content)
            self._session.add(submission)
        else:
            submission.content = content
            submission.status = "submitted"
        self._session.commit()
        return submission

    def view_my_submission(self, assignment_id: int) -> Submission | None:
        return (
            self._session.query(Submission)
            .filter_by(assignment_id=assignment_id, student_id=self._user.id)
            .first()
        )
