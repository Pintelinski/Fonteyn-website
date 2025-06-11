import sqlite3
import sys
import hashlib
import os
from config import CONFIG

class BookingDB:
    @staticmethod
    def initialize(database_connection: sqlite3.Connection):
        cursor = database_connection.cursor()
        print("Creating tables...")
        cursor.execute(BookingDB.CREATE_TABLE_BOOKING)
        cursor.execute(BookingDB.CREATE_TABLE_AUTH)
        database_connection.commit()


    CREATE_TABLE_BOOKING = """
    CREATE TABLE IF NOT EXISTS booking (
        booking_numb INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        surname_booking TEXT NOT NULL,
        numb_people INTEGER NOT NULL,
        room_id TEXT NOT NULL,
        check_in DATE NOT NULL,
        check_out DATE NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY (username) 
            REFERENCES auth(username)
            ON UPDATE CASCADE
            ON DELETE RESTRICT
    )
    """
    CREATE_TABLE_AUTH = """
    CREATE TABLE IF NOT EXISTS auth (
        username TEXT NOT NULL UNIQUE PRIMARY KEY,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL
    )
    """
    @staticmethod
    def hash_password(password: str, salt: bytes = None) -> tuple:
        if salt is None:
            salt = os.urandom(32)
        hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000
        )
        return hash.hex(), salt.hex()


    INSERT_BOOKING = "INSERT INTO booking VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"

def main():
    # Create data directory if it doesn't exist
    db_path = CONFIG['database']['name']
    db_dir = os.path.dirname(db_path)
    
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    # Connect to the database
    conn = sqlite3.connect(CONFIG['database']['name'])
    
    # Initialize database tables
    BookingDB.initialize(conn)
    print("Database tables created successfully!")

    # Create some example users with salted and hashed passwords
    cursor = conn.cursor()
    
    # Example users (username, password)
    users = [
        ('admin', 'admin123'),
        ('user1', 'password123'),
        ('user2', 'wordpass123'),
    ]

    # Insert users with salted and hashed passwords
    for username, password in users:
        password_hash, salt = BookingDB.hash_password(password)
        cursor.execute("""
            INSERT OR REPLACE INTO auth (username, password_hash, salt)
            VALUES (?, ?, ?)
        """, (username, password_hash, salt))

    conn.commit()
    print("Example users created successfully!")
    
    conn.close()
    return 0

# --- Program entry ---
if __name__ == "__main__":
    sys.exit(main())