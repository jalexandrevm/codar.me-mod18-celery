from statistics import mode
from django.db import models

# Create your models here.


class Agendamento(models.Model):
    prestador = models.ForeignKey(
        "auth.User", related_name="agendamentos", on_delete=models.CASCADE
    )
    data_horario = models.DateTimeField()
    nome_cliente = models.CharField(max_length=200)
    email_cliente = models.EmailField()
    telefone_cliente = models.CharField(max_length=20)
    cancelado = models.BooleanField(default=False)

    class Meta:
        ordering = ["-data_horario"]

    def __str__(self):
        return f"""{self.id} - {self.data_horario} - {self.nome_cliente}"""


class Endereco(models.Model):
    prestador = models.ForeignKey(
        "auth.User", related_name="enderecos", on_delete=models.CASCADE
    )
    cep = models.CharField(max_length=10, unique=False)
    estado = models.CharField(max_length=2, unique=False)
    cidade = models.CharField(max_length=50, unique=False)
    bairro = models.CharField(max_length=50, unique=False)
    rua = models.CharField(max_length=100)
    complemento = models.CharField(max_length=50)

    class Meta:
        ordering = ["-cep"]
