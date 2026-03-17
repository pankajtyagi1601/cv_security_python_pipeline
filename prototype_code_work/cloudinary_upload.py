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
    result = cloudinary.uploader.upload(
        image_path,
        folder="guard_vision_intruders"
    )
    return result["secure_url"]