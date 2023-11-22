import psycopg2
from dotenv import load_dotenv
import os
from datetime import date
from page_analyzer.parser import get_tags


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def get_id_by_url(url):
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cursor:
        cursor.execute('''
                SELECT * FROM urls WHERE name = %s
                ''', (url,))
        received_url = cursor.fetchall()
        id = received_url[0][0]
    conn.close()
    return id


def add_url(url):
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cursor:
        created = date.today()
        cursor.execute('''
                        INSERT INTO urls (name, created_at)
                        VALUES (%s, %s)
                        ''', (url, created))
        conn.commit()
    conn.close()


def get_url_with_checks(id):
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cursor:
        cursor.execute('''
                       SELECT * FROM url_checks
                       WHERE url_id = %s
                       ORDER BY id DESC
                       ''', (id,))
        url_checks = cursor.fetchall()
    conn.close()

    return url_checks


def get_urls_names():
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cursor:
        cursor.execute("SELECT name FROM urls")
        in_db = cursor.fetchall()
    conn.close()
    return [url[0] for url in in_db]


def get_urls():
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
    return urls_list


def get_url_by_id(id):
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM urls WHERE id = %s", (id,))
        received_url = cursor.fetchall()
        url = received_url[0][1]
        created = received_url[0][2]
    conn.close()
    return url, created


def add_check(id, status):
    created = date.today()
    url, _ = get_url_by_id(id)
    h1, title, description = get_tags(url)
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cur() as cur:
        created = date.today()
        cur.execute('''
                    INSERT INTO url_checks (
                        url_id, status_code, h1, title, description, created_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ''', (id, status, h1, title, description, created))
        conn.commit()
    conn.close()
