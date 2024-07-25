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
from app_default.models import Country, State
from app_default.serializers import CountrySerializer, StateSerializer
from app_default.views import retry
from app_project.views import CustomPageNumberPagination
from rest_framework import generics
from django.db.models import Q


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=ClientSerializer)
@swagger_auto_schema(method='PUT', request_body=ClientSerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all client details",)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
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
@retry(retries=3, delay=2)
def ClientApiById(request, ClientId=""):
    try:
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
    except:
        return JsonResponse("", safe=False)
from django.db import transaction   
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give CompanyId to get all project detail",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def ClientByCompanyId(request, CompanyId=""):
    try:
        if request.method == 'GET':
            BATCH_SIZE = 100
            client = Client.objects.filter(
                    CompanyId=CompanyId)
            total_client=client.count()
            all_serialized_data = []
            for i in range(0, total_client, BATCH_SIZE):
                with transaction.atomic():
                    batch_tasks = client[i:i+BATCH_SIZE]
                    serializer = ClientSerializer(batch_tasks, many=True)
                    serialized_data = serializer.data
                    all_serialized_data.extend(serialized_data)
            return JsonResponse(all_serialized_data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


class ClientApiByCompanyId(generics.ListAPIView):
    queryset =Client.objects.all()
    pagination_class = CustomPageNumberPagination
    serializer_class = ClientSerializer 
    def post(self, request, *args, **kwargs):
        filterData = JSONParser().parse(request)
        Keyword = filterData.get('SearchKeyword', '')
        if filterData['CompanyId']:
            self.queryset = self.queryset.filter(CompanyId=filterData['CompanyId'])

        if Keyword:
            self.queryset = self.queryset.filter(Q(CustomerDisplayName__icontains=Keyword)|Q(CompanyName__icontains=Keyword))
        page = self.paginate_queryset(self.queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)



@csrf_exempt
@swagger_auto_schema(method='POST', request_body=ClientOtherDetailsSerializer)
@swagger_auto_schema(method='PUT', request_body=ClientOtherDetailsSerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all client details",)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
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
@retry(retries=3, delay=2)
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
@retry(retries=3, delay=2)
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
@retry(retries=3, delay=2)
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
@retry(retries=3, delay=2)
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
@retry(retries=3, delay=2)
def ClientAddressApiByClientId(request, ClientId=""):
    try:
        if request.method == 'GET': 
            clientAddress = ClientAddress.objects.filter(
                    ClientId=ClientId)
            clientAddressSerializer = ClientAddressSerializer(
                    clientAddress,many=True)
            clientData=[]
            for row in clientAddressSerializer.data:
                country=Country.objects.get(CountryId=row['Country'])
                countrySerializer=CountrySerializer(country)
                row['CountryName']=countrySerializer.data['Country']
                try:
                    state=State.objects.get(StateId=row['State'])
                    stateSerializer=StateSerializer(state)
                    row['StateName']=stateSerializer.data['State']
                except:
                    row['StateName']=[]
                clientData.append(row)

            return JsonResponse(clientData, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    



@csrf_exempt
@swagger_auto_schema(method='POST', request_body=ContactPersonSerializer)
@swagger_auto_schema(method='PUT', request_body=ContactPersonSerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all client details",)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
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
@retry(retries=3, delay=2)
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