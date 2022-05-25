from tamarcado.settings.base import *

# para usar vários arquivos de settings configurar:
# /tamarcado/asgi.py > alterar local do módulo settings
# para a nova pasta e criar a pasta '__init__'
# /tamarcado/wsgi.py > alterar local do módulo settings
# /manage.py > alterar local do módulo settings
# na variável BASE_DIR, incluir mais um '.parent'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]
LOGGING = {
    **LOGGING,
    # "loggers": {"": {"level": "DEBUG", "handlers": ["console", "file"]}},
}

# usando o MailHog
EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND_DEV", "")
EMAIL_HOST = os.environ.get("EMAIL_HOST_DEV", "")
EMAIL_PORT = os.environ.get("EMAIL_PORT_DEV", "")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER_DEV", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD_DEV", "")
EMAIL_USE_SSL = False
EMAIL_USE_TSL = False
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL_DEV", "")

# celery com redis local
CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/0"
