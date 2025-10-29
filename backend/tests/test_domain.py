import pytest
from datetime import datetime, timedelta
from app import create_app, db
from app.models.user import User
from app.models.classroom import Classroom
from app.models.assignment import Assignment
from app.domain.classroom_domain import ClassroomDomain
from app.domain.assignment_domain import AssignmentDomain


@pytest.fixture()
def app_ctx():
    app = create_app()
    app.config.update(SQLALCHEMY_DATABASE_URI="sqlite:///:memory:")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def test_add_student_domain(app_ctx):
    s = User(name="Stu", email="s@e.com", password_hash="x", role="student")
    t = User(name="Tea", email="t@e.com", password_hash="x", role="teacher")
    db.session.add_all([s, t])
    db.session.commit()

    c = Classroom(name="C1", code="CODE1", teacher_id=t.id)
    db.session.add(c)
    db.session.commit()

    dom = ClassroomDomain(db.session)
    dom.add_student(c, s)

    assert s in c.students


def test_assignment_is_open(app_ctx):
    t = User(name="Tea", email="t@e.com", password_hash="x", role="teacher")
    db.session.add(t)
    db.session.commit()

    c = Classroom(name="C1", code="CODE1", teacher_id=t.id)
    db.session.add(c)
    db.session.commit()

    future_due = datetime.utcnow() + timedelta(days=1)
    a = Assignment(title="A1", description="", max_marks=100, due_date=future_due, class_id=c.id)
    db.session.add(a)
    db.session.commit()

    dom = AssignmentDomain(db.session, a)
    assert dom.is_open() is True

    a.due_date = datetime.utcnow() - timedelta(days=1)
    db.session.commit()
    assert dom.is_open() is False
