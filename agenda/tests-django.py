from django.test import TestCase, Client
from agenda.models import Agendamento

# Create your tests here.
class TestAgendamentoCriar(TestCase):
    def test_criar_agendamento_ok(self):
        obj = Agendamento(
            data_horario="2022-04-11T11:30:00Z",
            nome_cliente="Izabel Pires",
            email_cliente="izapir@gente.com",
            telefone_cliente="(18)3219-0291"
        )
        obj.save()
        self.assertIn(obj, Agendamento.objects.all())
    def test_criar_agendamento_data_anterior(self):
        obj = Agendamento(
            data_horario="2022-04-04T11:30:00Z",
            nome_cliente="Pietro Pires",
            email_cliente="piepir@gente.com",
            telefone_cliente="(18)3219-0291"
        )
        obj.save()
        self.assertIn(obj, Agendamento.objects.all())
    def test_criar_agendamento_hora_fora_atendimento(self):
        cliente = Client()
        obj = Agendamento(
            data_horario="2022-04-11T07:30:00Z",
            nome_cliente="Fabrício Santos",
            email_cliente="fabsan@gente.com",
            telefone_cliente="(18)3219-0291"
        )
        obj.save()
        self.assertIn(obj, Agendamento.objects.all())
    def test_criar_agendamento_email_data_hora_repetido(self):
        cliente = Client()
        obj1 = Agendamento(
            data_horario="2022-04-11T07:30:00Z",
            nome_cliente="Fabrício Santos",
            email_cliente="fabsan@gente.com",
            telefone_cliente="(18)3219-0291"
        )
        obj1.save()
        obj2 = Agendamento(
            data_horario="2022-04-11T07:30:00Z",
            nome_cliente="Gustavo Gomes",
            email_cliente="fabsan@gente.com",
            telefone_cliente="(18)3219-0291"
        )
        obj2.save()
        self.assertIn(obj1, Agendamento.objects.all())
        self.assertIn(obj2, Agendamento.objects.all())

class TestSerializerAgendamento(TestCase):
    def test_cria_agendamento_ok(self):
        obj = {
            "data_horario": "2022-04-11T11:30:00Z",
            "nome_cliente": "Izabel Pires",
            "email_cliente": "izapir@gente.com",
            "telefone_cliente": "(18)3219-0291"
        }
        cliente = Client()
        response = cliente.post("/api/agendamentos/", obj)
        self.assertEqual(response.status_code, 201)
    def test_cria_agendamento_data_anterior(self):
        obj = {
            "data_horario": "2022-04-02T11:30:00Z",
            "nome_cliente": "Izabel Pires",
            "email_cliente": "izapir@gente.com",
            "telefone_cliente": "(18)3219-0291"
        }
        cliente = Client()
        response = cliente.post("/api/agendamentos/", obj)
        self.assertEqual(response.status_code, 400)
    def test_cria_agendamento_hora_fora_atendimento(self):
        obj = {
            "data_horario": "2022-04-15T06:30:00Z",
            "nome_cliente": "Izabel Pires",
            "email_cliente": "izapir@gente.com",
            "telefone_cliente": "(18)3219-0291"
        }
        cliente = Client()
        response = cliente.post("/api/agendamentos/", obj)
        self.assertEqual(response.status_code, 400)
    def test_cria_agendamento_hora_errada(self):
        obj = {
            "data_horario": "2022-04-15T09:01:00Z",
            "nome_cliente": "Izabel Pires",
            "email_cliente": "izapir@gente.com",
            "telefone_cliente": "(18)3219-0291"
        }
        cliente = Client()
        response = cliente.post("/api/agendamentos/", obj)
        self.assertEqual(response.status_code, 400)
    def test_valida_cria_agendamento_mesmo_dia(self):
        obj = {
            "data_horario": "2022-04-15T09:00:00Z",
            "nome_cliente": "Izabel Pires",
            "email_cliente": "izapir@gente.com",
            "telefone_cliente": "(18)3219-0291"
        }
        cliente = Client()
        response = cliente.post("/api/agendamentos/", obj)
        self.assertEqual(response.status_code, 201)
        obj["email_cliente"] = "iza@gente.com"
        response = cliente.post("/api/agendamentos/", obj)
        self.assertEqual(response.status_code, 400)
    def test_valida_cria_agendamento_mesmo_dia_email(self):
        obj = {
            "data_horario": "2022-04-15T09:00:00Z",
            "nome_cliente": "Izabel Pires",
            "email_cliente": "izapir@gente.com",
            "telefone_cliente": "(18)3219-0291"
        }
        cliente = Client()
        response = cliente.post("/api/agendamentos/", obj)
        self.assertEqual(response.status_code, 201)
        obj["data_horario"] = "2022-04-15T09:30:00Z"
        response = cliente.post("/api/agendamentos/", obj)
        self.assertEqual(response.status_code, 400)
    def test_valida_cria_agendamento_mesmo_dia_apos_cancelar(self):
        obj = {
            "data_horario": "2022-04-15T09:00:00Z",
            "nome_cliente": "Izabel Pires",
            "email_cliente": "izapir@gente.com",
            "telefone_cliente": "(18)3219-0291"
        }
        cliente = Client()
        response = cliente.post("/api/agendamentos/", obj)
        self.assertEqual(response.status_code, 201)
        response = cliente.delete(f"/api/agendamentos/{response.json()['id']}/")
        self.assertEqual(response.status_code, 202)
        response = cliente.post("/api/agendamentos/", obj)
        self.assertEqual(response.status_code, 201)
