import sqlite3
import hashlib
from datetime import datetime
import os
import hashlib
import hmac

DB_NAME = "chat_app.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # Chat rooms table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # Messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (room_id) REFERENCES rooms(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hidden_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            message_id INTEGER NOT NULL,
            UNIQUE(username, message_id)
        )
    """)

    # Create default room
    cursor.execute("""
        INSERT OR IGNORE INTO rooms (name, created_at)
        VALUES (?, ?)
    """, ("General", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    connection.commit()
    connection.close()

def hash_password(password):
    salt = os.urandom(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        100_000
    )
    return salt.hex() + ":" + password_hash.hex()


def register_user(username, password):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        hashed_password = hash_password(password)

        cursor.execute("""
            INSERT INTO users (username, password, created_at)
            VALUES (?, ?, ?)
        """, (
            username,
            hashed_password,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        connection.commit()
        return True, "Registration successful."

    except sqlite3.IntegrityError:
        return False, "Username already exists."

    finally:
        connection.close()


def authenticate_user(username, password):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, password FROM users
        WHERE username = ?
    """, (username,))

    user = cursor.fetchone()

    if not user:
        connection.close()
        return False

    user_id, stored_password = user

    # --------------------------------------------------
    # New PBKDF2 password format
    # --------------------------------------------------
    if ":" in stored_password:
        try:
            salt_hex, stored_hash_hex = stored_password.split(":")

            salt = bytes.fromhex(salt_hex)
            stored_hash = bytes.fromhex(stored_hash_hex)

            password_hash = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                salt,
                100_000
            )

            result = hmac.compare_digest(
                password_hash,
                stored_hash
            )

            connection.close()
            return result

        except (ValueError, TypeError):
            connection.close()
            return False

    # --------------------------------------------------
    # Old SHA-256 password - verify and upgrade
    # --------------------------------------------------
    old_hash = hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()

    if hmac.compare_digest(stored_password, old_hash):

        new_password = hash_password(password)

        cursor.execute("""
            UPDATE users
            SET password = ?
            WHERE id = ?
        """, (new_password, user_id))

        connection.commit()
        connection.close()

        return True

    connection.close()
    return False

def create_room(room_name):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO rooms (name, created_at)
            VALUES (?, ?)
        """, (
            room_name,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        connection.commit()
        return True, "Room created successfully."

    except sqlite3.IntegrityError:
        return False, "Room already exists."

    finally:
        connection.close()


def get_rooms():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT name FROM rooms
        ORDER BY name
    """)

    rooms = [row[0] for row in cursor.fetchall()]

    connection.close()

    return rooms


def get_room_id(room_name):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id FROM rooms
        WHERE name = ?
    """, (room_name,))

    result = cursor.fetchone()

    connection.close()

    return result[0] if result else None


def save_message(room_name, username, message):
    room_id = get_room_id(room_name)

    if room_id is None:
        return None

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO messages (
            room_id,
            username,
            message,
            timestamp
        )
        VALUES (?, ?, ?, ?)
    """, (
        room_id,
        username,
        message,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    message_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return message_id

def get_message_history(room_name, username, limit=100):
    room_id = get_room_id(room_name)

    if room_id is None:
        return []

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            m.id,
            m.username,
            m.message,
            m.timestamp
        FROM messages m
        WHERE m.room_id = ?
        AND NOT EXISTS (
            SELECT 1
            FROM hidden_messages h
            WHERE h.username = ?
            AND CAST(h.message_id AS INTEGER) = m.id
        )
        ORDER BY m.id DESC
        LIMIT ?
    """, (
        room_id,
        username,
        limit
    ))

    messages = cursor.fetchall()

    connection.close()

    return list(reversed(messages))

def clear_chat_for_user(username, room_name):
    room_id = get_room_id(room_name)

    if room_id is None:
        return False

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO hidden_messages (
            username,
            message_id
        )
        SELECT ?, id
        FROM messages
        WHERE room_id = ?
    """, (
        username,
        room_id
    ))

    connection.commit()
    connection.close()

    return True
def hide_message_for_user(username, message_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO hidden_messages (
            username, message_id
        )
        VALUES (?, ?)
    """, (username, int(message_id)))

    connection.commit()
    connection.close()

    return True
if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully.")