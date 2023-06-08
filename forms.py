from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, Email, Length, URL, Optional

class AuthForm(FlaskForm):
    """Login form."""

    class Meta:
        """Disable CSRF."""
        csrf = False

    email = StringField(
        'Email',
        validators=[InputRequired(), Email(), Length(max=30)],
    )

    password = PasswordField(
        'Password',
        validators=[InputRequired(), Length(min=6, max=50)],
    )




