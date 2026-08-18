import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "development-secret-key")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///expense_tracker.db",
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False