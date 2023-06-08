import tempfile
from app import s3
from app import bucket_name
from models import db


def upload_pictures_to_s3(file, user):
    """
    takes the files presetent at request.files and uploads them to amazon
    s3 bucket.
    """

    file_name = file.filename
    print(f"filename={file_name} type={type(file_name)}")
    file_content = file.read()

    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(file_content)
    temp_file.close()

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
        return url
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
                "Key": f"users/{user.id}/{user.profile_img_url}",
            },
            ExpiresIn=3600,
        )
        print("url generation successful")
        print("url=", url)
        return url
    except Exception as e:
        return f"Error getting presigned url: {str(e)}"
