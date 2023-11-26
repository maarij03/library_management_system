# controller/admin.py

from flask import Blueprint, request, jsonify
from datetime import timedelta
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from ..model.db import init_db
import app
admin_bp = Blueprint("admin", __name__)

# Initialize the database
init_db()

# Register Admin
@app.route("/admin/register", methods=["POST"])
def admin_register():
    conn = init_db()
    cursor = conn.cursor()

    admin_email = request.json.get("email", None)
    admin_password = request.json.get("password", None)

    # Check if the email is already registered
    cursor.execute("SELECT * FROM admins WHERE email=%s", (admin_email,))
    existing_admin = cursor.fetchone()

    if existing_admin:
        return {"msg": "Email already registered"}, 400

    # Save the admin data
    cursor.execute("INSERT INTO admins (email, password) VALUES (%s, %s)", (admin_email, admin_password))
    conn.commit()

    return {"msg": "Admin registered successfully"}, 201


@admin_bp.route("/admin/login", methods=["POST"])
def login():
    # Get the database connection from the global context
    conn = init_db()
    cursor = conn.cursor()

    admin_email = request.json.get("email", None)
    admin_password = request.json.get("password", None)

    # Check if the provided credentials match the registered admin
    cursor.execute("SELECT * FROM admins WHERE email=%s AND password=%s", (admin_email, admin_password))
    registered_admin = cursor.fetchone()

    if registered_admin:
        # Generate an access token
        access_token = create_access_token(identity=admin_email)
        conn.close()  # Close the connection
        return {'access_token': access_token}, 200
    else:
        conn.close()  # Close the connection
        return {"msg": "Invalid credentials"}, 401

@admin_bp.route("/admin/books/add", methods=["POST"])
@jwt_required()
def add_new_book():
    # Get the database connection from the global context
    conn = init_db()
    cursor = conn.cursor()

    current_admin = get_jwt_identity()

    title = request.json.get("title", None)
    description = request.json.get("description", None)
    category = request.json.get("category", None)

    # Validate the input
    if not title or not description or not category:
        conn.close()  # Close the connection
        return {"msg": "Missing required parameters"}, 400

    # Save the new book
    cursor.execute("INSERT INTO books (title, description, category) VALUES (%s, %s, %s)", (title, description, category))
    conn.commit()

    conn.close()  # Close the connection
    return {"msg": "New book added successfully"}, 201

@admin_bp.route("/admin/borrow_requests", methods=["GET"])
@jwt_required()
def get_borrow_requests():
    # Get the database connection from the global context
    conn = init_db()
    cursor = conn.cursor()

    current_admin = get_jwt_identity()

    # Fetch pending borrow requests
    cursor.execute("SELECT * FROM borrowings WHERE status='pending'")
    borrow_requests = cursor.fetchall()

    conn.close()  # Close the connection
    return jsonify({"borrow_requests": borrow_requests}), 200

@admin_bp.route("/admin/accept_borrow_request/<int:request_id>", methods=["POST"])
@jwt_required()
def accept_borrow_request(request_id):
    # Get the database connection from the global context
    conn = init_db()
    cursor = conn.cursor()

    current_admin = get_jwt_identity()

    # Check if the request exists
    cursor.execute("SELECT * FROM borrowings WHERE id=%s AND status='pending'", (request_id,))
    borrowing_request = cursor.fetchone()

    if not borrowing_request:
        conn.close()  # Close the connection
        return {"msg": "Borrow request not found or already accepted/declined"}, 404

    # Accept the borrow request
    cursor.execute("UPDATE borrowings SET status='accepted' WHERE id=%s", (request_id,))
    conn.commit()

    conn.close()  # Close the connection
    return {"msg": "Borrow request accepted successfully"}, 200

@admin_bp.route("/admin/mark_book_returned/<int:borrowing_id>", methods=["POST"])
@jwt_required()
def mark_book_returned(borrowing_id):
    # Get the database connection from the global context
    conn = init_db()
    cursor = conn.cursor()

    current_admin = get_jwt_identity()

    # Check if the borrowing exists
    cursor.execute("SELECT * FROM borrowings WHERE id=%s AND status='accepted'", (borrowing_id,))
    borrowing = cursor.fetchone()

    if not borrowing:
        conn.close()  # Close the connection
        return {"msg": "Borrowing not found or not accepted"}, 404

    # Mark the book as returned
    cursor.execute("UPDATE borrowings SET status='returned', returned_date=NOW() WHERE id=%s", (borrowing_id,))
    conn.commit()

    conn.close()  # Close the connection
    return {"msg": "Book marked as returned successfully"}, 200

if __name__ == "__main__":
    app.run(debug=True, port=3000)