release: python manage.py migrate
web: celery worker -A covid_19 -l INFO --concurrency=1 & gunicorn covid_19.wsgi
