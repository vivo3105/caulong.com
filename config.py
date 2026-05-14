import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Azure App Service sets WEBSITE_SITE_NAME; /home is its persistent storage.
_ON_AZURE = bool(os.environ.get('WEBSITE_SITE_NAME'))
_DB_PATH = (
    '/home/caulong.db'
    if _ON_AZURE
    else os.path.join(BASE_DIR, 'caulong.db')
)
_UPLOAD_PATH = (
    '/home/uploads'
    if _ON_AZURE
    else os.path.join(BASE_DIR, 'app', 'static', 'uploads')
)

# Ensure upload directory exists
os.makedirs(_UPLOAD_PATH, exist_ok=True)


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'caulong-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{_DB_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = _UPLOAD_PATH
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
    WTF_CSRF_ENABLED = True
    POSTS_PER_PAGE = 12
