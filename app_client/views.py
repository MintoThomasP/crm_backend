from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse

from app_client.models import Client, ClientOtherDetails
from app_client.serializers import ClientDocumentsSerializer, ClientOtherDetailsSerializer, ClientSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser



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
    




@csrf_exempt
@swagger_auto_schema(method='POST', request_body=ClientOtherDetailsSerializer)
@swagger_auto_schema(method='PUT', request_body=ClientOtherDetailsSerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all client details",)
@api_view(['GET','POST','PUT'])
def ClientOtherDetailsApi(request):
    try:
        if request.method == 'GET':
            clientOtherDetails = ClientOtherDetails.objects.all()
            clientOtherDetailsSerializer = ClientOtherDetailsSerializer(
                    clientOtherDetails, many=True)
            return JsonResponse(clientOtherDetailsSerializer.data, safe=False)
        elif request.method == 'POST':
            clientOtherDetailsData = JSONParser().parse(request)
            clientOtherDetailsSerializer = ClientOtherDetailsSerializer(
                data=clientOtherDetailsData)
            if clientOtherDetailsSerializer.is_valid():
                clientOtherDetailsSerializer.save()
                return JsonResponse(clientOtherDetailsSerializer.data['ClientOtherDetailId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            clientOtherDetailsData = JSONParser().parse(request)
            clientOtherDetails = ClientOtherDetails.objects.get(
                ClientOtherDetailId=clientOtherDetailsData['ClientOtherDetailId'])
            clientOtherDetailsSerializer = ClientOtherDetailsSerializer(
                clientOtherDetails, data=clientOtherDetailsData)
            if clientOtherDetailsSerializer.is_valid():
                clientOtherDetailsSerializer.save()
                return JsonResponse(clientOtherDetailsSerializer.data['ClientOtherDetailId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give ClientOtherDetailsId to get one clientOtherDetailsdetail",)
@api_view(['GET','DELETE'])
def ClientOtherDetailsApiById(request, ClientOtherDetailId=""):
    try:
        if request.method == 'GET': 
            clientOtherDetails = ClientOtherDetails.objects.get(
                    ClientOtherDetailId=ClientOtherDetailId)
            clientOtherDetailsSerializer = ClientOtherDetailsSerializer(
                    clientOtherDetails)
            return JsonResponse(clientOtherDetailsSerializer.data, safe=False)
        elif request.method == 'DELETE':
            clientOtherDetails = ClientOtherDetails.objects.get(ClientOtherDetailId=ClientOtherDetailId)
            clientOtherDetails.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    


class UploadClientDocument(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request,  *args, **kwargs):
        try:
                Serializer = ClientDocumentsSerializer(
                    data=request.data)
                if Serializer.is_valid():
                    Serializer.save()
                    return JsonResponse(Serializer.data['ClientDocumentId'], safe=False)
                else:
                    return JsonResponse("", safe=False)
        except:
            return JsonResponse("", safe=False)