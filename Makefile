install:
	pip install --upgrade poetry && poetry build && poetry install

dev:
	poetry run flask --app page_analyzer:app run --debug

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app --error-logfile error.log --log-level debug

build:
	./build.sh

lint:
	poetry run flake8 page_analyzer