from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse

from app_client.models import Client
from app_client.serializers import ClientSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view



@csrf_exempt
@swagger_auto_schema(method='POST', request_body=ClientSerializer)
@swagger_auto_schema(method='PUT', request_body=ClientSerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all client details",)
@api_view(['GET','POST','PUT'])
def clientApi(request):
    try:
        if request.method == 'GET':
            client = Client.objects.all()
            clientSerializer = ClientSerializer(
                    client, many=True)
            return JsonResponse(clientSerializer.data, safe=False)
        elif request.method == 'POST':
            clientData = JSONParser().parse(request)
            clientSerializer = ClientSerializer(
                data=clientData)
            if clientSerializer.is_valid():
                clientSerializer.save()
                return JsonResponse(clientSerializer.data['ClientId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            clientData = JSONParser().parse(request)
            client = Client.objects.get(
                ClientId=clientData['ClientId'])
            clientSerializer = ClientSerializer(
                client, data=clientData)
            if clientSerializer.is_valid():
                clientSerializer.save()
                return JsonResponse(clientSerializer.data['ClientId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give ClientId to get one clientdetail",)
@api_view(['GET','DELETE'])
def ClientApiById(request, ClientId=""):
    try:
        if request.method == 'GET': 
            client = Client.objects.get(
                    ClientId=ClientId)
            clientSerializer = ClientSerializer(
                    client)
            return JsonResponse(clientSerializer.data, safe=False)
        elif request.method == 'DELETE':
            client = Client.objects.get(ClientId=ClientId)
            client.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    