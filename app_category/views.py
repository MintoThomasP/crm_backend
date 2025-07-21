from app_project.views import CustomPageNumberPagination
from rest_framework.response import Response
from rest_framework import status
import json
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from app_client.models import Client
from app_client.serializers import ClientSerializer
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
@swagger_auto_schema(method='POST', request_body=CategorySerializer, operation_description="NOTE: API for save category")
@swagger_auto_schema(method='PUT', request_body=CategorySerializer, operation_description="NOTE: API for edit category")
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
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get Category by CategoryId",)
@swagger_auto_schema(method='DELETE', operation_description="NOTE: API for delete Category by CategoryId",)
@api_view(['GET', 'DELETE'])
@retry(retries=3, delay=2)
def CategoryApiById(request, CompanyId="", CategoryId=""):
    try:
        if request.method == 'GET':
            category = Category.objects.get(
                CategoryId=CategoryId, CompanyId=CompanyId)
            categorySerializer = CategorySerializer(
                category)
            categoryData = categorySerializer.data
            subcategory = Category.objects.filter(
                RefId=CategoryId, ActiveStatus=1)
            subcategorySerializer = CategorySerializer(subcategory, many=True)
            categoryData['Subcategory'] = subcategorySerializer.data

            return JsonResponse(categoryData, safe=False)
        elif request.method == 'DELETE':
            category = Category.objects.get(
                CategoryId=CategoryId, CompanyId=CompanyId)
            category.ActiveStatus = 0
            category.save()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("Invalid", safe=False)


def get_subcategoriesbysectiontype(category_id):
    subcategories = Category.objects.filter(
        RefId=category_id, ActiveStatus=1).exclude(SectionType=3).order_by('-SortId')
    subcategory_serializer = CategorySerializer(subcategories, many=True)
    subcategory_data = []
    for subcategory in subcategory_serializer.data:
        children = get_subcategoriesbysectiontype(subcategory['CategoryId'])
        subcategory['Subcategory'] = children
        subcategory['Ledger'] = get_ledger_by_categoryid(
            subcategory['CategoryId'])
        subcategory_data.append(subcategory)
    return subcategory_data


def get_ledger_by_categoryid(category_id):
    subcategories = Category.objects.filter(
        RefId=category_id, SectionType=3).order_by('-SortId')
    subcategory_serializer = CategorySerializer(subcategories, many=True)
    subcategory_data = subcategory_serializer.data
    return subcategory_data


@csrf_exempt
@swagger_auto_schema(method='POST', operation_description="NOTE: API for get Category by SectionType",)
@api_view(['POST'])
@retry(retries=3, delay=2)
def GetAllCategoryBySectionTypeApi(request):
    # try:
    if request.method == 'POST':
        categoryData = JSONParser().parse(request)
        category = Category.objects.filter(
            Q(RefId__isnull=True) | Q(RefId=""), ActiveStatus=1, SectionType=categoryData['SectionType'], CompanyId=categoryData['CompanyId']).order_by('-SortId')
        categorySerializer = CategorySerializer(
            category, many=True)
        categoryData = []
        for row in categorySerializer.data:
            try:
                categoryType = CategoryType.objects.get(
                    CategoryTypeId=row['CategoryType'])
                categoryTypeSerializer = CategoryTypeSerializer(categoryType)
                row['CategoryTypeName'] = categoryTypeSerializer.data['CategoryType']
            except:
                row['CategoryTypeName'] = ""
            row['Subcategory'] = get_subcategoriesbysectiontype(
                row['CategoryId'])
            row['Ledger'] = get_ledger_by_categoryid(row['CategoryId'])
            # report_data = get_report_data(row['CategoryId'])
            # if report_data:
            #     row['Report'] = report_data
            categoryData.append(row)
        return JsonResponse(categorySerializer.data, safe=False)
    else:
        return JsonResponse("", safe=False)
    # except:
    #     return JsonResponse("", safe=False)


# class LedgerCategoryPagination(generics.ListAPIView):
#     queryset = Category.objects.all().order_by('-SortId')
#     pagination_class = CustomPageNumberPagination
#     serializer_class = CategorySerializer

