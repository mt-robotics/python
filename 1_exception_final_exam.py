import logging
import psycopg2

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .config import config

DB_NAME = config.DB_NAME
DB_USER_NAME = config.DB_USER_NAME
DB_PASSWORD = config.DB_PASSWORD
DB_HOST = config.DB_HOST


class UserValidationError(Exception):
    """
    Custom exception class for user validation errors.

    Attributes:
        message (str): The error message.
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class ServiceError(Exception):
    """
    Custom exception class for service errors.

    Attributes:
        message (str): The error message.

    Raises:
        Exception: The base exception class.
    """

    def __init__(self, message):
        self.message = message
        super().__init__(f"Service Error: {self.message}")


def register_user(username: str, email: str, password: str, age: int):
    """
    Registers a new user with the given username, email, password, and age.

    Args:
        username (str): The username of the new user.
        email (str): The email address of the new user.
        password (str): The password of the new user.
        age (int): The age of the new user.

    Raises:
        UserValidationError: If the username, email, password, or age is invalid.
        ServiceError: If there is an error during the registration process.
    """
    if len(username) not in range(3, 21):
        logging.warning(
            "Username validation failed: not in the required length (%d characters)",
            len(username),
        )
        raise UserValidationError(
            "Username must be at lease 3 characters and no more than 20 characters"
        )

    if not username.isalnum():
        logging.warning("Username validation failed: contains invalid characters")
        raise UserValidationError("Username must only contain letters or numbers")

    if not "@" in email:
        logging.warning("Email validation failed: '%s'", email)
        raise UserValidationError("Email must contain '@'")

    if len(password) < 8:
        logging.warning("Password validation failed: too short")
        raise UserValidationError("Password must be at least 8 characters")

    if age < 18:
        logging.warning("Age validation failed: less than or equal to 18 (%d)", age)
        raise UserValidationError("Age must be 18 or older")

    try:
        with psycopg2.connect(dbname=DB_NAME, user=DB_USER_NAME, host=DB_HOST) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (username, email, password, age) VALUES (%s, %s, %s, %s)",
                    (username, email, password, age),
                )
                conn.commit()

    except psycopg2.Error as e:
        logging.error("Database error during registration: %s", str(e))
        raise ServiceError("Registration temporarily unavailable") from None
    except Exception as e:
        logging.error("Unexpected Error: %s", str(e))
        raise ServiceError("Internal error") from None


app = FastAPI()


class UserRegister(BaseModel):  # Define data shape for automatic input validation
    """
    Define the data shape for automatic input validation of user registration.

    Attributes:
        username (str): The username of the new user.
        email (str): The email address of the new user.
        password (str): The password of the new user.
        age (int): The age of the new user.
    """

    username: str
    email: str
    password: str
    age: int


@app.post("/register")
def register_endpoint(
    user: UserRegister,
) -> None:  # FastAPI auto-parses JSON → UserRegister object
    """
    Handles the registration of a new user.

    Args:
        user (UserRegister): The user registration data.

    Raises:
        HTTPException: If an error occurs during registration.

    Returns:
        None
    """
    try:
        register_user(user.username, user.email, user.password, user.age)
        logging.info("New user registered successfully")
    except ServiceError as e:
        logging.error("error: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))
    except UserValidationError as e:
        logging.warning("error: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e))
