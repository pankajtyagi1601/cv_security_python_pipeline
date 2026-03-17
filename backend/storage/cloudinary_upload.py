# storage/cloudinary_upload.py
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
import os

load_dotenv()  # loads variables from .env

cloud_name = os.getenv("CLOUD_NAME")
api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")

cloudinary.config(
    cloud_name=cloud_name,
    api_key=api_key,
    api_secret=api_secret
)

def upload_image(image_path):
    """
    Takes a local file path, uploads to Cloudinary.
    Returns a permanent public HTTPS URL.
    """
    result = cloudinary.uploader.upload(
        image_path,
        folder="cv_security_events"
    )
    return result["secure_url"]