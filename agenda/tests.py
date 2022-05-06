from datetime import datetime, timezone
import json
from agenda.models import Agendamento
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from unittest import mock

# Create your tests here.
class TestListaAgendamento(APITestCase):
    def setUp(self) -> None:
        usr_test = User()
        usr_test.username = "jalexandrevm"
        usr_test.email = "testando@gente.com"
        usr_test.set_password("123")
        usr_test.date_joined = datetime.now(tz=timezone.utc)
        usr_test.save()

    def test_listagem_vazia(self):
        self.client.login(username="jalexandrevm", password="123")
        response = self.client.get(
            "/api/agendamentos/?username=jalexandrevm",
        )
        data = json.loads(response.content)
        self.assertEqual(data, [])

    def test_listagem_agendamentos_criados(self):
        Agendamento.objects.create(
            data_horario=datetime(2022, 4, 15, 10, 30, tzinfo=timezone.utc),
            nome_cliente="Pinheiro",
            email_cliente="pin@gente.com",
            telefone_cliente="3465-5218",
            prestador=User.objects.filter(username="jalexandrevm")[0],
        )
        agendamento_serializado = {
            "id": 1,
            "data_horario": "2022-04-15T10:30:00Z",
            "nome_cliente": "Pinheiro",
            "email_cliente": "pin@gente.com",
            "telefone_cliente": "3465-5218",
            "prestador": "jalexandrevm",
        }
        self.client.login(username="jalexandrevm", password="123")
        response = self.client.get("/api/agendamentos/?username=jalexandrevm")
        data = json.loads(response.content)
        self.assertEqual(data[0], agendamento_serializado)


class TestCriacaoAgendamento(APITestCase):
    def setUp(self) -> None:
        usr_test = User()
        usr_test.username = "jalexandrevm"
        usr_test.set_password("123")
        usr_test.email = "testando@gente.com"
        usr_test.date_joined = datetime.now(tz=timezone.utc)
        usr_test.save()

    def test_cria_agendamento(self):
        agendamento_request_data = {
            "data_horario": "2025-04-15T10:30:00Z",
            "nome_cliente": "Pinheiro",
            "email_cliente": "pin@gente.com",
            "telefone_cliente": "3465-5218",
            "prestador": "jalexandrevm",
        }
        response = self.client.post(
            "/api/agendamentos/", agendamento_request_data, format="json"
        )
        sucesso = self.client.login(username="jalexandrevm", password="123")
        if sucesso:
            agendamento_criado = self.client.get(
                f"/api/agendamentos/{response.json()['id']}/?username={response.json()['prestador']}"
            )
            self.assertEqual(response.json(), agendamento_criado.json())
            self.assertEqual(response.status_code, 201)
            self.assertEqual(agendamento_criado.status_code, 200)
            self.assertEqual(response.json()["nome_cliente"], "Pinheiro")
            self.assertEqual(response.json()["email_cliente"], "pin@gente.com")

    def test_cria_agendamento_data_passado(self):
        agendamento_request_data = {
            "data_horario": "2022-04-01T10:30:00Z",
            "nome_cliente": "Pinheiro",
            "email_cliente": "pin@gente.com",
            "telefone_cliente": "3465-5218",
            "prestador": "jalexandrevm",
        }
        response = self.client.post(
            "/api/agendamentos/", agendamento_request_data, format="json"
        )
        erro = "Agendamento não pode ser no passado!"
        self.assertEqual(response.status_code, 400)
        self.assertIn(erro, response.json()["data_horario"])

    def test_cria_agendamento_hora_invalida(self):
        agendamento_request_data = {
            "data_horario": "2025-04-15T10:32:00Z",
            "nome_cliente": "Pinheiro",
            "email_cliente": "pin@gente.com",
            "telefone_cliente": "3465-5218",
            "prestador": "jalexandrevm",
        }
        response = self.client.post(
            "/api/agendamentos/", agendamento_request_data, format="json"
        )
        erro = "Agendamentos devem ser de 30 em 30 minutos!"
        self.assertEqual(response.status_code, 400)
        self.assertIn(erro, response.json()["data_horario"])

    def test_cria_agendamento_email_repetido(self):
        agendamento_request_data = {
            "data_horario": "2025-04-15T10:30:00Z",
            "nome_cliente": "Pinheiro",
            "email_cliente": "pin@gente.com",
            "telefone_cliente": "3465-5218",
            "prestador": "jalexandrevm",
        }
        response = self.client.post(
            "/api/agendamentos/", agendamento_request_data, format="json"
        )
        self.assertEqual(response.status_code, 201)
        agendamento_request_data["data_horario"] = "2025-04-15T11:30:00Z"
        response = self.client.post(
            "/api/agendamentos/", agendamento_request_data, format="json"
        )
        erro = "Mesmo e-mail não pode agendar mais de uma vez por dia!"
        self.assertEqual(response.status_code, 400)
        self.assertIn(erro, response.json()["non_field_errors"])

    def test_cria_agendamento_telefone_invalido(self):
        agendamento_request_data = {
            "data_horario": "2022-04-15T10:30:00Z",
            "nome_cliente": "Pinheiro",
            "email_cliente": "pin@gente.com",
            "telefone_cliente": "+3465-5218",
            "prestador": "jalexandrevm",
        }
        response = self.client.post(
            "/api/agendamentos/", agendamento_request_data, format="json"
        )
        erro = "Formato do telefone inválido !!! (+ppp(ddd)NNNNN-nnnn)"
        self.assertEqual(response.status_code, 400)
        self.assertIn(erro, response.json()["telefone_cliente"])

    def test_cria_agendamento_usuario_inexistente(self):
        agendamento_request_data = {
            "data_horario": "2025-04-15T10:30:00Z",
            "nome_cliente": "Pinheiro",
            "email_cliente": "pin@gente.com",
            "telefone_cliente": "3465-5218",
            "prestador": "andre",
        }
        response = self.client.post(
            "/api/agendamentos/", agendamento_request_data, format="json"
        )
        self.assertIn("Usuário não existe!", response.json()["prestador"])
        pass


