# model/db.py
import pymysql
from flask import Flask

def init_db(app: Flask):
    # Setup pymysql database
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='library_management_system',
    )
    cursor = conn.cursor()

    # Create tables if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            category VARCHAR(255)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS borrowings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            book_id INT,
            user_email VARCHAR(255),
            borrowing_date_from DATETIME,
            borrowing_date_to DATETIME,
            returned_date DATETIME,
            status VARCHAR(50) DEFAULT 'pending',
            FOREIGN KEY (book_id) REFERENCES books(id),
            FOREIGN KEY (user_email) REFERENCES customers(email)
        )
    ''')
    conn.commit()
