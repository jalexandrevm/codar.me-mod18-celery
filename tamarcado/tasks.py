from celery import Celery

app = Celery(
    "tasks",
    broker="redis://127.0.0.1:6379/0",
    backend="redis://127.0.0.1:6379/0",
)


@app.task
def verifica(num):
    soma = 0
    while (num**2) ** 0.5 > 0:
        soma += num
        num -= 1
    return soma
