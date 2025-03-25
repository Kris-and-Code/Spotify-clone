import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    FIREBASE_CREDENTIALS = os.getenv('FIREBASE_CREDENTIALS')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30 