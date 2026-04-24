import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration shared across all environments."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

    # General
    DEBUG = False
    TESTING = False

    # API Keys
    JCDECAUX_API_KEY = os.environ.get("JCDECAUX_API_KEY")
    OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")
    GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")

    CONTRACT_NAME = "dublin"
    WEATHER_CITY = "Dublin"

    # Database configuration
    DB_USER = os.environ.get("DB_USER")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")
    DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
    DB_PORT = os.environ.get("DB_PORT", "3306")
    DB_NAME = os.environ.get("DB_NAME")

    # For email sending
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    SECRET_KEY = os.environ.get("SECRET_KEY")
    DEBUG = False
