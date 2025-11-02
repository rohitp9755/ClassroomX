from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, abort, jsonify
from flask_login import login_required, current_user
from ..utils.role import role_required
from app import db
from app.models.classroom import Classroom
from app.models.assignment import Assignment
from app.models.project import Project
from app.models.goal import Goal
from app.models.study_session import StudySession
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


# Study Tracker Endpoints
@student_bp.get("/tracker")
@login_required
@role_required("student")
def tracker_dashboard():
    projects = db.session.query(Project).filter_by(student_id=current_user.id).order_by(Project.created_at.desc()).all()
    
    # Calculate analytics
    total_projects = len(projects)
    total_goals = sum(len(p.goals) for p in projects)
    completed_goals = sum(sum(1 for g in p.goals if g.is_completed) for p in projects)
    total_study_time = sum(sum((g.total_study_time or 0) for g in p.goals) for p in projects)
    
    # Recent sessions (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_sessions = db.session.query(StudySession).join(Goal).join(Project).filter(
        Project.student_id == current_user.id,
        StudySession.start_time >= week_ago
    ).order_by(StudySession.start_time.desc()).limit(10).all()
    
    return render_template("student/tracker_dashboard.html", 
                         projects=projects,
                         total_projects=total_projects,
                         total_goals=total_goals,
                         completed_goals=completed_goals,
                         total_study_time=total_study_time,
                         recent_sessions=recent_sessions)


@student_bp.post("/tracker/projects")
@login_required
@role_required("student")
def create_project():
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    color = request.form.get("color", "#3b82f6")
    
    if not name:
        return redirect(url_for("student.tracker_dashboard"))
    
    project = Project(
        name=name,
        description=description if description else None,
        color=color,
        student_id=current_user.id
    )
    db.session.add(project)
    db.session.commit()
    return redirect(url_for("student.tracker_dashboard"))


@student_bp.post("/tracker/projects/<int:project_id>/goals")
@login_required
@role_required("student")
def create_goal(project_id: int):
    project = db.session.get(Project, project_id)
    if not project or project.student_id != current_user.id:
        return abort(403)
    
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    target_date_str = request.form.get("target_date", "")
    target_date = datetime.fromisoformat(target_date_str.replace("Z", "+00:00")) if target_date_str else None
    
    if not title:
        return redirect(url_for("student.tracker_dashboard"))
    
    goal = Goal(
        title=title,
        description=description if description else None,
        target_date=target_date,
        project_id=project_id
    )
    db.session.add(goal)
    db.session.commit()
    return redirect(url_for("student.tracker_dashboard"))


@student_bp.post("/tracker/goals/<int:goal_id>/toggle")
@login_required
@role_required("student")
def toggle_goal(goal_id: int):
    goal = db.session.get(Goal, goal_id)
    if not goal or goal.project.student_id != current_user.id:
        return abort(403)
    
    if goal.is_completed:
        goal.mark_incomplete()
    else:
        goal.mark_complete()
    
    db.session.commit()
    return jsonify({"is_completed": goal.is_completed})


@student_bp.post("/tracker/goals/<int:goal_id>/delete")
@login_required
@role_required("student")
def delete_goal(goal_id: int):
    goal = db.session.get(Goal, goal_id)
    if not goal or goal.project.student_id != current_user.id:
        return abort(403)
    
    db.session.delete(goal)
    db.session.commit()
    return redirect(url_for("student.tracker_dashboard"))


@student_bp.post("/tracker/projects/<int:project_id>/delete")
@login_required
@role_required("student")
def delete_project(project_id: int):
    project = db.session.get(Project, project_id)
    if not project or project.student_id != current_user.id:
        return abort(403)
    
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for("student.tracker_dashboard"))


@student_bp.post("/tracker/sessions")
@login_required
@role_required("student")
def create_session():
    goal_id = request.form.get("goal_id", type=int)
    duration = request.form.get("duration", type=int)  # in seconds
    notes = request.form.get("notes", "").strip()
    
    if not goal_id or not duration or duration <= 0:
        return jsonify({"error": "Invalid session data"}), 400
    
    goal = db.session.get(Goal, goal_id)
    if not goal or goal.project.student_id != current_user.id:
        return abort(403)
    
    session = StudySession(
        goal_id=goal_id,
        duration=duration,
        notes=notes if notes else None,
        end_time=datetime.utcnow()
    )
    
    # Update goal's total study time
    goal.total_study_time = (goal.total_study_time or 0) + duration
    
    db.session.add(session)
    db.session.commit()
    
    return jsonify({"success": True, "session_id": session.id})


@student_bp.get("/tracker/analytics")
@login_required
@role_required("student")
def tracker_analytics():
    projects = db.session.query(Project).filter_by(student_id=current_user.id).all()
    
    # Weekly study time (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    weekly_sessions = db.session.query(StudySession).join(Goal).join(Project).filter(
        Project.student_id == current_user.id,
        StudySession.start_time >= week_ago
    ).all()
    
    daily_time = {}
    for session in weekly_sessions:
        day = session.start_time.date().isoformat()
        daily_time[day] = daily_time.get(day, 0) + session.duration
    
    # Generate last 7 days data for chart
    chart_data = []
    for i in range(7):
        date = (datetime.utcnow() - timedelta(days=6-i)).date()
        date_key = date.isoformat()
        chart_data.append({
            "date": date_key,
            "day_name": date.strftime('%A')[:3],
            "hours": daily_time.get(date_key, 0) / 3600
        })
    
    # Project progress stats
    project_stats = []
    for project in projects:
        completed = sum(1 for g in project.goals if g.is_completed)
        total = len(project.goals)
        project_stats.append({
            "name": project.name,
            "progress": (completed / total * 100) if total > 0 else 0,
            "total_goals": total,
            "completed_goals": completed,
        })
    
    return render_template("student/tracker_analytics.html",
                         daily_time=daily_time,
                         chart_data=chart_data,
                         project_stats=project_stats,
                         projects=projects)
