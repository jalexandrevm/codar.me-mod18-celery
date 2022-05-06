from datetime import date
import json
from django.conf import settings
import requests
import logging

# projeto final módulo 16
def is_cep(cep_str):
    if settings.TESTING == True:
        # logging.info(f"Requisição não realizada, em modo teste!")
        if cep_str == "00000000":
            return True
        return False
    cep_consulta = requests.get(f"https://brasilapi.com.br/api/cep/v2/{cep_str}")
    if cep_consulta.status_code != 200:
        return False
    return True


# projeto final módulo 16
def get_cep(cep_str):
    if settings.TESTING == True:
        return {
            "status_code": "200",
            "text": json.dumps(
                {
                    "cep": "00000000",
                    "state": "MA",
                    "city": "São Luís",
                    "neighborhood": "Centro",
                    "street": "Rua Doutor Luiz de Freitas Melro",
                }
            ),
        }
    return requests.get(f"https://brasilapi.com.br/api/cep/v2/{cep_str}")


def is_feriado(date: date):
    # logging.info(f"Fazendo uma requisição para BrasilAPI na data: {date}")
    if settings.TESTING == True:
        # logging.info(f"Requisição não realizada, em modo teste!")
        if date.day == 25 and date.month == 12:
            return True
        return False
    ano = date.year
    retorno = requests.get(f"https://brasilapi.com.br/api/feriados/v1/{ano}")
    if not retorno.status_code == 200:
        # logging.error(f"Algum erro aconteceu ao consultar BrasilAPI!")
        return False
        # raise ValueError("Problema ao buscar feriados nacionais!")
    feriados = json.loads(retorno.text)
    for feriado in feriados:
        data_as_str = feriado["date"]
        data = date.fromisoformat(data_as_str)
        if data == date:
            return True
    return False
