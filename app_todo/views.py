from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from app_default.views import retry
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from rest_framework import generics
from app_project.views import CustomPageNumberPagination
from app_todo.models import Todo
from app_todo.serailizers import TodoSerializer

from django.utils import timezone
# Create your views here.




@csrf_exempt
@swagger_auto_schema(method='POST', request_body=TodoSerializer,operation_description="NOTE:API for save Todo")
@swagger_auto_schema(method='PUT', request_body=TodoSerializer,operation_description="NOTE:API for edit Todo")
@api_view(['POST','PUT'])
@retry(retries=3, delay=2)
def TodoApi(request):
    try:
        
        if request.method == 'POST':
            todoData = JSONParser().parse(request)
            todoSerializer = TodoSerializer(
                data=todoData)
            if todoSerializer.is_valid():
                todoSerializer.save()

                return JsonResponse(todoSerializer.data['TodoId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            todoData = JSONParser().parse(request)
            todo = Todo.objects.get(
                TodoId=todoData['TodoId'])
            todoSerializer = TodoSerializer(
                todo, data=todoData)
            if todoSerializer.is_valid():
                todoSerializer.save()
                return JsonResponse(todoSerializer.data['TodoId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get Todo by TodoId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete Todo by TodoId",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def TodoApiById(request, TodoId=""):
    try:
        if request.method == 'GET': 
            todo = Todo.objects.get(
                    TodoId=TodoId)
            todoSerializer = TodoSerializer(
                    todo)
            return JsonResponse(todoSerializer.data, safe=False)
        elif request.method == 'DELETE':
            todo = Todo.objects.get(TodoId=TodoId)
            todo.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    



class TodoPagination(generics.ListAPIView):
    queryset =Todo.objects.all()
    pagination_class = CustomPageNumberPagination
    serializer_class = TodoSerializer 
    def post(self, request, *args, **kwargs):
        try:
            filterData = JSONParser().parse(request)
            if filterData['Status']:
                status=filterData['Status']
                self.queryset = self.queryset.filter(IsCompleted=status)
            if filterData['UserId']:
                self.queryset = self.queryset.filter(UserId=filterData['UserId'])
            if filterData['StartDate'] and filterData['EndDate']:
                start_date = timezone.datetime.strptime(filterData['StartDate'], '%Y-%m-%d').date()
                end_date = (timezone.datetime.strptime(filterData['EndDate'], '%Y-%m-%d')).date()

                
                self.queryset = self.queryset.filter(ScheduledOn__range=(start_date,end_date))
            page = self.paginate_queryset(self.queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
        except:
            return JsonResponse("", safe=False)