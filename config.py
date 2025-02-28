import os
from dotenv import load_dotenv
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-à-changer-en-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'art_database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'artworks')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    # Configuration JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-à-changer'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    # Configuration email
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465  # Port SSL
    MAIL_USE_SSL = True  # Utiliser SSL au lieu de TLS
    MAIL_USE_TLS = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')
    ADMIN_EMAIL = os.environ.get('MAIL_USERNAME')

    # Configuration de l'URL de base pour les liens
    BASE_URL = os.environ.get('BASE_URL') or 'http://localhost:5000'

    # Configuration logging
    LOG_FILE = os.path.join(basedir, 'app.log')
    LOG_LEVEL = 'DEBUG'
    
    # Configuration logging détaillé pour les emails
    LOGGING_CONFIG = {
        'version': 1,
        'formatters': {
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        },
        'handlers': {
            'email_log': {
                'class': 'logging.FileHandler',
                'filename': os.path.join(basedir, 'email.log'),
                'formatter': 'detailed',
                'level': 'DEBUG'
            }
        },
        'loggers': {
            'flask_mail': {
                'handlers': ['email_log'],
                'level': 'DEBUG'
            }
        }
    }

    # Configuration CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = 'dev-csrf-secret-key-change-in-production'  # Change this in production!
