from flask import (
Flask, redirect,
render_template,
request,
flash,
url_for,
get_flashed_messages
)
import validators
import psycopg2
import os
from datetime import date, datetime
from urllib.parse import urlparse
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

@app.route('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        'index.html',
        messages=messages,
        )


@app.post('/urls')
def get_url():
    received_url = request.form.get('url')
    if validators.url(received_url):
        parsed_url = urlparse(received_url).hostname
        created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM urls")
        in_db = cursor.fetchall()
        conn.commit()
        cursor = conn.cursor()
        if parsed_url in [url[0] for url in in_db]:
            flash('Url already in list.', 'warning')
        else:
            cursor.execute("INSERT INTO urls (name, created_at) VALUES (%s, %s)", (parsed_url, created))
            flash('Url was added to list.', 'success')
        cursor.execute("SELECT * FROM urls WHERE name = %s", (parsed_url,))
        received_url = cursor.fetchall()
        id = received_url[0][0]
        conn.commit()
    else:
        flash('Url is not valid!', 'warning')
        conn.close()
        return redirect(url_for('index'))
    conn.close()
    return redirect(
        url_for('url_info', id=id),
    )

@app.post('/urls/<id>/checks')
def get_url_check(id):
    created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO url_checks  (url_id, status_code, h1, title, description, created_at) VALUES (%s, %s, %s, %s, %s, %s)", (id, 'код ответа', 'h1', 'title', 'description', created))
    return redirect(
        url_for('url_info', id=id),
    )

@app.get('/urls/<id>')
def url_info(id):
    messages = get_flashed_messages(with_categories=True)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM urls WHERE id = %s", (id,))
    received_url = cursor.fetchall()
    name = received_url[0][1]
    created = received_url[0][2]
    cursor.execute("SELECT * FROM url_checks WHERE url_id = %s ORDER BY created_at DESC", (id,))
    url_checks = cursor.fetchall()
    return render_template(
        'info.html',
        id=id,
        name=name,
        created=created,
        messages=messages,
        url_checks=url_checks,
    )

@app.get('/urls')
def create():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM urls ORDER BY created_at DESC")
    urls_list = cursor.fetchall()
    conn.commit()
    cursor.close()
    return render_template(
        'urls.html',
        urls_list=urls_list,
    )
 

if __name__ == '__main__':
    app.run()
