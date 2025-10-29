from sqlalchemy.orm import Session
from app.models.classroom import Classroom
from app.models.user import User
from app.domain.classroom_domain import ClassroomDomain


class ClassService:
    def __init__(self, sa_session: Session) -> None:
        self._session = sa_session
        self._domain = ClassroomDomain(sa_session)

    def create_class(self, teacher: User, name: str) -> Classroom:
        code = self._domain.generate_code()
        classroom = Classroom(name=name, code=code, teacher_id=teacher.id)
        self._session.add(classroom)
        self._session.commit()
        return classroom

    def join_class(self, student: User, code: str) -> Classroom:
        classroom = self._session.query(Classroom).filter_by(code=code).first()
        if classroom is None:
            raise ValueError("Invalid class code")
        if student not in classroom.students:
            classroom.students.append(student)
            self._session.commit()
        return classroom

    def get_class_stats(self, classroom: Classroom) -> dict:
        return {
            "num_students": len(classroom.students),
            "num_assignments": len(classroom.assignments),
        }
