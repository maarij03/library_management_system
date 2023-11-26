# controller/customer.py

from flask import Blueprint, request, jsonify
from datetime import timedelta, datetime
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from model.db import init_db
import app
customer_bp = Blueprint("customer", __name__)

# Initialize the database
init_db()

@customer_bp.route("/register", methods=["POST"])
def register():
    conn, cursor = init_db()  # Get the connection and cursor

    customer_email = request.json.get("email", None)
    customer_password = request.json.get("password", None)

    # Check if the email is already registered
    cursor.execute("SELECT * FROM customers WHERE email=%s", (customer_email,))
    existing_customer = cursor.fetchone()

    if existing_customer:
        return {"msg": "Email already registered"}, 400

    # Save the customer data
    cursor.execute("INSERT INTO customers (email, password) VALUES (%s, %s)", (customer_email, customer_password))
    conn.commit()

    return {"msg": "Customer registered successfully"}, 201

@customer_bp.route("/login", methods=["POST"])
def login():
    conn, cursor = init_db()  # Get the connection and cursor

    customer_email = request.json.get("email", None)
    customer_password = request.json.get("password", None)

    # Check if the provided credentials match the registered customer
    cursor.execute("SELECT * FROM customers WHERE email=%s AND password=%s", (customer_email, customer_password))
    registered_customer = cursor.fetchone()

    if registered_customer:
        # Generate an access token
        access_token = create_access_token(identity=customer_email)
        return {'access_token': access_token}, 200
    else:
        return {"msg": "Invalid credentials"}, 401

@customer_bp.route("/books", methods=["GET"])
@jwt_required()
def search_books():
    conn, cursor = init_db()  # Get the connection and cursor
    current_user = get_jwt_identity()

    # Get search parameters from query string
    title = request.args.get("title", None)
    description = request.args.get("description", None)
    category = request.args.get("category", None)

    # Apply search conditions using LIKE queries
    conditions = []
    if title:
        conditions.append(f"title LIKE '%{title}%'")
    if description:
        conditions.append(f"description LIKE '%{description}%'")
    if category:
        conditions.append(f"category LIKE '%{category}%'")

    # Construct the SQL query
    where_clause = " AND ".join(conditions) if conditions else "1"
    query = f"SELECT * FROM books WHERE {where_clause} LIMIT 10"

    # Execute the query
    cursor.execute(query)
    books = cursor.fetchall()

    return jsonify({"books": books}), 200

@customer_bp.route("/books/page/<int:page>", methods=["GET"])
@jwt_required()
def list_books(page):
    conn, cursor = init_db()  # Get the connection and cursor
    current_user = get_jwt_identity()

    # Set the number of books per page
    books_per_page = 10

    # Calculate the offset based on the page number
    offset = (page - 1) * books_per_page

    # Fetch books for the specified page
    cursor.execute(f"SELECT * FROM books LIMIT {books_per_page} OFFSET {offset}")
    books = cursor.fetchall()

    return jsonify({"books": books}), 200

@customer_bp.route("/books/request_borrowing", methods=["POST"])
@jwt_required()
def request_borrowing():
    conn, cursor = init_db()  # Get the connection and cursor
    current_user = get_jwt_identity()
    user_email = current_user

    # Get book_id and borrowing dates from the request
    book_id = request.json.get("book_id", None)
    borrowing_date_from_str = request.json.get("borrowing_date_from", None)
    borrowing_date_to_str = request.json.get("borrowing_date_to", None)

    # Validate the input
    if not book_id or not borrowing_date_from_str or not borrowing_date_to_str:
        return {"msg": "Missing required parameters"}, 400

    # Convert string dates to datetime objects
    try:
        borrowing_date_from = datetime.strptime(borrowing_date_from_str, "%Y-%m-%d %H:%M:%S")
        borrowing_date_to = datetime.strptime(borrowing_date_to_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return {"msg": "Invalid date format"}, 400

    # Check if the book exists
    cursor.execute("SELECT * FROM books WHERE id=%s", (book_id,))
    book = cursor.fetchone()

    if not book:
        return {"msg": "Book not found"}, 404

    # Check if the book is available for borrowing (not already borrowed)
    cursor.execute("SELECT * FROM borrowings WHERE book_id=%s AND (borrowing_date_to > %s OR borrowing_date_to IS NULL)", (book_id, datetime.now()))
    existing_borrowings = cursor.fetchall()

    if existing_borrowings:
        return {"msg": "Book is not available for borrowing"}, 400

    # Save the borrowing request
    cursor.execute("INSERT INTO borrowings (book_id, user_email, borrowing_date_from, borrowing_date_to) VALUES (%s, %s, %s, %s)",
                   (book_id, user_email, borrowing_date_from, borrowing_date_to))
    conn.commit()

    return {"msg": "Borrowing request submitted successfully"}, 201

@customer_bp.route("/books/borrowings", methods=["GET"])
@jwt_required()
def get_borrowings():
    conn, cursor = init_db()  # Get the connection and cursor
    current_user = get_jwt_identity()

    # Fetch borrowings for the current user
    cursor.execute("SELECT * FROM borrowings WHERE user_email=%s", (current_user,))
    borrowings = cursor.fetchall()

    return jsonify({"borrowings": borrowings}), 200

if __name__ == "__main__":
    app.run(debug=True, port=3000)
