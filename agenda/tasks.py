import csv
from io import StringIO
import os
from django.contrib.auth.models import User
from agenda.serializers import PrestadorSerializer
from tamarcado.celery import app
from django.core.mail import EmailMessage
import smtplib
import email.message


@app.task
def gera_relatorio_prestador():
    prestadores = User.objects.all()
    serializer = PrestadorSerializer(prestadores, many=True)
    output = StringIO()
    escritor = csv.writer(output)
    escritor.writerow(
        [
            "prestador",
            "nome_cliente",
            "email_cliente",
            "telefone_cliente",
            "data_horario",
        ]
    )
    for prest in serializer.data:
        for agend in prest["agendamentos"]:
            escritor.writerow(
                [
                    agend["prestador"],
                    agend["nome_cliente"],
                    agend["email_cliente"],
                    agend["telefone_cliente"],
                    agend["data_horario"],
                ]
            )
    email_resposta = EmailMessage(
        "Relatório dos Prestadores",
        "Enviando o relatório dos prestadores no seu e-mail.",
        os.environ.get("EMAIL_HOST_USER", ""),
        ["cliente@gente.com"],
    )
    email_resposta.attach("relatorio.csv", output.getvalue(), "text/csv")
    email_resposta.send()
    print(output.getvalue())
    return output.getvalue()
