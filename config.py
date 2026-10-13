from dotenv import load_dotenv
import os

load_dotenv()

def get_env(key: str) -> str:
    value = os.getenv(key)

    if value is None:
        raise RuntimeError(f"Missing environment variable : {key}")

    return value

DB_CONFIG = {
    "dbname": get_env("DB_NAME"),
    "user": get_env("DB_USER"),
    "password": get_env("DB_PASSWORD"),
    "host": get_env("DB_HOST"),
    "port": int(get_env("DB_PORT"))
}

STUDENT_TABLE = get_env("STUDENT_TABLE")
STORAGE_TABLE = get_env("STORAGE_TABLE")