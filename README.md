# Witch Chess Server

The backend counterpart to the frontend repository found here: https://github.com/SpookyLamb/witch-chess

This project uses Python and Django, the former must already be installed for it to work. In order for the websockets to work locally, Docker is required to run redis.

## Local Dev
* (OPTIONAL) Create and start a virtual environment via pyenv.
* Install requirements: $ `pip install -r requirements.txt`
* Run migrations to create database: $ `python manage.py migrate`
* Start redis: $ `docker run --rm -p 6379:6379 redis:7`
* Start the server: $ `python manage.py runserver`

## Deployment
* Use whatever service you would like that is compatible with Django, following their instructions.
* The real server (run by myself) uses Fly.io
