from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse

from app_client.models import Client
from app_client.serializers import ClientSerializer


@csrf_exempt
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
    