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
from forms import AuthForm

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
@app.route("/s3", methods=["POST"])
def pictures():
    """
    basic route to test our S3 config
    """

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
        s3.upload_file(temp_file.name, bucket_name, f"users/1/{file_name}")
        print("File uploaded successfully.")
    except Exception as e:
        print(f"Error uploading file: {str(e)}")

    return "hi"


@app.route("/s3", methods=["GET"])
def get_file():
    """
    testing getting a file from S3
    """

    try:
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": "users/test_s3.txt"},
            ExpiresIn=3600,
        )
        print("url generation successful")
        print("url=", url)
        return url
    except Exception as e:
        print(f"Error uploading file: {str(e)}")

    return "after try-except"


# auth routes
@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = AuthForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                password=form.password.data,
                email=form.email.data,
            )
            db.session.commit()

        except IntegrityError:
            error = {"error":"email already exists"}
            return jsonify(error)

        do_login(user)

        return redirect("/")

    else:
        return render_template("users/signup.html", form=form)


@app.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    print(email, password)
    if email != "test" or password != "test":
        return jsonify({"msg": "Bad email or password"}), 401

    access_token = create_access_token(identity=email)
    return jsonify(access_token=access_token)


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
