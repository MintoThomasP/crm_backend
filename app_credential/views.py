from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from app_client.models import Client
from app_client.serializers import ClientSerializer
from app_company.models import Company
from app_company.serializers import CompanySerializer
from app_credential.models import Credentials
from app_credential.serializers import CredentialsSerializer
from app_default.views import retry
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from rest_framework import generics
from app_project.views import CustomPageNumberPagination
from app_staff.models import Staff
from app_staff.serializers import StaffSerializer
# Create your views here.





@csrf_exempt
@swagger_auto_schema(method='POST', request_body=CredentialsSerializer,operation_description="NOTE: API for save Credentials")
@swagger_auto_schema(method='PUT', request_body=CredentialsSerializer,operation_description="NOTE: API for edit Credentials")
@api_view(['POST','PUT'])
@retry(retries=3, delay=2)
def CredentialsApi(request):
    # try:

        if request.method == 'POST':
            credentialsData = JSONParser().parse(request)
            credentialsSerializer = CredentialsSerializer(
                data=credentialsData)
            if credentialsSerializer.is_valid():
                credentialsSerializer.save()

                return JsonResponse(credentialsSerializer.data['CredentialId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            credentialsData = JSONParser().parse(request)
            credentials = Credentials.objects.get(
                CredentialId=credentialsData['CredentialId'])
            credentialsSerializer = CredentialsSerializer(
                credentials, data=credentialsData)
            if credentialsSerializer.is_valid():
                credentialsSerializer.save()
                return JsonResponse(credentialsSerializer.data['CredentialId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    # except:
    #     return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get Credentials by CredentialId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete Credentials by CredentialId",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def CredentialsApiById(request, CredentialId=""):
    try:
        if request.method == 'GET': 
            credentials = Credentials.objects.get(
                    CredentialId=CredentialId)
            credentialsSerializer = CredentialsSerializer(
                    credentials)
            return JsonResponse(credentialsSerializer.data, safe=False)
        elif request.method == 'DELETE':
            credentials = Credentials.objects.get(CredentialId=CredentialId)
            credentials.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    





class CredentialsPagination(generics.ListAPIView):
    queryset =Credentials.objects.all().order_by('-SortId')
    pagination_class = CustomPageNumberPagination
    serializer_class = CredentialsSerializer 
    def post(self, request, *args, **kwargs):
        try:
            filterData = JSONParser().parse(request)
           
            if filterData['UserId']:
                self.queryset = self.queryset.filter(UserId=filterData['UserId'])
            if filterData['CompanyId']:
                self.queryset = self.queryset.filter(CompanyId=filterData['CompanyId'])
            if filterData['AccessTo']:
                self.queryset = self.queryset.filter(AccessTo__icontains=filterData['AccessTo'])
            if filterData['ClientId']:
                self.queryset = self.queryset.filter(ClientId__in=filterData['ClientId'])
          
            page = self.paginate_queryset(self.queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                data = []

                for row in serializer.data:
                    try:
                        try:
                            staff=Staff.objects.get(StaffId=row['UserId'])
                            staffSerializer=StaffSerializer(staff)
                            row['UserIdName']=staffSerializer.data['StaffName']
                        except:
                            company=Company.objects.get(CompanyId=row['UserId'])
                            companySerializer=CompanySerializer(company)
                            row['UserIdName']=companySerializer.data['CompanyName']
                    except:
                        row['UserIdName']=""
                    try:
                        client=Client.objects.get(ClientId=row['ClientId'])
                        clientSerializer=ClientSerializer(client)
                        row['ClientName']=clientSerializer.data['CustomerDisplayName']
                    except:
                        row['ClientName']=""
                    data.append(row)
                return self.get_paginated_response(data)
        except:
            return JsonResponse("", safe=False)