#     def post(self, request, *args, **kwargs):
#         page = self.paginate_queryset(self.queryset)
#         filterData = JSONParser().parse(request)
#         Keyword = filterData.get('SearchKeyword', '')
#         if filterData['CompanyId']:
#             self.queryset = self.queryset.filter(
#                 CompanyId=filterData['CompanyId'])
#         if filterData['SectionType']:
#             self.queryset = self.queryset.filter(
#                 SectionType=filterData['SectionType'])
#         if filterData['ActiveStatus']:
#             self.queryset = self.queryset.filter(
#                 ActiveStatus=filterData['ActiveStatus'])
#         if Keyword:
#             self.queryset = self.queryset.filter(Category__icontains=Keyword)
#         if page is not None:
#             serializer = self.get_serializer(page, many=True)
#             data = []

#             for row in serializer.data:
#                 row['CategoryPath'] = get_category_path(
#                     get_maincategories(row['RefId']))
#                 try:
#                     categoryType = CategoryType.objects.get(
#                         CategoryTypeId=row['CategoryType'])
#                     categoryTypeSerializer = CategoryTypeSerializer(
#                         categoryType)
#                     row['CategoryTypeName'] = categoryTypeSerializer.data['CategoryType']
#                 except:
#                     row['CategoryTypeName'] = ""

#                 data.append(row)
#             return self.get_paginated_response(data)


@csrf_exempt
@retry(retries=3, delay=2)
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get all ledger category",)
@api_view(['GET'])
def GetAllLedgerCategory(request, CompanyId=""):
    # try:
    if request.method == 'GET':
        category = Category.objects.filter(
            ActiveStatus=1, SectionType='3', CompanyId=CompanyId).order_by('-SortId')
        categorySerializer = CategorySerializer(
            category, many=True)
        categoryData = []
        for row in categorySerializer.data:
            row['CategoryPath'] = get_category_path(
                get_maincategories(row['RefId']))
            try:
                categoryType = CategoryType.objects.get(
                    CategoryTypeId=row['CategoryType'])
                categoryTypeSerializer = CategoryTypeSerializer(categoryType)
                row['CategoryTypeName'] = categoryTypeSerializer.data['CategoryType']
            except:
                row['CategoryTypeName'] = ""

            categoryData.append(row)
        return JsonResponse(categorySerializer.data, safe=False)
    else:
        return JsonResponse("", safe=False)
    # except:
    #     return JsonResponse("", safe=False)


def get_category_path(category):
    path = ""
    for data in category:
        path = data['Category'] + " \ " + \
            get_category_path(data['Subcategory'])
    return path


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=ReportSerializer, operation_description="NOTE: API for save Report")
@swagger_auto_schema(method='PUT', request_body=ReportSerializer, operation_description="NOTE: API for edit Report")
@api_view(['POST', 'PUT'])
def ReportApi(request):
    try:
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
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get report by ReportId",)
@swagger_auto_schema(method='DELETE', operation_description="NOTE: API for delete report by ReportId",)
@api_view(['GET', 'DELETE'])
def ReportApiById(request, ReportId=""):
    try:
        if request.method == 'GET':
            report = Report.objects.get(
                ReportId=ReportId)
            reportSerializer = ReportSerializer(
                report)
            reportData = reportSerializer.data
            return JsonResponse(reportData, safe=False)
        elif request.method == 'DELETE':
            report = Report.objects.get(ReportId=ReportId)
            report.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("Invalid", safe=False)


