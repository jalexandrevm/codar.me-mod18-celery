import csv
from datetime import datetime, timedelta, timezone
from urllib import response
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from agenda.libs.brasil_api import get_cep, is_cep
import json

from agenda.models import Agendamento
from agenda.serializers import (
    AgendamentoSerializer,
    EnderecoSerializer,
    PrestadorSerializer,
)
from agenda.tasks import gera_relatorio_prestador
from agenda.utils import (
    data_str_to_datetime_list,
    get_horarios_disponiveis,
    get_list_feriados,
)
from tamarcado.settings.base import TESTING


class IsSuperUserOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        return False


class IsOwnerOrCreateOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            return True
        user_consulta = request.query_params.get("username", None)
        if request.user.username == user_consulta:
            return True
        return False


class IsReadOnlyAccess(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "GET":
            return True
        return False


class IsPrestador(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.prestador == request.user:
            return True
        return False


# agora vamos alterar de mixin para generics
# class AgendamentoListCreate(
#     mixins.ListModelMixin,  # adicionar mixin de listagem
#     mixins.CreateModelMixin,  # adicionar mixin de criação
#     generics.GenericAPIView,  # classe genérica
# ):
# list e create juntos do generics


class AgendamentoListCreate(generics.ListCreateAPIView):
    # queryset = Agendamento.objects.all()
    serializer_class = AgendamentoSerializer
    permission_classes = [IsOwnerOrCreateOnly]

    def get_queryset(self):
        username = self.request.query_params.get("username", None)
        queryset = Agendamento.objects.filter(prestador__username=username)
        return queryset


@api_view(http_method_names=["POST"])
def user_create(request):
    if request.method == "POST":
        name = request.data["username"]
        pass_word = request.data["password"]
        email = request.data["email"]
        if (name != None) and (pass_word != None) and (email != None):
            usr_data = {
                "username": name,
                "password": pass_word,
                "email": email,
            }
            usr_seriado = PrestadorSerializer(data=usr_data)
            if usr_seriado.is_valid():
                usr_seriado.save()
                return JsonResponse(usr_seriado.data, status=201)
        seriado_erro = PrestadorSerializer(data=request.data)
        seriado_erro.is_valid()
        return JsonResponse(seriado_erro.errors, status=400)


@api_view(http_method_names=["GET"])
def health_check(request):
    return Response({"status": "OK"}, status=200)


# projeto final módulo 16
@api_view(http_method_names=["POST"])
def prestador_endereco_create(request, pk):
    usr = get_object_or_404(User, id=pk)
    if request.method == "POST":
        if is_cep(request.data["cep"]):
            cep_api = get_cep(request.data["cep"])
        if cep_api.status_code != 200:
            return JsonResponse(json.loads(cep_api.text), status=400, safe=False)
        if not request.data.get("estado"):
            request.data["estado"] = json.loads(cep_api.text)["state"]
        if not request.data.get("cidade"):
            request.data["cidade"] = json.loads(cep_api.text)["city"]
        if not request.data.get("bairro"):
            request.data["bairro"] = json.loads(cep_api.text)["neighborhood"]
        if not request.data.get("rua"):
            request.data["rua"] = json.loads(cep_api.text)["street"]
        request.data["prestador"] = usr.username
        end_seriado = EnderecoSerializer(data=request.data)
        if end_seriado.is_valid():
            end_seriado.save()
            return JsonResponse(end_seriado.data, status=201)
        return JsonResponse(end_seriado.errors, status=400)


# @permission_classes([permissions.IsAdminUser])
@api_view(http_method_names=["GET"])
@permission_classes([IsSuperUserOnly])
def get_relatorio_prestador(request):
    if request.query_params.get("formato") == "csv":
        # response = HttpResponse(
        #     content_type="text/csv",
        #     headers={
        #         "Content-Disposition": f'attachment; filename="relatorio_{datetime.utcnow().strftime("%Y-%m-%d_%")}.csv"'
        #     },
        # )
        resp = gera_relatorio_prestador.delay()
        return Response({"task_id": resp.task_id})
    else:
        prestadores = User.objects.all()
        serializer = PrestadorSerializer(prestadores, many=True)
        return Response(serializer.data)


# desativado para personalizar relatório
# class PrestadorList(generics.ListAPIView):
#     serializer_class = PrestadorSerializer
#     queryset = User.objects.all()
#     permission_classes = [IsSuperUserOnly]


# desativados com o uso do generics
# def get(self, request, *args, **kwargs):
#     return self.list(request, *args, **kwargs)

# def post(self, request, *args, **kwargs):
#     return self.create(request, *args, **kwargs)


# agora vamos alterar de mixin para generics
# class AgendamentoDetalheAlteraCancela(
#     mixins.RetrieveModelMixin,
#     mixins.UpdateModelMixin,
#     mixins.DestroyModelMixin,
#     generics.GenericAPIView,
# ):


class AgendamentoDetalheAlteraCancela(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsPrestador]
    # queryset = Agendamento.objects.all()
    serializer_class = AgendamentoSerializer

    def get_queryset(self):
        username = self.request.query_params.get("username", None)
        queryset = Agendamento.objects.filter(prestador__username=username)
        return queryset

    # lookup_field = "id" # prefira usar pk na URL

    # def get(self, request, *args, **kwargs):
    #     return self.retrieve(request, *args, **kwargs)

    # def delete(self, request, *args, **kwargs):
    #     return self.destroy(request, *args, **kwargs)

    # def patch(self, request, *args, **kwargs):
    #     return self.partial_update(request, *args, **kwargs)

    # def put(self, request, *args, **kwargs):
    #     return self.update(request, *args, **kwargs)


class HorariosList(APIView):
    permission_classes = [IsReadOnlyAccess]

    def get(self, request):
        data = request.query_params.get("data", None)
        username = self.request.query_params.get("username", None)
        if not data:
            data = datetime.now().date()
        else:
            data = datetime.fromisoformat(data).date()
        if not username:
            raise serializers.ValidationError(
                "Para listar horários disponíveis é preciso de um usuário cadastrado!"
            )
        return JsonResponse(
            get_horarios_disponiveis(data, username), status=200, safe=False
        )


# IMPLEMENTADO ANTES E ALTERADO PARA TESTAR MOCK
# class HorariosList(APIView):
#     permission_classes = [IsReadOnlyAccess]

#     def get(self, request):
#         data = request.query_params.get("data", None)
#         username = self.request.query_params.get("username", None)
#         if data and username:
#             try:
#                 if TESTING == True:
#                     if data.split("-")[1] == "12" and data.split("-")[2] == "25":
#                         return JsonResponse([], safe=False)
#                 else:
#                     if data in get_list_feriados(data.split("-")[0]):
#                         return JsonResponse([], safe=False)
#                 data_ini = data_fim = datetime.fromisoformat(data).replace(
#                     tzinfo=timezone.utc
#                 )
#                 if data_ini < datetime.now(tz=timezone.utc):
#                     raise serializers.ValidationError(
#                         "Agendamento não pode ser no passado!"
#                     )
#                 data_fim += timedelta(hours=23, minutes=59)
#                 objs = (
#                     Agendamento.objects.filter(prestador__username=username)
#                     .filter(data_horario__gte=data_ini)
#                     .filter(data_horario__lt=data_fim)
#                     .filter(cancelado=False)
#                 )
#                 lista_horarios_dia = data_str_to_datetime_list(data)
#                 for item in objs:
#                     if item.data_horario in lista_horarios_dia:
#                         lista_horarios_dia.remove(item.data_horario)
#                 return JsonResponse(lista_horarios_dia, status=200, safe=False)
#             except ValueError as v_error:
#                 dict_error = {"erro": str(v_error)}
#                 return JsonResponse(dict_error, status=400, safe=False)
#         raise serializers.ValidationError(
#             "Para listar horários disponíveis é preciso de uma data válda e de um usuário cadastrado!"
#         )


# Create your views here.
# @api_view(http_method_names=["GET", "POST"])
# def agendamento_list_create(request):
#     if request.method == "GET":
#         # qs = Agendamento.objects.all() # mudar para apenas ativo
#         qs = Agendamento.objects.filter(cancelado=False)
#         serializer = AgendamentoSerializer(qs, many=True)
#         return JsonResponse(serializer.data, safe=False)
#     if request.method == "POST":
#         serializer = AgendamentoSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return JsonResponse(serializer.data, status=201)
#         return JsonResponse(serializer.errors, status=400)

# @api_view(http_method_names=["GET", "DELETE", "PUT", "PATCH"])
# def agendamento_detail_delete_alter(request, id):
#     obj = get_object_or_404(Agendamento, id=id)
#     if request.method == "GET":
#         serializer = AgendamentoSerializer(obj)
#         return JsonResponse(serializer.data)
#     if request.method == "DELETE":
#         # obj.delete() # alterado para apenas cancelar
#         # exercício 5 pra cancelar agendamento
#         obj.cancelado = True
#         obj.save()
#         serializer = AgendamentoSerializer(obj)
#         return JsonResponse(serializer.data, status=202)
#     # deprecated use POST or PATCH
#     if request.method == "PUT":
#         serializer = AgendamentoSerializer(data=request.data)
#         if serializer.is_valid():
#             dado_valido = serializer.validated_data
#             obj.data_horario = dado_valido.get("data_horario", obj.data_horario)
#             obj.nome_cliente = dado_valido.get("nome_cliente", obj.nome_cliente)
#             obj.email_cliente = dado_valido.get("email_cliente", obj.email_cliente)
#             obj.telefone_cliente = dado_valido.get("telefone_cliente", obj.telefone_cliente)
#             obj.save()
#             return JsonResponse(serializer.data, status=202)
#         return JsonResponse(serializer.errors, status=400)
#     if request.method == "PATCH":
#         serializer = AgendamentoSerializer(obj, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return JsonResponse(serializer.data, status=202)
#         return JsonResponse(serializer.errors, status=400)

# @api_view(http_method_names=["GET"])
# def horarios_list(request):
#     if request.method == "GET":
#         data = request.query_params.get("data")
#         if data:
#             try:
#                 data_ini = data_fim = datetime.fromisoformat(data).replace(tzinfo=pytz.UTC)
#                 data_fim += timedelta(hours=23, minutes=59)
#                 objs = Agendamento.objects.filter(data_horario__gte=data_ini).filter(data_horario__lt=data_fim).filter(cancelado=False)
#                 serializer = AgendamentoSerializer(objs, many=True)
#                 return JsonResponse(serializer.data, status=200, safe=False)
#             except ValueError as v_error:
#                 dict_error = {"erro": str(v_error)}
#                 return JsonResponse(dict_error, status=400, safe=False)
#         objs = Agendamento.objects.all().filter(cancelado=False)#.order_by('-data_horario')
#         serializer = AgendamentoSerializer(objs, many=True)
#         return JsonResponse(serializer.data, status=200, safe=False)
#     return JsonResponse(request.data, status=400)
