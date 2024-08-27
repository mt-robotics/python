import os
from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv()

# Check if the environment variables are loaded successfully
def check_env_variables():
    postgres_vars = ["POSTGRES_HOST", "POSTGRES_PORT", "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB_MV"]
    for var in postgres_vars:
        value = os.getenv(var)
        if value:
            print(f"{var} loaded successfully")
        else:
            print(f"Warning: {var} is not set.")

# Call the function to check environment variables
check_env_variables()

# retrieve environment variables
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5432)

POSTGRES_DB_MV = os.getenv("POSTGRES_DB_MV", "postgres")
POSTGRES_URL_MV = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB_MV}"
