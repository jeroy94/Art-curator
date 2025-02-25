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
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    # Configuration JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-à-changer'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    # Configuration email
    MAIL_SERVER = 'smtp.gmail.com'  # À modifier selon votre serveur SMTP
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'votre-email@gmail.com'  # À remplacer par votre email
    MAIL_PASSWORD = 'votre-mot-de-passe'  # À remplacer par votre mot de passe
    MAIL_DEFAULT_SENDER = 'votre-email@gmail.com'  # À remplacer par votre email
    ADMIN_EMAIL = 'admin@example.com'  # À remplacer par l'email de l'administrateur

    # Configuration CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = 'dev-csrf-secret-key-change-in-production'  # Change this in production!