@csrf_exempt
@swagger_auto_schema(method='POST', operation_description="NOTE: API for get category and subcategories by CategoryType",)
@api_view(['POST'])
def GetCategoryandSubCategoriesByCategoryType(request):
    # try:
    if request.method == 'POST':
        category_data = JSONParser().parse(request)
        categoryType = CategoryType.objects.filter(
            CategoryTypeId__in=category_data['CategoryType'])
        categoryType_serializer = CategoryTypeSerializer(
            categoryType, many=True)
        data = []
        for category_type in categoryType_serializer.data:
            categories = Category.objects.filter(
                Q(RefId__isnull=True) | Q(RefId=""),
                ActiveStatus=1,
                SectionType=category_data['SectionType'], CategoryType=category_type[
                    'CategoryTypeId'], CompanyId=category_data['CompanyId']
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
            category_type['Subcategory'] = category_serializer.data
            category_type['Category'] = category_type['CategoryType']
            category_type['CategoryId'] = category_type['CategoryTypeId']
            data.append(category_type)
        return JsonResponse(data, safe=False)
    else:
        return JsonResponse([], safe=False)
    # except:
    #     return JsonResponse("", safe=False)


def get_subcategories(category_id):
    subcategories = Category.objects.filter(
        RefId=category_id, ActiveStatus=1).order_by('-SortId')
    subcategory_serializer = CategorySerializer(subcategories, many=True)
    subcategory_data = []
    for subcategory in subcategory_serializer.data:
        children = get_subcategories(subcategory['CategoryId'])
        if children:
            subcategory['Subcategory'] = children
        else:
            subcategory['Subcategory'] = []

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
@swagger_auto_schema(method='POST', operation_description="NOTE: API for get category and subcategories and report details by SectionType",)
@api_view(['POST'])
def GetAllCategoryandSubCategories(request):
    try:
        if request.method == 'POST':
            category_data = JSONParser().parse(request)

            # Fetch all categories at once and group by RefId for faster processing
            all_categories = Category.objects.filter(
                Q(RefId__isnull=True) | Q(RefId="") | Q(RefId__isnull=False),
                ActiveStatus=1,
                SectionType=category_data['SectionType'],
                CompanyId=category_data['CompanyId'],
            ).order_by('-SortId')

            # Serialize categories once
            category_serializer = CategorySerializer(all_categories, many=True)
            category_map = {}

            # Organize categories by CategoryId and RefId for quick lookup
            for category in category_serializer.data:
                category_id = category['CategoryId']
                ref_id = category['RefId']
                if ref_id:
                    category_map.setdefault(ref_id, []).append(category)
                else:
                    category_map.setdefault(None, []).append(category)

            # Build nested structure without recursion
            def attach_subcategories(parent_category):
                subcategories = category_map.get(
                    parent_category['CategoryId'], [])
                for subcategory in subcategories:
                    attach_subcategories(subcategory)
                    subcategory['Subcategory'] = category_map.get(
                        subcategory['CategoryId'], [])

                    # Attach report data for subcategory
                    report_data = get_report_data(subcategory['CategoryId'])
                    if report_data:
                        subcategory['Report'] = report_data

                parent_category['Subcategory'] = subcategories

            # Prepare final data structure
            category_data = []
            for root_category in category_map.get(None, []):
                attach_subcategories(root_category)

                # Attach report data for main category
                report_data = get_report_data(root_category['CategoryId'])
                if report_data:
                    root_category['Report'] = report_data

                category_data.append(root_category)

            return JsonResponse(category_data, safe=False)
        else:
            return JsonResponse([], safe=False)
    except Exception as e:
        return JsonResponse({"error": "Invalid", "details": str(e)}, safe=False)


def get_report_data(category_id):
    # Fetch all reports in one go to avoid repeated DB calls
    reports = Report.objects.filter(CategoryId=category_id)
    report_serializer = ReportSerializer(reports, many=True)
    return report_serializer.data


@csrf_exempt
@swagger_auto_schema(method='POST', operation_description="NOTE: API for get Monthly Client report",)
@api_view(['POST'])
@retry(retries=3, delay=2)
def GetClientReportMonthly(request):
    data = JSONParser().parse(request)

    report = Report.objects.filter(ClientId=data['ClientId'], Month=data['Month'],
                                   Year=data['Year'], ReportType=data['ReportType']).order_by('-OrderNo')
    reportSerializer = ReportSerializer(
        report, many=True)
    reportData = []
    for report in reportSerializer.data:
        report['ReportRefFile'] = []
        try:
            category = Category.objects.get(
                CategoryId=report['CategoryId'])
            categorySerializer = CategorySerializer(
                category)
            report['CategoryName'] = categorySerializer.data['Category']
            if categorySerializer.data['RefId']:
                report['RefId'] = categorySerializer.data['RefId']
            else:
                report['RefId'] = categorySerializer.data['CategoryType']
            reportFiles = ReportRefFile.objects.filter(
                ReportId=report['ReportId'])
            reportFilesSerializer = ReportRefFileSerializer(
                reportFiles, many=True)
            report['ReportRefFile'] = reportFilesSerializer.data
        except:
            category = CategoryType.objects.get(
                CategoryTypeId=report['CategoryId'])
            categorySerializer = CategoryTypeSerializer(
                category)
            report['CategoryName'] = categorySerializer.data['CategoryType']
            report['RefId'] = ""
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
                            filedata = {
                                'ReportId': reportSerializer.data['ReportId'],
                                'ReportRefFile': file['ReportRefFile'],
                                'OrderNo': file['ReportRefFile']
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


class BulkCreateReportView(APIView):
    def post(self, request, *args, **kwargs):
        try:

            if request.data['RefFiles']:
                if request.data['ReportId']:
                    report = Report.objects.get(
                        ReportId=request.data['ReportId'])
                    serializer = ReportSerializer(report, data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                        return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    serializer = ReportSerializer(data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                        return Response("Saved", status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except:
            if request.data['ReportId']:
                report = Report.objects.get(
                    ReportId=request.data['ReportId'])
                serializer = ReportSaveSerializer(report, data=request.data)
                if serializer.is_valid():
                    serializer.save()
            else:
                serializer = ReportSaveSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
            return Response("Saved", status=status.HTTP_201_CREATED)
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
@swagger_auto_schema(method='DELETE', operation_description="NOTE: API for delete report ref file by ReportRefFileId",)
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


def get_maincategories(category_id, data=[]):
    subcategories = Category.objects.filter(CategoryId=category_id)
    subcategory_serializer = CategorySerializer(subcategories, many=True)
    subcategory = subcategory_serializer.data
    subcategory[0]['Subcategory'] = data
    if subcategory[0]['RefId']:
        children = get_maincategories(subcategory[0]['RefId'], subcategory)
        returnData = children
    else:
        subcategory[0]['RefId'] = subcategory[0]['CategoryType']
        categoryType = CategoryType.objects.get(
            CategoryTypeId=subcategory[0]['CategoryType'])
        categoryTypeSerializer = CategoryTypeSerializer(categoryType)
        mainCategory = []
        mainCategory.append({
            'UsageType': categoryTypeSerializer.data['UsageType'],
            'OrderNo': categoryTypeSerializer.data['OrderNo'],
            'Ref': categoryTypeSerializer.data['Ref'],
            'CategoryId': categoryTypeSerializer.data['CategoryTypeId'],
            'RefId': '',
            'Category': categoryTypeSerializer.data['CategoryType'],
            'SectionType': '',
            'CategoryType': '',
            'ActiveStatus': ''
        })
        mainCategory[0]['Subcategory'] = subcategory
        returnData = mainCategory
    return returnData


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get main category by CategoryId",)
@api_view(['GET'])
def GetMainCategorybySubCategoryId(request, CategoryId=""):
    if request.method == 'GET':
        response_data = get_maincategories(CategoryId)
        return JsonResponse(response_data, safe=False)
    else:
        return JsonResponse([], safe=False)


@csrf_exempt
@swagger_auto_schema(method='POST', operation_description="NOTE: API for save ClientLedgerId")
@api_view(['POST'])
def saveClientLedgerId(request, ClientId="", ReportType=""):
    clientData = JSONParser().parse(request)

    response_data = []
    for id in clientData:
        try:
            mainCategory = get_maincategories(id)
            if response_data:
                response_data = checkSameCategory(
                    response_data, mainCategory[0])
            else:
                response_data.append(mainCategory[0])
        except Exception as e:
            # print(f"Error processing id {id}: {e}")
            continue

    return JsonResponse(response_data, safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get Main category by ClientId")
@api_view(['GET'])
def GetMainCategorybyClientId(request, ClientId="", ReportType=""):
    if request.method == 'GET':
        try:
            client = Client.objects.get(ClientId=ClientId)
            clientSerializer = ClientSerializer(client)
            response_data = []
            ledgerId = []
            if ReportType == "1":
                ledgerId = clientSerializer.data.get('PLLedger', [])
            elif ReportType == "2":
                ledgerId = clientSerializer.data.get('BalanceSheetLedger', [])
            for id in ledgerId:
                try:
                    mainCategory = get_maincategories(id)
                    if len(response_data):
                        response_data = checkSameCategory(
                            response_data, mainCategory[0])
                    else:
                        response_data.append(mainCategory[0])
                except:
                    continue

            return JsonResponse(response_data, safe=False)

        except:
            return JsonResponse([], safe=False)

    return JsonResponse("", safe=False)


def checkSameCategory(ExistCategoryList, NewCategory):
    category_found = False
    for cat_data in ExistCategoryList:
        if cat_data['CategoryId'] == NewCategory['CategoryId']:
            category_found = True
            if len(NewCategory['Subcategory']):
                cat_data['Subcategory'] = checkSameCategory(
                    cat_data['Subcategory'], NewCategory['Subcategory'][0])
            break

    if not category_found:
        ExistCategoryList.append(NewCategory)

    return ExistCategoryList
