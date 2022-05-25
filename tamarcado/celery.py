from celery import Celery
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tamarcado.settings.dev")


app = Celery(
    "tamarcado",
    # broker=os.environ.get("BROKER_URL", "redis://127.0.0.1:6379/0"),
    # backend=os.environ.get("BACKEND_URL", "redis://127.0.0.1:6379/0"),
)
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()


@app.task
def verifica(num):
    soma = 0
    while (num**2) ** 0.5 > 0:
        soma += num
        num -= 1
    return soma
