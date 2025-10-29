from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import login_required, current_user
from ..utils.role import role_required
from app import db
from app.models.classroom import Classroom
from app.models.assignment import Assignment
from app.services.class_service import ClassService
from app.services.submission_service import SubmissionService

student_bp = Blueprint("student", __name__)


@student_bp.get("/dashboard")
@login_required
@role_required("student")
def dashboard():
    classes = (
        db.session.query(Classroom)
        .join(Classroom.students)
        .filter_by(id=current_user.id)
        .all()
    )
    return render_template("student/dashboard.html", classes=classes)


@student_bp.post("/classes/join")
@login_required
@role_required("student")
def join_class():
    code = request.form.get("class_code", "").strip().upper()
    svc = ClassService(db.session)
    classroom = svc.join_class(current_user, code)
    return redirect(url_for("student.view_class", class_id=classroom.id))


@student_bp.get("/classes/<int:class_id>")
@login_required
@role_required("student")
def view_class(class_id: int):
    classroom = db.session.get(Classroom, class_id)
    if not classroom or current_user not in classroom.students:
        return abort(404)
    return render_template("student/class_view.html", classroom=classroom)


@student_bp.get("/assignments/<int:assignment_id>")
@login_required
@role_required("student")
def view_assignment(assignment_id: int):
    assignment = db.session.get(Assignment, assignment_id)
    if not assignment:
        return abort(404)
    if current_user not in assignment.classroom.students:
        return abort(403)
    submission = (
        db.session.query(Assignment).get(assignment_id).submissions
    )
    # We'll let the template compute status by finding current user's submission
    return render_template("student/assignment_view.html", assignment=assignment)


@student_bp.post("/assignments/<int:assignment_id>/submit")
@login_required
@role_required("student")
def submit_assignment(assignment_id: int):
    assignment = db.session.get(Assignment, assignment_id)
    if not assignment:
        return abort(404)
    if current_user not in assignment.classroom.students:
        return abort(403)
    content = request.form.get("content", "")
    svc = SubmissionService(db.session)
    svc.submit(assignment, current_user, content)
    return redirect(url_for("student.view_assignment", assignment_id=assignment_id))
