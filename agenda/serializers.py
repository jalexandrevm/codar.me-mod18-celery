from dataclasses import fields
from datetime import date, datetime, time, timedelta, tzinfo
import re
from django.forms import ValidationError
from django.contrib.auth.models import User
import pytz
from rest_framework import serializers
from django.utils import timezone
from agenda.models import Agendamento, Endereco


class EnderecoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endereco
        fields = [
            "id",
            "cep",
            "estado",
            "cidade",
            "bairro",
            "rua",
            "complemento",
            "prestador",
        ]

    prestador = serializers.CharField()

    def validate_prestador(self, value):
        try:
            prestador_banco = User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Usuário não existe!")
        return prestador_banco


class AgendamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agendamento
        fields = [
            "id",
            "data_horario",
            "nome_cliente",
            "email_cliente",
            "telefone_cliente",
            "prestador",
        ]

    prestador = serializers.CharField()
    # código abaixo foi substituído mas deixado de propósito
    # incluir atributos que serão serializados
    # data_horario = serializers.DateTimeField()
    # nome_cliente = serializers.CharField(max_length=200)
    # email_cliente = serializers.EmailField()
    # telefone_cliente = serializers.CharField(max_length=20)
    def validate_prestador(self, value):
        try:
            prestador_banco = User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Usuário não existe!")
        return prestador_banco

    def validate_data_horario(self, value):
        # excluir horários passados
        if value < timezone.now():
            raise serializers.ValidationError("Agendamento não pode ser no passado!")
        # excluir fora do horário de serviço
        if (
            (
                (0 <= value.weekday() <= 4)
                and not (
                    (time(hour=9) <= value.time() < time(hour=12))
                    or (time(hour=13) <= value.time() < time(hour=18))
                )
            )
            or (
                value.weekday() == 5
                and not (time(hour=9) <= value.time() < time(hour=13))
            )
            or (value.weekday() == 6)
        ):
            raise serializers.ValidationError(
                "Agendamentos apenas de segunda a sexta das 9 às 12 pela manhã e das 13 às 18 pela tarde ou no sábado das 9 às 13!"
            )
        # horário deve ser múltiplo de 30 minutos
        if (value.minute % 30) != 0:
            raise serializers.ValidationError(
                "Agendamentos devem ser de 30 em 30 minutos!"
            )
        return value

    # exercício 6 validar telefone
    def validate_telefone_cliente(self, value):
        """para funcionar, precisa vir com máscara +ppp(ddd)NNNNN-nnnn
        o código do país e o DDD estão opcionais
        para celular deve ter 9 seguido de 7, 8 ou 9
        para fixo deve começar com 2 ou 3"""
        padrao = "(\+[1-9]{1}[0-9]{0,2})?(\([1-9]{1}[0-9]{1,2}\))?((([9]{1}[7-9]{1})|([2-3]{1}))([0-9]{3})\-([0-9]{4}))"
        resposta = re.fullmatch(padrao, value)
        if resposta == None:
            raise serializers.ValidationError(
                "Formato do telefone inválido !!! (+ppp(ddd)NNNNN-nnnn)"
            )
        return value

    def validate(self, attrs):
        """Validações diversas para e-mails e horários
        email_cliente: terminado com .br deve ter +55 no telefone
        email_cliente: não pode agendar mais de 1 vez por dia
        data_horario: precisa ser de 30 em 30 minutos"""
        # primeiro pegamos valores da requisição
        data_horario = attrs.get("data_horario", "")
        telefone_cliente = attrs.get("telefone_cliente", "")
        email_cliente = attrs.get("email_cliente", "")
        prestador = attrs.get("prestador", "")
        # regra da aula para e-mail terminando em .br
        # tem que ter +55 no telefone
        if (
            email_cliente.endswith(".br")
            and telefone_cliente.startswith("+")
            and not telefone_cliente.starswith("+55")
        ):
            raise serializers.ValidationError("E-mail .br deve ter fone +55 !")
        # regras de validação para horários
        if data_horario:
            data_horario = datetime.fromisoformat(str(data_horario)).replace(
                tzinfo=pytz.UTC
            )
            lst_email = (
                Agendamento.objects.filter(email_cliente=email_cliente)
                .filter(cancelado=False)
                .dates("data_horario", "day")
            )
            # recusa agendamento caso e-mail já exista no dia
            # horários cancelados são desconsiderados
            if data_horario.date() in lst_email:
                raise serializers.ValidationError(
                    "Mesmo e-mail não pode agendar mais de uma vez por dia!"
                )
            data_ini = data_fim = data_horario - timedelta(
                hours=data_horario.hour, minutes=data_horario.minute
            )
            data_fim += timedelta(hours=23, minutes=59)
            lst_horarios_dia = (
                Agendamento.objects.filter(prestador__username=prestador)
                .filter(data_horario__gt=data_ini)
                .filter(data_horario__lt=data_fim)
                .filter(cancelado=False)
                .datetimes("data_horario", "minute")
            )
            # recusa caso horários indisponível
            # horários cancelados são desconsiderados
            if data_horario in lst_horarios_dia:
                raise serializers.ValidationError(
                    "Horário não está disponível!", code=200
                )
        return attrs

    # Serializer deprecated ModelSerializer automates those methods


class PrestadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "agendamentos", "enderecos"]

    email = serializers.EmailField()
    agendamentos = AgendamentoSerializer(many=True, read_only=True)
    enderecos = EnderecoSerializer(many=True, read_only=True)


""" def create(self, validated_data):
        agendamento = Agendamento.objects.create(
            data_horario = validated_data["data_horario"],
            nome_cliente = validated_data["nome_cliente"],
            email_cliente = validated_data["email_cliente"],
            telefone_cliente = validated_data["telefone_cliente"],
        )
        return agendamento
    def update(self, instance, validated_data):
        instance.data_horario = validated_data.get("data_horario", instance.data_horario)
        instance.nome_cliente = validated_data.get("nome_cliente", instance.nome_cliente)
        instance.email_cliente = validated_data.get("email_cliente", instance.email_cliente)
        instance.telefone_cliente = validated_data.get("telefone_cliente", instance.telefone_cliente)
        instance.save()
        return instance
 """
