"""SQLAlchemy models for Friender."""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime
from geoalchemy2 import Geometry, Geography
from sqlalchemy import func
from geoalchemy2.functions import ST_DWithin
from geoalchemy2.elements import WKTElement
from s3_helpers import get_presigned_url
from geo_helpers import get_lat_long_by_zip

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

    liker_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"))

    likee_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"))


class Rejects(db.Model):
    """represents a match between two users"""

    __tablename__ = "rejects"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    rejecter_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"))

    rejectee_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"))


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

    # location = db.Column(Geometry(geometry_type="POINT", srid=4326))
    location = db.Column(Geography(geometry_type="POINT", srid=4326))

    match_radius = db.Column(db.Integer, nullable=False, default=10000)

    profile_img_file_name = db.Column(
        db.String(255),
        nullable=False,
        default="",
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

    # messages = db.relationship("Message", backref="user")

    def __repr__(self):
        return f"<User #{self.id}:, {self.email}>"

    @classmethod
    def signup(cls, email, password):
        """Sign up user.

        Hashes password and adds user to session.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode("UTF-8")

        user = User(
            email=email,
            password=hashed_pwd,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, email, password):
        """Find user with `email` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If this can't find matching user (or if password is wrong), returns
        False.
        """

        user = cls.query.filter_by(email=email).one_or_none()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

    def serialize(self):
        """serializes SQA object to be returned"""
        return {
            "id": self.id,
            "email": self.email,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "hobbies": self.hobbies,
            "interests": self.interests,
            "zipcode": self.zip_code,
            "radius": self.match_radius,
            "profile_img_url": get_presigned_url(self)
            if self.profile_img_file_name != ""
            else DEFAULT_IMAGE_URL,
        }


    def set_location(self):
        """Sets the user location based on their zip code"""
        lat, long = get_lat_long_by_zip(self.zip_code)
        self.location = WKTElement(f"POINT({lat} {long})", srid=4326)

    def nearby_users(self):
        """Gets users within curren users radius"""

        radius = self.match_radius * 1609.34  # convert miles to meters
        nearby_users = User.query.filter(
            func.ST_DWithin(User.location, self.location, radius)
        ).all()

        return nearby_users

    def get_potential_matches(self):
        nearby_users = self.nearby_users()

        users_to_exclude = self.likes + self.rejects + self.rejected_by + [self]

        potential_matches = [
            user.serialize() for user in nearby_users if user not in users_to_exclude
        ]

        return potential_matches

    def get_matches(self):
        matches = [user.serialize() for user in self.likes if user in self.liked_by]
        print('get_matches return=',matches)
        return matches


# # messages
# class Message(db.Model):
#     """messages sent between two users"""

#     __tablename__ = "messages"

#     id = db.Column(
#         db.Integer,
#         primary_key=True,
#     )

#     from_user = db.Column(
#         db.Integer, db.ForeignKey("users.id", ondelete="cascade"))

#     to_user = db.Column(
#         db.Integer, db.ForeignKey("users.id", ondelete="cascade"))

#     body = db.Column(db.String(255), nullable=False)

#     sent_at = db.Column(
#         db.DateTime,
#         nullable=False,
#         default=datetime.utcnow,
#     )
