import requests
from flask import Flask, redirect, request, session, url_for, render_template,g,jsonify
import app_config
import psycopg2
from urllib.parse import urlencode


app = Flask(__name__)
app.config.from_object(app_config)
app.secret_key = "your_secret_key_here"  # Set a unique and secret key

createDatabase = """
CREATE TABLE IF NOT EXISTS users (
    email VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    role VARCHAR(255),
    status BOOLEAN
);

INSERT INTO users (email, name, role, status)
VALUES (LOWER('tbnguy36@CougarNet.UH.EDU'), 'Nguyen, Binh', 'admin', TRUE)
ON CONFLICT (email) DO NOTHING;
"""

def get_user_by_email(email):
    if not email:
        return None
    """Retrieve a specific user from the database by email."""
    g.db_cursor.execute("SELECT email, name, role, status FROM users WHERE email = %s", (email,))
    user = g.db_cursor.fetchone()

    if user:
        return {
            "email": user[0],
            "name": user[1],
            "role": user[2],
            "status": user[3],
        }
    return None  # Return None if the user is not found


@app.before_request
def before_request():
    """Create a database connection before each request."""
    g.db_conn = psycopg2.connect(
        host=app_config.DB_HOST,
        port=app_config.DB_PORT,
        dbname=app_config.DB_NAME,
        user=app_config.DB_USER,
        password=app_config.DB_PASSWORD
    )
    g.db_cursor = g.db_conn.cursor()
    g.db_cursor.execute(createDatabase)
    g.db_conn.commit()
    print("Database connected")

# After request: Close the connection
@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db_cursor.close()
    g.db_conn.close()
    return response

# Microsoft Login URL
@app.route("/login")
def login():
    auth_url = f"{app_config.AUTHORITY}/oauth2/v2.0/authorize?"
    auth_params = {
        'client_id': app_config.CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': url_for('auth_response', _external=True),
        'scope': ' '.join(app_config.SCOPE),
        'state': '12345'  # Security measure
    }
    return redirect(auth_url + urlencode(auth_params))

@app.route("/add_user", methods=["POST"])
def add_user():
    data = request.json  # Get JSON data from frontend
    email = data.get("email").lower()
    name = data.get("name")
    role = data.get("role", "basicUser")  # Default role if not provided
    status = data.get("status", True)  # Default status to active (True) if not provided

    # Check if the user already exists in the database
    g.db_cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = g.db_cursor.fetchone()  # Use fetchone to get a single result

    # If the user exists and is deactivated, return 401 Unauthorized
    if user:
        if not user[3]:  # Assuming user[3] is the 'status' column in your database
            return jsonify({"error": "User is deactivated."}), 401

    # If the user doesn't exist or is active, insert or do nothing
    if not user:
        g.db_cursor.execute(
            "INSERT INTO users (email, name, role, status) VALUES (%s, %s, %s, %s) ON CONFLICT (email) DO NOTHING",
            (email, name, role, status),
        )
        g.db_conn.commit()

    return jsonify({"message": "User added successfully"}), 201


@app.route("/update_user", methods=["POST"])
def update_user():
    # if "user" not in session:
    #     return "Unauthorized", 403

    updated_users = request.json.get('users')  # Get the updated users from the request
    print("updated user:" ,updated_users)
    for user_data in updated_users:
        email = user_data.get("email").lower()
        new_name = user_data.get("name")
        new_role = user_data.get("role")
        new_status = user_data.get("status")
        if user_data.get("status") == "True":
            new_status = True
        else:
            new_status = False
        # Prepare the SQL query to update the user information
        query = """
            UPDATE users 
            SET name = %s, role = %s, status = %s 
            WHERE email = %s
        """
        g.db_cursor.execute(query, (new_name, new_role, new_status, email))
        g.db_conn.commit()

    return {"message": "User information updated successfully"}, 200

@app.route("/delete_user", methods=["POST"])
def delete_user():

    data = request.json
    email = data.get("email").lower()
    print("deleteing email: ",email)
    # Check if the user exists before attempting to delete
    g.db_cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = g.db_cursor.fetchone()
    if not user:
        return {"message": "User not found"}, 404

    g.db_cursor.execute("DELETE FROM users WHERE email = %s", (email,))
    g.db_conn.commit()
    return {"message": "User deleted"}, 200


# Authentication Callback
@app.route(app_config.REDIRECT_PATH)
def auth_response():
    code = request.args.get('code')
    if not code:
        return "Error: No authorization code received", 400

    token_url = f"{app_config.AUTHORITY}/oauth2/v2.0/token"
    token_data = {
        'client_id': app_config.CLIENT_ID,
        'client_secret': app_config.CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': url_for('auth_response', _external=True),
    }

    token_response = requests.post(token_url, data=token_data)
    token_info = token_response.json()
    access_token = token_info.get('access_token')

    if access_token:
        session['access_token'] = access_token

        # Fetch user info from Microsoft Graph API
        graph_url = 'https://graph.microsoft.com/v1.0/me'
        headers = {'Authorization': f'Bearer {access_token}'}
        user_info = requests.get(graph_url, headers=headers).json()

        session['user'] = {
            'name': user_info.get('displayName').lower(),
            'email': user_info.get('userPrincipalName').lower(),
        }
        url = f"http://localhost:{app_config.PORT}/add_user"
        data = session['user']
        res = requests.post(url,json=data)
        return redirect(url_for('index'))
    
    return "Error: Unable to retrieve token", 400

# Home Page
@app.route("/")
def index():
    user = session.get("user")  # Get user info from session
    userinfo = None
    if user:
        userinfo = get_user_by_email(user['email'])
    print(userinfo)
    return render_template("index.html", user=userinfo)

# Logout
@app.route("/logout")
def logout():
    session.clear()  # Clear session
    return redirect("https://login.microsoftonline.com/common/oauth2/v2.0/logout?post_logout_redirect_uri=" + url_for('index', _external=True))

@app.route("/admin")
def admin_dash():
    user = session.get("user")
    if not user:
        return "Forbidden", 403
    userInfo = get_user_by_email(user['email'])
    if (userInfo['role'].lower() != "admin"):
        return "Forbidden", 403
    g.db_cursor.execute("SELECT * FROM users")
    users = g.db_cursor.fetchall()
    print("users: ", users)
    return render_template("admin.html",users=users)

@app.route("/reactivate", methods=["POST"])
def reactivate_account():
    try:
        # Get the email from the request body
        data = request.get_json()  # Parse the JSON request
        email = data.get('email')

        if not email:
            return jsonify({"success": False, "message": "No email provided"}), 400
        
        # Reactivate the user's account (update the database)
        g.db_cursor.execute("UPDATE users SET status = %s WHERE email = %s", (True, email))  # Assuming True means active
        g.db_cursor.connection.commit()  # Commit the changes to the database
        
        return jsonify({"success": True, "message": "Account reactivated successfully"})
    
    except Exception as e:
        print(f"Error reactivating account: {e}")
        return jsonify({"success": False, "message": "An error occurred while reactivating the account"}), 500
    
if __name__ == "__main__":
    app.run(host='localhost', port=5002)
