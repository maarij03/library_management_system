import json
from flask_jwt_extended import create_access_token

def test_admin_login(client):
    # Test admin login functionality
    response = client.post('/admin/login', json={'email': 'admin@example.com', 'password': 'admin'})
    assert response.status_code == 200
    assert 'access_token' in json.loads(response.data)

def test_add_new_book(client):
    access_token = create_access_token(identity='admin@example.com')

    response = client.post('/admin/books/add', json={'title': 'New Book', 'description': 'A great book', 'category': 'Fiction'},
                           headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 201

def test_accept_borrow_request(client):
    access_token = create_access_token(identity='admin@example.com')

    # Test accepting a borrow request by admin
    response = client.post('/admin/accept_borrow_request/1', headers={'Authorization': f'Bearer {access_token}'})
    assert response.status_code == 200
