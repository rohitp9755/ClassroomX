
# ClassroomX

A Google Classroom–style web app (college project level) demonstrating OOP principles in Python using Flask, SQLAlchemy, Flask-Login, and Tailwind CSS (Jinja2 templates). Uses SQLite for easy local setup.

## Tech Stack
- Backend: Python 3.x, Flask (Blueprints)
- ORM: SQLAlchemy (SQLite)
- Auth: Flask-Login + Flask-Bcrypt
- Frontend: HTML + Tailwind CSS (CDN) with Jinja2
- Testing: pytest
- Optional: Flask-Migrate, python-dotenv

## Project Structure
backend/app/
- models: SQLAlchemy models (`User`, `Classroom`, `Assignment`, `Submission`)
- domain: OOP business logic wrappers (encapsulation, inheritance, polymorphism)
- services: app services consuming domain/models (`AuthService`, `ClassService`, etc.)
- controllers: Flask blueprints (public, auth, teacher, student)
- templates: Jinja2 views styled with Tailwind
- utils: `role_required` decorator

## Setup
```bash
python -m venv venv
. venv/Scripts/Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
# Create .env with:
# FLASK_ENV=development
# SECRET_KEY=dev-secret-change-me
# DATABASE_URL=sqlite:///dev.db
python backend/seed.py
python backend/run.py
```

Alternatively, with Flask CLI:
```bash
$env:FLASK_APP="backend/app"
flask run
```

## Tests
```bash
pytest
```
Tests included:
- Domain: `ClassroomDomain.add_student()` and `AssignmentDomain.is_open()`
- Service: `AuthService` signup/login + hashing

## OOP Design
- User domain hierarchy: `UserBase` (abstract) with `Teacher` and `Student` implementing role-specific behavior
- Domain classes use dependency injection of SQLAlchemy session
- Services orchestrate persistence + domain rules; controllers remain thin

## Basic Flows
- Teacher: login → dashboard → create class (generates code) → create assignments → view/grade submissions
- Student: signup/login → dashboard → join class via code → view assignments → submit → view grade

## Seed Data
`python backend/seed.py` creates:
- 1 teacher (teacher@example.com / password)
- 2 students (bob@example.com, carol@example.com / password)
- 1 class `CS101` with code `ABC123`
- 2 assignments and 2 submissions

## Notes
- CSRF kept simple for college scope (use at your discretion)
- Tailwind via CDN to avoid build steps
- SQLite file `dev.db` in project directory
