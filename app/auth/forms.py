from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    PasswordField,
    StringField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    ValidationError,
)

from app.extensions import db
from app.models import User


class RegistrationForm(FlaskForm):
    name = StringField(
        "Full name",
        validators=[
            DataRequired(),
            Length(min=2, max=100),
        ],
    )
    email = StringField(
        "Email address",
        validators=[
            DataRequired(),
            Email(),
            Length(max=255),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8, max=128),
        ],
    )
    confirm_password = PasswordField(
        "Confirm password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
    )
    submit = SubmitField("Create account")

    def validate_email(self, email) -> None:
        email.data = email.data.strip().lower()

        existing_user = db.session.scalar(
            db.select(User).where(User.email == email.data)
        )

        if existing_user is not None:
            raise ValidationError(
                "An account with this email already exists."
            )


class LoginForm(FlaskForm):
    email = StringField(
        "Email address",
        validators=[
            DataRequired(),
            Email(),
            Length(max=255),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(max=128),
        ],
    )
    remember = BooleanField("Remember me")
    submit = SubmitField("Log in")