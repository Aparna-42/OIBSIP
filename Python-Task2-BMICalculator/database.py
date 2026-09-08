import sqlite3


def create_database():
    try:
        connection = sqlite3.connect("bmi_tracker.db")
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bmi_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                weight REAL NOT NULL,
                height REAL NOT NULL,
                bmi REAL NOT NULL,
                category TEXT NOT NULL,
                recorded_at TEXT NOT NULL
            )
        """)

        connection.commit()
        connection.close()

        return True

    except sqlite3.Error:
        return False


def save_record(name, weight, height, bmi, category, recorded_at):
    try:
        connection = sqlite3.connect("bmi_tracker.db")
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO bmi_records
            (name, weight, height, bmi, category, recorded_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, weight, height, bmi, category, recorded_at))

        connection.commit()
        connection.close()

        return True

    except sqlite3.Error:
        return False


def get_records(name=None):
    try:
        connection = sqlite3.connect("bmi_tracker.db")
        cursor = connection.cursor()

        if name:
            cursor.execute("""
                SELECT name, weight, height, bmi, category, recorded_at
                FROM bmi_records
                WHERE name = ?
                ORDER BY recorded_at DESC
            """, (name,))
        else:
            cursor.execute("""
                SELECT name, weight, height, bmi, category, recorded_at
                FROM bmi_records
                ORDER BY recorded_at DESC
            """)

        records = cursor.fetchall()

        connection.close()

        return records

    except sqlite3.Error:
        return None