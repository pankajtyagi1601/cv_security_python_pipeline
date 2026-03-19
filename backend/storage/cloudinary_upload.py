# storage/cloudinary_upload.py
from utils.logger import logger
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
import os, time

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
            
def upload_with_retry(image_path, retries=3):
    """
    Uploads to Cloudinary with exponential backoff retry.
    
    Attempt 1 fails → wait 1s → retry
    Attempt 2 fails → wait 2s → retry  
    Attempt 3 fails → raise exception → event_worker catches it
    
    Backoff prevents hammering Cloudinary if it's temporarily down.
    """
    last_exception = None

    for attempt in range(retries):
        try:
            url = upload_image(image_path)
            if attempt > 0:
                logger.info(f"Upload succeeded on attempt {attempt + 1}")
            return url

        except Exception as e:
            last_exception = e
            wait = 2 ** attempt  # 1s, 2s, 4s
            logger.error(f"Upload attempt {attempt + 1}/{retries} failed: {e}")

            if attempt < retries - 1:
                logger.info(f"Retrying in {wait}s...")
                time.sleep(wait)

    # All retries exhausted
    raise Exception(
        f"Upload failed after {retries} attempts. "
        f"Last error: {last_exception}"
    )