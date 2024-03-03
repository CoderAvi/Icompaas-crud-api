import json
from app import app

import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture
def client():  
    # Create a test client using the Flask application for testing
    with app.test_client() as client:
        yield client

def test_get_all_users_success(client):
    # Test case for successfully retrieving all users
    with patch('app.pymysql.connect') as mock_connect:
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor

        # Mocking the database query result to simulate multiple users
        mock_cursor.fetchall.return_value = [('test1@gmail.com', 'Avinash', 'kumar'), ('test2@gmail.com', 'Abhijeet', 'Jaiswal')]

        # For making the API request
        response = client.get('/users')

    # Assertions
    assert response.status_code == 200
    assert response.get_json() == [
        {'email': 'test1@gmail.com', 'first_name': 'Avinash', 'last_name': 'kumar'},
        {'email': 'test2@gmail.com', 'first_name': 'Abhijeet', 'last_name': 'Jaiswal'}
    ]

def test_get_user_by_email_success(client):
    # Test case for successfully retrieving a user by email
    with patch('app.pymysql.connect') as mock_connect:
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor

        # Mocking the database query result to simulate a single user
        mock_cursor.fetchall.return_value = [('test@gmail.com', 'Avinash', 'kumar')]

        # For making the API request
        response = client.get('/users', query_string={'email': 'test@gmail.com'})

    # Assertions
    assert response.status_code == 200
    assert response.get_json() == [{'email': 'test@gmail.com', 'first_name': 'Avinash', 'last_name': 'kumar'}]

def test_get_user_by_invalid_email(client):
    # Test case for attempting to retrieve a user with an invalid email format
    # Should return a 400 Bad Request
    response = client.get('/users', query_string={'email': 'invalid_email'})

    # Assertions
    assert response.status_code == 400
    assert response.get_json() == {'status': 'error', 'error_message': 'Email id is not valid'}

def test_get_user_not_found(client):
    # Test case for attempting to retrieve a user that kumars not exist
    # Should return a 404 Not Found
    with patch('app.pymysql.connect') as mock_connect:
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor

        # Mocking the database query result to simulate no users found
        mock_cursor.fetchall.return_value = []

        # For making the API request
        response = client.get('/users', query_string={'email': 'nonexistent@gmail.com'})

    # Assertions
    assert response.status_code == 404
    assert response.get_json() == {'status': 'error', 'error_message': 'No user found'}

def test_get_users_empty_result(client):
    # Test case for successfully retrieving users, but the result set is empty
    with patch('app.pymysql.connect') as mock_connect:
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor

        # Mocking the database query result to simulate no users found
        mock_cursor.fetchall.return_value = []

        # For making the API request
        response = client.get('/users', query_string={'email': 'nonexistent@gmail.com'})

    # Assertions
    assert response.status_code == 404
    assert response.get_json() == {'status': 'error', 'error_message': 'No user found'}

def test_get_users_database_error(client):
    # Test case for handling a database error during user retrieval
    with patch('app.pymysql.connect') as mock_connect:
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor

        # Mocking the database error during query execution
        mock_cursor.execute.side_effect = Exception('Database error')

        # For making the API request
        response = client.get('/users', query_string={'email': 'test@gmail.com'})

    # Assertions
    assert response.status_code == 500
    assert response.get_json() == {'status': 'error', 'error_message': 'Database error'}




def test_create_user_success(client):
    # Test case for successfully creating a user
    with patch('app.pymysql.connect') as mock_connect:
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor

        # Mocking the database query result to simulate a user not existing
        mock_cursor.fetchone.return_value = None

        # Mocking the password hashing
        with patch('hashlib.sha256') as mock_sha256:
            mock_sha256.return_value.hexdigest.return_value = 'hashed_password'

            # For making the API request
            user_data = {
                'email': 'newuser@gmail.com',
                'first_name': 'New',
                'last_name': 'User',
                'password': 'Password123!'
            }
            response = client.post('/users', json=user_data)

    # Assertions
    assert response.status_code == 201
    assert response.get_json() == {'status': 'success', 'message': 'User created successfully'}

def test_create_user_existing_email(client):
    # Test case for attempting to create a user with an existing email
    with patch('app.pymysql.connect') as mock_connect:
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor

        # Mocking the database query result to simulate an existing user
        mock_cursor.fetchone.return_value = ('existing@gmail.com', 'Existing', 'User', 'hashed_password')

        # For making the API request
        user_data = {
            'email': 'existing@gmail.com',
            'first_name': 'Existing',
            'last_name': 'User',
            'password': 'Password123!'
        }
        response = client.post('/users', json=user_data)

    # Assertions
    assert response.status_code == 409
    assert response.get_json() == {'status': 'error', 'error_message': 'User with the same email id already exists'}


def test_create_user_empty_fields(client):
    # Test case for creating a user with empty fields
    user_data = {'email': '', 'first_name': '', 'last_name': '', 'password': ''}
    response = client.post('/users', json=user_data)

    # Assertions
    assert response.status_code == 400
    assert response.get_json() == {'status': 'error', 'error_message': 'Email cannot be empty, First name cannot be empty, Last name cannot be empty, Password cannot be empty'}

def test_create_user_invalid_email(client):
    # Test case for creating a user with an invalid email format
    user_data = {'email': 'invalid_email', 'first_name': 'Avinash', 'last_name': 'kumar', 'password': 'Password123!'}
    response = client.post('/users', json=user_data)

    # Assertions
    assert response.status_code == 400
    assert response.get_json() == {'status': 'error', 'error_message': 'email id is not valid'}

