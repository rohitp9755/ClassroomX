from datetime import datetime, timedelta
from app import create_app, db, bcrypt
from app.models.user import User
from app.models.classroom import Classroom
from app.models.assignment import Assignment
from app.models.submission import Submission


def main():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        def ph(p: str) -> str:
            return bcrypt.generate_password_hash(p).decode()

        teacher = User(name="Alice Teacher", email="teacher@example.com", password_hash=ph("password"), role="teacher")
        s1 = User(name="Bob Student", email="bob@example.com", password_hash=ph("password"), role="student")
        s2 = User(name="Carol Student", email="carol@example.com", password_hash=ph("password"), role="student")

        db.session.add_all([teacher, s1, s2])
        db.session.commit()

        classroom = Classroom(name="CS101", code="ABC123", teacher_id=teacher.id)
        classroom.students.extend([s1, s2])
        db.session.add(classroom)
        db.session.commit()

        a1 = Assignment(title="Homework 1", description="Intro problems", max_marks=100, due_date=datetime.utcnow() + timedelta(days=7), class_id=classroom.id)
        a2 = Assignment(title="Project 1", description="Small project", max_marks=100, due_date=datetime.utcnow() + timedelta(days=14), class_id=classroom.id)
        db.session.add_all([a1, a2])
        db.session.commit()

        sub1 = Submission(assignment_id=a1.id, student_id=s1.id, content="My answers...", status="submitted")
        sub2 = Submission(assignment_id=a1.id, student_id=s2.id, content="Here it is", status="submitted")
        db.session.add_all([sub1, sub2])
        db.session.commit()

        print("Seeded: teacher, 2 students, 1 class (CS101), 2 assignments, 2 submissions")


if __name__ == "__main__":
    main()
