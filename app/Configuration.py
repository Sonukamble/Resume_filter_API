from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

class Config:
    # Environment configuration
    HOST_IP = os.getenv("HOST_IP")
    HOST_PORT = int(os.getenv("HOST_PORT", 8000))  # Default to 8000 if not specified

    # Database configuration
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_SERVER = os.getenv("MYSQL_SERVER")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))  # Default to 3306 if not specified
    MYSQL_DATABASE = os.getenv("MYSQL_DB")
    MYSQL_SAMPLE_DATABASE = os.getenv("MYSQL_SAMPLE_DB")

    # File paths
    TEMPORARY_FILE_PATH = os.getenv("TEMPORARY_FILE")

    # Google API configuration
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GOOGLE_PROMPT = os.getenv("GOOGLE_PROMPT")

    # Google Client configuration
    GOOGLE_CLIENT_ID = os.getenv("CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("CLIENT_SECRET")
