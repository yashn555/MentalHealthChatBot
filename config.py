import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from a .env file

HF_API_KEY = os.getenv("HF_API_KEY")

DB_CONFIG = {
    'username': os.getenv("DB_USERNAME"),
    'password': os.getenv("DB_PASSWORD"),
    'host': os.getenv("DB_HOST"),
    'port': int(os.getenv("DB_PORT", 3307)),
    'database': os.getenv("DB_NAME")
}

SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_CONFIG['username']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
