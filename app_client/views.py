from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse

from app_client.models import Client, ClientAddress, ClientDocuments, ClientOtherDetails, ContactPerson
from app_client.serializers import ClientAddressSerializer, ClientDocumentsSerializer, ClientOtherDetailsSerializer, ClientSerializer, ContactPersonSerializer
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
    # try:
        if request.method == 'GET': 
            client = Client.objects.get(
                    ClientId=ClientId)
            clientSerializer = ClientSerializer(
                    client)
            clientData=clientSerializer.data
            clientOtherDetails = ClientOtherDetails.objects.filter(ClientId=ClientId)
            clientOtherDetailsSerializer = ClientOtherDetailsSerializer(
                    clientOtherDetails, many=True)
            clientFiles=[]
            
            for row in clientOtherDetailsSerializer.data:
                clientDocuments=ClientDocuments.objects.filter(ClientOtherDetailId=row['ClientOtherDetailId'])
                clientDocumentsSerializer = ClientDocumentsSerializer(
                    clientDocuments,many=True)
                row['ClientDocuments']=clientDocumentsSerializer.data
                clientFiles.append(row)
            clientData['ClientOtherDetails']=clientFiles
            clientAddress = ClientAddress.objects.filter(ClientId=ClientId)
            clientAddressSerializer = ClientAddressSerializer(
                    clientAddress, many=True)
            clientData['ClientAddress']=clientAddressSerializer.data
            contactPerson = ContactPerson.objects.filter(ClientId=ClientId)
            contactPersonSerializer = ContactPersonSerializer(
                    contactPerson, many=True)
            clientData['ContactPersons']=contactPersonSerializer.data
            return JsonResponse(clientData, safe=False)
        elif request.method == 'DELETE':
            client = Client.objects.get(ClientId=ClientId)
            client.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    # except:
    #     return JsonResponse("", safe=False)
    




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
        


@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give ClientDocumentId to get one ClientDocument detail",)
@api_view(['GET','DELETE'])
def QuotationFileApiById(request, ClientDocumentId=""):
    try:
        if request.method == 'GET': 
            clientDocuments = ClientDocuments.objects.get(
                    ClientDocumentId=ClientDocumentId)
            clientDocumentsSerializer = ClientDocumentsSerializer(
                    clientDocuments)
            return JsonResponse(clientDocumentsSerializer.data, safe=False)
        elif request.method == 'DELETE':
            clientDocuments = ClientDocuments.objects.get(ClientDocumentId=ClientDocumentId)
            clientDocuments.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=ClientAddressSerializer)
@swagger_auto_schema(method='PUT', request_body=ClientAddressSerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all client details",)
@api_view(['GET','POST','PUT'])
def ClientAddressApi(request):
    try:
        if request.method == 'GET':
            clientAddress = ClientAddress.objects.all()
            clientAddressSerializer = ClientAddressSerializer(
                    clientAddress, many=True)
            return JsonResponse(clientAddressSerializer.data, safe=False)
        elif request.method == 'POST':
            clientAddressData = JSONParser().parse(request)
            clientAddressSerializer = ClientAddressSerializer(
                data=clientAddressData)
            if clientAddressSerializer.is_valid():
                clientAddressSerializer.save()
                return JsonResponse(clientAddressSerializer.data['ClientAddressId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            clientAddressData = JSONParser().parse(request)
            clientAddress = ClientAddress.objects.get(
                ClientAddressId=clientAddressData['ClientAddressId'])
            clientAddressSerializer = ClientAddressSerializer(
                clientAddress, data=clientAddressData)
            if clientAddressSerializer.is_valid():
                clientAddressSerializer.save()
                return JsonResponse(clientAddressSerializer.data['ClientAddressId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give ClientAddressId to get one clientAddressdetail",)
@api_view(['GET','DELETE'])
def ClientAddressApiById(request, ClientAddressId=""):
    try:
        if request.method == 'GET': 
            clientAddress = ClientAddress.objects.get(
                    ClientAddressId=ClientAddressId)
            clientAddressSerializer = ClientAddressSerializer(
                    clientAddress)
            return JsonResponse(clientAddressSerializer.data, safe=False)
        elif request.method == 'DELETE':
            clientAddress = ClientAddress.objects.get(ClientAddressId=ClientAddressId)
            clientAddress.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give ClientId to get clientAddressdetail",)
@api_view(['GET',])
def ClientAddressApiByClientId(request, ClientId=""):
    try:
        if request.method == 'GET': 
            clientAddress = ClientAddress.objects.filter(
                    ClientId=ClientId)
            clientAddressSerializer = ClientAddressSerializer(
                    clientAddress,many=True)
            return JsonResponse(clientAddressSerializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    



@csrf_exempt
@swagger_auto_schema(method='POST', request_body=ContactPersonSerializer)
@swagger_auto_schema(method='PUT', request_body=ContactPersonSerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all client details",)
@api_view(['GET','POST','PUT'])
def ContactPersonApi(request):
    try:
        if request.method == 'GET':
            contactPerson = ContactPerson.objects.all()
            contactPersonSerializer = ContactPersonSerializer(
                    contactPerson, many=True)
            return JsonResponse(contactPersonSerializer.data, safe=False)
        elif request.method == 'POST':
            contactPersonData = JSONParser().parse(request)
            contactPersonSerializer = ContactPersonSerializer(
                data=contactPersonData)
            if contactPersonSerializer.is_valid():
                contactPersonSerializer.save()
                return JsonResponse(contactPersonSerializer.data['ContactPersonId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            contactPersonData = JSONParser().parse(request)
            contactPerson = ContactPerson.objects.get(
                ContactPersonId=contactPersonData['ContactPersonId'])
            contactPersonSerializer = ContactPersonSerializer(
                contactPerson, data=contactPersonData)
            if contactPersonSerializer.is_valid():
                contactPersonSerializer.save()
                return JsonResponse(contactPersonSerializer.data['ContactPersonId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give ContactPersonId to get one contactPersondetail",)
@api_view(['GET','DELETE'])
def ContactPersonApiById(request, ContactPersonId=""):
    try:
        if request.method == 'GET': 
            contactPerson = ContactPerson.objects.get(
                    ContactPersonId=ContactPersonId)
            contactPersonSerializer = ContactPersonSerializer(
                    contactPerson)
            return JsonResponse(contactPersonSerializer.data, safe=False)
        elif request.method == 'DELETE':
            contactPerson = ContactPerson.objects.get(ContactPersonId=ContactPersonId)
            contactPerson.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)