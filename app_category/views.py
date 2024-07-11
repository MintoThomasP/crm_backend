from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q
from app_category.models import Category
from app_category.serializers import CategorySerializer
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