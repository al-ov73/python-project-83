import requests
from flask import flash


def response_from(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
