import sqlite3
import bcrypt

DATABASE_NAME = "users.db"


def get_connection():
    return sqlite3.connect(DATABASE_NAME, check_same_thread=False)


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def hash_password(password: str):
    return bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()


def verify_password(password, hashed_password):
    return bcrypt.checkpw(
        password.encode(),
        hashed_password.encode()
    )


def username_exists(username):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE username=?",
        (username,)
    )

    user = cursor.fetchone()

    conn.close()

    return user is not None


def email_exists(email):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE email=?",
        (email,)
    )

    user = cursor.fetchone()

    conn.close()

    return user is not None


def create_user(full_name, username, email, password):

    if username_exists(username):
        return False, "Username already exists."

    if email_exists(email):
        return False, "Email already registered."

    hashed = hash_password(password)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users(
            full_name,
            username,
            email,
            password
        )
        VALUES(?,?,?,?)
    """, (
        full_name,
        username,
        email,
        hashed
    ))

    conn.commit()
    conn.close()

    return True, "Account created successfully."


def login_user(email, password):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            full_name,
            username,
            email,
            password
        FROM users
        WHERE email=?
    """, (email,))

    user = cursor.fetchone()

    conn.close()

    if user is None:
        return None

    if verify_password(password, user[4]):

        return {
            "id": user[0],
            "full_name": user[1],
            "username": user[2],
            "email": user[3]
        }

    return None