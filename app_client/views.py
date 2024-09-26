from datetime import date
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from app_client.models import Client, ClientAddress, ClientBankDetails, ClientDocuments, ClientOtherDetails, ClientVisitRegister, ContactPerson
from app_client.serializers import ClientAddressSerializer, ClientBankDetailsSerializer, ClientDocumentsSerializer, ClientOtherDetailsSerializer, ClientSerializer, ClientVisitRegisterSerializer, ContactPersonSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from app_basic.models import Country, State
from app_basic.serializers import CountrySerializer, StateSerializer
from app_default.views import retry
from app_project.models import ProjectTask
from app_project.serializers import ProjectTaskSerializer
from app_project.views import CustomPageNumberPagination
from rest_framework import generics
from django.db.models import Q
from django.db import transaction   

@csrf_exempt
@swagger_auto_schema(method='POST', request_body=ClientSerializer,operation_description="NOTE: API for save Client")
@swagger_auto_schema(method='PUT', request_body=ClientSerializer,operation_description="NOTE: API for edit Client")
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all client by company id",)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
def clientApi(request,CompanyId=""):
    try:
        if request.method == 'GET':
            client = Client.objects.filter(ActiveStatus=1,CompanyId=CompanyId)
            clientSerializer = ClientSerializer(
                    client, many=True)
            clientData=[]
            for row in clientSerializer.data:
                projectTask=ProjectTask.objects.filter(ClientId=row['ClientId'],TaskType="Task")
                projectTaskSerializer=ProjectTaskSerializer(projectTask,many=True)
                work_status_count = {'Pending': 0, 'Completed': 0, 'Due': 0, 'Not Completed': 0, 'Finished': 0, 'Delay Finished': 0}
                current_date = str(date.today())
            
                for task in projectTaskSerializer.data:
                    if task['Status'] == '1' or task['Status'] == '2':
                        work_status_count['Pending'] += 1
                
                    if task['Status'] == '3':
                        work_status_count['Completed'] += 1
            
                    if task['CreatedDate'] < current_date and task['Status'] == '1':
                        work_status_count['Due'] += 1

                    if task['Status'] == '8' or task['Status'] == '9':
                        work_status_count['Delay Finished'] += 1

                    if task['Status'] == '4' or task['Status'] == '5' or task['Status'] == '6':
                        work_status_count['Not Completed'] += 1   

                    if task['Status'] == '7':
                        work_status_count['Finished'] += 1

                row['WorkStatusCount'] = work_status_count
                clientData.append(row)
            
                
            return JsonResponse(clientData, safe=False)
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
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get Client by ClientId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete Client by ClientId",)
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
            client.ActiveStatus=0
            client.save()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get Client by CompanyId",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def ClientByCompanyId(request, CompanyId=""):
    try:
        if request.method == 'GET':
            BATCH_SIZE = 100
            client = Client.objects.filter(
                    CompanyId=CompanyId,ActiveStatus=1)
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
    queryset =Client.objects.filter(ActiveStatus=1).order_by('-SortId')
    pagination_class = CustomPageNumberPagination
    serializer_class = ClientSerializer 
    def post(self, request, *args, **kwargs):
        try:
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
        except:
            return JsonResponse("", safe=False)



@csrf_exempt
@swagger_auto_schema(method='POST', request_body=ClientOtherDetailsSerializer,operation_description="NOTE: API for save ClientOtherDetails")
@swagger_auto_schema(method='PUT', request_body=ClientOtherDetailsSerializer,operation_description="NOTE: API for edit ClientOtherDetails")
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all ClientOtherDetails",)
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
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get ClientOtherDetails by ClientOtherDetailsId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete ClientOtherDetails by ClientOtherDetailsId",)
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
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get ClientDocument by ClientDocumentId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete ClientDocument by ClientDocumentId",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def ClientDocumentApiById(request, ClientDocumentId=""):
    try:
        if request.method == 'GET': 
            clientDocuments = ClientDocuments.objects.get(
                    ClientDocumentId=ClientDocumentId)
            clientDocumentsSerializer = ClientDocumentsSerializer(
                    clientDocuments)
            return JsonResponse(clientDocumentsSerializer.data, safe=False)
        elif request.method == 'DELETE':
            clientDocuments = ClientDocuments.objects.get(ClientDocumentId=ClientDocumentId)
            ClientDocuments.objects.get(ClientDocumentId=ClientDocumentId).Document.delete(save=True)
            clientDocuments.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=ClientAddressSerializer,operation_description="NOTE: API for save ClientAddress")
