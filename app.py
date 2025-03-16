import requests
from flask import Flask, redirect, request, session, url_for, render_template,g,jsonify, Response
import app_config
import psycopg2
from urllib.parse import urlencode
import os
import subprocess
import base64
import io

app = Flask(__name__)
app.config.from_object(app_config)
app.secret_key = "your_secret_key_here"  # Set a unique and secret key
SAVE_DIR = "saved_tex_files"
os.makedirs(SAVE_DIR, exist_ok=True)


createDatabase = """
CREATE TABLE IF NOT EXISTS users (
    email VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    role VARCHAR(255),
    account_status BOOLEAN
);

CREATE TABLE IF NOT EXISTS forms (
    form_id SERIAL PRIMARY KEY,
    email VARCHAR(255),
    form_name VARCHAR(255),
    form_content TEXT,
    status VARCHAR(255),
    user_signature BYTEA,
    approver_signature BYTEA
);

INSERT INTO users (email, name, role, account_status)
VALUES 
    (LOWER('tbnguy36@CougarNet.UH.EDU'), 'Nguyen, Binh', 'admin', TRUE),
    (LOWER('fmmancil@cougarnet.uh.edu'), 'Mancilla, Fernando', 'admin', TRUE),
    (LOWER('rlpham3@cougarnet.uh.edu'), 'Pham, Ryan', 'admin', TRUE),
    (LOWER('john.doe@CougarNet.UH.EDU'), 'John Doe', 'basicUser', TRUE),
    (LOWER('jane.smith@CougarNet.UH.EDU'), 'Jane Smith', 'basicUser', FALSE),
    (LOWER('alice.johnson@CougarNet.UH.EDU'), 'Alice Johnson', 'vipUser', TRUE),
    (LOWER('bob.williams@CougarNet.UH.EDU'), 'Bob Williams', 'vipUser', FALSE)
ON CONFLICT (email) DO NOTHING;

"""


def save_signature(base64_str):
    image_data = base64.b64decode(base64_str.split(",")[1])  # Remove header
    with open("signature.png", "wb") as f:
        f.write(image_data)

