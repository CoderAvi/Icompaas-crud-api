import json
import pymysql
import hashlib
from flask import Flask, request, jsonify, make_response
import re

app = Flask(__name__)

# MySQL configurations
host = 'icompaas-db.c7suguekuh6r.us-east-1.rds.amazonaws.com'
user = 'coderavi'
password = 'Ambujacement'
database = 'icompaasdb'

# Helper function to create a database connection
def create_connection():
    return pymysql.connect(host=host, user=user, password=password, database=database)

# Helper function for email validation
def is_valid_email(email):
    # Use regular expression to check email format
    email_regex = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    return bool(re.match(email_regex, email))

# Helper function for password validation
def is_valid_password(password):
    # Check password strength (at least 8 characters, one special char, and one numeric value)
    return bool(re.match(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$', password))

# Create user
@app.route("/users", methods=["POST"])
def create_user():
    try:
        conn = create_connection()
        cursor = conn.cursor()

        data = request.get_json()
        email = data['email']
        first_name = data['first_name']
        last_name = data['last_name']
        password = data['password']

       # Validate request payload
        required_fields = {'email': 'Email', 'first_name': 'First name', 'last_name': 'Last name', 'password': 'Password'}
        error_messages = [f"{field_name} cannot be empty" for field, field_name in required_fields.items() if not data.get(field) or not data[field].strip()]
        
        if error_messages:
            return make_response(jsonify(status='error', error_message=', '.join(error_messages)), 400)
        
        # Additional Validations
        if not is_valid_email(email):
            return make_response(jsonify(status='error', error_message='email id is not valid'), 400)

        if not is_valid_password(password):
            return make_response(jsonify(status='error', error_message='Password should be of atleast 8 characters and must contain atleast one special characters and one numeric value'), 400)

        # Check if user with the same email already exists
        check_query = f"SELECT * FROM USER WHERE email_id = '{email}'"
        cursor.execute(check_query)
        existing_user = cursor.fetchone()

        if existing_user:
            return make_response(jsonify(status='error', error_message='User with the same email id already exists'), 409)

        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Insert user into the database
        insert_query = f"INSERT INTO USER (email_id, firstname, lastname, password) VALUES ('{email}', '{first_name}', '{last_name}', '{hashed_password}')"
        cursor.execute(insert_query)
        conn.commit()

        # Close the database connection
        conn.close()

        return make_response(jsonify(status='success', message='User created successfully'), 201)

    except Exception as e:
        return make_response(jsonify(status='error', error_message=str(e)), 500)


if __name__ == '__main__':
    app.run(debug=True)


# Get all users or a specific user by email
@app.route("/users", methods=["GET"])
def get_users():
    try:
        conn = create_connection()
        cursor = conn.cursor()

        email = request.args.get('email')

        if email and not is_valid_email(email):
            return make_response(jsonify(status='error', error_message='Email id is not valid'), 400)

        if not email:
            query = f"SELECT * FROM USER"
        else:
            query = f"SELECT * FROM USER WHERE email_id = '{email}'"

        cursor.execute(query)
        results = cursor.fetchall()

        if not results:
            return make_response(jsonify(status='error', error_message='No user found'), 404)

        users = []
        for result in results:
            user = {
                'email': result[0],
                'first_name': result[1],
                'last_name': result[2]
            }
            users.append(user)

        # Close the database connection
        conn.close()

        return jsonify(users)

    except Exception as e:
        return make_response(jsonify(status='error', error_message=str(e)), 500)
    

# Update user
@app.route("/users", methods=["PUT"])
def update_user():
    try:
        conn = create_connection()
        cursor = conn.cursor()

        email = request.args.get('email')
        if not email or not is_valid_email(email):
            return make_response(jsonify(status='error', error_message='Invalid or missing email'), 400)

        data = request.get_json()
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        # Check if at least one field is provided for update
        if not any([first_name, last_name, password]):
            return make_response(jsonify(status='error', error_message='At least one field (first_name, last_name, password) is required for update'), 400)

        # Check if email is provided in the request body
        if 'email' in data:
            return make_response(jsonify(status='error', error_message='Email cannot be updated'), 400)

        # Get existing user details
        check_query = f"SELECT * FROM USER WHERE email_id = '{email}'"
        cursor.execute(check_query)
        existing_user = cursor.fetchone()

        if not existing_user:
            return make_response(jsonify(status='error', error_message='User not found'), 404)

        existing_first_name, existing_last_name, existing_password = existing_user[1], existing_user[2], existing_user[3]

        # Check if details remain unchanged
        if (
            (first_name == existing_first_name or first_name is None) and
            (last_name == existing_last_name or last_name is None) and
            (password == existing_password or password is None)
        ):
            return make_response(jsonify(status='success', message='User details remain unchanged'), 200)

        # Update user fields
        update_query = "UPDATE USER SET"

        if first_name:
            update_query += f" firstname = '{first_name}',"
        if last_name:
            update_query += f" lastname = '{last_name}',"
        if password:
            update_query += f" password = '{password}',"

        # Remove the trailing comma
        update_query = update_query.rstrip(',')

        update_query += f" WHERE email_id = '{email}'"

        cursor.execute(update_query)
        conn.commit()

        # Close the database connection
        conn.close()

        return jsonify(status='success', message='User updated successfully')

    except Exception as e:
        return make_response(jsonify(status='error', error_message=str(e)), 500)


# Delete user
@app.route("/users", methods=["DELETE"])
def delete_user():
    try:
        conn = create_connection()
        cursor = conn.cursor()

        # Get email from query parameter
        email = request.args.get('email')

        if not email:
            # If no email provided, check if any user exists
            check_users_query = "SELECT * FROM USER"
            cursor.execute(check_users_query)
            existing_users = cursor.fetchall()

            if not existing_users:
                return make_response(jsonify(status='error', error_message='No user found to delete'), 404)

            # Delete all users
            query = "DELETE FROM USER"
        else:
            # Validate email format
            if not is_valid_email(email):
                return make_response(jsonify(status='error', error_message='Invalid email format'), 400)

            # Check if user with the specified email exists
            check_query = f"SELECT * FROM USER WHERE email_id = '{email}'"
            cursor.execute(check_query)
            existing_user = cursor.fetchone()

            if not existing_user:
                return make_response(jsonify(status='error', error_message='User not found'), 404)

            # Delete the user with the specified email
            query = f"DELETE FROM USER WHERE email_id = '{email}'"

        cursor.execute(query)
        conn.commit()

        # Close the database connection
        conn.close()

        return jsonify(status='success', message='User deleted successfully')

    except Exception as e:
        return make_response(jsonify(status='error', error_message=str(e)), 500)

@app.errorhandler(404)
def resource_not_found(e):
    return make_response(jsonify(error='Not found!'), 404)

if __name__ == '__main__':
    app.run(debug=True)
