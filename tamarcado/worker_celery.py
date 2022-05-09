from celery import Celery

app = Celery("tamarcado", broker="redis://localhost:6379/0")


@app.task
def verifica(num):
    soma = 0
    while (num**2) ** 0.5 > 0:
        soma += num
        num -= 1
    return soma
