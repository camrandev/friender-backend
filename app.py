import os
from dotenv import load_dotenv

from flask import Flask, request, g, jsonify
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
    JWTManager,
)
from models import connect_db, db, User, Message
from forms import AuthForm, ProfileForm
from werkzeug.datastructures import MultiDict
from s3_helpers import s3, upload_pictures_to_s3, get_presigned_url
from flask_sock import Sock

from datetime import datetime
import asyncio

load_dotenv()

CURR_USER_KEY = "curr_user"

app = Flask(__name__)
CORS(app)
sock = Sock(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_ECHO"] = False
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = True
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
# toolbar = DebugToolbarExtension(app)
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)

connect_db(app)


### User Routes
@app.route("/user/<path:email>/potentials", methods=["GET"])
def get_potential_matches(email):
    user = User.query.filter_by(email=email).first()

    if not user:
        raise NameError("a user with this email does not exist")
    # call user.getPotentials
    potentials = user.get_potential_matches()


    return jsonify(potentials=potentials)

@app.route("/user/<path:email>/matches", methods=["GET"])
def get_matches(email):
    user = User.query.filter_by(email=email).first()

    if not user:
        raise NameError("a user with this email does not exist")
    # call user.getmatches
    matches = user.get_matches()


    return jsonify(matches=matches)


@app.route("/user/<path:email>", methods=["GET"])
def get_one_user(email):
    user = User.query.filter_by(email=email).first()
    if not user:
        raise NameError("a user with this email does not exist")

    user = user.serialize()
    return jsonify(user=user)


@app.route("/user/<path:email>/update", methods=["PATCH", "PUT"])
def update_profile(email):
    user = User.query.filter_by(email=email).first()
    if not user:
        raise NameError("a user with this email does not exist")


    email = request.form.get("email", user.email)
    first_name = request.form.get("firstName", user.first_name)
    last_name = request.form.get("lastName", user.last_name)
    hobbies = request.form.get("hobbies", user.hobbies)
    interests = request.form.get("interests", user.interests)
    zip_code = request.form.get("zipcode", user.zip_code)
    match_radius = request.form.get("radius", user.match_radius)
    profile_image_file = request.files.get("profileImg", None)

    data = {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "hobbies": hobbies,
        "interests": interests,
        "zip_code": zip_code,
        "match_radius": match_radius,
    }

    form = ProfileForm(MultiDict(data))


    if form.validate():
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.hobbies = hobbies
        user.interests = interests
        user.zip_code = zip_code
        user.match_radius = match_radius

        user.set_location()
        if profile_image_file:
            user.profile_img_file_name = upload_pictures_to_s3(profile_image_file, user)

        db.session.commit()

        return jsonify(user=user.serialize())
    else:
        return jsonify({"errors": form.errors}), 400


@app.route("/user/<path:email>/likes", methods=["POST"])
def likes(email):
    likee_id = request.json.get("likeeId", None)
    user = User.query.filter_by(email=email).first()
    likee = User.query.get_or_404(likee_id)

    user.likes.append(likee)
    db.session.commit()
    return jsonify(potentials=user.get_potential_matches()), 201


@app.route("/user/<path:email>/rejects", methods=["POST"])
def rejects(email):
    rejectee_id = request.json.get("rejecteeId", None)
    user = User.query.filter_by(email=email).first()
    rejectee = User.query.get_or_404(rejectee_id)

    user.rejects.append(rejectee)
    db.session.commit()
    return jsonify(user=user.serialize()), 201


# auth routes
@app.route("/signup", methods=["POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    form = AuthForm(data={"email": email, "password": password})

    # TODO: catch validation errors and return them
    if form.validate_on_submit():
        try:
            user = User.signup(
                email=email,
                password=password,
            )
            db.session.commit()
            access_token = create_access_token(identity=user.email)
            return jsonify(access_token=access_token), 201
        except IntegrityError:
            error = {"error": "email already exists"}
            return jsonify(error)
    else:
        return jsonify({"errors": form.errors}), 400


@app.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    form = AuthForm(data={"email": email, "password": password})

    if form.validate_on_submit():
        user = User.authenticate(
            email=email,
            password=password,
        )
        if user:
            access_token = create_access_token(identity=user.email)
            return jsonify(access_token=access_token)
        else:
            error = {"error": "Credentials did not authenticate."}
            return jsonify(error)
    else:
        return jsonify({"errors": form.errors}), 400


# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200



# Route for getting all messages between to matched users
#  /user/email/matches/email2
# do the query
# from sqlalchemy import or_

@app.route("/user/<from_email>/matches/<to_email>", methods=["GET"])
def get_messages_between_users():
    user_email_1 = "user1@example.com"
    user_email_2 = "user2@example.com"

    messages = Message.query.join(
        User,
        or_(User.id == Message.from_user, User.id == Message.to_user)).filter(or_(
        User.email == user_email_1, User.email == user_email_2)).order_by(
        Message.sent_at).all()

    return jsonify(messages=messages), 200


# WebSockets

# Global mapping of email to WebSocket
ws_map = {}

@sock.route('/user/<from_email>/chat/<to_email>')
async def chat(ws, from_email, to_email):
    print("\n\n Hit the WebSocket \n\n")
    from_user = User.query.filter_by(email=from_email).first()
    to_user = User.query.filter_by(email=to_email).first()


    if not from_user or not to_user:
        await ws.send("Invalid user email")
        return

    # Add WebSocket to global map
    ws_map[from_email] = ws

    while True:
        msg = await ws.receive()
        message = Message(from_user=from_user.id, to_user=to_user.id, body=msg, sent_at=datetime.utcnow())
        db.session.add(message)
        db.session.commit()

        # Send the message to the `to_user` if they are currently connected
        if to_email in ws_map:
            await ws_map[to_email].send(msg)

        await ws.send(f"Message sent at {message.sent_at}")


