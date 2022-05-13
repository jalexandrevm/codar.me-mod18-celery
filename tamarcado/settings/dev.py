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
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_HOST = "0.0.0.0"
# EMAIL_PORT = "1025"