@swagger_auto_schema(method='PUT', request_body=ClientAddressSerializer,operation_description="NOTE: API for edit ClientAddress")
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all ClientAddress",)
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
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get clientAddress by ClientAddressId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete clientAddress by ClientAddressId",)
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
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get ClientAddress by ClientId",)
@api_view(['GET'])
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
@swagger_auto_schema(method='POST', request_body=ContactPersonSerializer,operation_description="NOTE: API for save ContactPerson")
@swagger_auto_schema(method='PUT', request_body=ContactPersonSerializer,operation_description="NOTE: API for edit ContactPerson")
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get all ContactPerson",)
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
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get ContactPerson by ContactPersonId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete ContactPerson by ContactPersonId",)
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
    


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=ClientVisitRegisterSerializer,operation_description="NOTE: API for save ClientVisitRegister")
@swagger_auto_schema(method='PUT', request_body=ClientVisitRegisterSerializer,operation_description="NOTE: API for edit ClientVisitRegister")
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all ClientVisitRegister by ClientId",)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
def ClientVisitRegisterApi(request,ClientId=""):
    try:
        if request.method == 'GET':
            clientVisitRegister = ClientVisitRegister.objects.filter(ClientId=ClientId)
            clientVisitRegister_serializer = ClientVisitRegisterSerializer(
                clientVisitRegister, many=True)  
            return JsonResponse(clientVisitRegister_serializer.data, safe=False)

        elif request.method == 'POST':
            clientVisitRegisterData = JSONParser().parse(request)
            # return JsonResponse(clientVisitRegisterData, safe=False)
            clientVisitRegisterSerializer = ClientVisitRegisterSerializer(
                data=clientVisitRegisterData)
            if clientVisitRegisterSerializer.is_valid():
                clientVisitRegisterSerializer.save()
                return JsonResponse(clientVisitRegisterSerializer.data['ClientVisitRegisterId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            clientVisitRegisterData = JSONParser().parse(request)
            clientVisitRegister = ClientVisitRegister.objects.get(
                ClientVisitRegisterId=clientVisitRegisterData['ClientVisitRegisterId'])
            clientVisitRegisterSerializer = ClientVisitRegisterSerializer(
                clientVisitRegister, data=clientVisitRegisterData)
            if clientVisitRegisterSerializer.is_valid():
                clientVisitRegisterSerializer.save()
                return JsonResponse(clientVisitRegisterSerializer.data['ClientVisitRegisterId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("Invalid request", safe=False)
    except:
        return JsonResponse("", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get ClientVisitRegister by ClientVisitRegisterId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete ClientVisitRegister by ClientVisitRegisterId",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def ClientVisitRegisterApiById(request, ClientVisitRegisterId=""):
    try:
        if request.method == 'GET':
            clientVisitRegister = ClientVisitRegister.objects.get(ClientVisitRegisterId=ClientVisitRegisterId)
            clientVisitRegisterSerializer = ClientVisitRegisterSerializer(clientVisitRegister)
            return JsonResponse(clientVisitRegisterSerializer.data, safe=False)
        elif request.method == 'DELETE':
            clientVisitRegister = ClientVisitRegister.objects.get(
                ClientVisitRegisterId=ClientVisitRegisterId)
            clientVisitRegister.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("Invalid request", safe=False)
    except:
        return JsonResponse("", safe=False)
    




@csrf_exempt
@swagger_auto_schema(method='POST', request_body=ClientBankDetailsSerializer,operation_description="NOTE: API for save ClientBankDetails")
@swagger_auto_schema(method='PUT', request_body=ClientBankDetailsSerializer,operation_description="NOTE: API for edit ClientBankDetails")
@api_view(['POST','PUT'])
@retry(retries=3, delay=2)
def ClientBankDetailsApi(request):
    try:
        if request.method == 'POST':
            clientBankDetailsData = JSONParser().parse(request)
            clientBankDetailsSerializer = ClientBankDetailsSerializer(
                data=clientBankDetailsData)
            if clientBankDetailsData['PrimaryAccount']==True:
                clientBankDetails=ClientBankDetails.objects.filter(PrimaryAccount=1,ClientId=clientBankDetailsData['ClientId'])
                for bank in clientBankDetails:
                    bank.PrimaryAccount=False
                    bank.save()
            if clientBankDetailsSerializer.is_valid():
                clientBankDetailsSerializer.save()
                clientBankDetails = ClientBankDetails.objects.filter(ClientId=clientBankDetailsData['ClientId'])
                if len(clientBankDetails)==1:
                    for row in clientBankDetails:
                        row.PrimaryAccount=True
                        row.save()
                
                return JsonResponse(clientBankDetailsSerializer.data['BankDetailId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            clientBankDetailsData = JSONParser().parse(request)
            clientBankDetails = ClientBankDetails.objects.get(
                BankDetailId=clientBankDetailsData['BankDetailId'])
            clientBankDetailsSerializer = ClientBankDetailsSerializer(
                clientBankDetails, data=clientBankDetailsData)
            if clientBankDetailsData['PrimaryAccount']==True:
                clientBankDetails=ClientBankDetails.objects.filter(PrimaryAccount=1,ClientId=clientBankDetailsData['ClientId'])
                for bank in clientBankDetails:
                    bank.PrimaryAccount=False
                    bank.save()
            if clientBankDetailsSerializer.is_valid():
                clientBankDetailsSerializer.save()
                
                    
                return JsonResponse(clientBankDetailsSerializer.data['BankDetailId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get ClientBankDetails by ClientBankDetailsId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete ClientBankDetails by ClientBankDetailsId",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def ClientBankDetailsApiById(request, BankDetailId=""):
    try:
        if request.method == 'GET': 
            clientBankDetails = ClientBankDetails.objects.get(
                    BankDetailId=BankDetailId)
            clientBankDetailsSerializer = ClientBankDetailsSerializer(
                    clientBankDetails)
            return JsonResponse(clientBankDetailsSerializer.data, safe=False)
        elif request.method == 'DELETE':
            clientBankDetails = ClientBankDetails.objects.get(BankDetailId=BankDetailId)
            clientBankDetails.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    



@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get ClientBankDetails by ClientId",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def ClientBankDetailsApiByClientId(request, ClientId=""):
    try:
        if request.method == 'GET': 
            clientBankDetails = ClientBankDetails.objects.filter(
                    ClientId=ClientId)
            clientBankDetailsSerializer = ClientBankDetailsSerializer(
                clientBankDetails,many=True)
            return JsonResponse(clientBankDetailsSerializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)