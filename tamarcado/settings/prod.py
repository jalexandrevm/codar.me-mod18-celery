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
