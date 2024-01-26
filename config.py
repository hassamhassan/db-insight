import os
from dotenv import load_dotenv

# Assuming this script is in the same directory as the .env file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


DATABASE_URL = os.environ["DATABASE_URL"]
ACCESS_TOKEN_EXPIRE = os.environ["ACCESS_TOKEN_EXPIRE"]
JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALGORITHM = os.environ["JWT_ALGORITHM"]
