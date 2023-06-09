import tempfile
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

# s3 client
s3 = boto3.client(
    "s3",
    os.environ["AWS_REGION"],
    aws_access_key_id=os.environ["AWS_ACESS_KEY"],
    aws_secret_access_key=os.environ["AWS_SECRET_KEY"],
)

bucket_name = os.environ["S3_BUCKET"]


def upload_pictures_to_s3(file, user):
    """
    takes the files presetent at request.files and uploads them to amazon
    s3 bucket.
    """

    file_name = file.filename
    file_content = file.read()

    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(file_content)
    temp_file.close()

    try:
        s3.upload_file(temp_file.name, bucket_name, f"users/{user.id}/{file_name}")
        print("File uploaded successfully.")

        return file_name
    except Exception as e:
        return f"Error uploading file: {str(e)}"


def get_presigned_url(user):
    """
    given a user object, get the profile image presigned URL for that user
    """

    try:
        url = s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": bucket_name,
                "Key": f"users/{user.id}/{user.profile_img_file_name}",
            },
            ExpiresIn=3600,
        )
        return url
    except Exception as e:
        return f"Error getting presigned url: {str(e)}"
