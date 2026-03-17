from dotenv import load_dotenv
import os

load_dotenv()  # loads variables from .env

cloud_name = os.getenv("CLOUD_NAME")
api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")

print(api_key)
print(cloud_name)
print(api_secret)