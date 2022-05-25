from tamarcado.settings.base import *

# para usar vários arquivos de settings configurar:
# /tamarcado/asgi.py > alterar local do módulo settings
# para a nova pasta e criar a pasta '__init__'
# /tamarcado/wsgi.py > alterar local do módulo settings
# /manage.py > alterar local do módulo settings
# na variável BASE_DIR, incluir mais um '.parent'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["*"]

# defina essas variáveis em seu ambiente de produção
# definindo protocolo SSL
# caso use outro desativar ambos abaixo

EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND_PROD", "")
EMAIL_HOST = os.environ.get("EMAIL_HOST_PROD", "")
EMAIL_PORT = os.environ.get("EMAIL_PORT_PROD", "")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER_PROD", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD_PROD", "")
EMAIL_USE_SSL = True
EMAIL_USE_TSL = False

CELERY_BROKER_URL = os.environ.get("REDIS_URL", "")
CELERY_RESULT_BACKEND = os.environ.get("REDIS_URL", "")
