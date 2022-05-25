from tamarcado.settings.base import *

import django_on_heroku

django_on_heroku.settings(locals())
DEBUG = False

ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND_PROD", "")
EMAIL_HOST = os.environ.get("EMAIL_HOST_PROD", "")
EMAIL_PORT = os.environ.get("EMAIL_PORT_PROD", "")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER_PROD", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD_PROD", "")
EMAIL_USE_SSL = True
EMAIL_USE_TSL = False

CELERY_BROKER_URL = os.environ.get("REDIS_URL", "")
CELERY_RESULT_BACKEND = os.environ.get("REDIS_URL", "")
