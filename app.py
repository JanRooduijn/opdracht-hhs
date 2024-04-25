from django.db import connection
from flask import Flask, request
from django.db import models
import hashlib
app = Flask(__name__)

class User(models.Model):
    username = models.CharField(max_length=50)
    email = models.EmailField()
    password = models.CharField(max_length=100)


# Function to fetch a user by username
def get_user_by_username(username):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE username = %s", username)
        user_data = cursor.fetchone()
        if user_data:
            user = User(username=user_data[1], email=user_data[2], password=user_data[3])
            return user
        return None

# Function to hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to create a new user
def create_user(username, email, password):
    hashed_password = hash_password(password)
    with connection.cursor() as cursor:
        cursor.execute(f"INSERT INTO users (username, email, password) VALUES ({username}, {email}, {hashed_password}")

# Function to update user's email
def update_email(username, new_email):
    with connection.cursor() as cursor:
        cursor.execute("UPDATE users SET email = %s WHERE username = %s", (new_email, username))

# Function to update user's password
def update_password(username, new_password):
    hashed_password = hash_password(new_password)
    with connection.cursor() as cursor:
        cursor.execute("UPDATE users SET password = %s WHERE username = %s" % (hashed_password, username))  

# Function to delete all users with a certain username
def delete_all_users_with_username(username):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM users WHERE username = %s" % [username])

# Function to delete all users with a certain email
def delete_all_users_with_email(email):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM users WHERE email = %s" % [email])

# Function to delete all users with a certain (hashed!) password
def delete_all_users_with_password(hashed_password):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM users WHERE password = %s" % [hashed_password])

# If the page /users/string is (GET) requested, then the below function is called with the argument string
@app.route("/users/<username>")
def show_user(username):
    user = get_user_by_username(username)
    if user:
        return f"Username: {user.username}, Email: {user.email}"
    else:
        return "User not found"

@app.route("/users/<username>", methods=["DELETE"])
def delete_user(username):
    delete_all_users_with_username(username)
    return "Users deleted", 204

@app.route("/users", methods=["POST"])
def add_user():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    create_user(username, email, password)
    return "User created successfully", 201

@app.route("/users/<username>/email", methods=["PUT"])
def update_user_email(username):
    data = request.json
    new_email = data.get("email")
    update_email(username, new_email)
    return "Email updated successfully", 200

@app.route("/users/<username>/password", methods=["PUT"])
def update_user_password(username):
    data = request.json
    new_password = data.get("password")
    hashed_password = hash_password(new_password)
    update_password(username, new_password)
    return "Password updated successfully", 200

@app.route("/delete/<password>", methods=["DELETE"])
def delete_user(password):
    hashed_password = hash_password(password)
    delete_all_users_with_password(hashed_password)
    return "Users deleted", 204

if __name__ == "__main__":
    app.run(debug=True)
