from datetime import date, datetime, timedelta, timezone
import requests
from agenda.libs import brasil_api
from agenda.models import Agendamento


def get_horarios_disponiveis(data: date, username: str):
    """
    Retorna uma lista de horários disponíveis do tipo
    datetime referentes a data passada de um username
    """
    if brasil_api.is_feriado(data):
        return []

    dt_hora_inicial = datetime(data.year, data.month, data.day, 9, tzinfo=timezone.utc)
    dt_hora_fim_dia = datetime(data.year, data.month, data.day, 18, tzinfo=timezone.utc)
    dt_hora_ini_almoco = datetime(
        data.year, data.month, data.day, 12, tzinfo=timezone.utc
    )
    dt_hora_fim_almoco = datetime(
        data.year, data.month, data.day, 13, tzinfo=timezone.utc
    )
    list_horarios = []
    agendados_dia = (
        Agendamento.objects.filter(prestador__username=username)
        .filter(data_horario__gte=dt_hora_inicial)
        .filter(data_horario__lt=dt_hora_fim_dia)
    )
    if data.weekday() <= 4:
        while dt_hora_inicial < dt_hora_fim_dia:
            if not (
                dt_hora_ini_almoco <= dt_hora_inicial < dt_hora_fim_almoco
            ) and dt_hora_inicial not in agendados_dia.datetimes(
                "data_horario", "minute"
            ):
                list_horarios.append(dt_hora_inicial)
            dt_hora_inicial += timedelta(minutes=30)
        return list_horarios
    elif data.weekday() == 5:
        while dt_hora_inicial < dt_hora_fim_almoco:
            if dt_hora_inicial not in agendados_dia.datetimes("data_horario", "minute"):
                list_horarios.append(dt_hora_inicial)
            dt_hora_inicial += timedelta(minutes=30)
        return list_horarios


# função substituída pela função acima para testar MOCK
def data_str_to_datetime_list(data_str) -> list:
    dt_obj = datetime.fromisoformat(data_str).replace(tzinfo=timezone.utc)
    lista_horas = []
    hora1 = datetime(dt_obj.year, dt_obj.month, dt_obj.day, hour=9, tzinfo=timezone.utc)
    hora_almoco_ini = datetime(
        dt_obj.year, dt_obj.month, dt_obj.day, hour=12, tzinfo=timezone.utc
    )
    hora_almoco_fim = datetime(
        dt_obj.year, dt_obj.month, dt_obj.day, hour=13, tzinfo=timezone.utc
    )
    hora_fim_dia = datetime(
        dt_obj.year, dt_obj.month, dt_obj.day, hour=18, tzinfo=timezone.utc
    )
    if dt_obj.weekday() <= 4:
        while hora1 < hora_fim_dia:
            if not (hora_almoco_ini <= hora1 < hora_almoco_fim):
                lista_horas.append(hora1)
            hora1 += timedelta(minutes=30)
        return lista_horas
    elif dt_obj.weekday() == 5:
        while hora1 < hora_almoco_fim:
            lista_horas.append(hora1)
            hora1 += timedelta(minutes=30)
        return lista_horas


def get_list_feriados(ano_str) -> list:
    feriados_nacionais = requests.get(
        f"https://brasilapi.com.br/api/feriados/v1/{ano_str}"
    )
    if feriados_nacionais.status_code != 200:
        raise ValueError("Não foi possível consultar!")
    lista_feriados_nacionais = []
    for item in feriados_nacionais.json():
        lista_feriados_nacionais.append(item["date"])
    return lista_feriados_nacionais
