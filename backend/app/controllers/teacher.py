from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import login_required, current_user
from ..utils.role import role_required
from app import db
from app.models.classroom import Classroom
from app.models.assignment import Assignment
from app.services.class_service import ClassService
from app.services.assignment_service import AssignmentService
from app.services.submission_service import SubmissionService

teacher_bp = Blueprint("teacher", __name__)


@teacher_bp.get("/dashboard")
@login_required
@role_required("teacher")
def dashboard():
    classes = db.session.query(Classroom).filter_by(teacher_id=current_user.id).all()
    return render_template("teacher/dashboard.html", classes=classes)


@teacher_bp.get("/classes/new")
@login_required
@role_required("teacher")
def new_class():
    return render_template("teacher/new_class.html")


@teacher_bp.post("/classes")
@login_required
@role_required("teacher")
def create_class():
    name = request.form.get("name", "").strip()
    service = ClassService(db.session)
    classroom = service.create_class(current_user, name)
    return redirect(url_for("teacher.view_class", class_id=classroom.id))


@teacher_bp.get("/classes/<int:class_id>")
@login_required
@role_required("teacher")
def view_class(class_id: int):
    classroom = db.session.get(Classroom, class_id)
    if not classroom or classroom.teacher_id != current_user.id:
        return abort(404)
    return render_template("teacher/class_view.html", classroom=classroom)


@teacher_bp.get("/classes/<int:class_id>/assignments/new")
@login_required
@role_required("teacher")
def new_assignment(class_id: int):
    classroom = db.session.get(Classroom, class_id)
    if not classroom or classroom.teacher_id != current_user.id:
        return abort(404)
    return render_template("teacher/new_assignment.html", classroom=classroom)


@teacher_bp.post("/classes/<int:class_id>/assignments")
@login_required
@role_required("teacher")
def create_assignment(class_id: int):
    classroom = db.session.get(Classroom, class_id)
    if not classroom or classroom.teacher_id != current_user.id:
        return abort(404)
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "")
    max_marks = int(request.form.get("max_marks", 100))
    due_date = request.form.get("due_date")
    from datetime import datetime
    due_dt = datetime.fromisoformat(due_date)
    service = AssignmentService(db.session)
    service.post_assignment(classroom, title, description, max_marks, due_dt)
    return redirect(url_for("teacher.view_class", class_id=class_id))


@teacher_bp.get("/assignments/<int:assignment_id>/submissions")
@login_required
@role_required("teacher")
def view_submissions(assignment_id: int):
    assignment = db.session.get(Assignment, assignment_id)
    if not assignment or assignment.classroom.teacher_id != current_user.id:
        return abort(404)
    return render_template("teacher/submissions.html", assignment=assignment)


@teacher_bp.post("/assignments/<int:assignment_id>/grade")
@login_required
@role_required("teacher")
def grade(assignment_id: int):
    submission_id = int(request.form.get("submission_id"))
    marks = float(request.form.get("marks"))
    svc = SubmissionService(db.session)
    svc.grade(submission_id, marks)
    return redirect(url_for("teacher.view_submissions", assignment_id=assignment_id))
