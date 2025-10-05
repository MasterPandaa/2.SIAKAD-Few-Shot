import logging
import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = int(os.environ.get("SQLALCHEMY_POOL_SIZE", 10))
    SQLALCHEMY_POOL_RECYCLE = int(
        os.environ.get("SQLALCHEMY_POOL_RECYCLE", 3600))
    AUTO_CREATE_DB = os.environ.get(
        "AUTO_CREATE_DB", "false").lower() == "true"
    JSON_SORT_KEYS = False

    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

    @staticmethod
    def validate():
        if not Config.SECRET_KEY:
            raise ValueError("SECRET_KEY must be set in environment variables")
        if not Config.JWT_SECRET_KEY:
            raise ValueError(
                "JWT_SECRET_KEY must be set in environment variables")
        if not Config.SQLALCHEMY_DATABASE_URI:
            raise ValueError(
                "DATABASE_URL must be set in environment variables")

    @staticmethod
    def configure_logging():
        logging.basicConfig(
            level=getattr(logging, Config.LOG_LEVEL, logging.INFO),
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        )
