from urllib.parse import urljoin, urlparse

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError

from app.auth import auth
from app.auth.forms import LoginForm, RegistrationForm
from app.extensions import db
from app.models import User


def is_safe_redirect_target(target: str | None) -> bool:
    if not target:
        return False

    reference_url = urlparse(request.host_url)
    target_url = urlparse(urljoin(request.host_url, target))

    return (
        target_url.scheme in {"http", "https"}
        and reference_url.netloc == target_url.netloc
    )


@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(
            name=form.name.data.strip(),
            email=form.email.data.strip().lower(),
        )
        user.set_password(form.password.data)

        db.session.add(user)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash(
                "An account with this email already exists.",
                "danger",
            )
            return redirect(url_for("auth.register"))

        login_user(user)

        flash(
            "Your account was created successfully.",
            "success",
        )
        return redirect(url_for("main.home"))

    return render_template("auth/register.html", form=form)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()

        user = db.session.scalar(
            db.select(User).where(User.email == email)
        )

        if user is None or not user.check_password(form.password.data):
            flash(
                "Invalid email address or password.",
                "danger",
            )
            return render_template("auth/login.html", form=form)

        login_user(user, remember=bool(form.remember.data))

        flash("You are now logged in.", "success")

        next_page = request.args.get("next")

        if is_safe_redirect_target(next_page):
            return redirect(next_page)

        return redirect(url_for("main.home"))

    return render_template("auth/login.html", form=form)


@auth.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")

    return redirect(url_for("main.home"))