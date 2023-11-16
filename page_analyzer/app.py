from flask import (
Flask, redirect,
render_template,
request,
flash,
url_for,
get_flashed_messages
)

import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/urls', methods=['POST'])
def create():
    # Get the username and email from the request body
    username = request.form.get('username')
    email = request.form.get('email')
 
    # Insert the data into the database
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (username, email) VALUES (%s, %s)", (username, email))
    conn.commit()
 
    return 'User created successfully!'
 
 
if __name__ == '__main__':
    app.run()
