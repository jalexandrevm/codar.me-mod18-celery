release: python manage.py migrate
worker: celery -A tamarcado worker -Q celery --loglevel=INFO
web: gunicorn tamarcado.wsgi
