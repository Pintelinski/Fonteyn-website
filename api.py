import sqlite3
import hashlib
import os
import logging
from flask import jsonify, request
from functools import wraps
from config import CONFIG
import mysql.connector
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

DB_HOST = "127.0.0.1" #"host.docker.internal"
DB_PORT = "3306"
DB_USER = "webapp_user"
DB_PASSWORD = "Admin123!"  
DB_NAME = "fonteyn_database"

conn = mysql.connector.connect(
    host = DB_HOST,
    port = DB_PORT,
    user = DB_USER,
    password = DB_PASSWORD,
    database = DB_NAME
)

#database connection
"""def get_db():
    conn = sqlite3.connect(CONFIG["database"]["name"])
    conn.row_factory = sqlite3.Row
    return conn
"""
    
# Initialize logging
def verify_auth(auth_header):
    try:
        CHECK = """SELECT * FROM auth WHERE username = %s"""
        username, password = auth_header.split(':')
        cursor = conn.cursor(dictionary=True)  #database connection
        cursor.execute(CHECK, (username,)) #lookup user in the auth table
        user = cursor.fetchone()  #fetch the user data
        #if user exists, hash the password and compare it with the stored hash
        if user:
            password_hash, salt = hash_password(password, bytes.fromhex(user['salt']))
            return password_hash == user['password_hash']
        return False
    except:
        return False #returne False if any error occurs
    finally:
        cursor.close()  #close the cursor
#Decorator to require authentication for certain routes
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if not auth or not verify_auth(auth):
            return jsonify({'error': 'Unauthorized'}), 401 #return 401 if auth is not provided or invalid
        return f(*args, **kwargs)
    return decorated

#API endpoint for retrieving all users
def get_users():
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT username FROM auth')
        users = cursor.fetchall()  #fetch all users from the auth table
        return jsonify([{'username': user[0]} for user in users])
    except Exception as e:
        logging.error(f"Error in get_users: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        cursor.close()  #close the cursor

#API endpoint for retrieving all bookings
def get_bookings():
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM booking')
    bookings = cursor.fetchall()  #fetch all bookings from the booking table
    cursor.close()  #close the cursor
    return jsonify([dict(booking) for booking in bookings])

#API endpoint for creating a new booking
def create_booking():
    cursor = conn.cursor()
    park = request.form['park']
    name = request.form['name']
    email = request.form['email']
    date = request.form['date']
    people = int(request.form['people'])
    duration = int(request.form['duration'])
    roomType = request.form['roomType']

    current_datetime = datetime.now()
    input_datetime = datetime.strptime(date, '%Y-%m-%d')
    if input_datetime < current_datetime:
        return "The date you entered is in the past!", 400
    
    if roomType == 'single' and people > 1:
            return "Unfortunately, the single accomodation only suits 1 person!", 400
    elif roomType == 'double' and people > 2:
            return "Unfortunately, the double accomodation only suits up to 2 persons!", 400
    elif roomType == 'suite' and people > 6:
            return "Unfortunately, the suite accomodation only suits up to 6 persons!", 400
    
    if duration > 30:
            return "If you intend to stay for more than 30 days please contact us directly!"
    
    duration_delta = timedelta(days = duration)
    end_datetime = datetime.strptime(date, '%Y-%m-%d') + duration_delta
    end_date = end_datetime.date()

    INSERT_BOOKING = """
            INSERT INTO bookings (park, name, email, start_date, end_date, people, room_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    mail(park, name, email, date, end_date, people, roomType)
    cursor = conn.cursor()
    cursor.execute(INSERT_BOOKING, (park, name, email, date, end_date, people, roomType))
    conn.commit()
    cursor.close()
    return jsonify({'message': 'Booking created successfully'}), 201



#Password hashing function
def hash_password(password: str, salt: bytes = None) -> tuple:
    if salt is None:
        salt = os.urandom(32) #Generate 32 random bytes for the salt
    hash = hashlib.pbkdf2_hmac(
        'sha256', #Hash algorithm
        password.encode('utf-8'), #Convert password to bytes
        salt, #salt for randomization
        100000 #Number of iterations
    )
    return hash.hex(), salt.hex() #Return as hex strings for storage

#API endpoint for user login
def login():
    credentials = request.get_json()
    if verify_auth(f"{credentials['username']}:{credentials['password']}"):
        return jsonify({'message': 'Login successful'}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

#API endpoint for user registration
def register():
    user_data = request.get_json()
    
    # Check if username already exists
    cursor = conn.cursor()
    
    REGISTER_CHECK = """SELECT 1 FROM auth WHERE username = %s"""

    cursor.execute(REGISTER_CHECK, (user_data['username'],))
    existing_user = cursor.fetchone()  #fetch the user data
    
    if existing_user:
        cursor.close()
        return jsonify({'error': 'Username already taken'}), 400
    
    password_hash, salt = hash_password(user_data['password']) #hash the password for the storage
    
    try:
        REGISTER = """INSERT INTO auth (username, password_hash, salt) VALUES (%s, %s, %s)"""
        cursor.execute(REGISTER,
            (user_data['username'], password_hash, salt)
        )
        conn.commit()
        return jsonify({'message': 'Registration successful'}), 201
    except Exception as e:
        logging.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Failed to register user'}), 500
    finally:
        cursor.close()

def mail(park, name, email, start_date, end_date, people, roomType):      
    FROM = 'agenda.mailservice@gmail.com'
    TO = email

    SUBJECT = f"Your booking at Fonteyn Holiday Parks"
    TEXT = f"Dear {name}, \n\nYou have made a booking at Fonteyn Holiday Parks\n - Your booking has been confirmed at: {start_date}\n - Your stay is till {end_date}.\n - You have booked a {roomType} type room for {people} person(s).\n - The park you have chosen is: {park}.\n\nThank you for choosing Fonteyn Holiday Parks! \n\nBest regards,\nFonteyn Holiday Parks Team"

    msg = MIMEMultipart()
    msg['From'] = FROM
    msg['To'] = TO
    msg['Subject'] = SUBJECT

    msg.attach(MIMEText(TEXT, 'plain'))
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login('agenda.mailservice@gmail.com', 'tbmy zjot irka laht')
            server.sendmail(FROM, TO, msg.as_string())  
            print(f"Email sent to {TO} successfully.")
    except smtplib.SMTPException as e:
        print(f"Failed to send email to {TO}: {e}") 