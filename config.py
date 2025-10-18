import os

secret_key = os.getenv("SECRET_KEY", "dev-secret")
database_url = os.getenv("DATABASE_URL", "database.db")

