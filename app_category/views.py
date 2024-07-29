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
from app_category.models import Category, Report, ReportRefFile
from app_category.serializers import CategorySerializer, ReportRefFileSerializer, ReportSaveSerializer, ReportSerializer, SaveReportRefFileSerializer
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
def GetCategoryandSubCategoriesByCategoryType(request):
    # try:
        if request.method == 'POST':
            category_data = JSONParser().parse(request)
            categoryType=CategoryType.objects.filter(CategoryTypeId__in=category_data['CategoryType'])
            categoryType_serializer = CategoryTypeSerializer(categoryType, many=True)
            data = []
            for category_type in categoryType_serializer.data:
                categories = Category.objects.filter(
                    Q(RefId__isnull=True) | Q(RefId=""),
                    ActiveStatus=1,
                    SectionType=category_data['SectionType'],CategoryType=category_type['CategoryTypeId']
                ).order_by('CategoryType')
                category_serializer = CategorySerializer(categories, many=True)
                
                for category in category_serializer.data:
                    subcategories = get_subcategories(category['CategoryId'])
                    if subcategories:
                        category['Subcategory'] = subcategories
                    else:
                    
                        category['Subcategory'] = []
                    # report_data = get_report_data(category['CategoryId'])
                    # if report_data:
                    #     category['Report'] = report_data
                category_type['Subcategory']=category_serializer.data
                category_type['Category']=category_type['CategoryType']
                category_type['CategoryId']=category_type['CategoryTypeId']
                data.append(category_type)
            return JsonResponse(data, safe=False)
        else:
            return JsonResponse([], safe=False)
    # except:
    #     return JsonResponse("Invalid", safe=False)

@csrf_exempt
@api_view(['POST'])
def GetAllCategoryandSubCategories(request):
    try:
        if request.method == 'POST':
            category_data = JSONParser().parse(request)
            categories = Category.objects.filter(
                Q(RefId__isnull=True) | Q(RefId=""),
                ActiveStatus=1,
                SectionType=category_data['SectionType'],
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

    report = Report.objects.filter(ClientId=data['ClientId'],Month=data['Month'],Year=data['Year'],ReportType=data['ReportType']).order_by('-OrderNo')
    reportSerializer = ReportSerializer(
        report, many=True)
    reportData=[]
    for report in reportSerializer.data:
        report['ReportRefFile']=[]
        try:
            category = Category.objects.get(
                CategoryId=report['CategoryId'])
            categorySerializer = CategorySerializer(
                category)
            report['CategoryName']=categorySerializer.data['Category']
            if categorySerializer.data['RefId']:
                report['RefId']=categorySerializer.data['RefId']
            else:
                report['RefId']=categorySerializer.data['CategoryType']
            reportFiles=ReportRefFile.objects.filter(ReportId=report['ReportId'])
            reportFilesSerializer = ReportRefFileSerializer(
                reportFiles,many=True)
            report['ReportRefFile']=reportFilesSerializer.data
        except:
            category = CategoryType.objects.get(
                CategoryTypeId=report['CategoryId'])
            categorySerializer = CategoryTypeSerializer(
                category)
            report['CategoryName']=categorySerializer.data['CategoryType']
            report['RefId']=""
        reportData.append(report)
    return JsonResponse(reportData, safe=False)


class SaveReportRefFile(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request,  *args, **kwargs):
        try:
                Serializer = SaveReportRefFileSerializer(
                    data=request.data)
                if Serializer.is_valid():
                    Serializer.save()
                    return JsonResponse(Serializer.data['ReportRefFileId'], safe=False)
                else:
                    return JsonResponse("", safe=False)
        except:
            return JsonResponse("", safe=False)
        
class SaveReport(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request,  *args, **kwargs):
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
                    if report['RefFiles']:
                        for file in report['RefFiles']:
                            filedata={
                                'ReportId':reportSerializer.data['ReportId'],
                                'ReportRefFile':file['ReportRefFile'],
                                'OrderNo':file['ReportRefFile']
                            }
                           
                            Serializer = SaveReportRefFileSerializer(
                                data=filedata)
                            if Serializer.is_valid():
                                Serializer.save()
        return JsonResponse("added", safe=False)
    


# class BulkCreateReportView(APIView):
#     parser_classes = (MultiPartParser, FormParser)

#     def post(self, request):
#         data = request.data
#         reports_data = []

#         # Extract reports data
#         for report in data:
#             if report['ReportId']:
#                 report = Report.objects.get(
#                     ReportId=data['ReportId'])
#                 reportSerializer = ReportSerializer(
#                     report, data=report)
#                 if reportSerializer.is_valid():
#                     reportSerializer.save()
#             else:
#                 reportSerializer = ReportSerializer(
#                     data=report)
#                 if reportSerializer.is_valid():
#                     reportSerializer.save()
#                     if report['RefFiles']:
#                         for file in report['RefFiles']:
#                             filedata={
#                                 'ReportId':reportSerializer.data['ReportId'],
#                                 'ReportRefFile':file['ReportRefFile'],
#                                 'OrderNo':file['ReportRefFile']
#                             }
                           
#                             Serializer = SaveReportRefFileSerializer(
#                                 data=filedata)
#                             if Serializer.is_valid():
#                                 Serializer.save()
#         return JsonResponse("added", safe=False)
    

from rest_framework import status
from rest_framework.response import Response
class BulkCreateReportView(APIView):
    def post(self, request, *args, **kwargs):
        try:
        
            if request.data['RefFiles']:
                if request.data['ReportId']:
                    report = Report.objects.get(
                        ReportId=request.data['ReportId'])
                    serializer = ReportSerializer(report,data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                        return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    serializer = ReportSerializer(data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                        return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except:
            if request.data['ReportId']:
                report = Report.objects.get(
                    ReportId=request.data['ReportId'])
                serializer = ReportSaveSerializer(report,data=request.data)
                if serializer.is_valid():
                    serializer.save()
            else:
                serializer = ReportSaveSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# class BulkCreateReportView(APIView):
#     def post(self, request, *args, **kwargs):
       
#         serializer = BulkReportSerializer(data=request.data)
#         if serializer.is_valid():
#             reports_data = serializer.validated_data.get('reports',[])
#             created_reports = []
#             for report_data in reports_data:
#                 report_serializer = ReportSerializer(data=report_data)
#                 if report_serializer.is_valid():
#                     report = report_serializer.save()
#                     created_reports.append(report_serializer.data)
#                 else:
#                     return Response(report_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#             return Response(created_reports, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


@csrf_exempt
@api_view(['DELETE'])
def DeleteReportRefFileById(request, ReportRefFileId=""):
    try:
        if request.method == 'DELETE':
            report = ReportRefFile.objects.get(ReportRefFileId=ReportRefFileId)
            report.ReportRefFile.delete(save=True)
            report.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("Invalid", safe=False)
