Team Vernon

# COSC 4353 Project

HOW TO RUN THIS PROGRAM
We are using PostgresSQL with database named "vernon"

# Step 1 : set up env variable in this format

- Create in .env file in the working directory and import these value

CLIENT_ID=
CLIENT_SECRET=
PORT = 5002
DB_HOST = localhost
DB_PORT =
DB_NAME = vernon
DB_USER =
DB_PASSWORD =

# Step 2: create a virtual environment for the app:

Window:
py -m venv .venv
.venv\scripts\activate

MacOS/Linux:
python3 -m venv .venv
source .venv/bin/activate

# Step 3: install dependencies in requirements.txt

pip install -r requirements.txt
or
pip3 install -r requirements.txt

# Step 4: Run the app:

python app.py
