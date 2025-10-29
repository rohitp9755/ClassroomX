import random
import string
from sqlalchemy.orm import Session
from app.models.classroom import Classroom
from app.models.user import User


class ClassroomDomain:
    def __init__(self, sa_session: Session, classroom: Classroom | None = None) -> None:
        self._session = sa_session
        self._classroom = classroom

    def generate_code(self, length: int = 6) -> str:
        alphabet = string.ascii_uppercase + string.digits
        return "".join(random.choice(alphabet) for _ in range(length))

    def add_student(self, classroom: Classroom, user: User) -> None:
        if user.role != "student":
            raise ValueError("Only students can join classrooms")
        if user not in classroom.students:
            classroom.students.append(user)
            self._session.commit()

    def remove_student(self, classroom: Classroom, user: User) -> None:
        if user in classroom.students:
            classroom.students.remove(user)
            self._session.commit()