def test_create_user_weak_password(client):
    # Test case for creating a user with a weak password
    user_data = {'email': 'test@gmail.com', 'first_name': 'Avinash', 'last_name': 'kumar', 'password': 'weakpass'}
    response = client.post('/users', json=user_data)

    # Assertions
    assert response.status_code == 400
    assert response.get_json() == {'status': 'error', 'error_message': 'Password should be of atleast 8 characters and must contain atleast one special characters and one numeric value'}

def test_create_user_database_error(client):
    # Test case for handling a database error during user creation
    with patch('app.pymysql.connect') as mock_connect:
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor

        # Mocking the database query result to simulate an existing user
        mock_cursor.fetchone.return_value = None

        # Mocking the database error during insertion
        mock_cursor.execute.side_effect = Exception('Database error')

        # For making the API request
        user_data = {
            'email': 'newuser@gmail.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'Password123!'
        }
        response = client.post('/users', json=user_data)

    # Assertions
    assert response.status_code == 500
    assert response.get_json() == {'status': 'error', 'error_message': 'Database error'}

def test_update_user_success(client):
    # Test case for successfully updating user details
    with patch('app.pymysql.connect') as mock_connect:
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor

        # Mocking the database query result to simulate an existing user
        mock_cursor.fetchone.return_value = ('test@gmail.com', 'Avinash', 'kumar', 'hashed_password')

        # For making the API request
        update_data = {'first_name': 'Updated', 'last_name': 'User', 'password': 'NewPassword123!'}
        response = client.put('/users', json=update_data, query_string={'email': 'test@gmail.com'})

    # Assertions
    assert response.status_code == 200
    assert response.get_json() == {'status': 'success', 'message': 'User updated successfully'}

def test_update_user_no_email(client):
    # Test case for attempting to update user details without providing an email parameter
    response = client.put('/users', json={'first_name': 'Updated'}, query_string={'email': ''})

    # Assertions
    assert response.status_code == 400
    assert response.get_json() == {'status': 'error', 'error_message': 'Invalid or missing email'}

def test_update_user_invalid_email(client):
    # Test case for attempting to update user details with an invalid email format
    response = client.put('/users', json={'first_name': 'Updated'}, query_string={'email': 'invalid_email'})

    # Assertions
    assert response.status_code == 400
    assert response.get_json() == {'status': 'error', 'error_message': 'Invalid or missing email'}

def test_update_user_no_fields(client):
    # Test case for attempting to update user details without providing any fields
    response = client.put('/users', json={}, query_string={'email': 'test@gmail.com'})

    # Assertions
    assert response.status_code == 400
    assert response.get_json() == {'status': 'error', 'error_message': 'At least one field (first_name, last_name, password) is required for update'}


def test_update_user_user_not_found(client):
    # Test case for attempting to update details for a user that kumars not exist
    with patch('app.pymysql.connect') as mock_connect:
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor

        # Mocking the database query result to simulate no user found
        mock_cursor.fetchone.return_value = None

        # For making the API request
        update_data = {'first_name': 'Updated', 'last_name': 'User', 'password': 'NewPassword123!'}
        response = client.put('/users', json=update_data, query_string={'email': 'nonexistent@gmail.com'})

    # Assertions
    assert response.status_code == 404
    assert response.get_json() == {'status': 'error', 'error_message': 'User not found'}



def test_update_user_database_error(client):
    # Test case for handling a database error during user update
    with patch('app.pymysql.connect') as mock_connect:
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor

        # Mocking the database error during update
        mock_cursor.execute.side_effect = Exception('Database error')

        # For making the API request
        update_data = {'first_name': 'Updated', 'last_name': 'User', 'password': 'NewPassword123!'}
        response = client.put('/users', json=update_data, query_string={'email': 'test@gmail.com'})

    # Assertions
    assert response.status_code == 500
    assert response.get_json() == {'status': 'error', 'error_message': 'Database error'}


def test_delete_user_success(client):
    # Test case for successfully deleting a user by email
    with patch('app.pymysql.connect') as mock_connect:
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor

        # Mocking the database query result to simulate an existing user
        mock_cursor.fetchone.return_value = ('test@gmail.com', 'Avinash', 'kumar', 'hashed_password')

        # For making the API request
        response = client.delete('/users', query_string={'email': 'test@gmail.com'})

    # Assertions
    assert response.status_code == 200
    assert response.get_json() == {'status': 'success', 'message': 'User deleted successfully'}



def test_delete_user_invalid_email(client):
    # Test case for attempting to delete a user with an invalid email format
    response = client.delete('/users', query_string={'email': 'invalid_email'})

    # Assertions
    assert response.status_code == 400
    assert response.get_json() == {'status': 'error', 'error_message': 'Invalid email format'}

def test_delete_user_not_found(client):
    # Test case for attempting to delete a user that kumars not exist
    with patch('app.pymysql.connect') as mock_connect:
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor

        # Mocking the database query result to simulate no user found
        mock_cursor.fetchone.return_value = None

        # For making the API request
        response = client.delete('/users', query_string={'email': 'nonexistent@gmail.com'})

    # Assertions
    assert response.status_code == 404
    assert response.get_json() == {'status': 'error', 'error_message': 'User not found'}


def test_delete_user_database_error(client):
    # Test case for handling a database error during user deletion
    with patch('app.pymysql.connect') as mock_connect:
        mock_cursor = MagicMock()
        mock_connect.return_value.cursor.return_value = mock_cursor

        # Mocking the database error during deletion
        mock_cursor.execute.side_effect = Exception('Database error')

        # For making the API request
        response = client.delete('/users', query_string={'email': 'test@gmail.com'})

    # Assertions
    assert response.status_code == 500
    assert response.get_json() == {'status': 'error', 'error_message': 'Database error'}


if __name__ == '__main__':
    pytest.main()
