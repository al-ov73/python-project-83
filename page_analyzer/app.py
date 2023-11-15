from flask import (
Flask, redirect,
render_template,
request,
flash,
url_for,
get_flashed_messages
)


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    index()