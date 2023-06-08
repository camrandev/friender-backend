import os
from dotenv import load_dotenv

from flask import Flask, request, session, g, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
    JWTManager,
)
import boto3
import tempfile
from models import connect_db, db, User
from forms import AuthForm, ProfileForm
from werkzeug.datastructures import MultiDict

load_dotenv()

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_ECHO"] = False
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = True
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
# toolbar = DebugToolbarExtension(app)
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)

connect_db(app)

# s3 client
s3 = boto3.client(
    "s3",
    os.environ["AWS_REGION"],
    aws_access_key_id=os.environ["AWS_ACESS_KEY"],
    aws_secret_access_key=os.environ["AWS_SECRET_KEY"],
)

bucket_name = os.environ["S3_BUCKET"]


# receive POST file upload from front-end
# have user in g.user global context
@app.route("/user/<path:email>/s3", methods=["POST"])
def pictures(email):
    """
    basic route to test our S3 config
    """

    user = User.query.filter_by(email=email).first()

    if not user:
        raise NameError("a user with this email does not exist")

    # Need to access user ID from request as well, plug that in

    file = request.files["test_file"]
    file_name = file.filename
    print(f"filename={file_name} type={type(file_name)}")
    file_content = file.read()

    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(file_content)
    temp_file.close()

    print(f"{request.files['test_file'].filename}")

    try:
        s3.upload_file(temp_file.name, bucket_name, f"users/{user.id}/{file_name}")
        print("File uploaded successfully.")
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": f"users/{user.id}/{file_name}"},
            ExpiresIn=3600,
        )
        user.profile_img_url = file_name
        db.session.commit()
        return jsonify(url=url), 201
    except Exception as e:
        print(f"Error uploading file: {str(e)}")

    return jsonify(error="something went wrong with the upload"), 500


@app.route("/user/<path:email>/s3", methods=["GET"])
def get_file(email):
    """
    testing getting a file from S3
    """

    user = User.query.filter_by(email=email).first()

    if not user:
        raise NameError("a user with this email does not exist")

    try:
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key":  f"users/{user.id}/{file_name}"},
            ExpiresIn=3600,
        )
        print("url generation successful")
        print("url=", url)
        return url
    except Exception as e:
        print(f"Error uploading file: {str(e)}")

    return "after try-except"


### User Routes
@app.route("/user/<path:email>/potentials", methods=["GET"])
def get_potential_matches(email):
    user = User.query.filter_by(email=email).first()

    if not user:
        raise NameError("a user with this email does not exist")
    # call user.getPotentials
    potentials = user.get_potential_matches()
    print("potentials", potentials)

    return jsonify(potentials=potentials)


@app.route("/user/<path:email>", methods=["GET"])
def get_one_user(email):
    user = User.query.filter_by(email=email).first()
    print("user=", user)
    if not user:
        raise NameError("a user with this email does not exist")

    user = user.serialize()
    return jsonify(user=user)


@app.route("/user/<path:email>/update", methods=["PATCH", "PUT"])
def update_profile(email):
    user = User.query.filter_by(email=email).first()
    if not user:
        raise NameError("a user with this email does not exist")

    email = request.json.get("email", None)
    first_name = request.json.get("firstName", None)
    last_name = request.json.get("lastName", None)
    hobbies = request.json.get("hobbies", None)
    interests = request.json.get("interests", None)
    zip_code = request.json.get("zipcode", None)
    match_radius = request.json.get("radius", None)
    profile_img_url = request.json.get("img_url", None)

    data = {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "hobbies": hobbies,
        "interests": interests,
        "zip_code": zip_code,
        "match_radius": match_radius,
        "profile_img_url": profile_img_url,
    }

    form = ProfileForm(MultiDict(data))

    print("\n\n\nform.data=", form.data)

    if form.validate():
        user.email = request.json.get("email", user.email)
        user.first_name = request.json.get("firstName", user.first_name)
        user.last_name = request.json.get("lastName", user.last_name)
        user.hobbies = request.json.get("hobbies", user.hobbies)
        user.interests = request.json.get("interests", user.interests)
        user.zip_code = request.json.get("zipcode", user.zip_code)
        user.match_radius = request.json.get("radius", user.match_radius)
        user.profile_img_url = request.json.get("img_url", user.profile_img_url)
        db.session.commit()

        return jsonify(user=user.serialize())
    else:
        return jsonify({"errors": form.errors}), 400

@app.route("/user/<path:email>/likes", methods=["POST"])
def likes(email):
    print('email=',email)
    likee_id = request.json.get("likeeId", None)
    user = User.query.filter_by(email=email).first()
    likee = User.query.get_or_404(likee_id)

    print('user=',user)
    print('likee=',likee)
    user.likes.append(likee)
    db.session.commit()
    return jsonify(user=user.serialize()), 201

@app.route("/user/<path:email>/rejects", methods=["POST"])
def rejects(email):
    print('email=',email)
    rejectee_id = request.json.get("rejecteeId", None)
    user = User.query.filter_by(email=email).first()
    rejectee = User.query.get_or_404(rejectee_id)

    print('user=',user)
    print('rejectee=',rejectee)
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
    print("form=", form.data)

    # TODO: catch validation errors and return them
    if form.validate_on_submit():
        print("\n\n\n0validated\n\n\n")
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
    print(email, password)

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


# for Update Profile route
# from geoalchemy2.elements import WKTElement

# # For instance, to set the location of a user at latitude 12.34 and longitude 56.78:
# user.location = WKTElement(f'POINT(12.34 56.78)', srid=4326)
