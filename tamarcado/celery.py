from celery import Celery
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tamarcado.settings.dev")


app = Celery(
    "tamarcado",
    broker="redis://127.0.0.1:6379/0",
    backend="redis://127.0.0.1:6379/0",
)
app.autodiscover_tasks()


@app.task
def verifica(num):
    soma = 0
    while (num**2) ** 0.5 > 0:
        soma += num
        num -= 1
    return soma
