from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.services.user_class import get_user_by_email, create_user
import secrets
from datetime import datetime, timedelta
from flask import current_app
from itsdangerous import URLSafeSerializer
from datetime import datetime, timezone

from app.services.user_class import (
    get_user_by_email,
    create_user,
    verify_user_email,
    set_reset_token,
    get_user_by_reset_token,
    update_password_with_token
)

from app.services.email_service import send_email

reviews = []
auth_bp = Blueprint("auth", __name__)


# Authentication blueprint
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = get_user_by_email(email)

        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid email or password", "danger")
            return redirect(url_for("main.index", auth="login"))

        # Prevent login until user has confirmed email address
        if not user.is_verified:
            flash("Please verify your email before logging in.", "warning")
            return redirect(url_for("main.index", auth="login"))

        login_user(user)
        flash("Login successful!", "success")
        return redirect(url_for("main.index"))

    return redirect(url_for("main.index", auth="login"))


@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("You have been successfully logged out.")
    return redirect(url_for("main.index"))

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        existing_user = get_user_by_email(email)

        if existing_user:
            flash("That email is already registered. Please log in.", "warning")
            return redirect(url_for("main.index", auth="login"))

        password_hash = generate_password_hash(password)
        verification_token = generate_token()

        create_user(email, password_hash, verification_token)

        verify_link = url_for("auth.verify_email", token=verification_token, _external=True)

        send_email(email, "Verify your email", f"Click here: {verify_link}")

        flash("Registration successful. Check your email to verify your account.", "success")
        return redirect(url_for("main.index", auth="login"))
        

    return redirect(url_for("main.index", auth="register"))

def generate_token():
    """ Generate a secure random token for verification/reset links"""
    return secrets.token_urlsafe(32)



@auth_bp.route("/verify-email/<token>")
def verify_email(token):
    success = verify_user_email(token)

    if success:
        flash("Email verified. You can now log in.", "success")
    else:
        flash("Invalid or expired verification link.", "danger")

    return redirect(url_for("main.index", auth="login"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        user = get_user_by_email(email)

        if user:
            reset_token = generate_token()
            expires_at = datetime.utcnow() + timedelta(hours=1)

            set_reset_token(email, reset_token, expires_at)

            reset_link = url_for("auth.reset_password", token=reset_token, _external=True)

            send_email(email, "Reset your password", f"Click here: {reset_link}")

        flash("If that email exists, a reset link has been sent.", "success")
        return redirect(url_for("main.index", auth="login"))

    return render_template("auth/forgot_password.html")

@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        token_row = get_user_by_reset_token(token)
        print("token_row:", token_row)

        if not token_row:
            flash("Invalid reset link.", "danger")
            return redirect(url_for("main.index", auth="login"))

        expires = token_row["reset_token_expires"]
        print("expires raw:", expires, type(expires))

        if expires is None:
            flash("Reset link has expired.", "danger")
            return redirect(url_for("auth.forgot_password"))

        if isinstance(expires, str):
            expires = datetime.fromisoformat(expires)

        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)

        if datetime.now(timezone.utc) > expires:
            flash("Reset link has expired.", "danger")
            return redirect(url_for("auth.forgot_password"))

        if request.method == "POST":
            password = request.form.get("password")
            password_hash = generate_password_hash(password)
            update_password_with_token(token, password_hash)

            flash("Password reset successful. Please log in.", "success")
            return redirect(url_for("main.index", auth="login"))

        return redirect(url_for("main.index", auth="reset", token=token))

    except Exception as e:
        print("RESET PASSWORD ERROR:", repr(e))
        raise
