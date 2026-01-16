# Authored By Certified Coders — v1.2 (2025-11-14)
import os
from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = os.getenv("OWNER_ID")
MONGO_URI = os.getenv("MONGO_URI")

API_ID = int(API_ID) if API_ID and API_ID.isdigit() else 27798659
OWNER_ID = int(OWNER_ID) if OWNER_ID and OWNER_ID.isdigit() else 7019293589