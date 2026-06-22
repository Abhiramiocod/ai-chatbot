import os
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
server_url = os.getenv("GOOGLE_SERVER_URL")

secret_key = os.getenv("SECRET_KEY")
