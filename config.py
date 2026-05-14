import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# On Azure App Service, /home is the persistent storage mount.
# Use DATABASE_URL env var to override (set in Azure App Settings).
_AZURE_HOME = '/home'
_ON_AZURE = os.path.exists(_AZURE_HOME) and os.environ.get('WEBSITE_INSTANCE_ID')
_DEFAULT_DB = (
    f'sqlite:///{ os.path.join(_AZURE_HOME, "caulong.db") }'
    if _ON_AZURE
    else f'sqlite:///{ os.path.join(BASE_DIR, "caulong.db") }'
)


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'caulong-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or _DEFAULT_DB
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads: use /home/uploads on Azure for persistence
    UPLOAD_FOLDER = (
        os.path.join(_AZURE_HOME, 'uploads')
        if _ON_AZURE
        else os.path.join(BASE_DIR, 'app', 'static', 'uploads')
    )

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
    WTF_CSRF_ENABLED = True
    POSTS_PER_PAGE = 12
