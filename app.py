import os
from dotenv import load_dotenv

from flask import Flask, request, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
import boto3

load_dotenv()

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
toolbar = DebugToolbarExtension(app)


# will be built in db model file
# connect_db(app)

#
s3 = boto3.client(
  "s3",
  os.environ['AWS_REGION'],
  aws_access_key_id=os.environ['AWS_ACESS_KEY'],
  aws_secret_access_key=os.environ['AWS_SECRET_KEY']
)

bucket_name = os.environ['S3_BUCKET']

# receive POST file upload from front-end
# have user in g.user global context
@app.route('/s3', methods=["GET", "POST"])
def pictures():
    """
    basic route to test our S3 config
    """

# f'users/{g.user.id}/{os.path.basename(file_path)}'
    try:
        s3.upload_file('./test_s3.txt', bucket_name, "test")
        print("File uploaded successfully.")
    except Exception as e:
        print(f"Error uploading file: {str(e)}")

    return s3
