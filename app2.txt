import identity
import identity.web
import requests
from flask import Flask, redirect, render_template, request, session, url_for, g
from flask_session import Session
import psycopg2
import app_config

app = Flask(__name__)
app.config.from_object(app_config)
Session(app)

# This section is needed for url_for("foo", _external=True) to automatically
# generate http scheme when this sample is running on localhost,
# and to generate https scheme when it is deployed behind reversed proxy.
# See also https://flask.palletsprojects.com/en/2.2.x/deploying/proxy_fix/
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

auth = identity.web.Auth(
    session=session,
    authority=app.config.get("AUTHORITY"),
    client_id=app.config["CLIENT_ID"],
    client_credential=app.config["CLIENT_SECRET"],
)

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

INSERT INTO users (email, name, role, status)
VALUES 
    (LOWER('tbnguy36@CougarNet.UH.EDU'), 'Nguyen, Binh', 'admin', TRUE),
    (LOWER('jdoe@example.com'), 'John Doe', 'basicUser', TRUE),
    (LOWER('janedoe@example.com'), 'Jane Doe', 'basicUser', TRUE),
    (LOWER('michael.smith@example.com'), 'Michael Smith', 'vipUser', TRUE),
    (LOWER('emily.jones@example.com'), 'Emily Jones', 'vipUser', TRUE),
    (LOWER('alex.brown@example.com'), 'Alex Brown', 'basicUser', TRUE)
ON CONFLICT (email) DO NOTHING;
"""

# Before request: Set up database connection
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

@app.route("/login")
def login():
    return render_template("login.html", version=identity.__version__, **auth.log_in(
        scopes=app_config.SCOPE,  # Have user consent to scopes during log-in
        redirect_uri=url_for("auth_response", _external=True),  # Optional. If present, this absolute URL must match your app's redirect_uri registered in Azure Portal
    ))

@app.route("/logout")
def logout():
    return redirect(auth.log_out(url_for("index", _external=True)))

@app.route("/")
def index():
    if not (app.config["CLIENT_ID"] and app.config["CLIENT_SECRET"]):
        return render_template('config_error.html')
    if not auth.get_user():
        return redirect(url_for("login"))
    return render_template('index.html', user=auth.get_user(), version=identity.__version__)

@app.route("/admin")
def admin_dash():
    g.db_cursor.execute("SELECT * FROM users")
    users = g.db_cursor.fetchall()
    print("users: ", users)
    return render_template("admin.html",users=users)

@app.route(app_config.REDIRECT_PATH)
def auth_response():
    result = auth.complete_log_in(request.args)
    if "error" in result:
        return render_template("auth_error.html", result=result)

    user = auth.get_user()
    if user:
        name = user.get("name").lower()
        email = user.get("preferred_username").lower()  # Email
        session["user"] = {"name": name, "email": email}

        # Check if the user already exists in the database
        g.db_cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = g.db_cursor.fetchone()

        if not existing_user:
            # Insert user if not exists
            g.db_cursor.execute("INSERT INTO users (email, name, role, status) VALUES (%s, %s, %s, %s)",
                               (email, name, "basicuser", True))
            g.db_conn.commit()

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host='localhost', port=5002)