class TestHorariosListar(APITestCase):
    def setUp(self) -> None:
        usr_test1 = User()
        usr_test1.username = "alex"
        usr_test1.set_password("123")
        usr_test1.email = "alex@gente.com"
        usr_test1.date_joined = datetime.now(tz=timezone.utc)
        usr_test1.is_superuser = True
        usr_test1.save()
        usr_test2 = User()
        usr_test2.username = "andre"
        usr_test2.set_password("123")
        usr_test2.email = "andre@gente.com"
        usr_test2.date_joined = datetime.now(tz=timezone.utc)
        usr_test2.save()
        agendamento_request_data = {
            "data_horario": "2025-04-25T10:30:00Z",
            "nome_cliente": "Pinheiro",
            "email_cliente": "pin@gente.com",
            "telefone_cliente": "3465-5218",
            "prestador": "alex",
        }
        self.client.post("/api/agendamentos/", agendamento_request_data, format="json")
        agendamento_request_data = {
            "data_horario": "2025-04-25T11:30:00Z",
            "nome_cliente": "Francisco",
            "email_cliente": "chico@gente.com",
            "telefone_cliente": "(98)3465-5218",
            "prestador": "alex",
        }
        self.client.post("/api/agendamentos/", agendamento_request_data, format="json")
        agendamento_request_data = {
            "data_horario": "2025-04-25T10:30:00Z",
            "nome_cliente": "Roberto",
            "email_cliente": "beto@gente.com",
            "telefone_cliente": "3465-5218",
            "prestador": "andre",
        }
        self.client.post("/api/agendamentos/", agendamento_request_data, format="json")
        agendamento_request_data = {
            "data_horario": "2025-04-25T09:30:00Z",
            "nome_cliente": "Eduardo",
            "email_cliente": "edu@gente.com",
            "telefone_cliente": "(98)3465-5218",
            "prestador": "andre",
        }
        self.client.post("/api/agendamentos/", agendamento_request_data, format="json")

    def test_lista_disponiveis(self):
        lista_alex = self.client.get("/api/horarios/?data=2025-04-25&username=alex")
        lista_andre = self.client.get("/api/horarios/?data=2025-04-25&username=andre")
        self.assertEqual(len(lista_alex.json()), 14)
        self.assertEqual(len(lista_andre.json()), 14)

    def test_lista_sem_autenticacao(self):
        retorno_andre = self.client.get("/api/prestadores/")
        self.assertEqual(
            retorno_andre.json()["detail"],
            "Authentication credentials were not provided.",
        )

    def test_lista_sem_permissao(self):
        self.client.login(username="andre", password="123")
        retorno_andre = self.client.get("/api/prestadores/")
        self.assertEqual(
            retorno_andre.json()["detail"],
            "You do not have permission to perform this action.",
        )

    def test_lista_permissao_super_user(self):
        self.client.login(username="alex", password="123")
        retorno_alex = self.client.get("/api/prestadores/")
        self.assertEqual(retorno_alex.status_code, 200)

    @mock.patch("agenda.libs.brasil_api.is_feriado", return_value=True)
    def test_lista_feriado(self, _):
        response = self.client.get("/api/horarios/?data=2023-12-25&username=alex")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    @mock.patch("agenda.libs.brasil_api.is_feriado", return_value=False)
    def test_lista_dia_normal(self, _):
        response = self.client.get("/api/horarios/?data=2025-04-25&username=alex")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 14)
