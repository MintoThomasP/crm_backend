from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from app_default.views import retry
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q
from app_category.models import Category, Report
from app_category.serializers import CategorySerializer, ReportSerializer
from app_default.models import CategoryType
from app_default.serializers import CategoryTypeSerializer

# Create your views here.




@csrf_exempt
@swagger_auto_schema(method='POST', request_body=CategorySerializer)
@swagger_auto_schema(method='PUT', request_body=CategorySerializer)
@api_view(['POST', 'PUT'])
def CategoryApi(request):
    try:
        # if request.method == 'GET':
        #     category = Category.objects.filter(
        #         Q(RefId__isnull=True) | Q(RefId=""),ActiveStatus=1).order_by('-SortId')
        #     categorySerializer = CategorySerializer(
        #         category, many=True)
        #     categoryData=[]
        #     for row in categorySerializer.data:
        #         subcategory = Category.objects.filter(RefId=row['CategoryId'])
        #         subcategorySerializer=CategorySerializer(subcategory, many=True)
        #         row['Subcategory']=subcategorySerializer.data
        #         categoryData.append(row)
        #     return JsonResponse(categoryData, safe=False)
        if request.method == 'POST':
            categoryData = JSONParser().parse(request)
            categorySerializer = CategorySerializer(
                data=categoryData)
            if categorySerializer.is_valid():
                categorySerializer.save()
                return JsonResponse(categorySerializer.data['CategoryId'], safe=False)
            return JsonResponse("Failed", safe=False)
        elif request.method == 'PUT':
            categoryData = JSONParser().parse(request)
            category = Category.objects.get(
                CategoryId=categoryData['CategoryId'])
            categorySerializer = CategorySerializer(
                category, data=categoryData)
            if categorySerializer.is_valid():
                categorySerializer.save()
                return JsonResponse(categorySerializer.data['CategoryId'], safe=False)
            return JsonResponse("Failed", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("Invalid", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: give CategoryId to get one Category Detail",)
@api_view(['GET', 'DELETE'])
def CategoryApiById(request, CategoryId=""):
    try:
        if request.method == 'GET':
            category = Category.objects.get(
                CategoryId=CategoryId)
            categorySerializer = CategorySerializer(
                category)
            categoryData=categorySerializer.data
            subcategory = Category.objects.filter(RefId=CategoryId,ActiveStatus=1)
            subcategorySerializer=CategorySerializer(subcategory, many=True)
            categoryData['Subcategory']=subcategorySerializer.data
           
            return JsonResponse(categoryData, safe=False)
        elif request.method == 'DELETE':
            category = Category.objects.get(CategoryId=CategoryId)
            category.ActiveStatus=0
            category.save()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("Invalid", safe=False)




@csrf_exempt
@api_view(['POST'])
def GetAllCategoryBySectionTypeApi(request):
    try:
        if request.method == 'POST':
            categoryData = JSONParser().parse(request)
            category = Category.objects.filter(
                Q(RefId__isnull=True) | Q(RefId=""),ActiveStatus=1,SectionType=categoryData['SectionType']).order_by('-SortId')
            categorySerializer = CategorySerializer(
                category, many=True)
            categoryData=[]
            for row in categorySerializer.data:
                try:
                    categoryType=CategoryType.objects.get(CategoryTypeId=row['CategoryType'])
                    categoryTypeSerializer=CategoryTypeSerializer(categoryType)
                    row['CategoryTypeName']=categoryTypeSerializer.data['CategoryType']
                except:
                    row['CategoryTypeName']=""
                categoryData.append(row)
            return JsonResponse(categorySerializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("Invalid", safe=False)
    







@csrf_exempt
@swagger_auto_schema(method='POST', request_body=ReportSerializer)
@swagger_auto_schema(method='PUT', request_body=ReportSerializer)
@api_view(['POST', 'PUT'])
def ReportApi(request):
    # try:
        # if request.method == 'GET':
        #     report = Report.objects.all()
        #     reportSerializer = ReportSerializer(
        #         report, many=True)
        #     return JsonResponse(reportSerializer.data, safe=False)
        if request.method == 'POST':
            reportData = JSONParser().parse(request)
            for report in reportData:
                if report['ReportId']:
                    report = Report.objects.get(
                        ReportId=reportData['ReportId'])
                    reportSerializer = ReportSerializer(
                        report, data=report)
                    if reportSerializer.is_valid():
                        reportSerializer.save()
                else:
                    reportSerializer = ReportSerializer(
                        data=report)
                    if reportSerializer.is_valid():
                        reportSerializer.save()
            return JsonResponse("ok", safe=False)
        else:
            return JsonResponse("", safe=False)
    # except:
    #     return JsonResponse("Invalid", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: give ReportId to get one Report Detail",)
@api_view(['GET', 'DELETE'])
def ReportApiById(request, ReportId=""):
    try:
        if request.method == 'GET':
            report = Report.objects.get(
                ReportId=ReportId)
            reportSerializer = ReportSerializer(
                report)
            reportData=reportSerializer.data
            return JsonResponse(reportData, safe=False)
        elif request.method == 'DELETE':
            report = Report.objects.get(ReportId=ReportId)
            report.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("Invalid", safe=False)





def get_subcategories(category_id):
    subcategories = Category.objects.filter(RefId=category_id, ActiveStatus=1).order_by('-SortId')
    subcategory_serializer = CategorySerializer(subcategories, many=True)
    subcategory_data = []
    for subcategory in subcategory_serializer.data:
        children = get_subcategories(subcategory['CategoryId'])
        if children:
            subcategory['Subcategory'] = children
        else:
            subcategory['Subcategory']=[]

        report_data = get_report_data(subcategory['CategoryId'])
        if report_data:
            subcategory['Report'] = report_data
        subcategory_data.append(subcategory)
    return subcategory_data

def get_report_data(category_id):
    reports = Report.objects.filter(CategoryId=category_id)
    report_serializer = ReportSerializer(reports, many=True)
    return report_serializer.data

@csrf_exempt
@api_view(['POST'])
def GetAllCategoryandSubCategories(request):
    try:
        if request.method == 'POST':
            category_data = JSONParser().parse(request)
            categories = Category.objects.filter(
                Q(RefId__isnull=True) | Q(RefId=""),
                ActiveStatus=1,
                SectionType=category_data['SectionType']
            ).order_by('-SortId')
            category_serializer = CategorySerializer(categories, many=True)
            category_data = []
            for category in category_serializer.data:
                subcategories = get_subcategories(category['CategoryId'])
                if subcategories:
                    category['Subcategory'] = subcategories
                else:
                   
                    category['Subcategory'] = []
                report_data = get_report_data(category['CategoryId'])
                if report_data:
                    category['Report'] = report_data
                category_data.append(category)
            return JsonResponse(category_data, safe=False)
        else:
            return JsonResponse([], safe=False)
    except:
        return JsonResponse("Invalid", safe=False)

@csrf_exempt
@api_view(['POST'])
@retry(retries=3, delay=2)
def GetClientReportMonthly(request):
    data = JSONParser().parse(request)

    report = Report.objects.filter(ClientId=data['ClientId'],Month=data['Month'],Year=data['Year']).order_by('-OrderNo')
    reportSerializer = ReportSerializer(
        report, many=True)
    reportData=[]
    for report in reportSerializer.data:
        category = Category.objects.get(
            CategoryId=report['CategoryId'])
        categorySerializer = CategorySerializer(
            category)
        report['CategoryName']=categorySerializer.data['Category']
        reportData.append(report)
    return JsonResponse(reportData, safe=False)
