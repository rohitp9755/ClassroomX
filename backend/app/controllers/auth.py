from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import logout_user
from app import db
from app.services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)


@auth_bp.get("/signup")
def signup():
    return render_template("auth/signup.html")


@auth_bp.post("/signup")
def signup_post():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    role = request.form.get("role", "student")
    service = AuthService(db.session)
    try:
        service.signup(name, email, password, role)
        flash("Account created. Please log in.", "success")
        return redirect(url_for("auth.login"))
    except Exception as e:
        flash(str(e), "error")
        return redirect(url_for("auth.signup"))


@auth_bp.get("/login")
def login():
    return render_template("auth/login.html")


@auth_bp.post("/login")
def login_post():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    service = AuthService(db.session)
    user = service.login(email, password)
    if not user:
        flash("Invalid credentials", "error")
        return redirect(url_for("auth.login"))
    if user.role == "teacher":
        return redirect(url_for("teacher.dashboard"))
    return redirect(url_for("student.dashboard"))


@auth_bp.get("/logout")
def logout():
    logout_user()
    return redirect(url_for("public.index"))
