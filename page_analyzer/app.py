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
from datetime import datetime, date
from urllib.parse import urlparse
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

def response_from(url):
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session.get(url) 
    
    
def get_tags(url):
    html_content = response_from(url).text 
    soup = BeautifulSoup(html_content, "html.parser")
    if soup.h1:
        h1 = str(soup.h1.string)
    else:
        h1 = ''
    if soup.title:
        title = str(soup.title.string) if soup.title.string else ''
    else:
        title = ''
    if soup.find('meta', {'name':'description'}):
        description = soup.find('meta', {'name':'description'}).get('content')
    else:
        description = ''
    return h1, title, description

@app.route('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    check_message = 'Проверить' 
    return render_template(
        'index.html',
        messages=messages,
        check_message=check_message,
        )


@app.post('/urls')
def get_url():
    received_url = request.form.get('url')
    if validators.url(received_url):
        conn = psycopg2.connect(DATABASE_URL)
        scheme = urlparse(received_url).scheme
        hostname = urlparse(received_url).hostname
        parsed_url = (scheme + '://' + hostname)
        created = date.today()
        with conn.cursor() as cursor:
            cursor.execute("SELECT name FROM urls")
            in_db = cursor.fetchall()
            cursor = conn.cursor()
            if parsed_url in [url[0] for url in in_db]:
                flash('Страница уже существует', 'warning')
            else:
                cursor.execute('''
                               INSERT INTO urls (name, created_at)
                               VALUES (%s, %s)
                               ''', (parsed_url, created))
                conn.commit()
                flash('Страница успешно добавлена', 'success')
            cursor.execute('''
                           SELECT * FROM urls WHERE name = %s
                           ''', (parsed_url,))
            received_url = cursor.fetchall()
            id = received_url[0][0]
        conn.close()
        return redirect(
            url_for('url_info', id=id),
            code=302,
        )
    else:
        flash('Некорректный URL', 'warning')
        return redirect(
            url_for('index'),
            code=422,
            check_message=received_url,
        )


@app.post('/urls/<id>/checks')
def get_url_check(id):
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM urls WHERE id = %s", (id,))
        received_url = cursor.fetchall()
        url = (received_url[0][1])
    conn.close()
    r = response_from(url)
    status = r.status_code
    if int(status) != 200:
        flash('Произошла ошибка при проверке', 'warning')
        return redirect(
            url_for('url_info', id=id),
        )
    r = response_from(url)
    status = r.status_code
    created = date.today()
    conn = psycopg2.connect(DATABASE_URL)
    h1, title, description = get_tags(url)
    with conn.cursor() as cursor:
        cursor.execute('''
                       INSERT INTO url_checks (
                           url_id, status_code, h1, title, description, created_at
                       )
                       VALUES (%s, %s, %s, %s, %s, %s)
                       ''', (id, status, h1, title, description, created))
        conn.commit()
    conn.close()
    flash('Страница успешно проверена', 'success')
    return redirect(
        url_for('url_info', id=id),
        code=302,
    )

@app.get('/urls/<id>')
def url_info(id):
    messages = get_flashed_messages(with_categories=True)
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM urls WHERE id = %s", (id,))
        received_url = cursor.fetchall()
        name = received_url[0][1]
        created = received_url[0][2]
        cursor.execute('''
                       SELECT * FROM url_checks
                       WHERE url_id = %s
                       ORDER BY id DESC
                       ''', (id,))
        url_checks = cursor.fetchall()
    conn.close()
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
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cursor:
        cursor.execute('''
                       SELECT u.id, u.name, MAX(uc.created_at), uc.status_code
                       FROM urls AS u LEFT JOIN url_checks AS uc
                       ON u.id = uc.url_id
                       GROUP BY u.id, u.name, uc.status_code
                       ORDER BY u.id DESC
                       ''')
        urls_list = cursor.fetchall()
    conn.close()
    return render_template(
        'urls.html',
        urls_list=urls_list,
    )
 

if __name__ == '__main__':
    app.run()
