from flask_login import UserMixin
from sqlalchemy import text
from app.services.database import get_db
from datetime import datetime

class User(UserMixin):
    """ User model compatibile with Flask-Login"""
    def __init__(self, id, email, password_hash, is_verified=False):
        self.id = str(id)
        self.email = email
        self.password_hash = password_hash
        self.is_verified = bool(is_verified)


def get_user_by_id(user_id):
    """ Retrive a user form the database by ID"""
    engine = get_db()

    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT id, email, password_hash, is_verified
                FROM users
                WHERE id = :user_id
            """),
            {"user_id": user_id}
        )
        row = result.fetchone()

    if row:
        row = row._mapping
        return User(
            id=row["id"],
            email=row["email"],
            password_hash=row["password_hash"],
            is_verified=row["is_verified"]
        )

    return None


def get_user_by_email(email):
    """ Retrieve a user from the database by email address"""
    engine = get_db()

    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT id, email, password_hash, is_verified
                FROM users
                WHERE email = :email
            """),
            {"email": email}
        )
        row = result.fetchone()

    if row:
        row = row._mapping
        return User(
            id=row["id"],
            email=row["email"],
            password_hash=row["password_hash"],
            is_verified=row["is_verified"]
        )

    return None


def create_user(email, password_hash, verification_token):
    """ Create a new user and return the created User object"""
    engine = get_db()

    with engine.begin() as conn:
        result = conn.execute(
            text("""
                INSERT INTO users (email, password_hash, is_verified, verification_token)
                VALUES (:email, :password_hash, :is_verified, :verification_token)
            """),
            {
                "email": email,
                "password_hash": password_hash,
                "is_verified": False,
                "verification_token": verification_token
            }
        )
        user_id = result.lastrowid

    return User(
        id=user_id,
        email=email,
        password_hash=password_hash,
        is_verified=False
    )



def get_user_by_verification_token(token):
    """Retrieve a user by email verification token"""
    engine = get_db()

    with engine.connect() as conn:
        row = conn.execute(
            text("""
                SELECT id, email, password_hash, is_verified
                FROM users
                WHERE verification_token = :token
            """),
            {"token": token}
        ).fetchone()

    if row:
        row = row._mapping
        return User(
            id=row["id"],
            email=row["email"],
            password_hash=row["password_hash"],
            is_verified=row["is_verified"]
        )
    return None


def verify_user_email(token):
    """ Mark a user as verified and clear their verification token"""
    engine = get_db()

    with engine.begin() as conn:
        result = conn.execute(
            text("""
                UPDATE users
                SET is_verified = TRUE,
                    verification_token = NULL
                WHERE verification_token = :token
            """),
            {"token": token}
        )
        return result.rowcount > 0


def set_reset_token(email, reset_token, expires_at):
    """Store a password reset token and expiry time for a user"""
    engine = get_db()

    with engine.begin() as conn:
        result = conn.execute(
            text("""
                UPDATE users
                SET reset_token = :reset_token,
                    reset_token_expires = :expires_at
                WHERE email = :email
            """),
            {
                "email": email,
                "reset_token": reset_token,
                "expires_at": expires_at
            }
        )
        return result.rowcount > 0


def get_user_by_reset_token(token):
    """ Retrieve user reset token data for password reset validation"""
    engine = get_db()

    with engine.connect() as conn:
        row = conn.execute(
            text("""
                SELECT id, email, password_hash, is_verified, reset_token_expires
                FROM users
                WHERE reset_token = :token
            """),
            {"token": token}
        ).fetchone()

    return row._mapping if row else None


def update_password_with_token(token, password_hash):
    """Update a user's password and clear the reset token fields"""
    engine = get_db()

    with engine.begin() as conn:
        result = conn.execute(
            text("""
                UPDATE users
                SET password_hash = :password_hash,
                    reset_token = NULL,
                    reset_token_expires = NULL
                WHERE reset_token = :token
            """),
            {
                "password_hash": password_hash,
                "token": token
            }
        )
        return result.rowcount > 0
