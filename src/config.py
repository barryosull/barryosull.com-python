import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file once when this module is imported
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

API_ROOT_URL = os.getenv("API_ROOT_URL")