def get_user_by_email(email):
    if not email:
        return None
    """Retrieve a specific user from the database by email."""
    g.db_cursor.execute("SELECT email, name, role, account_status FROM users WHERE email = %s", (email,))
    user = g.db_cursor.fetchone()

    if user:
        return {
            "email": user[0],
            "name": user[1],
            "role": user[2],
            "account_status": user[3],
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
    account_status = data.get("account_status", True)  # Default status to active (True) if not provided

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
            "INSERT INTO users (email, name, role, account_status) VALUES (%s, %s, %s, %s) ON CONFLICT (email) DO NOTHING",
            (email, name, role, account_status),
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
        new_status = user_data.get("account_status")
        if user_data.get("account_status") == "True":
            new_status = True
        else:
            new_status = False
        # Prepare the SQL query to update the user information
        query = """
            UPDATE users 
            SET name = %s, role = %s, account_status = %s 
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
    g.db_cursor.execute("SELECT * FROM forms")
    forms = g.db_cursor.fetchall()
    return render_template("index.html", user=userinfo,forms = forms)

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

    g.db_cursor.execute("SELECT * FROM forms")
    forms = g.db_cursor.fetchall()
    print("forms: ",forms)
    print("forms len", len(forms))
    approver_signature_binary = None
    if (forms):
        updated_forms = []
        for form in forms:
            forms_list = form
            if form[6]:
                approver_signature_binary = form[6]
                forms_list = list(form)  # Convert the first tuple to a list
                forms_list[6] = base64.b64encode(approver_signature_binary).decode('utf-8')
                print("binary img generated: ",forms_list[6])  # Modify the list
            updated_forms.append(tuple(forms_list))
                  # Convert it back to a tuple if needed
        forms = updated_forms
    print("forms: ",forms)
    return render_template("admin.html",users=users,forms=forms)

@app.route("/reactivate", methods=["POST"])
def reactivate_account():
    try:
        # Get the email from the request body
        data = request.get_json()  # Parse the JSON request
        email = data.get('email')

        if not email:
            return jsonify({"success": False, "message": "No email provided"}), 400
        
        # Reactivate the user's account (update the database)
        g.db_cursor.execute("UPDATE users SET account_status = %s WHERE email = %s", (True, email))  # Assuming True means active
        g.db_cursor.connection.commit()  # Commit the changes to the database
        
        return jsonify({"success": True, "message": "Account reactivated successfully"})
    
    except Exception as e:
        print(f"Error reactivating account: {e}")
        return jsonify({"success": False, "message": "An error occurred while reactivating the account"}), 500

@app.route("/graduate-student-petition-form")
def handleGraduateStudentPetitionForm():
    user = session.get("user")
    userName = user['name'].split(",")

    print(userName)
    return render_template("forms/graduate_student_petition_form.html",userName=userName)

# @app.route('/user-forms')
# def user_forms():

@app.route('/approve-form', methods=['POST'])
def approve_form():
    try:
        print("approve formmmm")
        user = session.get("user")
        if not user or "email" not in user:
            print("yes")
            return jsonify({"error": "User not authenticated"}), 401
        print("data approve form got 0")
        data = request.get_json()
        print("data approve form got")
        formId = data.get("formId")
        print("form id",formId)
        approverSignatureBase64 = data.get("approverSignatureBase64")
        status = data.get("status")
        approver_signature_binary = None
        if approverSignatureBase64:
            try:
                approver_signature_binary = base64.b64decode(approverSignatureBase64.split(",")[1])
            except (IndexError, ValueError):
                return jsonify({"error": "Invalid signature format"}), 400

        print("hereeee")
        query = """
        UPDATE forms
        SET status = %s, approver_signature = %s
        WHERE form_id = %s;
        """
        data = (status,approver_signature_binary,formId)
        print("databaseee")
        g.db_cursor.execute(query,data)
        g.db_conn.commit()
        print("databaseee done")
        return jsonify({"message": "approved form"})

    except Exception as e:
        return jsonify({"Error message": "Error approved form"})
    

@app.route('/update-latex', methods=['POST'])
def update_latex():
    try:
        user = session.get("user")
        if not user or "email" not in user:
            return jsonify({"error": "User not authenticated"}), 401

        data = request.get_json()
        latex_content = data.get("content")
        signature_base64 = data.get("signature")

        if latex_content is None:
            return jsonify({"error": "Missing LaTeX content"}), 400

        # Convert signature from Base64 to binary
        signature_binary = None
        if signature_base64:
            try:
                signature_binary = base64.b64decode(signature_base64.split(",")[1])
            except (IndexError, ValueError):
                return jsonify({"error": "Invalid signature format"}), 400

        # Update both columns

        query = '''
        INSERT INTO forms (email, form_name, form_content, status, user_signature, approver_signature)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (form_id) 
        DO UPDATE SET 
            form_content = EXCLUDED.form_content,
            user_signature = EXCLUDED.user_signature;

        '''
        print("here 1")
        print(user["email"].lower().strip())
        user_email = user["email"].lower().strip()
        form_name = "graduate student petition form"
        status = "pending"
        approver_signature = None
        data = (user_email, form_name, latex_content, status, signature_binary,approver_signature)
        g.db_cursor.execute(query, data)

        g.db_conn.commit()
        print("here 2")
        # query = """
        #     SELECT *
        #     FROM users
        #     WHERE email = %s
        # """
        # g.db_cursor.execute(query, (user["email"].lower().strip(),))
        # updated_row = g.db_cursor.fetchone()
        # updated_row_list = list(updated_row)  # Convert tuple to list for modification
        # if isinstance(updated_row_list[5], memoryview):  # Assuming signature is at index 5
        #     updated_row_list[5] = bytes(updated_row_list[5])  # Convert to bytes
        # print("updated row: ", updated_row_list[4])
        # # updated_row = g.db_cursor.fetchone()
        # if not updated_row:
                
        #     return jsonify({"error": "No row updated. User may not exist"}), 404

        return jsonify({"message": "LaTeX and signature updated"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/show_pdf", methods=["POST"])
def show_pdf():
    data = request.get_json()

    if not data or "formId" not in data:
        return jsonify({"error": "Missing LaTeX content"}), 400

    formId = data["formId"]
    userEmail = data["userEmail"]
    print("got user email: ", formId)

    query_latex = """
    SELECT form_content, user_signature
    FROM forms
    WHERE form_id = %s
    """
    g.db_cursor.execute(query_latex, (formId,))
    result = g.db_cursor.fetchone()

    if not result or not result[0]:
        return jsonify({"error": "No LaTeX content found for this user"}), 404

    full_latex = result[0]  # Fetch LaTeX content from the database
    signature_image_data = result[1]  # Fetch signature image
    file_name = f"{userEmail}_petition"
    # Save the LaTeX content to a file
    with open(f"{file_name}.tex", "w", encoding="utf-8") as f:
        f.write(full_latex)

    # Save the signature image (if available)
    if signature_image_data:
        with open(f"{file_name}_signature.png", "wb") as f:
            f.write(signature_image_data)
        print("Signature image saved as signature.png")

    # Run `make` to compile LaTeX
    process = subprocess.run(["make",f"TEX_FILE={file_name}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if process.returncode != 0:
        print("Make failed with error:", process.stderr.decode())
        return jsonify({"error": process.stderr.decode()}), 500

    # Read generated PDF into memory
    pdf_output = io.BytesIO()
    with open(f"{file_name}.pdf", "rb") as f:
        pdf_output.write(f.read())

    pdf_output.seek(0)
    process = subprocess.run(["make","clean",f"TEX_FILE={file_name}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return Response(pdf_output, mimetype="application/pdf")


if __name__ == "__main__":
    app.run(host='localhost', port=app_config.PORT)
# hi