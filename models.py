"""SQLAlchemy models for Friender."""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime
from sqlalchemy import Enum
import enum

bcrypt = Bcrypt()
db = SQLAlchemy()

DEFAULT_IMAGE_URL = (
    "https://icon-library.com/images/default-user-icon/" + "default-user-icon-28.jpg"
)


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    app.app_context().push()
    db.app = app
    db.init_app(app)

class Likes(db.Model):
    """represents a match between two users"""

    __tablename__ = "likes"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    liker_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="cascade"))

    likee_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="cascade"))


class Rejects(db.Model):
    """represents a match between two users"""

    __tablename__ = "rejects"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    rejecter_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="cascade"))

    rejectee_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="cascade"))


"""
Like Model
- PK id
- liker_id
- likee_id

scenario 1: camran likes kenny
- like relationship created
- camran appears in kenny.liked_by
- kenny appears in camran.liked


Rejects Model

- kenny rejects camran
- reject relation created
- camran appears in kenny.rejected
- kenny appears in camran.rejected_by

"""

class User(db.Model):
    """User in the system."""

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.String(50),
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.String(100),
        nullable=False,
    )

    first_name = db.Column(
        db.String(50),
        nullable=False,
        default="",
    )

    last_name = db.Column(
        db.String(50),
        nullable=False,
        default="",
    )

    zip_code = db.Column(
        db.String(50),
        nullable=False,
        default="",
    )

    match_radius = db.Column(db.Integer, nullable=False, default=10000)

    profile_img_url = db.Column(
        db.String(255),
        nullable=False,
        default=DEFAULT_IMAGE_URL,
    )

    hobbies = db.Column(
        db.Text,
        nullable=False,
        default="",
    )

    interests = db.Column(
        db.Text,
        nullable=False,
        default="",
    )

    likes = db.relationship(
        "User",
        secondary="likes",
        primaryjoin=(Likes.liker_id == id),
        secondaryjoin=(Likes.likee_id == id),
        backref="liked_by",
    )

    rejects = db.relationship(
        "User",
        secondary="rejects",
        primaryjoin=(Rejects.rejecter_id == id),
        secondaryjoin=(Rejects.rejectee_id == id),
        backref="rejected_by",
    )

    messages = db.relationship("Message", backref="user")

    def __repr__(self):
        return f"<User #{self.id}:, {self.email}>"

    @classmethod
    def signup(cls, username, email, password, image_url=DEFAULT_IMAGE_URL):
        """Sign up user.

        Hashes password and adds user to session.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode("UTF-8")

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If this can't find matching user (or if password is wrong), returns
        False.
        """

        user = cls.query.filter_by(username=username).one_or_none()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

    # method - get potentials

    # get all users within the radius

    # filter previous value to filter the folowing
        #   user.liked
        #   user.rejected
        #   user.rejected_by

    def is_followed_by(self, other_user):
        """Is this user followed by `other_user`?"""

        found_user_list = [user for user in self.followers if user == other_user]
        return len(found_user_list) == 1

    def is_following(self, other_user):
        """Is this user following `other_use`?"""

        found_user_list = [user for user in self.following if user == other_user]
        return len(found_user_list) == 1






# messages
class Messages(db.Model):
    """messages sent between two users"""

    __tablename__ = "messages"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    from_user = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"))

    to_user = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"))

    body = db.Column(db.String(255), db.ForeignKey("users.id", ondelete="cascade"))

    sent_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
