from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, IntegerField
from wtforms.validators import InputRequired, Email, Length, URL, Optional

class AuthForm(FlaskForm):
    """Auth form for Login and Signup."""

    class Meta:
        """Disable CSRF."""
        csrf = False

    email = StringField(
        'Email',
        validators=[InputRequired(), Email(), Length(max=50)],
    )

    password = PasswordField(
        'Password',
        validators=[InputRequired(), Length(min=6, max=100)],
    )

class ProfileForm(FlaskForm):
    """Profile form."""

    class Meta:
        """Disable CSRF."""
        csrf = False

    email = StringField(
        'Email',
        validators=[InputRequired(), Email(), Length(max=50)],
    )

    first_name = StringField(
        "First Name",
        validators=[InputRequired(), Length(max=50)],
    )

    last_name = StringField(
        "Last Name",
        validators=[InputRequired(), Length(max=50)],
    )

    zip_code = StringField(
        "Zip Code",
        validators=[InputRequired(), Length(max=50)],
    )

    match_radius = IntegerField(
        "Match Radius",
        validators=[InputRequired()]
    )

    hobbies = StringField(
        "Hobbies",
        validators=[InputRequired()],
    )

    interests = StringField(
        "Interests",
        validators=[InputRequired()],
    )

