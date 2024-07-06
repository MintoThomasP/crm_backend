from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
# Create your views here.
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

from app_company.models import Company, CompanyDocuments
from app_company.serializers import CompanyDocumentsSerializer, CompanySerializer, SaveCompanyDocumentsSerializer, UploadCompanyDocumentsSerializer
from app_default.views import retry
@csrf_exempt
@swagger_auto_schema(method='POST', request_body=CompanySerializer)
@swagger_auto_schema(method='PUT', request_body=CompanySerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all company details",)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
def CompanyApi(request):
    try:
        if request.method == 'GET':
            company = Company.objects.all()
            companySerializer = CompanySerializer(
                    company, many=True)
            companyData=[]
            for row in companySerializer.data:
                try:
                    companyDocuments = CompanyDocuments.objects.filter(
                        CompanyId=row['CompanyId'])
                    companyDocumentsSerializer = CompanyDocumentsSerializer(
                        companyDocuments,many=True)
                    row['DocumentDetails']=companyDocumentsSerializer.data
                except:
                    row['DocumentDetails']=""
                companyData.append(row)
              

            return JsonResponse(companyData, safe=False)
        elif request.method == 'POST':
            companyData = JSONParser().parse(request)
            companySerializer = CompanySerializer(
                data=companyData)
            if companySerializer.is_valid():
                companySerializer.save()
                return JsonResponse(companySerializer.data['CompanyId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            companyData = JSONParser().parse(request)
            company = Company.objects.get(
                CompanyId=companyData['CompanyId'])
            companySerializer = CompanySerializer(
                company, data=companyData)
            if companySerializer.is_valid():
                companySerializer.save()
                return JsonResponse(companySerializer.data['CompanyId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give CompanyId to get one companydetail",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def CompanyApiById(request, CompanyId=""):
    try:
        if request.method == 'GET': 
            company = Company.objects.get(
                    CompanyId=CompanyId)
            companySerializer = CompanySerializer(
                    company)
            companyData=companySerializer.data
            try:
                companyDocuments = CompanyDocuments.objects.filter(
                    CompanyId=CompanyId)
                companyDocumentsSerializer = CompanyDocumentsSerializer(
                    companyDocuments,many=True)
                companyData['DocumentDetails']=companyDocumentsSerializer.data
            except:
                companyData['DocumentDetails']=""
            
            return JsonResponse(companyData, safe=False)
        elif request.method == 'DELETE':
            company = Company.objects.get(CompanyId=CompanyId)
            company.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    



@csrf_exempt
@swagger_auto_schema(method='POST', request_body=CompanyDocumentsSerializer)
@swagger_auto_schema(method='PUT', request_body=CompanyDocumentsSerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all company details",)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
def CompanyDocumentsApi(request):
    try:
        if request.method == 'GET':
            companyDocuments = CompanyDocuments.objects.all()
            companyDocumentsSerializer = CompanyDocumentsSerializer(
                    companyDocuments, many=True)
            return JsonResponse(companyDocumentsSerializer.data, safe=False)
        elif request.method == 'POST':
            companyDocumentsData = JSONParser().parse(request)
            companyDocumentsSerializer = SaveCompanyDocumentsSerializer(
                data=companyDocumentsData)
            if companyDocumentsSerializer.is_valid():
                companyDocumentsSerializer.save()
                return JsonResponse(companyDocumentsSerializer.data['CompanyDocumentId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            companyDocumentsData = JSONParser().parse(request)
            companyDocuments = CompanyDocuments.objects.get(
                CompanyDocumentId=companyDocumentsData['CompanyDocumentId'])
            companyDocumentsSerializer = SaveCompanyDocumentsSerializer(
                companyDocuments, data=companyDocumentsData)
            if companyDocumentsSerializer.is_valid():
                companyDocumentsSerializer.save()
                return JsonResponse(companyDocumentsSerializer.data['CompanyDocumentId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give CompanyDocumentId to get one companyDocumentsdetail",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def CompanyDocumentsApiById(request, CompanyDocumentId=""):
    try:
        if request.method == 'GET': 
            companyDocuments = CompanyDocuments.objects.get(
                    CompanyDocumentId=CompanyDocumentId)
            companyDocumentsSerializer = CompanyDocumentsSerializer(
                    companyDocuments)
            companyDocumentsData=companyDocumentsSerializer.data
            
            return JsonResponse(companyDocumentsData, safe=False)
        elif request.method == 'DELETE':
            companyDocuments = CompanyDocuments.objects.get(CompanyDocumentId=CompanyDocumentId)
            companyDocuments.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    




class UploadCompanyDocuments(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, CompanyDocumentId="", *args, **kwargs):
        try:

                companyDocuments = CompanyDocuments.objects.get(
                    CompanyDocumentId=CompanyDocumentId)
                try:
                    CompanyDocuments.objects.get(
                        CompanyDocumentId=CompanyDocumentId).Document.delete(save=True)
                except:
                    p = ""
                Serializer = UploadCompanyDocumentsSerializer(
                    companyDocuments, data=request.data)
                if Serializer.is_valid():
                    Serializer.save()
                    return JsonResponse("ok", safe=False)
                else:
                    return JsonResponse("", safe=False)
        except:
            return JsonResponse("", safe=False)