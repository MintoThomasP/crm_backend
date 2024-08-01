from django.dispatch import receiver
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from app_default.views import retry
from app_login.models import Login
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from app_default.models import TaskStatus
from app_default.serializers import TaskStatusSerializer
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from app_report.views import durationCalculation, pointCalculation
from app_site.serializers import NotificationSerializer
from app_staff.models import Staff
from datetime import datetime, time, timedelta
from app_staff.serializers import StaffSerializer
from rest_framework.pagination import PageNumberPagination
from app_project.models import CommentFile, Comments, Project, ProjectTask, ProjectTaskFile, ProjectTaskTiming, TaskReviews
from app_project.serializers import CommentFileSerializer, CommentsSerializer, ProjectSerializer, ProjectTaskFileSerializer, ProjectTaskSerializer, ProjectTaskTimingSerializer,  SaveProjectTaskFileSerializer, TaskReviewsSerializer, UploadProjectTaskFileSerializer
from dateutil.relativedelta import relativedelta
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from django.utils import timezone
from datetime import datetime

from rest_framework import generics
from django.db.models import Q

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 40 # Adjust the page size as needed
    page_size_query_param = 'page_size'

@csrf_exempt
@swagger_auto_schema(method='POST', request_body=ProjectSerializer)
@swagger_auto_schema(method='PUT', request_body=ProjectSerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all Project Details",)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
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
@retry(retries=3, delay=2)
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
    
class ProjectApiByCompanyId(generics.ListAPIView):
    queryset =Project.objects.all()
    pagination_class = CustomPageNumberPagination
    serializer_class = ProjectSerializer 
    def post(self, request, *args, **kwargs):
        filterData = JSONParser().parse(request)
        Keyword = filterData.get('SearchKeyword', '')
        if filterData['CompanyId']:
            self.queryset = self.queryset.filter(CompanyId=filterData['CompanyId'])

        if Keyword:
            self.queryset = self.queryset.filter(Q(ProjectName__icontains=Keyword)|Q(Description__icontains=Keyword))
        page = self.paginate_queryset(self.queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give CompanyId to get all project detail",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def ProjectByCompanyId(request, CompanyId=""):
    try:
        if request.method == 'GET': 
            project = Project.objects.filter(
                    CompanyId=CompanyId)
            projectSerializer = ProjectSerializer(
                    project,many=True)
            return JsonResponse(projectSerializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    

# class CustomPageNumberPagination(PageNumberPagination):

#     page_size = 40 # Adjust the page size as needed
#     page_size_query_param = 'page_size'


# class ProjectTaskPagination(generics.ListAPIView):
#     pagination_class = CustomPageNumberPagination
#     serializer_class = ProjectTaskSerializer 
#     def get(self, request, *args, **kwargs):
#         projectTask = ProjectTask.objects.filter(Q(RefId__isnull=True) | Q(RefId=""),TaskType='Task').order_by('-SortId')
#         projectTaskSerializer = ProjectTaskSerializer(
#                     projectTask, many=True)
#         page = self.paginate_queryset(projectTaskSerializer.data)
#         taskData=[]
#         if page is not None:
#             for row in page:
#                 row['Tickets']=[]
#                 try:
#                     projectTask = ProjectTask.objects.get(
#                         RefId=row['ProjectTaskId'])
#                     projectTaskSerializer=ProjectTaskSerializer(projectTask)
#                     row['Tickets']=projectTaskSerializer.data
#                 except:
#                     row['Tickets']=[]
                
#                 try:
#                     project=Project.objects.get(ProjectId=row['ProjectId'])
#                     projectSerializer=ProjectSerializer(project)
#                     row['ProjectName']=projectSerializer.data['ProjectName']
#                 except:
#                     row['ProjectName']=""
#                 try:
#                     staff=Staff.objects.get(StaffId=row['TaskAssignedTo'])
#                     staffSerializer=StaffSerializer(staff)
#                     row['AssignedTo']=staffSerializer.data['StaffName']
#                 except:
#                     row['AssignedTo']=""

#                 try:
#                     staff=Staff.objects.get(StaffId=row['TaskAssignedBy'])
#                     staffSerializer=StaffSerializer(staff)
#                     row['AssignedBy']=staffSerializer.data['StaffName']
#                 except:
#                     row['AssignedBy']=""


#                 try:
#                     staff=Staff.objects.get(StaffId=row['VerifiedBy'])
#                     staffSerializer=StaffSerializer(staff)
#                     row['VerifiedByName']=staffSerializer.data['StaffName']
#                 except:
#                     row['VerifiedByName']= ""
#                 try:
#                     taskStatus=TaskStatus.objects.get(StatusId=row['Status'])
#                     taskStatusSerializer=TaskStatusSerializer(taskStatus)
#                     row['StatusName']=taskStatusSerializer.data['Status']
#                 except:
#                     row['StatusName']=""


#                 try:
#                     projectTaskFile = ProjectTaskFile.objects.filter(ProjectTaskId=row['ProjectTaskId'])
#                     projectTaskFileSerializer = ProjectTaskFileSerializer(projectTaskFile,many=True)
#                     row['ProjectTaskFiles']=projectTaskFileSerializer.data
#                 except:
#                     row['ProjectTaskFiles']=""

#                 taskData.append(row)
#             return self.get_paginated_response(taskData)

        # return JsonResponse(taskData, safe=False)




class ProjectTaskPagination(generics.ListAPIView):
    queryset =ProjectTask.objects.filter(Q(RefId__isnull=True) | Q(RefId=""),TaskType='Task').order_by('-SortId')
    pagination_class = CustomPageNumberPagination
    serializer_class = ProjectTaskSerializer 
    def post(self, request, *args, **kwargs):
        filterData = JSONParser().parse(request)
        Keyword = filterData.get('SearchKeyword', '')
        if filterData['TaskAssignedTo']:
            self.queryset = self.queryset.filter(TaskAssignedTo=filterData['TaskAssignedTo'])
        if filterData['TaskAssignedBy']:
            self.queryset = self.queryset.filter(TaskAssignedBy=filterData['TaskAssignedBy'])
        if filterData['ProjectId']:
            self.queryset = self.queryset.filter(ProjectId=filterData['ProjectId'])
        if Keyword:
                self.queryset = self.queryset.filter(Q(Title__icontains=Keyword)|Q(Description__icontains=Keyword))
        if filterData['CreatedDate']:
            created_date_str = filterData['CreatedDate']
            created_date = datetime.strptime(created_date_str, '%Y-%m-%d').date()
            self.queryset = self.queryset.filter(CreatedDate__startswith=created_date)
        if filterData['EndDate']:
            end_date_str = filterData['EndDate']
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            self.queryset = self.queryset.filter(EndDate__startswith=end_date)

            
        
        page = self.paginate_queryset(self.queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = []

            for row in serializer.data:
                row['Tickets']=[]
                try:
                    projectTask = ProjectTask.objects.filter(
                        RefId=row['ProjectTaskId'],TaskType='Ticket').order_by('-SortId').first()
                    projectTaskSerializer=ProjectTaskSerializer(projectTask, many=True)
                    row['Tickets']=projectTaskSerializer.data
                except:
                    row['Tickets']=[]
                try:
                    projectTask = ProjectTask.objects.filter(RefId=row['ProjectTaskId'],TaskType='Subtask').order_by('-SortId')
                    projectTaskSerializer = ProjectTaskSerializer(projectTask, many=True)
                    subTasks=[]
                    for subtask in projectTaskSerializer.data:
                        try:                      
                            taskStatus=TaskStatus.objects.get(StatusId=subtask['Status'])
                            taskStatusSerializer=TaskStatusSerializer(taskStatus)
                            subtask['StatusName']=taskStatusSerializer.data['Status']
                        except:
                            subtask['StatusName']=""
                        subTasks.append(subtask)

                    row['SubTask'] = subTasks
                except:
                    row['SubTask'] =[]
                
                try:
                    project=Project.objects.get(ProjectId=row['ProjectId'])
                    projectSerializer=ProjectSerializer(project)
                    row['ProjectName']=projectSerializer.data['ProjectName']
                except:
                    row['ProjectName']=""
                try:
                    staff=Staff.objects.get(StaffId=row['TaskAssignedTo'])
                    staffSerializer=StaffSerializer(staff)
                    row['AssignedTo']=staffSerializer.data['StaffName']
                except:
                    row['AssignedTo']=""

                try:
                    staff=Staff.objects.get(StaffId=row['TaskAssignedBy'])
                    staffSerializer=StaffSerializer(staff)
                    row['AssignedBy']=staffSerializer.data['StaffName']
                except:
                    row['AssignedBy']=""


                try:
                    staff=Staff.objects.get(StaffId=row['VerifiedBy'])
                    staffSerializer=StaffSerializer(staff)
                    row['VerifiedByName']=staffSerializer.data['StaffName']
                except:
                    row['VerifiedByName']= ""
                try:
                    taskStatus=TaskStatus.objects.get(StatusId=row['Status'])
                    taskStatusSerializer=TaskStatusSerializer(taskStatus)
                    row['StatusName']=taskStatusSerializer.data['Status']
                except:
                    row['StatusName']=""


                try:
                    projectTaskFile = ProjectTaskFile.objects.filter(ProjectTaskId=row['ProjectTaskId'])
                    projectTaskFileSerializer = ProjectTaskFileSerializer(projectTaskFile,many=True)
                    row['ProjectTaskFiles']=projectTaskFileSerializer.data
                except:
                    row['ProjectTaskFiles']=""

                data.append(row)
            return self.get_paginated_response(data)
        


# from django.db import transaction
@csrf_exempt
@api_view(['GET'])
def RestTaskPoint(request):
            projectTask = ProjectTask.objects.filter(TaskType="Task")
            projectTaskSerializer = ProjectTaskSerializer(
                    projectTask, many=True)
            success=0
            failed=0
            data_return=[]
            for projectTask in projectTaskSerializer.data:
                # if projectTask['TotalDuration'] is None:

                projectTaskTiming = ProjectTaskTiming.objects.filter(ProjectTaskId=projectTask['ProjectTaskId'])
                projectTaskTimingSerializer = ProjectTaskTimingSerializer(projectTaskTiming, many=True)
                total_duration_minutes = 0
                if len(projectTaskTimingSerializer.data):
                    for row in projectTaskTimingSerializer.data:

                        try:
                            date_format = '%Y-%m-%dT%H:%M:%S.%f'
                            start_date = datetime.strptime(row['StartDate'], date_format)
                            end_date = datetime.strptime(row['EndDate'], date_format)
                        except:
                            date_format = '%Y-%m-%dT%H:%M:%S.%f'
                            try:
                                start_date = datetime.strptime(projectTask['StartDate'], date_format)
                            except:
                                try:
                                    hours, minutes = map(int, projectTask['Duration'].split(':'))
                                except:
                                    projectTask['Duration']="0:10"
                                duration = timedelta(hours=1, minutes=0)
                                try:
                                    ScheduledDeadline = datetime.strptime(projectTask['ScheduledDeadline'], date_format)
                                    start_date = ScheduledDeadline + duration
                                except:
                                    ScheduledDeadline = datetime.strptime(projectTask['SortId'], date_format)
                                    start_date = ScheduledDeadline + duration
                                
                                formatted_datetime = start_date.strftime('%Y-%m-%dT%H:%M:%S%z')
                                projectTask['StartDate'] = formatted_datetime[:-2] + ':' + formatted_datetime[-2:]
                            try:
                                end_date = datetime.strptime(projectTask['EndDate'], date_format)
                            except:
                                hours, minutes = map(int, projectTask['Duration'].split(':'))
                                duration = timedelta(hours=1, minutes=0)
                                end_date = start_date + duration
                                formatted_datetime = end_date.strftime('%Y-%m-%dT%H:%M:%S%z')
                                projectTask['EndDate'] = formatted_datetime[:-2] + ':' + formatted_datetime[-2:]

                        total_time_taken = end_date - start_date
                        total_time_taken_in_seconds = total_time_taken.total_seconds()
                        total_time_taken_data = {
                            'hours': round(total_time_taken_in_seconds // 3600),
                            'minutes': round((total_time_taken_in_seconds % 3600) // 60)
                        }
                        duration = f"{total_time_taken_data['hours']}:{total_time_taken_data['minutes']}"
                        row['Duration'] = duration
                        # row.save()

                        hours, minutes = map(int, duration.split(':'))
                        total_duration_minutes += hours * 60 + minutes

                    total_duration_hours = total_duration_minutes // 60
                    total_duration_remaining_minutes = total_duration_minutes % 60
                    total_duration = f"{total_duration_hours}:{total_duration_remaining_minutes}"

                    projectTask['TotalDuration'] = total_duration
                else:
                        date_format = '%Y-%m-%dT%H:%M:%S.%f'
                        try:
                            start_date = datetime.strptime(projectTask['StartDate'], date_format)
                        except:
                            try:
                                hours, minutes = map(int, projectTask['Duration'].split(':'))
                            except:
                                projectTask['Duration']="0:10"
                            duration = timedelta(hours=1, minutes=0)
                            try:
                                ScheduledDeadline = datetime.strptime(projectTask['ScheduledDeadline'], date_format)
                                start_date = ScheduledDeadline + duration
                            except:
                                ScheduledDeadline = datetime.strptime(projectTask['SortId'], date_format)
                                start_date = ScheduledDeadline + duration
                            
                            formatted_datetime = start_date.strftime('%Y-%m-%dT%H:%M:%S%z')
                            projectTask['StartDate'] = formatted_datetime[:-2] + ':' + formatted_datetime[-2:]
                        try:
                            end_date = datetime.strptime(projectTask['EndDate'], date_format)
                        except:
                            hours, minutes = map(int, projectTask['Duration'].split(':'))
                            duration = timedelta(hours=1, minutes=0)
                            end_date = start_date + duration
                            formatted_datetime = end_date.strftime('%Y-%m-%dT%H:%M:%S%z')
                            projectTask['EndDate'] = formatted_datetime[:-2] + ':' + formatted_datetime[-2:]
                        total_time_taken = end_date - start_date
                        total_time_taken_in_seconds = total_time_taken.total_seconds()
                        total_time_taken_data = {
                            'hours': round(total_time_taken_in_seconds // 3600),
                            'minutes': round((total_time_taken_in_seconds % 3600) // 60)
                        }
                        duration = f"{total_time_taken_data['hours']}:{total_time_taken_data['minutes']}"
                        projectTask['TotalDuration'] = duration
                projectTask['CompletionPoint']=round(float(pointCalculation(projectTask)),2)
                projectTaskLive = ProjectTask.objects.get(
                    ProjectTaskId=projectTask['ProjectTaskId'])
                projectTaskSerializerLive = ProjectTaskSerializer(
                    projectTaskLive, data=projectTask)
                
                data_return.append(projectTask)
                # if projectTaskSerializerLive.is_valid():
                #     success=success+1
                #     projectTaskSerializerLive.save()
            
                # else:
                #     failed=failed+1

            return JsonResponse(data_return, safe=False)

# def RestTaskPoint(request):
#     BATCH_SIZE = 100  # Adjust batch size as needed

#     def calculate_total_duration(project_task):
#         date_format = '%Y-%m-%dT%H:%M:%S.%f'
#         try:
#             start_date = datetime.strptime(project_task['StartDate'], date_format)
#         except:
#             try:
#                 hours, minutes = map(int, project_task['Duration'].split(':'))
#             except:
#                 project_task['Duration'] = "0:10"
#             duration = timedelta(hours=1, minutes=0)
#             try:
#                 scheduled_deadline = datetime.strptime(project_task['ScheduledDeadline'], date_format)
#                 start_date = scheduled_deadline + duration
#             except:
#                 scheduled_deadline = datetime.strptime(project_task['SortId'], date_format)
#                 start_date = scheduled_deadline + duration

#             formatted_datetime = start_date.strftime('%Y-%m-%dT%H:%M:%S%z')
#             project_task['StartDate'] = formatted_datetime[:-2] + ':' + formatted_datetime[-2:]

#         try:
#             end_date = datetime.strptime(project_task['EndDate'], date_format)
#         except:
#             hours, minutes = map(int, project_task['Duration'].split(':'))
#             duration = timedelta(hours=1, minutes=0)
#             end_date = start_date + duration
#             formatted_datetime = end_date.strftime('%Y-%m-%dT%H:%M:%S%z')
#             project_task['EndDate'] = formatted_datetime[:-2] + ':' + formatted_datetime[-2:]

#         total_time_taken = end_date - start_date
#         total_time_taken_in_seconds = total_time_taken.total_seconds()
#         total_time_taken_data = {
#             'hours': round(total_time_taken_in_seconds // 3600),
#             'minutes': round((total_time_taken_in_seconds % 3600) // 60)
#         }
#         return f"{total_time_taken_data['hours']}:{total_time_taken_data['minutes']}"

#     project_tasks = ProjectTask.objects.all()
#     total_tasks = project_tasks.count()

#     for i in range(0, total_tasks, BATCH_SIZE):
#         with transaction.atomic():
#             batch_tasks = project_tasks[i:i+BATCH_SIZE]
#             project_task_serializer = ProjectTaskSerializer(batch_tasks, many=True)
#             for project_task in project_task_serializer.data:
#                 if project_task['TotalDuration'] is None:
#                     project_task_timing = ProjectTaskTiming.objects.filter(ProjectTaskId=project_task['ProjectTaskId'])
#                     project_task_timing_serializer = ProjectTaskTimingSerializer(project_task_timing, many=True)
#                     total_duration_minutes = 0
#                     if len(project_task_timing):
#                         for row in project_task_timing:
#                             try:
#                                 date_format = '%Y-%m-%dT%H:%M:%S.%f'
#                                 start_date = datetime.strptime(row.StartDate, date_format)
#                                 end_date = datetime.strptime(row.EndDate, date_format)
#                             except:
#                                 total_duration = calculate_total_duration(project_task)
#                                 start_date = datetime.strptime(project_task['StartDate'], date_format)
#                                 end_date = datetime.strptime(project_task['EndDate'], date_format)
#                             total_time_taken = end_date - start_date
#                             total_time_taken_in_seconds = total_time_taken.total_seconds()
#                             total_time_taken_data = {
#                                 'hours': round(total_time_taken_in_seconds // 3600),
#                                 'minutes': round((total_time_taken_in_seconds % 3600) // 60)
#                             }
#                             duration = f"{total_time_taken_data['hours']}:{total_time_taken_data['minutes']}"
#                             row.Duration = duration
#                             row.save()

#                             hours, minutes = map(int, duration.split(':'))
#                             total_duration_minutes += hours * 60 + minutes

#                         total_duration_hours = total_duration_minutes // 60
#                         total_duration_remaining_minutes = total_duration_minutes % 60
#                         total_duration = f"{total_duration_hours}:{total_duration_remaining_minutes}"

#                         project_task['TotalDuration'] = total_duration
#                     else:
#                         project_task['TotalDuration'] = calculate_total_duration(project_task)

#                 project_task['CompletionPoint'] = round(pointCalculation(project_task), 2)
#                 project_task_serializer = ProjectTaskSerializer(data=project_task)
#                 if project_task_serializer.is_valid():
#                     project_task_serializer.save()

#     return JsonResponse("taskData", safe=False)



@csrf_exempt
@swagger_auto_schema(method='POST', request_body=ProjectTaskSerializer)
@swagger_auto_schema(method='PUT', request_body=ProjectTaskSerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all ProjectTask Details",)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
def ProjectTaskApi(request):
    # try:
        if request.method == 'GET':
            projectTask = ProjectTask.objects.filter(Q(RefId__isnull=True) | Q(RefId=""),TaskType='Task').order_by('-SortId')
            projectTaskSerializer = ProjectTaskSerializer(
                    projectTask, many=True)
            taskData=[]
            for row in projectTaskSerializer.data:
                row['Tickets']=[]
                try:
                    projectTask = ProjectTask.objects.get(
                        RefId=row['ProjectTaskId'])
                    projectTaskSerializer=ProjectTaskSerializer(projectTask)
                    row['Tickets']=projectTaskSerializer.data
                except:
                    row['Tickets']=[]
                
                try:
                    project=Project.objects.get(ProjectId=row['ProjectId'])
                    projectSerializer=ProjectSerializer(project)
                    row['ProjectName']=projectSerializer.data['ProjectName']
                except:
                    row['ProjectName']=""
                try:
                    staff=Staff.objects.get(StaffId=row['TaskAssignedTo'])
                    staffSerializer=StaffSerializer(staff)
                    row['AssignedTo']=staffSerializer.data['StaffName']
                except:
                    row['AssignedTo']=""

                try:
                    staff=Staff.objects.get(StaffId=row['TaskAssignedBy'])
                    staffSerializer=StaffSerializer(staff)
                    row['AssignedBy']=staffSerializer.data['StaffName']
                except:
                    row['AssignedBy']=""


                try:
                    staff=Staff.objects.get(StaffId=row['VerifiedBy'])
                    staffSerializer=StaffSerializer(staff)
                    row['VerifiedByName']=staffSerializer.data['StaffName']
                except:
                    row['VerifiedByName']= ""
                try:
                    taskStatus=TaskStatus.objects.get(StatusId=row['Status'])
                    taskStatusSerializer=TaskStatusSerializer(taskStatus)
                    row['StatusName']=taskStatusSerializer.data['Status']
                except:
                    row['StatusName']=""


                try:
                    projectTaskFile = ProjectTaskFile.objects.filter(ProjectTaskId=row['ProjectTaskId'])
                    projectTaskFileSerializer = ProjectTaskFileSerializer(projectTaskFile,many=True)
                    row['ProjectTaskFiles']=projectTaskFileSerializer.data
                except:
                    row['ProjectTaskFiles']=""

                taskData.append(row)

            return JsonResponse(taskData, safe=False)
        elif request.method == 'POST':
            projectTaskData = JSONParser().parse(request)
            projectTaskSerializer = ProjectTaskSerializer(
                data=projectTaskData)
            if projectTaskSerializer.is_valid():
                projectTaskSerializer.save()
                if projectTaskSerializer.data['TaskType']=="Task" or projectTaskSerializer.data['TaskType']=="Ticket":

                    login = Login.objects.get(UserId=projectTaskSerializer.data['TaskAssignedTo'])
                    if login.Token:
                        title="New task added"
                        if projectTaskSerializer.data['TaskType']=="Ticket":
                            title="New ticket raised"
                        sendNotification({
                            "title":title,
                            "body":projectTaskSerializer.data['Title'],
                            "token":login.Token,
                            "fromuser":projectTaskSerializer.data['TaskAssignedBy'],
                            "touser":projectTaskSerializer.data['TaskAssignedTo']
                        })


                return JsonResponse(projectTaskSerializer.data['ProjectTaskId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            projectTaskData = JSONParser().parse(request)
            projectTask = ProjectTask.objects.get(
                ProjectTaskId=projectTaskData['ProjectTaskId'])
            projectTaskSerializer = ProjectTaskSerializer(
                projectTask,data=projectTaskData)
            if projectTaskSerializer.is_valid():
                projectTaskSerializer.save()
                if projectTaskData['TaskType']!='Subtask':
                    if projectTaskData['Status']=='7' or  projectTaskData['Status']=='8' or  projectTaskData['Status']=='9' or projectTaskData['Status']==7 or  projectTaskData['Status']==8 or  projectTaskData['Status']==9:
                        projectTaskPoint = ProjectTask.objects.get(
                            ProjectTaskId=projectTaskData['ProjectTaskId'])
                        projectTaskPoint.CompletionPoint=pointCalculation(projectTaskSerializer.data)
                        projectTaskPoint.save()
                    if projectTaskSerializer.data['Status']=='3':
                        login = Login.objects.get(UserId=projectTaskSerializer.data['TaskAssignedBy'])
                        title="Need verification"
                        if projectTaskSerializer.data['TaskType']=="Ticket":
                            title="Ticket closed"
                        if login.Token :
                            sendNotification({
                                "title":title,
                                "body":projectTaskSerializer.data['Title'],
                                "token":login.Token,
                                "fromuser":projectTaskSerializer.data['TaskAssignedTo'],
                                "touser":projectTaskSerializer.data['TaskAssignedBy']
                            })
                    elif projectTaskSerializer.data['Status']=='4' or  projectTaskSerializer.data['Status']=='5' or  projectTaskSerializer.data['Status']=='6':
                        login = Login.objects.get(UserId=projectTaskSerializer.data['TaskAssignedTo'])
                        if login.Token :
                            sendNotification({
                                "title":"Not verified",
                                "body":projectTaskSerializer.data['Title'],
                                "token":login.Token,
                                "fromuser":projectTaskSerializer.data['TaskAssignedBy'],
                                "touser":projectTaskSerializer.data['TaskAssignedTo']

                            })
                    elif projectTaskSerializer.data['Status']=='7' or  projectTaskSerializer.data['Status']=='8' or  projectTaskSerializer.data['Status']=='9':
                    
                        login = Login.objects.get(UserId=projectTaskSerializer.data['TaskAssignedTo'])
                        if login.Token :
                            sendNotification({
                                "title":"Verified",
                                "body":projectTaskSerializer.data['Title'],
                                "token":login.Token,
                                "fromuser":projectTaskSerializer.data['TaskAssignedBy'],
                                "touser":projectTaskSerializer.data['TaskAssignedTo']
                            })

                return JsonResponse(projectTaskSerializer.data['ProjectTaskId'], safe=False)
            
            return JsonResponse("", safe=False)
        else:
            return JsonResponse("", safe=False)
    # except:
    #     return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give ProjectTaskId to get one task detail",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def ProjectTaskApiById(request, ProjectTaskId=""):
    # try:
        if request.method == 'GET': 
            projectTask = ProjectTask.objects.get(
                    ProjectTaskId=ProjectTaskId)
            projectTaskSerializer = ProjectTaskSerializer(
                    projectTask)
            ProjectTaskData=projectTaskSerializer.data
            try:
                projectSubTask = ProjectTask.objects.filter(RefId=ProjectTaskId).order_by('-SortId')
                projectSubTaskSerializer = ProjectTaskSerializer(projectSubTask, many=True)
                ProjectTaskData['SubTask'] = projectSubTaskSerializer.data
            except:
                ProjectTaskData['SubTask'] =[]
            try:
                taskStatus=TaskStatus.objects.get(StatusId=projectTaskSerializer.data['Status'])
                taskStatusSerializer=TaskStatusSerializer(taskStatus)
                ProjectTaskData['StatusName']=taskStatusSerializer.data['Status']
            except:
                ProjectTaskData['StatusName']=""
            ProjectTaskData['Tickets']=[]
            try:
                tickets = ProjectTask.objects.get(
                    RefId=ProjectTaskId)
                ticketSerializer=ProjectTaskSerializer(tickets)
                ProjectTaskData['Tickets']=ticketSerializer.data
            except:
                ProjectTaskData['Tickets']=[]

            try:
                project = Project.objects.get(ProjectId=projectTaskSerializer.data['ProjectId'])
                projectSerializer = ProjectSerializer(project)
                ProjectTaskData['ProjectName'] = projectSerializer.data['ProjectName']
            except:
                ProjectTaskData['ProjectName']=""
            try:
                staff = Staff.objects.get(StaffId=projectTaskSerializer.data['TaskAssignedBy'])
                staffSerializer = StaffSerializer(staff)
                ProjectTaskData['AssignedBy'] = staffSerializer.data['StaffName']
            except:
                ProjectTaskData['AssignedBy']=""
            
            try:
                staff = Staff.objects.get(StaffId=projectTaskSerializer.data['TaskAssignedTo'])
                staffSerializer = StaffSerializer(staff)
                ProjectTaskData['AssignedTo'] = staffSerializer.data['StaffName']
            except:
                ProjectTaskData['AssignedTo']=""


            try:
                staff=Staff.objects.get(StaffId=projectTaskSerializer.data['VerifiedBy'])
                staffSerializer=StaffSerializer(staff)
                ProjectTaskData['VerifiedByName']=staffSerializer.data['StaffName']
            except:
                ProjectTaskData['VerifiedByName']= ""
            try:
                projectTaskFile = ProjectTaskFile.objects.filter(ProjectTaskId=projectTaskSerializer.data['ProjectTaskId'])
                projectTaskFileSerializer = ProjectTaskFileSerializer(projectTaskFile,many=True)
                ProjectTaskData['ProjectTaskFiles']=projectTaskFileSerializer.data
            except:
                ProjectTaskData['ProjectTaskFiles']=""
            try:
                comment=Comments.objects.filter(ProjectTaskId=ProjectTaskId).order_by('SortId')
                commentSerializer = CommentsSerializer(comment,many=True)
                commentData=[]
                for fileSer in commentSerializer.data:
                    commentFile = CommentFile.objects.filter(CommentId=fileSer['CommentId'])
                    commentFileSerializer = CommentFileSerializer(commentFile,many=True)
                    fileSer['CommentFiles']=commentFileSerializer.data
                    commentData.append(fileSer)
                ProjectTaskData['Comments']=commentData

            except:
                ProjectTaskData['Comments']=[]
            return JsonResponse(ProjectTaskData, safe=False)
        elif request.method == 'DELETE':
            projectTask = ProjectTask.objects.get(ProjectTaskId=ProjectTaskId)
            try:
                ProjectTask.objects.filter(RefId=ProjectTaskId,TaskType='Subtask').delete()
            except:
                p=""
            try:
                ProjectTaskTiming.objects.filter(ProjectTaskId=ProjectTaskId).delete()
            except:
                p=""
            try:
                taskFile=ProjectTaskFile.objects.filter(ProjectTaskId=ProjectTaskId)
                for row in taskFile:
                    ProjectTaskFile.objects.get(
                        ProjectTaskFileId=row['ProjectTaskFileId']).TaskFile.delete(save=True)
                    row.delete()
            except:
                p=""
            try:
                TaskReviews.objects.filter(ProjectTaskId=ProjectTaskId).delete()
            except:
                p=""
            try:
                Comments.objects.filter(ProjectTaskId=ProjectTaskId).delete()
            except:
                p=""
            projectTask.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    # except:
    #     return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give ProjectId to get task detail",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def ProjectTaskApiByProjectId(request, ProjectId=""):
    try:
        if request.method == 'GET': 
            projectTask = ProjectTask.objects.filter(
                    ProjectId=ProjectId).order_by('-SortId')
            projectTaskSerializer = ProjectTaskSerializer(
                    projectTask,many=True)
            taskStatusName=[]
            for row in projectTaskSerializer.data:
                try:
                    projectsubTask = ProjectTask.objects.filter(RefId=row['ProjectTaskId']).order_by('-SortId')
                    projectsubTaskSerializer = ProjectTaskSerializer(projectsubTask, many=True)
                    row['SubTask'] = projectsubTaskSerializer.data
                except:
                    row['SubTask'] =[]
                try:
                    taskStatus=TaskStatus.objects.get(StatusId=row['Status'])
                    taskStatusSerializer=TaskStatusSerializer(taskStatus)
                    row['StatusName']=taskStatusSerializer.data['Status']
                except:
                    row['StatusName']=""

                try:
                    project = Project.objects.get(ProjectId=row['ProjectId'])
                    projectSerializer = ProjectSerializer(project)
                    row['ProjectName'] = projectSerializer.data['ProjectName']
                except:
                    row['ProjectName'] = ""
                try:
                    staff=Staff.objects.get(StaffId=row['VerifiedBy'])
                    staffSerializer=StaffSerializer(staff)
                    row['VerifiedByName']=staffSerializer.data['StaffName']
                except:
                    row['VerifiedByName']= ""
                
                try:
                    projectTaskFile = ProjectTaskFile.objects.filter(ProjectTaskId=row['ProjectTaskId'])
                    projectTaskFileSerializer = ProjectTaskFileSerializer(projectTaskFile,many=True)
                    row['ProjectTaskFiles']=projectTaskFileSerializer.data
                except:
                    row['ProjectTaskFiles']=""

                staff = Staff.objects.get(StaffId=row['TaskAssignedTo'])
                staffSerializer = StaffSerializer(staff)
                row['StaffName'] = staffSerializer.data['StaffName']
                taskStatusName.append(row)
            return JsonResponse(taskStatusName, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    


@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Get projecttask by staff",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def ProjectTaskApiByUserId(request, TaskAssignedTo=""):
    try:
        if request.method == 'GET': 
            projectTask = ProjectTask.objects.filter(
        Q(TaskAssignedTo=TaskAssignedTo) & 
        Q(TaskType='Task') | 
        (Q(TaskType='Ticket') & Q(TaskAssignedTo=TaskAssignedTo) & (Q(Status='2') | Q(Status='1')))
    ).order_by('-SortId')
           
            projectTaskSerializer = ProjectTaskSerializer(
                    projectTask,many=True)
            taskStatusName=[]
            for row in projectTaskSerializer.data:
                
                try:
                    projectTask = ProjectTask.objects.filter(RefId=row['ProjectTaskId']).order_by('-SortId')
                    projectTaskSerializer = ProjectTaskSerializer(projectTask, many=True)
                    subTasks=[]
                    for subtask in projectTaskSerializer.data:
                        try:                      
                            taskStatus=TaskStatus.objects.get(StatusId=subtask['Status'])
                            taskStatusSerializer=TaskStatusSerializer(taskStatus)
                            subtask['StatusName']=taskStatusSerializer.data['Status']
                        except:
                            subtask['StatusName']=""
                        subTasks.append(subtask)

                    row['SubTask'] = subTasks
                except:
                    row['SubTask'] =[]

                row['Tickets']=[]
                try:
                    projectTask = ProjectTask.objects.filter(
                        RefId=row['ProjectTaskId']).order_by('-SortId')
                    projectTaskSerializer=ProjectTaskSerializer(projectTask,many=True)
                    row['Tickets']=projectTaskSerializer.data[0]
                except:
                    row['Tickets']=[]
  
                try:                      
                    taskStatus=TaskStatus.objects.get(StatusId=row['Status'])
                    taskStatusSerializer=TaskStatusSerializer(taskStatus)
                    row['StatusName']=taskStatusSerializer.data['Status']
                except:
                    row['StatusName']=""

                try:
                    project = Project.objects.get(ProjectId=row['ProjectId'])
                    projectSerializer = ProjectSerializer(project)
                    row['ProjectName'] = projectSerializer.data['ProjectName']
                except:
                    row['ProjectName'] = ""
                try:
                    staff = Staff.objects.get(StaffId=row['TaskAssignedTo'])
                    staffSerializer = StaffSerializer(staff)
                    row['StaffName'] = staffSerializer.data['StaffName']
                except:
                    row['StaffName'] =""
                try:
                    staff = Staff.objects.get(StaffId=row['TaskAssignedBy'])
                    staffSerializer = StaffSerializer(staff)
                    row['TaskAssignedByName'] = staffSerializer.data['StaffName']
                except:
                    row['TaskAssignedByName'] =""


                try:
                    staff=Staff.objects.get(StaffId=row['VerifiedBy'])
                    staffSerializer=StaffSerializer(staff)
                    row['VerifiedByName']=staffSerializer.data['StaffName']
                except:
                    row['VerifiedByName']= ""
                try:
                    projectTaskFile = ProjectTaskFile.objects.filter(ProjectTaskId=row['ProjectTaskId'])
                    projectTaskFileSerializer = ProjectTaskFileSerializer(projectTaskFile,many=True)
                    row['ProjectTaskFiles']=projectTaskFileSerializer.data
                except:
                    row['ProjectTaskFiles']=""
                
                
                taskStatusName.append(row)
          

            return JsonResponse(taskStatusName, safe=False)
            
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    


@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Get projecttask by staff",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def ProjectTaskApiByTaskAssignedBy(request, TaskAssignedBy=""):
    try:
        if request.method == 'GET': 
            projectTask = ProjectTask.objects.filter(TaskAssignedBy=TaskAssignedBy,TaskType='Task').order_by('-SortId')
            projectTaskSerializer = ProjectTaskSerializer(projectTask, many=True)
            taskStatusName = []
            for row in projectTaskSerializer.data:
                
                try:
                    projectTask = ProjectTask.objects.filter(RefId=row['ProjectTaskId']).order_by('-SortId')
                    projectTaskSerializer = ProjectTaskSerializer(projectTask, many=True)
                    subTasks=[]
                    for subtask in projectTaskSerializer.data:
                        try:                      
                            taskStatus=TaskStatus.objects.get(StatusId=subtask['Status'])
                            taskStatusSerializer=TaskStatusSerializer(taskStatus)
                            subtask['StatusName']=taskStatusSerializer.data['Status']
                        except:
                            subtask['StatusName']=""
                        subTasks.append(subtask)

                    row['SubTask'] = subTasks
                except:
                    row['SubTask'] =[]
                try:
                    taskStatus = TaskStatus.objects.get(StatusId=row['Status'])
                    taskStatusSerializer = TaskStatusSerializer(taskStatus)
                    row['StatusName'] = taskStatusSerializer.data['Status']
                except:
                    row['StatusName'] =""

                try:
                    project = Project.objects.get(ProjectId=row['ProjectId'])
                    projectSerializer = ProjectSerializer(project)
                    row['ProjectName'] = projectSerializer.data['ProjectName']
                except:
                    row['ProjectName'] = ""
                try:
                    staff = Staff.objects.get(StaffId=row['TaskAssignedTo'])
                    staffSerializer = StaffSerializer(staff)
                    row['StaffName'] = staffSerializer.data['StaffName']
                except:
                    row['StaffName'] =[]
                try:
                    staff=Staff.objects.get(StaffId=row['VerifiedBy'])
                    staffSerializer=StaffSerializer(staff)
                    row['VerifiedByName']=staffSerializer.data['StaffName']
                except:
                    row['VerifiedByName']= ""
                
                try:
                    projectTaskFile = ProjectTaskFile.objects.filter(ProjectTaskId=row['ProjectTaskId'])
                    projectTaskFileSerializer = ProjectTaskFileSerializer(projectTaskFile,many=True)
                    row['ProjectTaskFiles']=projectTaskFileSerializer.data
                except:
                    row['ProjectTaskFiles']=""

                taskStatusName.append(row)

            return JsonResponse(taskStatusName, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)

    

@csrf_exempt
@swagger_auto_schema(method='POST',request_body=ProjectTaskSerializer,operation_description="Give ProjectId and TaskAssignedTo in payload",)
@api_view(['POST'])
@retry(retries=3, delay=2)
def ProjectTaskApiByUserIdAndProjectId(request):
    try:
        if request.method == 'POST':
            projectTaskData = JSONParser().parse(request)
            projectTask = ProjectTask.objects.filter(
                    ProjectId=projectTaskData['ProjectId'],TaskAssignedTo=projectTaskData['TaskAssignedTo']).order_by('-SortId')
            projectTaskSerializer = ProjectTaskSerializer(
                    projectTask,many=True)
            taskStatusName=[]
            for row in projectTaskSerializer.data:
                row['Tickets']=[]
                try:
                    projectTask = ProjectTask.objects.filter(RefId=row['ProjectTaskId']).order_by('-SortId')
                    projectTaskSerializer = ProjectTaskSerializer(projectTask, many=True)
                    row['SubTask'] = projectTaskSerializer.data
                except:
                    row['SubTask'] =[]
                try:
                    projectTask = ProjectTask.objects.get(
                        RefId=row['ProjectTaskId'])
                    projectTaskSerializer=ProjectTaskSerializer(projectTask)
                    row['Tickets']=projectTaskSerializer.data
                except:
                    row['Tickets']=[]
                try:
                    taskStatus=TaskStatus.objects.get(StatusId=row['Status'])
                    taskStatusSerializer=TaskStatusSerializer(taskStatus)
                    row['StatusName']=taskStatusSerializer.data['Status']
                except:
                    row['StatusName']=""
 
                try:
                    project = Project.objects.get(ProjectId=row['ProjectId'])
                    projectSerializer = ProjectSerializer(project)
                    row['ProjectName'] = projectSerializer.data['ProjectName']
                except:
                    row['ProjectName'] = ""
                staff = Staff.objects.get(StaffId=row['TaskAssignedTo'])
                staffSerializer = StaffSerializer(staff)
                row['StaffName'] = staffSerializer.data['StaffName']
                try:
                    staff=Staff.objects.get(StaffId=row['VerifiedBy'])
                    staffSerializer=StaffSerializer(staff)
                    row['VerifiedByName']=staffSerializer.data['StaffName']
                except:
                    row['VerifiedByName']= ""
 
                try:
                    projectTaskFile = ProjectTaskFile.objects.filter(ProjectTaskId=row['ProjectTaskId'])
                    projectTaskFileSerializer = ProjectTaskFileSerializer(projectTaskFile,many=True)
                    row['ProjectTaskFiles']=projectTaskFileSerializer.data
                except:
                    row['ProjectTaskFiles']=""
                taskStatusName.append(row)
            return JsonResponse(taskStatusName, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)



@csrf_exempt
@swagger_auto_schema(method='POST',request_body=ProjectTaskSerializer,operation_description="Give ProjectId and TaskAssignedTo in payload",)
@api_view(['POST'])
@retry(retries=3, delay=2)
def ProjectTaskApiByTaskAssignedByAndProjectId(request):
    try:
        if request.method == 'POST': 
            projectTaskData = JSONParser().parse(request)
            projectTask = ProjectTask.objects.filter(
                    ProjectId=projectTaskData['ProjectId'],TaskAssignedBy=projectTaskData['TaskAssignedBy']).order_by('-SortId')
            projectTaskSerializer = ProjectTaskSerializer(
                    projectTask,many=True)
            taskData=[]
            for row in projectTaskSerializer.data:
                try:
                    projectTask = ProjectTask.objects.filter(RefId=row['ProjectTaskId']).order_by('-SortId')
                    projectTaskSerializer = ProjectTaskSerializer(projectTask, many=True)
                    row['SubTask'] = projectTaskSerializer.data
                except:
                    row['SubTask'] =[]
                try:
                    taskStatus=TaskStatus.objects.get(StatusId=row['Status'])
                    taskStatusSerializer=TaskStatusSerializer(taskStatus)
                    row['StatusName']=taskStatusSerializer.data['Status']
                except:
                    row['StatusName']=""

                try:
                    project = Project.objects.get(ProjectId=row['ProjectId'])
                    projectSerializer = ProjectSerializer(project)
                    row['ProjectName'] = projectSerializer.data['ProjectName']
                except:
                    row['ProjectName']=""
                try:
                    staff = Staff.objects.get(StaffId=row['TaskAssignedBy'])
                    staffSerializer = StaffSerializer(staff)
                    row['StaffName'] = staffSerializer.data['StaffName']
                except:
                    row['StaffName']=""


                try:
                    staff=Staff.objects.get(StaffId=row['VerifiedBy'])
                    staffSerializer=StaffSerializer(staff)
                    row['VerifiedByName']=staffSerializer.data['StaffName']
                except:
                    row['VerifiedByName']= ""
                try:
                    projectTaskFile = ProjectTaskFile.objects.filter(ProjectTaskId=row['ProjectTaskId'])
                    projectTaskFileSerializer = ProjectTaskFileSerializer(projectTaskFile,many=True)
                    row['ProjectTaskFiles']=projectTaskFileSerializer.data
                except:
                    row['ProjectTaskFiles']=""

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
@retry(retries=3, delay=2)
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
@retry(retries=3, delay=2)
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
    

    
@csrf_exempt
@api_view(['POST'])
@retry(retries=3, delay=2)
def GetAllTasksStatus(request):
    try:
        if request.method == 'POST':
            Statusdata = JSONParser().parse(request)
            projectTask = ProjectTask.objects.filter(Status=Statusdata['StatusId']).order_by('-SortId')
            projectTaskSerializer = ProjectTaskSerializer(
                        projectTask,many=True)
            return JsonResponse(projectTaskSerializer.data, safe=False)
        else:
                return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
        



@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all project Task file",)
@swagger_auto_schema(method='PUT', request_body=SaveProjectTaskFileSerializer)
@swagger_auto_schema(method='POST', request_body=SaveProjectTaskFileSerializer)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
def ProjectTaskFileApi(request, pk=""):
    try:
        if request.method == 'GET':
            projectTaskFile = ProjectTaskFile.objects.all()
            projectTaskFileSerializer = ProjectTaskFileSerializer(
                projectTaskFile,many=True)
            return JsonResponse(projectTaskFileSerializer.data, safe=False)
        elif request.method == 'POST':
            projectTaskFile = JSONParser().parse(request)
            projectTaskFileSerializer = SaveProjectTaskFileSerializer(
                data=projectTaskFile)
            if projectTaskFileSerializer.is_valid():
                projectTaskFileSerializer.save()
                return JsonResponse(projectTaskFileSerializer.data['ProjectTaskFileId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            projectTaskFiledata = JSONParser().parse(request)
            projectTaskFile = ProjectTaskFile.objects.get(
                ProjectTaskFileId=projectTaskFiledata['ProjectTaskFileId'])
            projectTaskFileSerializer = SaveProjectTaskFileSerializer(
                projectTaskFile, data=projectTaskFiledata)
            if projectTaskFileSerializer.is_valid():
                projectTaskFileSerializer.save()
                return JsonResponse(projectTaskFileSerializer.data['ProjectTaskFileId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def CURDprojectTaskFileApiById(request, ProjectTaskFileId=""):
    try:
        if request.method == 'GET':
            projectTaskFile = ProjectTaskFile.objects.get(
                ProjectTaskFileId=ProjectTaskFileId)
            projectTaskFileSerializer = ProjectTaskFileSerializer(
                projectTaskFile)
            return JsonResponse(projectTaskFileSerializer.data, safe=False)
        elif request.method == 'DELETE':
            projectTaskFile = ProjectTaskFile.objects.get(ProjectTaskFileId=ProjectTaskFileId)
            ProjectTaskFile.objects.get(ProjectTaskFileId=ProjectTaskFileId).TaskFile.delete(save=True)
            projectTaskFile.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    


class UploadProjectTaskFile(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, ProjectTaskFileId="", *args, **kwargs):
        try:

                projectTaskFile = ProjectTaskFile.objects.get(
                    ProjectTaskFileId=ProjectTaskFileId)
                try:
                    ProjectTaskFile.objects.get(
                        ProjectTaskFileId=ProjectTaskFileId).TaskFile.delete(save=True)
                except:
                    p = ""
                Serializer = UploadProjectTaskFileSerializer(
                    projectTaskFile, data=request.data)
                if Serializer.is_valid():
                    Serializer.save()
                    return JsonResponse("ok", safe=False)
                else:
                    return JsonResponse("", safe=False)
        except:
            return JsonResponse("", safe=False)
        


@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all project Task file",)
@swagger_auto_schema(method='PUT', request_body=CommentsSerializer)
@swagger_auto_schema(method='POST', request_body=CommentsSerializer)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
def CommentApi(request, pk=""):
    # try:
        if request.method == 'GET':
            comment = Comments.objects.all()
            commentSerializer = CommentsSerializer(
                comment,many=True)
            return JsonResponse(commentSerializer.data, safe=False)
        elif request.method == 'POST':
            comment = JSONParser().parse(request)
            commentSerializer = CommentsSerializer(
                data=comment)
           
            if commentSerializer.is_valid():
                commentSerializer.save()
                task = ProjectTask.objects.get(ProjectTaskId=commentSerializer.data['ProjectTaskId'])
                try:
                    if comment['ShowNotification']:
                        if task.TaskAssignedBy != commentSerializer.data['CommentedBy'] and task.TaskAssignedTo == commentSerializer.data['CommentedBy']:
                            login = Login.objects.get(UserId=task.TaskAssignedBy)
                            if login.Token :
                                sendNotification({
                                    "title":"Comments",
                                    "body":commentSerializer.data['Comment'],
                                    "token":login.Token,
                                    "fromuser":commentSerializer.data['CommentedBy'],
                                    "touser":task.TaskAssignedBy
                                })
                        if task.TaskAssignedBy == commentSerializer.data['CommentedBy'] and task.TaskAssignedTo != commentSerializer.data['CommentedBy']:
                            login = Login.objects.get(UserId=task.TaskAssignedTo)
                            if login.Token :
                                sendNotification({
                                    "title":"Comments",
                                    "body":commentSerializer.data['Comment'],
                                    "token":login.Token,
                                    "fromuser":commentSerializer.data['CommentedBy'],
                                    "touser":task.TaskAssignedTo
                                })
                except:
                    p=""
               
                return JsonResponse(commentSerializer.data['CommentId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            commentdata = JSONParser().parse(request)
            comment = Comments.objects.get(
                CommentId=commentdata['CommentId'])
            commentSerializer = CommentsSerializer(
                comment, data=commentdata)
            if commentSerializer.is_valid():
                commentSerializer.save()
                return JsonResponse(commentSerializer.data['CommentId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    # except:
    #     return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def CURDCommentApiById(request, CommentId=""):
    try:
        if request.method == 'GET':
            comment = Comments.objects.get(
                CommentId=CommentId)
            commentSerializer = CommentsSerializer(
                comment)
            return JsonResponse(commentSerializer.data, safe=False)
        elif request.method == 'DELETE':
            comment = Comments.objects.get(CommentId=CommentId)
            comment.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    


@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all project Task file",)
@swagger_auto_schema(method='PUT', request_body=CommentFileSerializer)
@swagger_auto_schema(method='POST', request_body=CommentFileSerializer)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
def CommentFileApi(request, pk=""):
    try:
        if request.method == 'GET':
            commentFile = CommentFile.objects.all()
            commentFileSerializer = CommentFileSerializer(
                commentFile,many=True)
            return JsonResponse(commentFileSerializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def CURDCommentFileApiById(request, CommentFileId=""):
    try:
        if request.method == 'GET':
            commentFile = CommentFile.objects.get(
                CommentFileId=CommentFileId)
            commentFileSerializer = CommentFileSerializer(
                commentFile)
            return JsonResponse(commentFileSerializer.data, safe=False)
        elif request.method == 'DELETE':
            commentFile = CommentFile.objects.get(CommentFileId=CommentFileId)
            commentFile.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    


class UploadCommentFile(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request,  *args, **kwargs):
        try:
                Serializer = CommentFileSerializer(
                    data=request.data)
                if Serializer.is_valid():
                    Serializer.save()
                    return JsonResponse(Serializer.data['CommentFileId'], safe=False)
                else:
                    return JsonResponse("", safe=False)
        except:
            return JsonResponse("", safe=False)
        






@api_view(['POST'])
@retry(retries=3, delay=2)
def ProjectTaskApiFilteringforTaskAssignedTo(request,):
    try:
        if request.method == 'POST': 
            taskData = JSONParser().parse(request)
            if taskData['CreatedDate'] and taskData['Status']  and taskData['ProjectId']:
                CreatedDate = timezone.datetime.strptime(taskData['CreatedDate'], '%Y-%m-%d').date()
                projectTask = ProjectTask.objects.filter(
                        CreatedDate=CreatedDate,Status=taskData['Status'],TaskAssignedTo=taskData['TaskAssignedTo'],ProjectId=taskData['ProjectId']).order_by('-SortId')
            elif taskData['CreatedDate'] and taskData['Status']:
                CreatedDate = timezone.datetime.strptime(taskData['CreatedDate'], '%Y-%m-%d').date()
                projectTask = ProjectTask.objects.filter(
                        CreatedDate=CreatedDate,Status=taskData['Status'],TaskAssignedTo=taskData['TaskAssignedTo']).order_by('-SortId')
            elif taskData['CreatedDate'] and taskData['ProjectId']:
                CreatedDate = timezone.datetime.strptime(taskData['CreatedDate'], '%Y-%m-%d').date()
                projectTask = ProjectTask.objects.filter(
                        CreatedDate=CreatedDate,ProjectId=taskData['ProjectId'],TaskAssignedTo=taskData['TaskAssignedTo']).order_by('-SortId')
            elif taskData['Status']  and taskData['ProjectId']:
                projectTask = ProjectTask.objects.filter(
                        Status=taskData['Status'],TaskAssignedTo=taskData['TaskAssignedTo'],ProjectId=taskData['ProjectId']).order_by('-SortId')
            elif taskData['CreatedDate']:
                CreatedDate = timezone.datetime.strptime(CreatedDate, '%Y-%m-%d').date()
                projectTask = ProjectTask.objects.filter(
                        CreatedDate=CreatedDate,TaskAssignedTo=taskData['TaskAssignedTo']).order_by('-SortId')
            elif taskData['Status']:
                projectTask = ProjectTask.objects.filter(
                        Status=taskData['Status'],TaskAssignedTo=taskData['TaskAssignedTo']).order_by('-SortId')
            elif taskData['ProjectId']:
                projectTask = ProjectTask.objects.filter(
                        ProjectId=taskData['ProjectId'],TaskAssignedTo=taskData['TaskAssignedTo']).order_by('-SortId')
            else:
                projectTask = ProjectTask.objects.filter(TaskAssignedTo=taskData['TaskAssignedTo']).order_by('-SortId')
            projectTaskSerializer = ProjectTaskSerializer(
                    projectTask,many=True)
            taskStatusName=[]
            for row in projectTaskSerializer.data:
                # try:
                #     if row['TotalDuration']:
                #         Duration = row['Duration']
                #         duration_seconds=durationCalculation(Duration)
                #         TotalDuration = row['TotalDuration']
                #         TotalDuration_seconds=durationCalculation(TotalDuration)
                #         point = row['TaskPoint']
                #         row['CompletedPoint'] += round(pointCalculation(duration_seconds, TotalDuration_seconds, point),2)
                #         # row['CompletedPoint'] += round((row['TaskPoint']) - point, 2)
                        

                #     # if row['StartDate'] and row['EndDate']:
                #     #     try:
                #     #         date_format = '%m/%d/%Y, %I:%M:%S %p' 
                #     #         start_date = datetime.strptime(row['StartDate'], date_format)
                #     #         end_date = datetime.strptime(row['EndDate'], date_format)
                #     #     except:
                #     #         date_format = '%d/%m/%Y, %I:%M:%S %p'
                #     #         start_date = datetime.strptime(row['StartDate'], date_format)
                #     #         end_date = datetime.strptime(row['EndDate'], date_format)

                #     #     try:
                #     #         duration_parts = row['Duration'].split(':')
                #     #         hours = int(duration_parts[0])*60
                #     #         minutes = int(duration_parts[1])
                #     #         duration_min=hours + minutes
                #     #         duration_seconds=duration_min*60
                #     #     except:
                #     #         duration_seconds=3600
                #     #     total_time_taken_seconds = (end_date - start_date).total_seconds()
                #     #     if total_time_taken_seconds > duration_seconds:
                #     #         value1 = (total_time_taken_seconds / duration_seconds) * 100
                #     #         value_percentage = value1-100
                #     #         point=(row['TaskPoint']*value_percentage)/100
                #     #         row['CompletedPoint'] = round(row['TaskPoint'] - point)
                #     #     else:
                #     #         row['CompletedPoint'] = row['TaskPoint']
                # except:
                #     row['CompletedPoint']=""
                try:                     
                    taskStatus=TaskStatus.objects.get(StatusId=row['Status'])
                    taskStatusSerializer=TaskStatusSerializer(taskStatus)
                    row['StatusName']=taskStatusSerializer.data['Status']
                except:
                    row['StatusName']=""

                try:
                    project = Project.objects.get(ProjectId=row['ProjectId'])
                    projectSerializer = ProjectSerializer(project)
                    row['ProjectName'] = projectSerializer.data['ProjectName']
                except:
                    row['ProjectName'] = ""
                staff = Staff.objects.get(StaffId=row['TaskAssignedTo'])
                staffSerializer = StaffSerializer(staff)
                row['StaffName'] = staffSerializer.data['StaffName']

                try:
                    staff=Staff.objects.get(StaffId=row['VerifiedBy'])
                    staffSerializer=StaffSerializer(staff)
                    row['VerifiedByName']=staffSerializer.data['StaffName']
                except:
                    row['VerifiedByName']= ""
                try:
                    projectTaskFile = ProjectTaskFile.objects.filter(ProjectTaskId=row['ProjectTaskId'])
                    projectTaskFileSerializer = ProjectTaskFileSerializer(projectTaskFile,many=True)
                    row['ProjectTaskFiles']=projectTaskFileSerializer.data
                except:
                    row['ProjectTaskFiles']=""
                
                
                taskStatusName.append(row)
            return JsonResponse(taskStatusName, safe=False)
            
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    





@csrf_exempt
@api_view(['POST'])
@retry(retries=3, delay=2)
def ProjectTaskApiFilteringforTaskAssignedBy(request,):
    try:
        if request.method == 'POST': 
            taskData = JSONParser().parse(request)
            if taskData['CreatedDate'] and taskData['Status']  and taskData['ProjectId']:
                CreatedDate = timezone.datetime.strptime(taskData['CreatedDate'], '%Y-%m-%d').date()
                projectTask = ProjectTask.objects.filter(
                        CreatedDate=CreatedDate,Status=taskData['Status'],TaskAssignedBy=taskData['TaskAssignedBy'],ProjectId=taskData['ProjectId']).order_by('-SortId')
            elif taskData['CreatedDate'] and taskData['Status']:
                CreatedDate = timezone.datetime.strptime(taskData['CreatedDate'], '%Y-%m-%d').date()
                projectTask = ProjectTask.objects.filter(
                        CreatedDate=CreatedDate,Status=taskData['Status'],TaskAssignedBy=taskData['TaskAssignedBy']).order_by('-SortId')
            elif taskData['CreatedDate'] and taskData['ProjectId']:
                CreatedDate = timezone.datetime.strptime(taskData['CreatedDate'], '%Y-%m-%d').date()
                projectTask = ProjectTask.objects.filter(
                        CreatedDate=CreatedDate,ProjectId=taskData['ProjectId'],TaskAssignedBy=taskData['TaskAssignedBy']).order_by('-SortId')
            elif taskData['Status']  and taskData['ProjectId']:
                projectTask = ProjectTask.objects.filter(
                        Status=taskData['Status'],TaskAssignedBy=taskData['TaskAssignedBy'],ProjectId=taskData['ProjectId']).order_by('-SortId')
            elif taskData['CreatedDate']:
                CreatedDate = timezone.datetime.strptime(CreatedDate, '%Y-%m-%d').date()
                projectTask = ProjectTask.objects.filter(
                        CreatedDate=CreatedDate,TaskAssignedBy=taskData['TaskAssignedBy']).order_by('-SortId')
            elif taskData['Status']:
                projectTask = ProjectTask.objects.filter(
                        Status=taskData['Status'],TaskAssignedBy=taskData['TaskAssignedBy']).order_by('-SortId')
            elif taskData['ProjectId']:
                projectTask = ProjectTask.objects.filter(
                        ProjectId=taskData['ProjectId'],TaskAssignedBy=taskData['TaskAssignedBy']).order_by('-SortId')
            else:
                projectTask = ProjectTask.objects.filter(TaskAssignedBy=taskData['TaskAssignedBy']).order_by('-SortId')
            projectTaskSerializer = ProjectTaskSerializer(projectTask,many=True)
            taskStatusName=[]
            for row in projectTaskSerializer.data:
                # try:
                #     if row['TotalDuration']:
                #         Duration = row['Duration']
                #         duration_seconds=durationCalculation(Duration)
                #         TotalDuration = row['TotalDuration']
                #         TotalDuration_seconds=durationCalculation(TotalDuration)
                #         point = row['TaskPoint']
                #         row['CompletedPoint'] += round(pointCalculation(duration_seconds, TotalDuration_seconds, point),2)
                #         # row['CompletedPoint'] += round((row['TaskPoint']) - point, 2)
                        

                    # if row['StartDate'] and row['EndDate']:
                    #     try:
                    #         date_format = '%m/%d/%Y, %I:%M:%S %p' 
                    #         start_date = datetime.strptime(row['StartDate'], date_format)
                    #         end_date = datetime.strptime(row['EndDate'], date_format)
                    #     except:
                    #         date_format = '%d/%m/%Y, %I:%M:%S %p'
                    #         start_date = datetime.strptime(row['StartDate'], date_format)
                    #         end_date = datetime.strptime(row['EndDate'], date_format)

                    #     try:
                    #         duration_parts = row['Duration'].split(':')
                    #         hours = int(duration_parts[0])*60
                    #         minutes = int(duration_parts[1])
                    #         duration_min=hours + minutes
                    #         duration_seconds=duration_min*60
                    #     except:
                    #         duration_seconds=3600
                    #     total_time_taken_seconds = (end_date - start_date).total_seconds()
                    #     if total_time_taken_seconds > duration_seconds:
                    #         value1 = (total_time_taken_seconds / duration_seconds) * 100
                    #         value_percentage = value1-100
                    #         point=(row['TaskPoint']*value_percentage)/100
                    #         row['CompletedPoint'] = round(row['TaskPoint'] - point)
                    #     else:
                    #         row['CompletedPoint'] = row['TaskPoint']
                # except:
                #     row['CompletedPoint']=""
                try:                        
                    taskStatus=TaskStatus.objects.get(StatusId=row['Status'])
                    taskStatusSerializer=TaskStatusSerializer(taskStatus)
                    row['StatusName']=taskStatusSerializer.data['Status']
                except:
                    row['StatusName']=""

                try:
                    project = Project.objects.get(ProjectId=row['ProjectId'])
                    projectSerializer = ProjectSerializer(project)
                    row['ProjectName'] = projectSerializer.data['ProjectName']
                except:
                    row['ProjectName'] = ""
                staff = Staff.objects.get(StaffId=row['TaskAssignedTo'])
                staffSerializer = StaffSerializer(staff)
                row['StaffName'] = staffSerializer.data['StaffName']

                try:
                    staff=Staff.objects.get(StaffId=row['VerifiedBy'])
                    staffSerializer=StaffSerializer(staff)
                    row['VerifiedByName']=staffSerializer.data['StaffName']
                except:
                    row['VerifiedByName']= ""
                try:
                    projectTaskFile = ProjectTaskFile.objects.filter(ProjectTaskId=row['ProjectTaskId'])
                    projectTaskFileSerializer = ProjectTaskFileSerializer(projectTaskFile,many=True)
                    row['ProjectTaskFiles']=projectTaskFileSerializer.data
                except:
                    row['ProjectTaskFiles']=""
                
                
                taskStatusName.append(row)
            return JsonResponse(taskStatusName, safe=False)
            
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    



@api_view(['POST'])
@retry(retries=3, delay=2)
def GetAllProjectTaskApiByFiltering(request):
    # try:
        if request.method == 'POST':
            taskData = JSONParser().parse(request)
           
            
            
            
            if taskData['CreatedDate'] and taskData['Status'] and taskData['TaskAssignedTo'] and taskData['ProjectId']:
                CreatedDate = timezone.datetime.strptime(taskData['CreatedDate'], '%Y-%m-%d').date()
                projectTask = ProjectTask.objects.filter(CreatedDate=CreatedDate,ProjectId=taskData['ProjectId'],Status=taskData['Status'],TaskAssignedTo=taskData['TaskAssignedTo']).order_by('-SortId')
            elif taskData['CreatedDate'] and taskData['Status'] and taskData['ProjectId']:
                CreatedDate = timezone.datetime.strptime(taskData['CreatedDate'], '%Y-%m-%d').date()
                projectTask = ProjectTask.objects.filter(CreatedDate=CreatedDate,Status=taskData['Status'],ProjectId=taskData['ProjectId']).order_by('-SortId')
            elif taskData['CreatedDate'] and  taskData['TaskAssignedTo'] and taskData['ProjectId']:
                CreatedDate = timezone.datetime.strptime(taskData['CreatedDate'], '%Y-%m-%d').date()
                projectTask = ProjectTask.objects.filter(CreatedDate=CreatedDate,TaskAssignedTo=taskData['TaskAssignedTo'],ProjectId=taskData['ProjectId']).order_by('-SortId')
            elif taskData['Status'] and  taskData['TaskAssignedTo'] and taskData['ProjectId']:
                projectTask = ProjectTask.objects.filter(Status=taskData['Status'],TaskAssignedTo=taskData['TaskAssignedTo'],ProjectId=taskData['ProjectId']).order_by('-SortId')
            elif taskData['CreatedDate'] and taskData['Status'] and taskData['TaskAssignedTo']:
                CreatedDate = timezone.datetime.strptime(taskData['CreatedDate'], '%Y-%m-%d').date()
                projectTask = ProjectTask.objects.filter(CreatedDate=CreatedDate,Status=taskData['Status'],TaskAssignedTo=taskData['TaskAssignedTo']).order_by('-SortId')
            elif taskData['CreatedDate'] and taskData['Status']:
                CreatedDate = timezone.datetime.strptime(taskData['CreatedDate'], '%Y-%m-%d').date()
                projectTask = ProjectTask.objects.filter(CreatedDate=CreatedDate,Status=taskData['Status']).order_by('-SortId')
            elif taskData['CreatedDate'] and  taskData['TaskAssignedTo']:
                CreatedDate = timezone.datetime.strptime(taskData['CreatedDate'], '%Y-%m-%d').date()
                projectTask = ProjectTask.objects.filter(CreatedDate=CreatedDate,TaskAssignedTo=taskData['TaskAssignedTo']).order_by('-SortId')
            elif taskData['CreatedDate'] and  taskData['ProjectId']:
                CreatedDate = timezone.datetime.strptime(taskData['CreatedDate'], '%Y-%m-%d').date()
                projectTask = ProjectTask.objects.filter(CreatedDate=CreatedDate,ProjectId=taskData['ProjectId']).order_by('-SortId')
            elif taskData['TaskAssignedTo'] and taskData['ProjectId']:
                projectTask = ProjectTask.objects.filter(TaskAssignedTo=taskData['TaskAssignedTo'],ProjectId=taskData['ProjectId']).order_by('-SortId')

            elif taskData['Status'] and  taskData['TaskAssignedTo']:
                projectTask = ProjectTask.objects.filter(Status=taskData['Status'],TaskAssignedTo=taskData['TaskAssignedTo']).order_by('-SortId')
            elif taskData['Status'] and  taskData['ProjectId']:
                projectTask = ProjectTask.objects.filter(Status=taskData['Status'],ProjectId=taskData['ProjectId']).order_by('-SortId')
            elif taskData['Status']:
                projectTask = ProjectTask.objects.filter(Status=taskData['Status']).order_by('-SortId')
            elif taskData['CreatedDate']:
                CreatedDate = timezone.datetime.strptime(taskData['CreatedDate'], '%Y-%m-%d').date()
                projectTask = ProjectTask.objects.filter(CreatedDate=CreatedDate).order_by('-SortId')
            elif taskData['TaskAssignedTo']:
                projectTask = ProjectTask.objects.filter(TaskAssignedTo=taskData['TaskAssignedTo']).order_by('-SortId')
            elif taskData['ProjectId']:
                projectTask = ProjectTask.objects.filter(ProjectId=taskData['ProjectId']).order_by('-SortId')
            else:
                projectTask = ProjectTask.objects.all().order_by('-SortId')
            projectTaskSerializer = ProjectTaskSerializer(
                    projectTask, many=True)
            taskData=[]
            for row in projectTaskSerializer.data:
                try:
                    project=Project.objects.get(ProjectId=row['ProjectId'])
                    projectSerializer=ProjectSerializer(project)
                    row['ProjectName']=projectSerializer.data['ProjectName']
                except:
                    row['ProjectName']=""
                try:
                    staff=Staff.objects.get(StaffId=row['TaskAssignedTo'])
                    staffSerializer=StaffSerializer(staff)
                    row['AssignedTo']=staffSerializer.data['StaffName']
                except:
                    row['AssignedTo']=""

                try:
                    staff=Staff.objects.get(StaffId=row['TaskAssignedBy'])
                    staffSerializer=StaffSerializer(staff)
                    row['AssignedBy']=staffSerializer.data['StaffName']
                except:
                    row['AssignedBy']=""


                try:
                    staff=Staff.objects.get(StaffId=row['VerifiedBy'])
                    staffSerializer=StaffSerializer(staff)
                    row['VerifiedByName']=staffSerializer.data['StaffName']
                except:
                    row['VerifiedByName']= ""
                try:
                    taskStatus=TaskStatus.objects.get(StatusId=row['Status'])
                    taskStatusSerializer=TaskStatusSerializer(taskStatus)
                    row['StatusName']=taskStatusSerializer.data['Status']
                except:
                    row['StatusName']=""


                try:
                    projectTaskFile = ProjectTaskFile.objects.filter(ProjectTaskId=row['ProjectTaskId'])
                    projectTaskFileSerializer = ProjectTaskFileSerializer(projectTaskFile,many=True)
                    row['ProjectTaskFiles']=projectTaskFileSerializer.data
                except:
                    row['ProjectTaskFiles']=""

                taskData.append(row)

            return JsonResponse(taskData, safe=False)
        else:
            return JsonResponse("", safe=False)
    # except:
    #     return JsonResponse("", safe=False)
        




@api_view(['GET'])
def schedule_repeated_tasks(request):
    
    retries = 3
    for _ in range(retries):
        try:
            now = timezone.now()
            repeated_tasks = ProjectTask.objects.filter(IsRepeated=True)
            projectTaskSerializer = ProjectTaskSerializer(
                    repeated_tasks, many=True)
            data=[]
            i=0
            for task in repeated_tasks:
                next_due_date = None
        
                if task.RepeatInterval == 'daily':
                    next_due_date = task.LastAssigned + timedelta(days=1)
                    
                elif task.RepeatInterval == 'weekly':
                    next_due_date = task.LastAssigned + timedelta(weeks=1)
                elif task.RepeatInterval == 'monthly':
                    next_due_date = task.LastAssigned + relativedelta(months=1)

                if next_due_date and now <= next_due_date:
                    scheduled_deadline = next_due_date.strftime("%Y-%m-%dT%H:%M")
                    new_task = {
                        "ProjectId":task.ProjectId,
                        "TaskAssignedTo":task.TaskAssignedTo,
                        "TaskAssignedBy":task.TaskAssignedBy,
                        "Title":task.Title,
                        "Description":task.Description,
                        "Duration":task.Duration,
                        "Status":1,
                        "CreatedDate":now.strftime("%Y-%m-%d"),
                        "ScheduledDeadline":scheduled_deadline,
                        "TaskPoint":task.TaskPoint,
                        "TaskType":task.TaskType,
                        "RefId":task.RefId,
                        "IsRepeated":task.IsRepeated,
                        'RepeatInterval':task.RepeatInterval,
                        "LastAssigned":now
                    }
                    new_taskserializer = ProjectTaskSerializer(data=new_task)
                
                    if new_taskserializer.is_valid():
                        new_taskserializer.save()
                        subtasks = ProjectTask.objects.filter(RefId=task.ProjectTaskId)
                        subtaskSerializer=ProjectTaskSerializer(subtasks,many=True)
                        for subtask in subtaskSerializer.data:
                            new_subtask_data = {
                                "ProjectId": subtask['ProjectId'],
                                "TaskAssignedTo": subtask['TaskAssignedTo'],
                                "TaskAssignedBy": subtask['TaskAssignedBy'],
                                "Title": subtask['Title'],
                                "Description": subtask['Description'],
                                "Status": 1,
                                "CreatedDate": now.strftime("%Y-%m-%d"),
                                "ScheduledDeadline": scheduled_deadline,
                                "TaskPoint": subtask['TaskPoint'],
                                "TaskType": subtask['TaskType'],
                                "RefId": new_taskserializer.data['ProjectTaskId']

                            }
                            new_subtaskserializer = ProjectTaskSerializer(data=new_subtask_data)
                            if new_subtaskserializer.is_valid():
                                new_subtaskserializer.save()
                            else:
                
                                print(new_subtaskserializer.errors)

                        i=i+1
                        data.append(new_taskserializer.data)
                    

            return JsonResponse({"message": "Repeated tasks scheduled successfully.","data":data,"projectTaskSerializer":projectTaskSerializer.data,"count":i},safe=False)
        except NotImplementedError as e:
            # time.sleep(1)
            return JsonResponse({"error": "NotImplementedError occurred"}, status=500)
        # except Exception as e:
        #     # logger.error("Error: %s", e)
        #     return JsonResponse({"error": str(e)}, status=500)


# from django_q.tasks import schedule
# from django_q.models import Schedule
# from datetime import timedelta
# from django.utils import timezone

# schedule('app_project.views.schedule_repeated_tasks', 
#          schedule_type=Schedule.MINUTES, 
#          minutes=2,  # Adjust as necessary
#          next_run=timezone.now() + timedelta(seconds=10))






import logging
from typing import Any, Dict
from uuid import uuid4
from django.conf import settings
from django.core.cache import cache
import firebase_admin
from firebase_admin import credentials, auth, firestore
from app_staff.models import Staff

cred = credentials.Certificate(settings.GOOGLE_APPLICATION_CREDENTIALS) # path to credentials.json file


firebase_app = firebase_admin.initialize_app(cred, name='app_project')


# auth_client = auth.Client(app=firebase_app)
# firestore_client = firestore.client(app=firebase_app)

# logger = logging.getLogger(__name__)


# def cached(func):
#     def wrapper(*args, **kwargs):
#         user = kwargs.get('user')
#         key = 'token_' + str(user.StaffId)
#         token = cache.get(key)
#         if token is None:
#             token = func(*args, **kwargs)
#             cache.set(key, token, timeout=60 * 60) # 1 hour
#         return token

#     return wrapper

# class FirebaseService:
#     @staticmethod
#     @cached
#     def get_custom_token_for_user(user: Staff):
#         auth_claims = {
#             'uid': user.StaffId,
#         }
#         return auth_client.create_custom_token(uid=user.StaffId, developer_claims=auth_claims)
  
#     @staticmethod
#     def send_notification_to_user(user: Staff, message: Dict[str, Any]):
#         msg_id = str(uuid4())
#         notification_ref = firestore_client.collection(u'app-notifications') \
#             .document(u'{}'.format(user.StaffId)).collection("user-notifications").document(u'{}'.format(msg_id))
      
#         notification_ref.set({
#             u'message': message,
#             'id': msg_id
#         })
#         logger.info(u'Notification sent to user {}'.format(user.StaffId))




from django.http import JsonResponse
from firebase_admin import messaging, initialize_app, credentials
import firebase_admin

# Initialize the Firebase app (you only need to do this once)
cred = credentials.Certificate(settings.GOOGLE_APPLICATION_CREDENTIALS)
initialize_app(cred)
@csrf_exempt
@api_view(['POST'])
def send_notification(request):
    notifyData = JSONParser().parse(request)
    
    sendNotification(notifyData)
    




    

def sendNotification(notifyData):

    token = notifyData['token']
    if not token:
        return JsonResponse({'error': 'Token is required'}, status=400)
    
    message = messaging.Message(
        notification=messaging.Notification(
            title=notifyData['title'],
            body=notifyData['body'],
        ),
        token=token,
    )

    try:
        response = messaging.send(message)
        notificationdata={
            "Title":notifyData['title'],
            "Message":notifyData['body'],
            "FromUser":notifyData['fromuser'],
            "ToUser":notifyData['touser'],
        }
        notificationSerializer = NotificationSerializer(
                    data=notificationdata)
        if notificationSerializer.is_valid():
            notificationSerializer.save()
        return JsonResponse({'message': 'Notification sent', 'response': response})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all project Task file",)
@swagger_auto_schema(method='PUT', request_body=ProjectTaskTimingSerializer)
@swagger_auto_schema(method='POST', request_body=ProjectTaskTimingSerializer)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
def ProjectTaskTimingApi(request, pk=""):
    # try:
        if request.method == 'GET':
            projectTaskTiming = ProjectTaskTiming.objects.all()
            projectTaskTimingSerializer = ProjectTaskTimingSerializer(
                projectTaskTiming,many=True)
            return JsonResponse(projectTaskTimingSerializer.data, safe=False)
        elif request.method == 'POST':
            projectTaskTiming = JSONParser().parse(request)
            projectTaskTimingSerializer = ProjectTaskTimingSerializer(
                data=projectTaskTiming)
            if projectTaskTimingSerializer.is_valid():
                projectTaskTimingSerializer.save()
                return JsonResponse(projectTaskTimingSerializer.data['ProjectTaskTimingId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            projectTaskTimingdata = JSONParser().parse(request)
            projectTaskTiming = ProjectTaskTiming.objects.get(
                ProjectTaskTimingId=projectTaskTimingdata['ProjectTaskTimingId'])
            projectTaskTimingSerializer = ProjectTaskTimingSerializer(
                projectTaskTiming, data=projectTaskTimingdata)
            if projectTaskTimingSerializer.is_valid():
                projectTaskTimingSerializer.save()
                ProjectTaskTimingId=projectTaskTimingSerializer.data['ProjectTaskTimingId']
                ProjectTaskTimingCalculationById(ProjectTaskTimingId)
                projectTask=ProjectTask.objects.get(ProjectTaskId=projectTaskTiming.ProjectTaskId)
                projectTask.EndDate = projectTaskTimingdata['EndDate']
                projectTask.save()

                return JsonResponse(projectTaskTimingSerializer.data['ProjectTaskTimingId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    # except:
    #     return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def CURDprojectTaskTimingApiById(request, ProjectTaskTimingId=""):
    try:
        if request.method == 'GET':
            projectTaskTiming = ProjectTaskTiming.objects.get(
                ProjectTaskTimingId=ProjectTaskTimingId)
            projectTaskTimingSerializer = ProjectTaskTimingSerializer(
                projectTaskTiming)
            return JsonResponse(projectTaskTimingSerializer.data, safe=False)
        elif request.method == 'DELETE':
            projectTaskTiming = ProjectTaskTiming.objects.get(ProjectTaskTimingId=ProjectTaskTimingId)
            projectTaskTiming.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def ProjectTaskTimingApiByProjectTaskId(request, ProjectTaskId=""):
    try:
        if request.method == 'GET':
            projectTaskTiming = ProjectTaskTiming.objects.filter(
                ProjectTaskId=ProjectTaskId)
            projectTaskTimingSerializer = ProjectTaskTimingSerializer(
                projectTaskTiming,many=True)
            return JsonResponse(projectTaskTimingSerializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def getLastTimmingByTaskId(request, ProjectTaskId=""):
    try:
        if request.method == 'GET':
            projectTaskTiming = ProjectTaskTiming.objects.filter( Q(Q(EndDate__isnull=True) | Q(EndDate='')) & Q(ProjectTaskId=ProjectTaskId))
            projectTaskTimingSerializer = ProjectTaskTimingSerializer(
                projectTaskTiming,many=True)
            return JsonResponse(projectTaskTimingSerializer.data[0], safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    


# def ProjectTaskTimingCalculationById(request, ProjectTaskId=""):
#     try:
#         if request.method == 'GET':
#             projectTaskTiming = ProjectTaskTiming.objects.filter(ProjectTaskId=ProjectTaskId)
#             projectTaskTimingSerializer = ProjectTaskTimingSerializer(projectTaskTiming, many=True)
#             total_duration_minutes = 0

#             for row in projectTaskTiming:
#                 try:
#                     date_format = '%m/%d/%Y, %I:%M:%S %p'
#                     start_date = datetime.strptime(row.StartDate, date_format)
#                     end_date = datetime.strptime(row.EndDate, date_format)
#                 except:
#                     date_format = '%d/%m/%Y, %I:%M:%S %p'
#                     start_date = datetime.strptime(row.StartDate, date_format)
#                     end_date = datetime.strptime(row.EndDate, date_format)

#                 total_time_taken = end_date - start_date
#                 total_time_taken_in_seconds = total_time_taken.total_seconds()
#                 total_time_taken_data = {
#                     'hours': round(total_time_taken_in_seconds // 3600),
#                     'minutes': round((total_time_taken_in_seconds % 3600) // 60)
#                 }
#                 duration = f"{total_time_taken_data['hours']}:{total_time_taken_data['minutes']}"
#                 row.Duration = duration
#                 row.save()

#                 hours, minutes = map(int, duration.split(':'))
#                 total_duration_minutes += hours * 60 + minutes

#             total_duration_hours = total_duration_minutes // 60
#             total_duration_remaining_minutes = total_duration_minutes % 60
#             total_duration = f"{total_duration_hours}:{total_duration_remaining_minutes}"

#             projectTask = ProjectTask.objects.get(ProjectTaskId=ProjectTaskId)
#             projectTask.TotalDuration = total_duration
#             projectTask.save()

#             return JsonResponse("Updated", safe=False)
#         else:
#             return JsonResponse("", safe=False)
#     except:
#         return JsonResponse("", safe=False)


def ProjectTaskTimingCalculationById(ProjectTaskTimingId=""):
        TaskTiming = ProjectTaskTiming.objects.get(ProjectTaskTimingId=ProjectTaskTimingId)
        projectTaskTiming = ProjectTaskTiming.objects.filter(ProjectTaskId=TaskTiming.ProjectTaskId)
        projectTaskTimingSerializer = ProjectTaskTimingSerializer(projectTaskTiming, many=True)
        total_duration_minutes = 0

        for row in projectTaskTiming:

            try:
                date_format = '%Y-%m-%dT%H:%M:%S%z'
                start_date = datetime.strptime(row.StartDate, date_format)
                end_date = datetime.strptime(row.EndDate, date_format)
            except:
                date_format = '%Y-%m-%dT%H:%M:%S%z'
                start_date = datetime.strptime(row.StartDate, date_format)
                end_date = datetime.strptime(row.EndDate, date_format)

            total_time_taken = end_date - start_date
            total_time_taken_in_seconds = total_time_taken.total_seconds()
            total_time_taken_data = {
                'hours': round(total_time_taken_in_seconds // 3600),
                'minutes': round((total_time_taken_in_seconds % 3600) // 60)
            }
            duration = f"{total_time_taken_data['hours']}:{total_time_taken_data['minutes']}"
            row.Duration = duration
            row.save()

            hours, minutes = map(int, duration.split(':'))
            total_duration_minutes += hours * 60 + minutes

        total_duration_hours = total_duration_minutes // 60
        total_duration_remaining_minutes = total_duration_minutes % 60
        total_duration = f"{total_duration_hours}:{total_duration_remaining_minutes}"

        projectTask = ProjectTask.objects.get(ProjectTaskId=TaskTiming.ProjectTaskId)
        projectTask.TotalDuration = total_duration
        projectTask.save()



    


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def ProjectTaskTotalDurationCalculation(request):
    if request.method == 'GET':
        projectTask = ProjectTask.objects.all()
        projectTaskTimingSerializer = ProjectTaskSerializer(projectTask, many=True)
        total_duration_minutes = 0

        for row in projectTask:
            if row.StartDate and row.EndDate:
                date_formats = [
                    '%m/%d/%Y, %I:%M:%S %p',  # Example: 04/07/2024, 10:06:38 AM
                    '%m/%d/%Y, %H:%M:%S',     # Example: 04/07/2024, 10:06:38
                    '%d/%m/%Y, %I:%M:%S %p',  # Example: 07/04/2024, 10:06:38 AM
                    '%d/%m/%Y, %H:%M:%S',     # Example: 07/04/2024, 10:06:38,
                    "%Y-%m-%dT%H:%M:%S%z"
                ]

                start_date = end_date = None
                for date_format in date_formats:
                    try:
                        start_date = datetime.strptime(row.StartDate, date_format)
                        end_date = datetime.strptime(row.EndDate, date_format)
                        break
                    except ValueError:
                        continue

                if start_date and end_date:
                    total_time_taken = end_date - start_date
                    total_time_taken_in_seconds = total_time_taken.total_seconds()
                    total_time_taken_data = {
                        'hours': int(total_time_taken_in_seconds // 3600),
                        'minutes': int((total_time_taken_in_seconds % 3600) // 60)
                    }
                    duration = f"{total_time_taken_data['hours']}:{total_time_taken_data['minutes']:02}"
                    row.TotalDuration = duration
                    row.save()

        return JsonResponse("Updated", safe=False)





class GetAllTicketsApi(generics.ListAPIView):
    queryset =ProjectTask.objects.filter(TaskType='Ticket').order_by('-SortId')
    pagination_class = CustomPageNumberPagination
    serializer_class = ProjectTaskSerializer 
    def post(self, request, *args, **kwargs):
        filterData = JSONParser().parse(request)
        Keyword = filterData.get('SearchKeyword', '')
        if filterData['TaskAssignedTo']:
            self.queryset = self.queryset.filter(TaskAssignedTo=filterData['TaskAssignedTo'])
        if filterData['TaskAssignedBy']:
            self.queryset = self.queryset.filter(TaskAssignedBy=filterData['TaskAssignedBy'])
        if filterData['ProjectId']:
            self.queryset = self.queryset.filter(ProjectId=filterData['ProjectId'])
        if filterData['Status']:
            self.queryset = self.queryset.filter(Status=filterData['Status'])
        if Keyword:
                self.queryset = self.queryset.filter(Q(Title__icontains=Keyword)|Q(Description__icontains=Keyword))
        if filterData['CreatedDate']:
            created_date_str = filterData['CreatedDate']
            created_date = datetime.strptime(created_date_str, '%Y-%m-%d').date()
            self.queryset = self.queryset.filter(CreatedDate__startswith=created_date)
       
        page = self.paginate_queryset(self.queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = []

            for row in serializer.data:
                row['Tickets']=[]
                try:
                    projectTask = ProjectTask.objects.get(
                        RefId=row['ProjectTaskId'])
                    projectTaskSerializer=ProjectTaskSerializer(projectTask)
                    row['Tickets']=projectTaskSerializer.data
                except:
                    row['Tickets']=[]
                try:
                    project=Project.objects.get(ProjectId=row['ProjectId'])
                    projectSerializer=ProjectSerializer(project)
                    row['ProjectName']=projectSerializer.data['ProjectName']
                except:
                    row['ProjectName']=""
                try:
                    staff=Staff.objects.get(StaffId=row['TaskAssignedTo'])
                    staffSerializer=StaffSerializer(staff)
                    row['AssignedTo']=staffSerializer.data['StaffName']
                except:
                    row['AssignedTo']=""

                try:
                    staff=Staff.objects.get(StaffId=row['TaskAssignedBy'])
                    staffSerializer=StaffSerializer(staff)
                    row['AssignedBy']=staffSerializer.data['StaffName']
                except:
                    row['AssignedBy']=""


                try:
                    staff=Staff.objects.get(StaffId=row['VerifiedBy'])
                    staffSerializer=StaffSerializer(staff)
                    row['VerifiedByName']=staffSerializer.data['StaffName']
                except:
                    row['VerifiedByName']= ""
                try:
                    taskStatus=TaskStatus.objects.get(StatusId=row['Status'])
                    taskStatusSerializer=TaskStatusSerializer(taskStatus)
                    row['StatusName']=taskStatusSerializer.data['Status']
                except:
                    row['StatusName']=""


                try:
                    projectTaskFile = ProjectTaskFile.objects.filter(ProjectTaskId=row['ProjectTaskId'])
                    projectTaskFileSerializer = ProjectTaskFileSerializer(projectTaskFile,many=True)
                    row['ProjectTaskFiles']=projectTaskFileSerializer.data
                except:
                    row['ProjectTaskFiles']=""

                data.append(row)
            

            return self.get_paginated_response(data)
        




@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Get projecttask by staff",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def TicketsByTaskAssignedTo(request, TaskAssignedTo=""):
    try:
        if request.method == 'GET': 
            projectTask = ProjectTask.objects.filter(
                    TaskAssignedTo=TaskAssignedTo,TaskType='Ticket').order_by('-SortId')
            projectTaskSerializer = ProjectTaskSerializer(
                    projectTask,many=True)
            taskStatusName=[]
            for row in projectTaskSerializer.data:
                row['Tickets']=[]
                try:
                    projectTask = ProjectTask.objects.filter(
                        RefId=row['ProjectTaskId']).order_by('-SortId')
                    projectTaskSerializer=ProjectTaskSerializer(projectTask,many=True)
                    row['Tickets']=projectTaskSerializer.data[0]
                except:
                    row['Tickets']=[]
                
                try:                      
                    taskStatus=TaskStatus.objects.get(StatusId=row['Status'])
                    taskStatusSerializer=TaskStatusSerializer(taskStatus)
                    row['StatusName']=taskStatusSerializer.data['Status']
                except:
                    row['StatusName']=""

                try:
                    project = Project.objects.get(ProjectId=row['ProjectId'])
                    projectSerializer = ProjectSerializer(project)
                    row['ProjectName'] = projectSerializer.data['ProjectName']
                except:
                    row['ProjectName'] = ""
                try:
                    staff = Staff.objects.get(StaffId=row['TaskAssignedTo'])
                    staffSerializer = StaffSerializer(staff)
                    row['StaffName'] = staffSerializer.data['StaffName']
                except:
                    row['StaffName'] =""
                try:
                    staff = Staff.objects.get(StaffId=row['TaskAssignedBy'])
                    staffSerializer = StaffSerializer(staff)
                    row['TaskAssignedByName'] = staffSerializer.data['StaffName']
                except:
                    row['TaskAssignedByName'] =""


                try:
                    staff=Staff.objects.get(StaffId=row['VerifiedBy'])
                    staffSerializer=StaffSerializer(staff)
                    row['VerifiedByName']=staffSerializer.data['StaffName']
                except:
                    row['VerifiedByName']= ""
                try:
                    projectTaskFile = ProjectTaskFile.objects.filter(ProjectTaskId=row['ProjectTaskId'])
                    projectTaskFileSerializer = ProjectTaskFileSerializer(projectTaskFile,many=True)
                    row['ProjectTaskFiles']=projectTaskFileSerializer.data
                except:
                    row['ProjectTaskFiles']=""
                
                
                taskStatusName.append(row)
            MediaViewData = []
            batch_size = 50
            for start in range(0, len(taskStatusName), batch_size):
                batch = taskStatusName[start:start + batch_size]
                for media in batch:
                    MediaViewData.append(media)

            return JsonResponse(MediaViewData, safe=False)
            
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    


@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Get projecttask by staff",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def TicketsByTaskAssignedBy(request, TaskAssignedBy=""):
    try:
        if request.method == 'GET': 
            projectTask = ProjectTask.objects.filter(
                    TaskAssignedBy=TaskAssignedBy,TaskType='Ticket').order_by('-SortId')
            projectTaskSerializer = ProjectTaskSerializer(
                    projectTask,many=True)
            taskStatusName=[]
            for row in projectTaskSerializer.data:
                row['Tickets']=[]
                try:
                    projectTask = ProjectTask.objects.filter(
                        RefId=row['ProjectTaskId']).order_by('-SortId')
                    projectTaskSerializer=ProjectTaskSerializer(projectTask,many=True)
                    row['Tickets']=projectTaskSerializer.data[0]
                except:
                    row['Tickets']=[]
                
                try:                      
                    taskStatus=TaskStatus.objects.get(StatusId=row['Status'])
                    taskStatusSerializer=TaskStatusSerializer(taskStatus)
                    row['StatusName']=taskStatusSerializer.data['Status']
                except:
                    row['StatusName']=""

                try:
                    project = Project.objects.get(ProjectId=row['ProjectId'])
                    projectSerializer = ProjectSerializer(project)
                    row['ProjectName'] = projectSerializer.data['ProjectName']
                except:
                    row['ProjectName'] = ""
                try:
                    staff = Staff.objects.get(StaffId=row['TaskAssignedTo'])
                    staffSerializer = StaffSerializer(staff)
                    row['StaffName'] = staffSerializer.data['StaffName']
                except:
                    row['StaffName'] =""
                try:
                    staff = Staff.objects.get(StaffId=row['TaskAssignedBy'])
                    staffSerializer = StaffSerializer(staff)
                    row['TaskAssignedByName'] = staffSerializer.data['StaffName']
                except:
                    row['TaskAssignedByName'] =""


                try:
                    staff=Staff.objects.get(StaffId=row['VerifiedBy'])
                    staffSerializer=StaffSerializer(staff)
                    row['VerifiedByName']=staffSerializer.data['StaffName']
                except:
                    row['VerifiedByName']= ""
                try:
                    projectTaskFile = ProjectTaskFile.objects.filter(ProjectTaskId=row['ProjectTaskId'])
                    projectTaskFileSerializer = ProjectTaskFileSerializer(projectTaskFile,many=True)
                    row['ProjectTaskFiles']=projectTaskFileSerializer.data
                except:
                    row['ProjectTaskFiles']=""
                
                
                taskStatusName.append(row)
            MediaViewData = []
            batch_size = 50
            for start in range(0, len(taskStatusName), batch_size):
                batch = taskStatusName[start:start + batch_size]
                for media in batch:
                    MediaViewData.append(media)

            return JsonResponse(MediaViewData, safe=False)
            
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give LoginHistoryId to get one loginHistory detail",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def UpdateEndDate(request):
    project_tasks = ProjectTask.objects.filter(Q(EndDate__isnull=True) | Q(EndDate=""))
    project_task_serializer = ProjectTaskSerializer(project_tasks, many=True)
    timing_data = []

    for row in project_task_serializer.data:
        if row['StartDate'] and row['Status'] != '1':
            task_timings = ProjectTaskTiming.objects.filter(ProjectTaskId=row['ProjectTaskId']).order_by('-SortId')
            if task_timings.exists():
                task_timings_serializer = ProjectTaskTimingSerializer(task_timings, many=True)
                end_date = task_timings_serializer.data[0]['EndDate']
                projectTask=ProjectTask.objects.get(ProjectTaskId=row['ProjectTaskId'])
                projectTask.EndDate=end_date
                projectTask.save()
    return JsonResponse("Updated", safe=False)



@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give LoginHistoryId to get one loginHistory detail",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def UpdateStatus(request):
    project_tasks = ProjectTask.objects.filter(Q(Status='8') | Q(Status='9'),TaskType='Task')
    project_task_serializer = ProjectTaskSerializer(project_tasks, many=True)
    timing_data = []

    for row in project_task_serializer.data:
        if row['StartDate'] and row['EndDate']:
            date_formats = [
                    '%m/%d/%Y, %I:%M:%S %p',  # Example: 04/07/2024, 10:06:38 AM
                    '%m/%d/%Y, %H:%M:%S',     # Example: 04/07/2024, 10:06:38
                    '%d/%m/%Y, %I:%M:%S %p',  # Example: 07/04/2024, 10:06:38 AM
                    '%d/%m/%Y, %H:%M:%S',      # Example: 07/04/2024, 10:06:38
                    "%Y-%m-%dT%H:%M:%S%z"
                ]

            end_date = scheduled_deadline = None
            for date_format in date_formats:
                try:
                    
                    end_date = datetime.strptime(row['EndDate'], date_format)
                    scheduled_deadline = datetime.strptime(row['ScheduledDeadline'], date_format)
                    break
                except ValueError:
                    continue
            if row['TotalDuration']:
               
                Duration = row['Duration']
                duration_seconds=durationCalculation(Duration)
                TotalDuration = row['TotalDuration']
                TotalDuration_seconds=durationCalculation(TotalDuration)

                    
            task = ProjectTask.objects.get(ProjectTaskId=row['ProjectTaskId'])
            if end_date and scheduled_deadline:

                if end_date < scheduled_deadline and TotalDuration_seconds < duration_seconds:
                    task.Status = '7'
                    task.save()
                elif end_date > scheduled_deadline:
                    task.Status = '8'
                    task.save()
                elif TotalDuration_seconds > scheduled_deadline:
                    task.Status = '9'
                    task.save()
    return JsonResponse("updated", safe=False)


    