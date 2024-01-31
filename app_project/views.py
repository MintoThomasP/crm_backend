from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from app_default.models import TaskStatus
from app_default.serializers import TaskStatusSerializer

from app_staff.models import Staff

from app_staff.serializers import StaffSerializer

from app_project.models import Project, ProjectTask, TaskReviews
from app_project.serializers import ProjectSerializer, ProjectTaskSerializer, TaskReviewsSerializer

from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=ProjectSerializer)
@swagger_auto_schema(method='PUT', request_body=ProjectSerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all Project Details",)
@api_view(['GET','POST','PUT'])
def ProjectApi(request):
    try:
        if request.method == 'GET':
            project = Project.objects.all().order_by('-SortId')
            projectSerializer = ProjectSerializer(
                    project, many=True)
            return JsonResponse(projectSerializer.data, safe=False)
        elif request.method == 'POST':
            projectData = JSONParser().parse(request)
            projectSerializer = ProjectSerializer(
                data=projectData)
            if projectSerializer.is_valid():
                projectSerializer.save()

                return JsonResponse(projectSerializer.data['ProjectId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            projectData = JSONParser().parse(request)
            project = Project.objects.get(
                ProjectId=projectData['ProjectId'])
            projectSerializer = ProjectSerializer(
                project, data=projectData)
            if projectSerializer.is_valid():
                projectSerializer.save()
                return JsonResponse(projectSerializer.data['ProjectId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give ProjectId to get one project detail",)
@api_view(['GET','DELETE'])
def ProjectApiById(request, ProjectId=""):
    try:
        if request.method == 'GET': 
            project = Project.objects.get(
                    ProjectId=ProjectId)
            projectSerializer = ProjectSerializer(
                    project)
            return JsonResponse(projectSerializer.data, safe=False)
        elif request.method == 'DELETE':
            project = Project.objects.get(ProjectId=ProjectId)
            project.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=ProjectTaskSerializer)
@swagger_auto_schema(method='PUT', request_body=ProjectTaskSerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all ProjectTask Details",)
@api_view(['GET','POST','PUT'])
def ProjectTaskApi(request):
    # try:
        if request.method == 'GET':
            projectTask = ProjectTask.objects.all().order_by('-SortId')
            projectTaskSerializer = ProjectTaskSerializer(
                    projectTask, many=True)
            taskData=[]
            for row in projectTaskSerializer.data:
                project=Project.objects.get(ProjectId=row['ProjectId'])
                projectSerializer=ProjectSerializer(project)
                row['ProjectName']=projectSerializer.data['ProjectName']

                staff=Staff.objects.get(StaffId=row['TaskAssignedTo'])
                staffSerializer=StaffSerializer(staff)
                row['AssignedTo']=staffSerializer.data['StaffName']

                staff=Staff.objects.get(StaffId=row['TaskAssignedBy'])
                staffSerializer=StaffSerializer(staff)
                row['AssignedBy']=staffSerializer.data['StaffName']

                taskStatus=TaskStatus.objects.get(StatusId=row['Status'])
                taskStatusSerializer=TaskStatusSerializer(taskStatus)
                row['StatusName']=taskStatusSerializer.data['Status']
                taskData.append(row)

            return JsonResponse(taskData, safe=False)
        elif request.method == 'POST':
            projectTaskData = JSONParser().parse(request)
            projectTaskSerializer = ProjectTaskSerializer(
                data=projectTaskData)
            if projectTaskSerializer.is_valid():
                projectTaskSerializer.save()

                return JsonResponse(projectTaskSerializer.data['ProjectTaskId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            projectTaskData = JSONParser().parse(request)
            projectTask = ProjectTask.objects.get(
                ProjectTaskId=projectTaskData['ProjectTaskId'])
            projectTaskSerializer = ProjectTaskSerializer(
                projectTask, data=projectTaskData)
            if projectTaskSerializer.is_valid():
                projectTaskSerializer.save()
                return JsonResponse(projectTaskSerializer.data['ProjectTaskId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    # except:
    #     return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give ProjectTaskId to get one task detail",)
@api_view(['GET','DELETE'])
def ProjectTaskApiById(request, ProjectTaskId=""):
    try:
        if request.method == 'GET': 
            projectTask = ProjectTask.objects.get(
                    ProjectTaskId=ProjectTaskId)
            projectTaskSerializer = ProjectTaskSerializer(
                    projectTask)
            return JsonResponse(projectTaskSerializer.data, safe=False)
        elif request.method == 'DELETE':
            projectTask = ProjectTask.objects.get(ProjectTaskId=ProjectTaskId)
            projectTask.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give ProjectId to get task detail",)
@api_view(['GET'])
def ProjectTaskApiByProjectId(request, ProjectId=""):
    try:
        if request.method == 'GET': 
            projectTask = ProjectTask.objects.filter(
                    ProjectId=ProjectId)
            projectTaskSerializer = ProjectTaskSerializer(
                    projectTask,many=True)
            taskStatusName=[]
            for row in projectTaskSerializer.data:
                taskStatus=TaskStatus.objects.get(StatusId=row['Status'])
                taskStatusSerializer=TaskStatusSerializer(taskStatus)
                row['StatusName']=taskStatusSerializer.data['Status']
                taskStatusName.append(row)
            return JsonResponse(taskStatusName, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Get projecttask by staff",)
@api_view(['GET'])
def ProjectTaskApiByUserId(request, TaskAssignedTo=""):
    try:
        if request.method == 'GET': 
            projectTask = ProjectTask.objects.filter(
                    TaskAssignedTo=TaskAssignedTo)
            projectTaskSerializer = ProjectTaskSerializer(
                    projectTask,many=True)
            taskStatusName=[]
            for row in projectTaskSerializer.data:
                taskStatus=TaskStatus.objects.get(StatusId=row['Status'])
                taskStatusSerializer=TaskStatusSerializer(taskStatus)
                row['StatusName']=taskStatusSerializer.data['Status']
                taskStatusName.append(row)
            return JsonResponse(taskStatusName, safe=False)
            
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
# @csrf_exempt
# @swagger_auto_schema(method='GET',operation_description="NOTE: Get projecttask by staff",)
# @api_view(['GET'])
# def ProjectTaskApiByTaskAssignedBy(request, TaskAssignedBy=""):
#     try:
#         if request.method == 'GET': 
#             projectTask = ProjectTask.objects.filter(
#                     TaskAssignedBy=TaskAssignedBy)
#             projectTaskSerializer = ProjectTaskSerializer(
#                     projectTask,many=True)
#             taskStatusName=[]
#             for row in projectTaskSerializer.data:
#                 taskStatus=TaskStatus.objects.get(StatusId=row['Status'])
#                 taskStatusSerializer=TaskStatusSerializer(taskStatus)
#                 row['StatusName']=taskStatusSerializer.data['Status']
#                 taskStatusName.append(row)
#             return JsonResponse(taskStatusName, safe=False)
            
#         else:
#             return JsonResponse("", safe=False)
#     except:
#         return JsonResponse("", safe=False)
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Get projecttask by staff",)
@api_view(['GET'])
def ProjectTaskApiByTaskAssignedBy(request, TaskAssignedBy=""):
    # try:
        if request.method == 'GET': 
            projectTask = ProjectTask.objects.filter(TaskAssignedBy=TaskAssignedBy)
            projectTaskSerializer = ProjectTaskSerializer(projectTask, many=True)
            taskStatusName = []
            for row in projectTaskSerializer.data:
                taskStatus = TaskStatus.objects.get(StatusId=row['Status'])
                taskStatusSerializer = TaskStatusSerializer(taskStatus)
                row['StatusName'] = taskStatusSerializer.data['Status']
                project = Project.objects.get(ProjectId=row['ProjectId'])
                projectSerializer = ProjectSerializer(project)
                row['ProjectName'] = projectSerializer.data['ProjectName']
                staff = Staff.objects.get(StaffId=row['TaskAssignedTo'])
                staffSerializer = StaffSerializer(staff)
                row['StaffName'] = staffSerializer.data['StaffName']

                taskStatusName.append(row)

            return JsonResponse(taskStatusName, safe=False)
        else:
            return JsonResponse("", safe=False)
    # except:
    #     return JsonResponse("", safe=False)

@csrf_exempt
@swagger_auto_schema(method='POST',request_body=ProjectTaskSerializer,operation_description="Give ProjectId and TaskAssignedTo in payload",)
@api_view(['POST'])
def ProjectTaskApiByUserIdAndProjectId(request):
    try:
        if request.method == 'POST': 
            projectTaskData = JSONParser().parse(request)
            projectTask = ProjectTask.objects.filter(
                    ProjectId=projectTaskData['ProjectId'],TaskAssignedTo=projectTaskData['TaskAssignedTo'])
            projectTaskSerializer = ProjectTaskSerializer(
                    projectTask,many=True)
            taskStatusName=[]
            for row in projectTaskSerializer.data:
                taskStatus=TaskStatus.objects.get(StatusId=row['Status'])
                taskStatusSerializer=TaskStatusSerializer(taskStatus)
                row['StatusName']=taskStatusSerializer.data['Status']
                taskStatusName.append(row)
            return JsonResponse(taskStatusName, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='POST',request_body=ProjectTaskSerializer,operation_description="Give ProjectId and TaskAssignedTo in payload",)
@api_view(['POST'])
def ProjectTaskApiByTaskAssignedByAndProjectId(request):
    try:
        if request.method == 'POST': 
            projectTaskData = JSONParser().parse(request)
            projectTask = ProjectTask.objects.filter(
                    ProjectId=projectTaskData['ProjectId'],TaskAssignedBy=projectTaskData['TaskAssignedBy'])
            projectTaskSerializer = ProjectTaskSerializer(
                    projectTask,many=True)
            taskData=[]
            for row in projectTaskSerializer.data:
                taskStatus=TaskStatus.objects.get(StatusId=row['Status'])
                taskStatusSerializer=TaskStatusSerializer(taskStatus)
                row['StatusName']=taskStatusSerializer.data['Status']
                project = Project.objects.get(ProjectId=row['ProjectId'])
                projectSerializer = ProjectSerializer(project)
                row['ProjectName'] = projectSerializer.data['ProjectName']
                staff = Staff.objects.get(StaffId=row['TaskAssignedBy'])
                staffSerializer = StaffSerializer(staff)
                row['StaffName'] = staffSerializer.data['StaffName']
                taskData.append(row)
            return JsonResponse(taskData, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False) 

@csrf_exempt
@swagger_auto_schema(method='POST', request_body=TaskReviewsSerializer)
@swagger_auto_schema(method='PUT', request_body=TaskReviewsSerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get task reviews",)
@api_view(['GET','POST','PUT'])
def TaskReviewsApi(request):
    try:
        if request.method == 'GET':
            taskReview = TaskReviews.objects.all().order_by('-SortId')
            taskReviewSerializer = TaskReviewsSerializer(
                    taskReview, many=True)
            return JsonResponse(taskReviewSerializer.data, safe=False)
        elif request.method == 'POST':
            taskReviewData = JSONParser().parse(request)
            taskReviewSerializer = TaskReviewsSerializer(
                data=taskReviewData)
            if taskReviewSerializer.is_valid():
                taskReviewSerializer.save()

                return JsonResponse(taskReviewSerializer.data['TaskReviewId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            taskReviewData = JSONParser().parse(request)
            taskReview = TaskReviews.objects.get(
                TaskReviewId=taskReviewData['TaskReviewId'])
            taskReviewSerializer = TaskReviewsSerializer(
                taskReview, data=taskReviewData)
            if taskReviewSerializer.is_valid():
                taskReviewSerializer.save()
                return JsonResponse(taskReviewSerializer.data['TaskReviewId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give TaskReviewId to get one review",)
@api_view(['GET'])
def TaskReviewsApiById(request, TaskReviewId=""):
    try:
        if request.method == 'GET': 
            taskReview = TaskReviews.objects.get(
                    TaskReviewId=TaskReviewId)
            taskReviewSerializer = TaskReviewsSerializer(
                    taskReview)
            return JsonResponse(taskReviewSerializer.data, safe=False)
        elif request.method == 'DELETE':
            taskReview = TaskReviews.objects.get(TaskReviewId=TaskReviewId)
            taskReview.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)