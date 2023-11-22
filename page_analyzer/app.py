from flask import (
    Flask,
    redirect,
    render_template,
    request,
    flash,
    url_for,
    get_flashed_messages,
)
from page_analyzer.requests import response_from
from page_analyzer.validators import validate, normilyze
from page_analyzer.db import (
    get_id_by_url,
    add_url,
    get_url_with_checks,
    get_urls,
    get_url_by_id,
    add_check,
    get_urls_names
)
from dotenv import load_dotenv
import os


load_dotenv()


app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    check_message = 'https://www.example.com'
    return render_template(
        'index.html',
        messages=messages,
        check_message=check_message,
    )


@app.post('/urls')
def get_url():
    received_url = request.form.get('url')
    if not validate(received_url):
        flash('Некорректный URL', 'warning')
        return render_template(
            'index.html',
            check_message=received_url,
            messages=get_flashed_messages(with_categories=True)
        ), 422
    parsed_url = normilyze(received_url)
    urls = get_urls_names()
    if parsed_url in urls:
        flash('Страница уже существует', 'warning')
    else:
        add_url(parsed_url)
        flash('Страница успешно добавлена', 'success')
    id = get_id_by_url(parsed_url)
    return redirect(
        url_for('url_info', id=id),
    )


@app.post('/urls/<id>/checks')
def get_url_check(id):
    url, _ = get_url_by_id(id)
    response = response_from(url)
    if not response:
        return redirect(
            url_for('url_info', id=id),
        )
    status = response.status_code
    add_check(id, status)
    if status == 200:
        flash('Страница успешно проверена', 'success')
        return redirect(
            url_for('url_info', id=id),
        )


@app.route('/urls/<int:id>')
def url_info(id):
    messages = get_flashed_messages(with_categories=True)
    name, created = get_url_by_id(id)
    url_checks = get_url_with_checks(id)
    return render_template(
        'info.html',
        id=id,
        name=name,
        created=created,
        messages=messages,
        url_checks=url_checks,
    )


@app.get('/urls')
def get_urls_list():
    urls_list = get_urls()
    return render_template(
        'urls.html',
        urls_list=urls_list,
    )


@app.errorhandler(404)
def page_not_found(error):
    return render_template('error/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('error/500.html'), 500


if __name__ == '__main__':
    app.run()
