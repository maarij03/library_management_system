import json
from flask_jwt_extended import create_access_token

def test_customer_register(client):
    # Test customer registration functionality
    response = client.post('/register', json={'email': 'test@example.com', 'password': 'test'})
    assert response.status_code == 201

def test_customer_login(client):
    # Test customer login functionality
    response = client.post('/login', json={'email': 'test@example.com', 'password': 'test'})
    assert response.status_code == 200
    assert 'access_token' in json.loads(response.data)

def test_search_books(client):
    # Assuming the customer is logged in
    access_token = create_access_token(identity='test@example.com')

    response = client.get('/books?title=example', headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
    assert 'books' in json.loads(response.data)

def test_request_borrowing(client):
    access_token = create_access_token(identity='test@example.com')

    response = client.post('/books/request_borrowing', json={'book_id': 1, 'borrowing_date_from': '2023-01-01 10:00:00', 'borrowing_date_to': '2023-01-07 10:00:00'},
                           headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 201
