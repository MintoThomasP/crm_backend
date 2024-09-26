from django.shortcuts import render

# Create your views here.
from datetime import date
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from app_vendor.models import Vendor, VendorAddress, VendorBankDetails, VendorContactPerson, VendorDocuments
from app_vendor.serializers import VendorAddressSerializer, VendorBankDetailsSerializer, VendorContactPersonSerializer, VendorDocumentsSerializer, VendorSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from app_basic.models import Country, State
from app_basic.serializers import CountrySerializer, StateSerializer
from app_default.views import retry
from app_project.views import CustomPageNumberPagination
from rest_framework import generics
from django.db.models import Q
from django.db import transaction   

@csrf_exempt
@swagger_auto_schema(method='POST', request_body=VendorSerializer,operation_description="NOTE: API for save Vendor")
@swagger_auto_schema(method='PUT', request_body=VendorSerializer,operation_description="NOTE: API for edit Vendor")
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all vendor by company id",)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
def VendorApi(request,CompanyId=""):
    try:
        if request.method == 'GET':
            vendor = Vendor.objects.filter(ActiveStatus=1,CompanyId=CompanyId)
            vendorSerializer = VendorSerializer(
                    vendor, many=True)
            return JsonResponse(vendorSerializer.data, safe=False)
        elif request.method == 'POST':
            vendorData = JSONParser().parse(request)
            vendorSerializer = VendorSerializer(
                data=vendorData)
            if vendorSerializer.is_valid():
                vendorSerializer.save()
                return JsonResponse(vendorSerializer.data['VendorId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            vendorData = JSONParser().parse(request)
            vendor = Vendor.objects.get(
                VendorId=vendorData['VendorId'])
            vendorSerializer = VendorSerializer(
                vendor, data=vendorData)
            if vendorSerializer.is_valid():
                vendorSerializer.save()
                return JsonResponse(vendorSerializer.data['VendorId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get Vendor by VendorId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete Vendor by VendorId",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def VendorApiById(request, VendorId=""):
    try:
        if request.method == 'GET': 
            vendor = Vendor.objects.get(
                    VendorId=VendorId)
            vendorSerializer = VendorSerializer(
                    vendor)
            vendorData=vendorSerializer.data
            vendorDocuments=VendorDocuments.objects.filter(VendorId=VendorId)
            vendorDocumentsSerializer = VendorDocumentsSerializer(
                    vendorDocuments,many=True)
            vendorData['VendorDocuments']=vendorDocumentsSerializer.data
               
            vendorAddress = VendorAddress.objects.filter(VendorId=VendorId)
            vendorAddressSerializer = VendorAddressSerializer(
                    vendorAddress, many=True)
            vendorData['VendorAddress']=vendorAddressSerializer.data
            contactPerson = VendorContactPerson.objects.filter(VendorId=VendorId)
            contactPersonSerializer = VendorContactPersonSerializer(
                    contactPerson, many=True)
            vendorData['ContactPersons']=contactPersonSerializer.data
            return JsonResponse(vendorData, safe=False)
        elif request.method == 'DELETE':
            vendor = Vendor.objects.get(VendorId=VendorId)
            vendor.ActiveStatus=0
            vendor.save()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get Vendor by CompanyId",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def VendorByCompanyId(request, CompanyId=""):
    try:
        if request.method == 'GET':
            BATCH_SIZE = 100
            vendor = Vendor.objects.filter(
                    CompanyId=CompanyId,ActiveStatus=1)
            total_vendor=vendor.count()
            all_serialized_data = []
            for i in range(0, total_vendor, BATCH_SIZE):
                with transaction.atomic():
                    batch_tasks = vendor[i:i+BATCH_SIZE]
                    serializer = VendorSerializer(batch_tasks, many=True)
                    serialized_data = serializer.data
                    all_serialized_data.extend(serialized_data)
            return JsonResponse(all_serialized_data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


class VendorApiByCompanyId(generics.ListAPIView):
    queryset =Vendor.objects.filter(ActiveStatus=1).order_by('-SortId')
    pagination_class = CustomPageNumberPagination
    serializer_class = VendorSerializer 
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



    


class UploadVendorDocument(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request,  *args, **kwargs):
        try:
                Serializer = VendorDocumentsSerializer(
                    data=request.data)
                if Serializer.is_valid():
                    Serializer.save()
                    return JsonResponse(Serializer.data['VendorDocumentId'], safe=False)
                else:
                    return JsonResponse("", safe=False)
        except:
            return JsonResponse("", safe=False)





@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get VendorDocument by VendorDocumentId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete VendorDocument by VendorDocumentId",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def VendorDocumentApiById(request, VendorDocumentId=""):
    try:
        if request.method == 'GET': 
            vendorDocuments = VendorDocuments.objects.get(
                    VendorDocumentId=VendorDocumentId)
            vendorDocumentsSerializer = VendorDocumentsSerializer(
                    vendorDocuments)
            return JsonResponse(vendorDocumentsSerializer.data, safe=False)
        elif request.method == 'DELETE':
            vendorDocuments = VendorDocuments.objects.get(VendorDocumentId=VendorDocumentId)
            VendorDocuments.objects.get(VendorDocumentId=VendorDocumentId).Document.delete(save=True)
            vendorDocuments.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=VendorAddressSerializer,operation_description="NOTE: API for save VendorAddress")
@swagger_auto_schema(method='PUT', request_body=VendorAddressSerializer,operation_description="NOTE: API for edit VendorAddress")
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all VendorAddress",)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
def VendorAddressApi(request):
    try:
        if request.method == 'GET':
            vendorAddress = VendorAddress.objects.all()
            vendorAddressSerializer = VendorAddressSerializer(
                    vendorAddress, many=True)
            return JsonResponse(vendorAddressSerializer.data, safe=False)
        elif request.method == 'POST':
            vendorAddressData = JSONParser().parse(request)
            vendorAddressSerializer = VendorAddressSerializer(
                data=vendorAddressData)
            if vendorAddressSerializer.is_valid():
                vendorAddressSerializer.save()
                return JsonResponse(vendorAddressSerializer.data['VendorAddressId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            vendorAddressData = JSONParser().parse(request)
            vendorAddress = VendorAddress.objects.get(
                VendorAddressId=vendorAddressData['VendorAddressId'])
            vendorAddressSerializer = VendorAddressSerializer(
                vendorAddress, data=vendorAddressData)
            if vendorAddressSerializer.is_valid():
                vendorAddressSerializer.save()
                return JsonResponse(vendorAddressSerializer.data['VendorAddressId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get vendorAddress by VendorAddressId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete vendorAddress by VendorAddressId",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def VendorAddressApiById(request, VendorAddressId=""):
    try:
        if request.method == 'GET': 
            vendorAddress = VendorAddress.objects.get(
                    VendorAddressId=VendorAddressId)
            vendorAddressSerializer = VendorAddressSerializer(
                    vendorAddress)
            return JsonResponse(vendorAddressSerializer.data, safe=False)
        elif request.method == 'DELETE':
            vendorAddress = VendorAddress.objects.get(VendorAddressId=VendorAddressId)
            vendorAddress.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get VendorAddress by VendorId",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def VendorAddressApiByVendorId(request, VendorId=""):
    try:
        if request.method == 'GET': 
            vendorAddress = VendorAddress.objects.filter(
                    VendorId=VendorId)
            vendorAddressSerializer = VendorAddressSerializer(
                    vendorAddress,many=True)
            vendorData=[]
            for row in vendorAddressSerializer.data:
                country=Country.objects.get(CountryId=row['Country'])
                countrySerializer=CountrySerializer(country)
                row['CountryName']=countrySerializer.data['Country']
                try:
                    state=State.objects.get(StateId=row['State'])
                    stateSerializer=StateSerializer(state)
                    row['StateName']=stateSerializer.data['State']
                except:
                    row['StateName']=[]
                vendorData.append(row)

            return JsonResponse(vendorData, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    



@csrf_exempt
@swagger_auto_schema(method='POST', request_body=VendorContactPersonSerializer,operation_description="NOTE: API for save ContactPerson")
@swagger_auto_schema(method='PUT', request_body=VendorContactPersonSerializer,operation_description="NOTE: API for edit ContactPerson")
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get all ContactPerson",)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
def ContactPersonApi(request):
    try:
        if request.method == 'GET':
            contactPerson = VendorContactPerson.objects.all()
            contactPersonSerializer = VendorContactPersonSerializer(
                    contactPerson, many=True)
            return JsonResponse(contactPersonSerializer.data, safe=False)
        elif request.method == 'POST':
            contactPersonData = JSONParser().parse(request)
            contactPersonSerializer = VendorContactPersonSerializer(
                data=contactPersonData)
            if contactPersonSerializer.is_valid():
                contactPersonSerializer.save()
                return JsonResponse(contactPersonSerializer.data['ContactPersonId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            contactPersonData = JSONParser().parse(request)
            contactPerson = VendorContactPerson.objects.get(
                ContactPersonId=contactPersonData['ContactPersonId'])
            contactPersonSerializer = VendorContactPersonSerializer(
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
            contactPerson = VendorContactPerson.objects.get(
                    ContactPersonId=ContactPersonId)
            contactPersonSerializer = VendorContactPersonSerializer(
                    contactPerson)
            return JsonResponse(contactPersonSerializer.data, safe=False)
        elif request.method == 'DELETE':
            contactPerson = VendorContactPerson.objects.get(ContactPersonId=ContactPersonId)
            contactPerson.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    





@csrf_exempt
@swagger_auto_schema(method='POST', request_body=VendorBankDetailsSerializer,operation_description="NOTE: API for save VendorBankDetails")
@swagger_auto_schema(method='PUT', request_body=VendorBankDetailsSerializer,operation_description="NOTE: API for edit VendorBankDetails")
@api_view(['POST','PUT'])
@retry(retries=3, delay=2)
def VendorBankDetailsApi(request):
    try:
        if request.method == 'POST':
            vendorBankDetailsData = JSONParser().parse(request)
            vendorBankDetailsSerializer = VendorBankDetailsSerializer(
                data=vendorBankDetailsData)
            if vendorBankDetailsData['PrimaryAccount']==True:
                vendorBankDetails=VendorBankDetails.objects.filter(PrimaryAccount=1,VendorId=vendorBankDetailsData['VendorId'])
                for bank in vendorBankDetails:
                    bank.PrimaryAccount=False
                    bank.save()
            if vendorBankDetailsSerializer.is_valid():
                vendorBankDetailsSerializer.save()
                vendorBankDetails = VendorBankDetails.objects.filter(VendorId=vendorBankDetailsData['VendorId'])
                if len(vendorBankDetails)==1:
                    for row in vendorBankDetails:
                        row.PrimaryAccount=True
                        row.save()
                return JsonResponse(vendorBankDetailsSerializer.data['BankDetailId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            vendorBankDetailsData = JSONParser().parse(request)
            vendorBankDetails = VendorBankDetails.objects.get(
                BankDetailId=vendorBankDetailsData['BankDetailId'])
            vendorBankDetailsSerializer = VendorBankDetailsSerializer(
                vendorBankDetails, data=vendorBankDetailsData)
            if vendorBankDetailsData['PrimaryAccount']==True:
                vendorBankDetails=VendorBankDetails.objects.filter(PrimaryAccount=1,VendorId=vendorBankDetailsData['VendorId'])
                for bank in vendorBankDetails:
                    bank.PrimaryAccount=False
                    bank.save()
            if vendorBankDetailsSerializer.is_valid():
                vendorBankDetailsSerializer.save()
                return JsonResponse(vendorBankDetailsSerializer.data['BankDetailId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get VendorBankDetails by VendorBankDetailsId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete VendorBankDetails by VendorBankDetailsId",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def VendorBankDetailsApiById(request, BankDetailId=""):
    try:
        if request.method == 'GET': 
            vendorBankDetails = VendorBankDetails.objects.get(
                    BankDetailId=BankDetailId)
            vendorBankDetailsSerializer = VendorBankDetailsSerializer(
                    vendorBankDetails)
            return JsonResponse(vendorBankDetailsSerializer.data, safe=False)
        elif request.method == 'DELETE':
            vendorBankDetails = VendorBankDetails.objects.get(BankDetailId=BankDetailId)
            vendorBankDetails.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    



@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get VendorBankDetails by VendorId",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def VendorBankDetailsApiByVendorId(request, VendorId=""):
    try:
        if request.method == 'GET': 
            vendorBankDetails = VendorBankDetails.objects.filter(
                    VendorId=VendorId)
            vendorBankDetailsSerializer = VendorBankDetailsSerializer(
                vendorBankDetails,many=True)
            return JsonResponse(vendorBankDetailsSerializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)