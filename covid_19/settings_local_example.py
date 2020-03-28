# Define local custom DB
SECRET_KEY = ''  # Server Secret Key

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',  # We are using postgres for this project, install psycopg2
        'NAME': '',  # Database name
        'USER': '',  # Database username
        'PASSWORD': '',  # Database passwod
        'HOST': '',  # Database host
        'PORT': '',  # Set to empty string for default.

    }
}

# Specify celery broker more info: https://docs.celeryproject.org/en/latest/getting-started/brokers/
CELERY_BROKER_URL = ''

