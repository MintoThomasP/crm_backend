from django.dispatch import receiver
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from app_basic.models import TempleteType
from app_basic.serializers import TempleteTypeSerializer
from app_client.serializers import ClientVisitRegisterSerializer
from app_company.models import Company
from app_company.serializers import CompanySerializer
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
import logging
from typing import Any, Dict
from uuid import uuid4
from django.conf import settings
from django.core.cache import cache
import firebase_admin
from firebase_admin import credentials
from app_staff.models import Staff
from rest_framework import generics
from django.db.models import Q

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 40 # Adjust the page size as needed
    page_size_query_param = 'page_size'

@csrf_exempt
@swagger_auto_schema(method='POST', request_body=ProjectSerializer,operation_description="NOTE:API for save Project")
@swagger_auto_schema(method='PUT', request_body=ProjectSerializer,operation_description="NOTE:API for edit Project")
@swagger_auto_schema(method='GET',operation_description="NOTE:API for Get all Project Details by company id",)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
def ProjectApi(request,CompanyId=""):
    try:
        if request.method == 'GET':
            project = Project.objects.filter(CompanyId=CompanyId,ActiveStatus=1).order_by('-SortId')
            projectSerializer = ProjectSerializer(
                    project, many=True)
            
            projectData=[]
            for row in projectSerializer.data:
                projectTask=ProjectTask.objects.filter(ProjectId=row['ProjectId'],TaskType="Task")
                projectTaskSerializer=ProjectTaskSerializer(projectTask,many=True)
                work_status_count = {'Pending': 0, 'Completed': 0, 'Due': 0, 'Not Completed': 0, 'Finished': 0, 'Delay Finished': 0}
                current_date = str(date.today())
            
                for task in projectTaskSerializer.data:
                    if task['Status'] == '1' or task['Status'] == '2':
                        work_status_count['Pending'] += 1
                
                    if task['Status'] == '3':
                        work_status_count['Completed'] += 1
            
                    if task['CreatedDate'] < current_date and task['Status'] == '1':
                        work_status_count['Due'] += 1

                    if task['Status'] == '8' or task['Status'] == '9':
                        work_status_count['Delay Finished'] += 1

                    if task['Status'] == '4' or task['Status'] == '5' or task['Status'] == '6':
                        work_status_count['Not Completed'] += 1   

                    if task['Status'] == '7':
                        work_status_count['Finished'] += 1

                row['WorkStatusCount'] = work_status_count
                projectData.append(row)
            
                
            return JsonResponse(projectData, safe=False)
            
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
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get Project by ProjectId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete Project by ProjectId",)
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
            project.ActiveStatus=0
            project.save()

            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
class ProjectApiByCompanyId(generics.ListAPIView):
    queryset =Project.objects.filter(ActiveStatus=1).order_by('-SortId')
    pagination_class = CustomPageNumberPagination
    serializer_class = ProjectSerializer 
    def post(self, request, *args, **kwargs):
        try:
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
        except:
            return JsonResponse("", safe=False)

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get project by CompanyId",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def ProjectByCompanyId(request, CompanyId=""):
    try:
        if request.method == 'GET': 
            project = Project.objects.filter(
                    CompanyId=CompanyId,ActiveStatus=1)
            projectSerializer = ProjectSerializer(
                    project,many=True)
            return JsonResponse(projectSerializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    




from functools import reduce
import operator

class ProjectTaskPagination(generics.ListAPIView):
    queryset =ProjectTask.objects.filter(Q(RefId__isnull=True) | Q(RefId=""),TaskType='Task').order_by('-SortId')
    pagination_class = CustomPageNumberPagination
    serializer_class = ProjectTaskSerializer 
    def post(self, request, *args, **kwargs):
        # try:
            filterData = JSONParser().parse(request)
            Keyword = filterData.get('SearchKeyword', '')
            if len(filterData['TaskName']):
                self.queryset = self.queryset.filter(
                    reduce(operator.or_, (Q(Title__icontains=task_name) for task_name in filterData['TaskName']))
)
                self.queryset = self.queryset.filter(Title__icontains=filterData['TaskName'])
            if len(filterData['TaskAssignedTo']):
                self.queryset = self.queryset.filter(TaskAssignedTo__in=filterData['TaskAssignedTo'])
            if filterData['CompanyId']:
                project = Project.objects.filter(
                        CompanyId=filterData['CompanyId'],ActiveStatus=1)
                projectSerializer = ProjectSerializer(
                        project,many=True)
                projectId=[]
                for row in projectSerializer.data:
                    projectId.append(row['ProjectId'])
                self.queryset = self.queryset.filter(ProjectId__in=projectId)
            if len(filterData['Status']):
                status=filterData['Status']
                self.queryset = self.queryset.filter(Status__in=status)
            if len(filterData['TaskAssignedBy']):
                self.queryset = self.queryset.filter(TaskAssignedBy__in=filterData['TaskAssignedBy'])
            if len(filterData['ProjectId']):
                self.queryset = self.queryset.filter(ProjectId__in=filterData['ProjectId'])
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
                
                    try:
                        projectTask = ProjectTask.objects.filter(
                            RefId=row['ProjectTaskId'],TaskType='Ticket').order_by('-SortId')
                        projectTaskSerializer=ProjectTaskSerializer(projectTask, many=True)
                        row['Tickets']=projectTaskSerializer.data[0]
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
                        try:
                            staff=Staff.objects.get(StaffId=row['TaskAssignedBy'])
                            staffSerializer=StaffSerializer(staff)
                            row['AssignedBy']=staffSerializer.data['StaffName']
                        except:
                            company=Company.objects.get(CompanyId=row['TaskAssignedBy'])
                            companySerializer=CompanySerializer(company)
                            row['AssignedBy']=companySerializer.data['CompanyName']
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
        # except:
        #     return JsonResponse("", safe=False)
            



@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get Rest Task Point",)
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




@csrf_exempt
@swagger_auto_schema(method='POST', request_body=ProjectTaskSerializer,operation_description="NOTE: API for save ProjectTask")
@swagger_auto_schema(method='PUT', request_body=ProjectTaskSerializer,operation_description="NOTE: API for edit ProjectTask")
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all ProjectTask",)
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
                
                if projectTaskSerializer.data['IsRepeated'] == 1:
                    RepeatInterval=projectTaskSerializer.data['RepeatInterval']
                    Interval=projectTaskSerializer.data['Interval']
                    next_Scheduled_date=calculateNextScheduledDate(RepeatInterval,Interval,projectTaskData['ScheduledOn'])
                    
                    projectTask=ProjectTask.objects.get(ProjectTaskId=projectTaskSerializer.data['ProjectTaskId'])
                    projectTask.NextScheduledDate=next_Scheduled_date
                    projectTask.save()
                 
                if projectTaskSerializer.data['TaskType']=="Task" or projectTaskSerializer.data['TaskType']=="Ticket":
                    try:
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

                    except:
                        p=""

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
                if projectTaskSerializer.data['IsRepeated'] == 1:
                    RepeatInterval=projectTaskSerializer.data['RepeatInterval']
                    Interval=projectTaskSerializer.data['Interval']
                    next_Scheduled_date=calculateNextScheduledDate(RepeatInterval,Interval)
                    projectScheduleDate=ProjectTask.objects.get(ProjectTaskId=projectTaskData['ProjectTaskId'])
                    projectScheduleDate.NextScheduledDate=next_Scheduled_date
                    projectScheduleDate.save()
                if projectTaskSerializer.data['TaskType']!='Subtask' and projectTaskSerializer.data['TaskType']!='Ticket':
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
                    elif projectTaskSerializer.data['Status']=='7' or projectTaskSerializer.data['Status']=='8' or projectTaskSerializer.data['Status']=='9':
                        if projectTaskSerializer.data['ClientId']:
                            payload={
                                "ClientVisitRegisterId":"",
                                "ClientId":projectTaskSerializer.data['ClientId'],
                                "StaffId":projectTaskSerializer.data['TaskAssignedTo'],
                                "VisitedDate":projectTaskSerializer.data['EndDate'],
                                "Notes":"",
                            }
                            clientVisitRegisterSerializer = ClientVisitRegisterSerializer(
                                data=payload)
                            if clientVisitRegisterSerializer.is_valid():
                                clientVisitRegisterSerializer.save()
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
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get ProjectTask by ProjectTaskId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete ProjectTask by ProjectTaskId",)
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
                projectSubTask = ProjectTask.objects.filter(RefId=ProjectTaskId,TaskType='Subtask').order_by('-SortId')
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
                tickets = ProjectTask.objects.filter(
                    RefId=ProjectTaskId,TaskType='Ticket').order_by('-SortId')
                ticketSerializer=ProjectTaskSerializer(tickets,many=True)
                ProjectTaskData['Tickets']=ticketSerializer.data[0]
            except:
                ProjectTaskData['Tickets']=[]

            try:
                project = Project.objects.get(ProjectId=projectTaskSerializer.data['ProjectId'])
                projectSerializer = ProjectSerializer(project)
                ProjectTaskData['ProjectName'] = projectSerializer.data['ProjectName']
            except:
                ProjectTaskData['ProjectName']=""
            try:
                try:
                    staff = Staff.objects.get(StaffId=projectTaskSerializer.data['TaskAssignedBy'])
                    staffSerializer = StaffSerializer(staff)
                    ProjectTaskData['AssignedBy'] = staffSerializer.data['StaffName']
                except:
                    company = Company.objects.get(CompanyId=projectTaskSerializer.data['TaskAssignedBy'])
                    companySerializer = CompanySerializer(company)
                    ProjectTaskData['AssignedBy'] =companySerializer.data['CompanyName']
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
                projectTaskSerializer = ProjectTaskFileSerializer(
                    taskFile,many=True)
                for row in projectTaskSerializer.data:
                    project_task_file_obj = ProjectTaskFile.objects.get(ProjectTaskFileId=row['ProjectTaskFileId'])
                    project_task_file_obj.TaskFile.delete(save=True)
                    project_task_file_obj.delete()
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
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get ProjectTask by ProjectId",)
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
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get My Task",)
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
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get Task Assigned by me",)
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
@swagger_auto_schema(method='POST',request_body=ProjectTaskSerializer,operation_description="NOTE: API for get ProjectTask by TaskAssignedTo and ProjectId. paylaod { ProjectId, TaskAssignedTo}",)
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
@swagger_auto_schema(method='POST',request_body=ProjectTaskSerializer,operation_description="NOTE: API for get ProjectTask by ProjectId and TaskAssignedBy. payload { ProjectId,TaskAssignedBy}",)
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
@swagger_auto_schema(method='POST', request_body=TaskReviewsSerializer,operation_description="NOTE: API for save TaskReviews")
@swagger_auto_schema(method='PUT', request_body=TaskReviewsSerializer,operation_description="NOTE: API for edit TaskReviews")
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all task reviews")
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
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get TaskReviews by TaskReviewId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete TaskReviews by TaskReviewId",)
@api_view(['GET','DELETE'])
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
@swagger_auto_schema(method='POST',operation_description="NOTE: API for get all task by status. payload { StatusId}",)
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
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all project Task file",)
@swagger_auto_schema(method='PUT', request_body=SaveProjectTaskFileSerializer,operation_description="NOTE: API for edit ProjectTaskFile")
@swagger_auto_schema(method='POST', request_body=SaveProjectTaskFileSerializer,operation_description="NOTE: API for save ProjectTaskFile")
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
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get ProjectTaskFile by ProjectTaskFileId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete ProjectTaskFile by ProjectTaskFileId",)
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
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get all comments",)
@swagger_auto_schema(method='PUT', request_body=CommentsSerializer,operation_description="NOTE: API for edit comments")
@swagger_auto_schema(method='POST', request_body=CommentsSerializer,operation_description="NOTE: API for save comments")
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
def CommentApi(request, pk=""):
    try:
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
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get comments by CommentId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete comments by CommentId",)
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
@swagger_auto_schema(method='GET',operation_description="NOTE:API for Get all Comment File",)
@swagger_auto_schema(method='PUT', request_body=CommentFileSerializer,operation_description="NOTE:API for edit CommentFile")
@swagger_auto_schema(method='POST', request_body=CommentFileSerializer,operation_description="NOTE:API for save CommentFile")
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
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get CommentFile by CommentFileId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete CommentFile by CommentFileId",)
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
        





@swagger_auto_schema(method='POST',operation_description="NOTE: API for Filtering ProjectTask by TaskAssignedTo. payload {CreatedDate,Status,ProjectId,TaskAssignedTo }",)
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
@swagger_auto_schema(method='POST',operation_description="NOTE: API for Filtering ProjectTask by TaskAssignedBy. payload {CreatedDate,Status,ProjectId,TaskAssignedBy }",)
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
    


@swagger_auto_schema(method='POST',operation_description="NOTE: API for Filtering all ProjectTask. payload {CreatedDate,Status,ProjectId,TaskAssignedTo }",)
@api_view(['POST'])
@retry(retries=3, delay=2)
def GetAllProjectTaskApiByFiltering(request):
    try:
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
    except:
        return JsonResponse("", safe=False)
        




# @api_view(['GET'])
# def schedule_repeated_tasks(request):
    
#     retries = 3
#     for _ in range(retries):
#         try:
#             now = timezone.now()
#             repeated_tasks = ProjectTask.objects.filter(IsRepeated=True)
#             projectTaskSerializer = ProjectTaskSerializer(
#                     repeated_tasks, many=True)
#             data=[]
#             i=0
#             for task in repeated_tasks:
#                 next_due_date = None
        
#                 if task.RepeatInterval == 'daily':
#                     next_due_date = task.LastAssigned + timedelta(days=1)
                    
#                 elif task.RepeatInterval == 'weekly':
#                     next_due_date = task.LastAssigned + timedelta(weeks=1)
#                 elif task.RepeatInterval == 'monthly':
#                     next_due_date = task.LastAssigned + relativedelta(months=1)

#                 if next_due_date and now <= next_due_date:
#                     scheduled_deadline = next_due_date.strftime("%Y-%m-%dT%H:%M")
#                     new_task = {
#                         "ProjectId":task.ProjectId,
#                         "TaskAssignedTo":task.TaskAssignedTo,
#                         "TaskAssignedBy":task.TaskAssignedBy,
#                         "Title":task.Title,
#                         "Description":task.Description,
#                         "Duration":task.Duration,
#                         "Status":1,
#                         "CreatedDate":now.strftime("%Y-%m-%d"),
#                         "ScheduledDeadline":scheduled_deadline,
#                         "TaskPoint":task.TaskPoint,
#                         "TaskType":task.TaskType,
#                         "RefId":task.RefId,
#                         "IsRepeated":task.IsRepeated,
#                         'RepeatInterval':task.RepeatInterval,
#                         "LastAssigned":now
#                     }
#                     new_taskserializer = ProjectTaskSerializer(data=new_task)
                
#                     if new_taskserializer.is_valid():
#                         new_taskserializer.save()
#                         subtasks = ProjectTask.objects.filter(RefId=task.ProjectTaskId)
#                         subtaskSerializer=ProjectTaskSerializer(subtasks,many=True)
#                         for subtask in subtaskSerializer.data:
#                             new_subtask_data = {
#                                 "ProjectId": subtask['ProjectId'],
#                                 "TaskAssignedTo": subtask['TaskAssignedTo'],
#                                 "TaskAssignedBy": subtask['TaskAssignedBy'],
#                                 "Title": subtask['Title'],
#                                 "Description": subtask['Description'],
#                                 "Status": 1,
#                                 "CreatedDate": now.strftime("%Y-%m-%d"),
#                                 "ScheduledDeadline": scheduled_deadline,
#                                 "TaskPoint": subtask['TaskPoint'],
#                                 "TaskType": subtask['TaskType'],
#                                 "RefId": new_taskserializer.data['ProjectTaskId']

#                             }
#                             new_subtaskserializer = ProjectTaskSerializer(data=new_subtask_data)
#                             if new_subtaskserializer.is_valid():
#                                 new_subtaskserializer.save()
#                             else:
                
#                                 print(new_subtaskserializer.errors)

#                         i=i+1
#                         data.append(new_taskserializer.data)
                    

#             return JsonResponse({"message": "Repeated tasks scheduled successfully.","data":data,"projectTaskSerializer":projectTaskSerializer.data,"count":i},safe=False)
#         except NotImplementedError as e:
#             # time.sleep(1)
#             return JsonResponse({"error": "NotImplementedError occurred"}, status=500)
#         # except Exception as e:
#         #     # logger.error("Error: %s", e)
#         #     return JsonResponse({"error": str(e)}, status=500)



# from datetime import datetime
# import json
# from datetime import date
# @api_view(['GET'])
# def schedule_repeated_tasks(request):
    
#     retries = 3
#     for _ in range(retries):
#         try:
#             now = timezone.now()
#             repeated_tasks = ProjectTask.objects.filter(IsRepeated=True)
#             projectTaskSerializer = ProjectTaskSerializer(
#                     repeated_tasks, many=True)
#             data = []
#             i = 0
#             for task in repeated_tasks:
#                 given_date = datetime.now()
#                 day_of_week = int((given_date.weekday()+ 1))
              
#                 next_Schduled_date = None
#                 scheduled_deadline = None
#                 if task.RepeatInterval == 'daily':
#                     scheduled_days_str = task.ScheduledDays.strip('[] ') 
#                     ScheduledDays = list(map(int, scheduled_days_str.split(',')))
#                     if day_of_week in ScheduledDays:
#                         next_Schduled_date = now + timedelta(days=1)
#                         scheduled_deadline = now + timedelta(days=1)
#                         # next_Schduled_date = (timezone.now() + timedelta(days=1))
#                         # scheduled_deadline = now + timedelta(days=1)
#                         # next_Schduled_date = next_Schduled_date.date()
#                         # for day in ScheduledDays:
#                         #     n=1
#                         #     next_date = given_date + timedelta(days=n)
#                         #     next_day = next_date.weekday() + 1
#                         #     print(next_day,"next_day")
#                         #     n+1
#                         #     if day in ScheduledDays:
#                         #         next_Schduled_date =next_date
#                         #         print(next_Schduled_date)
                                
#                         #         break
                        
                    
#                 elif task.RepeatInterval == 'weekly':
#                     next_Schduled_date = task.LastAssigned + timedelta(weeks=1)
#                     scheduled_deadline = now + timedelta(weeks=1)
#                 elif task.RepeatInterval == 'monthly':
#                     # now=date.today()
#                     scheduled_days_str = task.ScheduledDays.strip('[] ') 
#                     ScheduledDays = list(map(int, scheduled_days_str.split(',')))
#                     month=int(given_date.strftime("%m"))
#                     day=given_date.strftime("%d")
#                     year=given_date.strftime("%Y")
#                     if month in ScheduledDays:
#                         createdDay=(task.SortId).strftime("%d")
#                         if createdDay == day:
#                             next_Schduled_date = date(year=int(year), month=int(month), day=int(day))
#                             next_Schduled_date = datetime.combine(next_Schduled_date, datetime.min.time())
#                             scheduled_deadline =  now + relativedelta(months=1)
#                             # next_Schduled_date=f"{year}-{month}-{day}"
#                             # next_Schduled_date = datetime.date(datetime.strptime(next_Schduled_date, '%Y-%m-%d'))
                           

                        
#                             # next_Schduled_date = task.LastAssigned + relativedelta(months=1)
#                             # scheduled_deadline = next_Schduled_date.strftime("%Y-%m-%dT%H:%M")
#                             # print(scheduled_deadline)
                
#                 if next_Schduled_date and now <= next_Schduled_date:
#                     # scheduled_deadline = timezone.now() + relativedelta(months=1)
                    
#                     new_task = {
#                         "ProjectId":task.ProjectId,
#                         "TaskAssignedTo":task.TaskAssignedTo,
#                         "TaskAssignedBy":task.TaskAssignedBy,
#                         "Title":task.Title,
#                         "Description":task.Description,
#                         "Duration":task.Duration,
#                         "Status":1,
#                         "CreatedDate":given_date.strftime("%Y-%m-%dT%H:%M:%S%z"),
#                         "ScheduledDeadline":scheduled_deadline.strftime("%Y-%m-%dT%H:%M"),
#                         "TaskPoint":task.TaskPoint,
#                         "TaskType":task.TaskType,
#                         "RefId":task.RefId,
#                         "LastAssigned":given_date,
#                         "ClientId":task.ClientId
#                     }
                    
#                     new_taskserializer = ProjectTaskSerializer(data=new_task)
                   
#                     if new_taskserializer.is_valid():
#                         new_taskserializer.save()
#                         subtasks = ProjectTask.objects.filter(RefId=task.ProjectTaskId)
#                         subtaskSerializer=ProjectTaskSerializer(subtasks,many=True)
#                         for subtask in subtaskSerializer.data:
#                             new_subtask_data = {
#                                 "ProjectId": subtask['ProjectId'],
#                                 "TaskAssignedTo": subtask['TaskAssignedTo'],
#                                 "TaskAssignedBy": subtask['TaskAssignedBy'],
#                                 "Title": subtask['Title'],
#                                 "Description": subtask['Description'],
#                                 "Status": 1,
#                                 "CreatedDate": given_date,
#                                 "ScheduledDeadline": scheduled_deadline,
#                                 "TaskPoint": subtask['TaskPoint'],
#                                 "TaskType": subtask['TaskType'],
#                                 "RefId": new_taskserializer.data['ProjectTaskId']

#                             }
#                             new_subtaskserializer = ProjectTaskSerializer(data=new_subtask_data)
#                             if new_subtaskserializer.is_valid():
#                                 new_subtaskserializer.save()
#                             else:
#                                 print(new_subtaskserializer.errors)

#                         i=i+1
#                         data.append(new_taskserializer.data)
                    

#             return JsonResponse({"message": "Repeated tasks scheduled successfully.","data":data,"projectTaskSerializer":projectTaskSerializer.data,"count":i},safe=False)
#         except NotImplementedError as e:
#             return JsonResponse({"error": "NotImplementedError occurred"}, status=500)
    

from datetime import datetime
import json
from datetime import date
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Auto schedule repeated task",)
@api_view(['GET'])
def schedule_repeated_tasks(request):
    
    retries = 3
    for _ in range(retries):
        try:
            now = timezone.now()
            repeated_tasks = ProjectTask.objects.filter(IsRepeated=True)
            projectTaskSerializer = ProjectTaskSerializer(
                    repeated_tasks, many=True)
         
            data = []
            i = 0
            for task in repeated_tasks:
                given_date = datetime.now()
                day_of_week = int((given_date.weekday()+ 1))
               
                next_Schduled_date = None
                scheduled_deadline = None
                
                currentDate=given_date.strftime("%Y-%m-%d")
                currentScheduledDate=task.NextScheduledDate.strftime("%Y-%m-%d")
               
                if task.RepeatInterval == 'daily' and currentDate == currentScheduledDate:
                    
                    interval=task.Interval
                    if day_of_week == 7:
                        interval=interval+1
                        next_Schduled_date = now + timedelta(days=interval)
                        
                        scheduled_deadline = next_Schduled_date + timedelta(days=interval)
                        
                    else:
                        next_Schduled_date = now + timedelta(days=interval)
                        scheduled_deadline = next_Schduled_date + timedelta(days=interval)
                        
                elif task.RepeatInterval == 'weekly' and currentDate == currentScheduledDate:
                    
                    interval=task.Interval
                    if day_of_week == 7:
                        interval=interval+1
                        next_Schduled_date = now + timedelta(weeks=interval)
                        scheduled_deadline = next_Schduled_date + timedelta(weeks=interval)
                    else:
                        next_Schduled_date = now + timedelta(weeks=interval)
                        scheduled_deadline = next_Schduled_date + timedelta(weeks=interval)
                        
                elif task.RepeatInterval == 'monthly' and currentDate == currentScheduledDate:
                 
                    interval=task.Interval
                    if day_of_week == 7:
                        interval=interval+1
                        next_Schduled_date = now + relativedelta(months=interval)
                        scheduled_deadline = next_Schduled_date + relativedelta(months=interval)
                    else:
                        next_Schduled_date = now + relativedelta(months=interval)
                        scheduled_deadline = next_Schduled_date + relativedelta(months=interval)
                        
                elif task.RepeatInterval == 'yearly' and currentDate == currentScheduledDate:
                    interval = task.Interval
                    if day_of_week == 7:
                        interval=interval+1
                        next_Schduled_date = now + relativedelta(years=interval)
                        scheduled_deadline = next_Schduled_date + relativedelta(years=interval)
                    else:
                        next_Schduled_date = now + relativedelta(years=interval)
                        scheduled_deadline = next_Schduled_date + relativedelta(years=interval)
   
                           
                
                if currentDate == currentScheduledDate and (task.RepeatInterval == 'daily' or task.RepeatInterval == 'weekly' or task.RepeatInterval == 'monthly'):
                  
                    new_task = {
                        "ProjectId":task.ProjectId,
                        "TaskAssignedTo":task.TaskAssignedTo,
                        "TaskAssignedBy":task.TaskAssignedBy,
                        "Title":task.Title,
                        "Description":task.Description,
                        "Duration":task.Duration,
                        "Status":1,
                        "CreatedDate":given_date.strftime("%Y-%m-%dT%H:%M:%S%z"),
                        "ScheduledDeadline":scheduled_deadline.strftime("%Y-%m-%dT%H:%M"),
                        "TaskPoint":task.TaskPoint,
                        "TaskType":task.TaskType,
                        "RefId":task.RefId,
                        "NextScheduledDate":next_Schduled_date,
                        "Interval":task.Interval,
                        "ClientId":task.ClientId,
                        "IsRepeated":True,
                        "RepeatInterval":task.RepeatInterval

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
                                "CreatedDate": given_date,
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
            return JsonResponse({"error": "NotImplementedError occurred"}, status=500)
        

        
# from django_q.tasks import schedule
# from django_q.models import Schedule
# from datetime import timedelta
# from django.utils import timezone

# schedule('app_project.views.schedule_repeated_tasks', 
#          schedule_type=Schedule.MINUTES, 
#          minutes=2,  # Adjust as necessary
#          next_run=timezone.now() + timedelta(seconds=10))








cred = credentials.Certificate(settings.GOOGLE_APPLICATION_CREDENTIALS) # path to credentials.json file


firebase_app = firebase_admin.initialize_app(cred, name='app_project')





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
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get all Project task timing")
@swagger_auto_schema(method='PUT', request_body=ProjectTaskTimingSerializer,operation_description="NOTE: API for save ProjectTaskTiming")
@swagger_auto_schema(method='POST', request_body=ProjectTaskTimingSerializer,operation_description="NOTE: API for edit ProjectTaskTiming")
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
def ProjectTaskTimingApi(request, pk=""):
    try:
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
                ProjectTaskId=projectTaskTimingSerializer.data['ProjectTaskId']
                ProjectTaskTimingCalculationById(ProjectTaskId)
                projectTask=ProjectTask.objects.get(ProjectTaskId=projectTaskTiming.ProjectTaskId)
                projectTask.EndDate = projectTaskTimingdata['EndDate']
                projectTask.save()

                return JsonResponse(projectTaskTimingSerializer.data['ProjectTaskTimingId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get ProjectTaskTiming by ProjectTaskTimingId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete ProjectTaskTiming by ProjectTaskTimingId",)
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
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get ProjectTaskTiming by ProjectTaskId",)
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
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get LastTiming of a task",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def getLastTimmingByTaskId(request, ProjectTaskId=""):
    try:
        if request.method == 'GET':
            projectTaskTiming = ProjectTaskTiming.objects.filter( Q(Q(EndDate__isnull=True) | Q(EndDate='')) & Q(ProjectTaskId=ProjectTaskId)).order_by('-SortId')
            projectTaskTimingSerializer = ProjectTaskTimingSerializer(
                projectTaskTiming,many=True)
            return JsonResponse(projectTaskTimingSerializer.data[0], safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    





def ProjectTaskTimingCalculationById(ProjectTaskId=""):
        # TaskTiming = ProjectTaskTiming.objects.get(ProjectTaskTimingId=ProjectTaskTimingId)
        projectTaskTiming = ProjectTaskTiming.objects.filter(ProjectTaskId=ProjectTaskId)
        projectTaskTimingSerializer = ProjectTaskTimingSerializer(projectTaskTiming, many=True)
        total_duration_minutes = 0
        for row in projectTaskTiming:
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

        projectTask = ProjectTask.objects.get(ProjectTaskId=ProjectTaskId)
        projectTask.TotalDuration = total_duration
        projectTask.save()



    


# @csrf_exempt
# @swagger_auto_schema(method='GET', operation_description="",)
# @api_view(['GET'])
# @retry(retries=3, delay=2)
# def ProjectTaskTotalDurationCalculation(request):
#     if request.method == 'GET':
#         projectTask = ProjectTask.objects.all()
#         projectTaskTimingSerializer = ProjectTaskSerializer(projectTask, many=True)
#         total_duration_minutes = 0

#         for row in projectTask:
#             if row.StartDate and row.EndDate:
#                 date_formats = [
#                     '%m/%d/%Y, %I:%M:%S %p',  # Example: 04/07/2024, 10:06:38 AM
#                     '%m/%d/%Y, %H:%M:%S',     # Example: 04/07/2024, 10:06:38
#                     '%d/%m/%Y, %I:%M:%S %p',  # Example: 07/04/2024, 10:06:38 AM
#                     '%d/%m/%Y, %H:%M:%S',     # Example: 07/04/2024, 10:06:38,
#                     "%Y-%m-%dT%H:%M:%S%z"
#                 ]

#                 start_date = end_date = None
#                 for date_format in date_formats:
#                     try:
#                         start_date = datetime.strptime(row.StartDate, date_format)
#                         end_date = datetime.strptime(row.EndDate, date_format)
#                         break
#                     except ValueError:
#                         continue

#                 if start_date and end_date:
#                     total_time_taken = end_date - start_date
#                     total_time_taken_in_seconds = total_time_taken.total_seconds()
#                     total_time_taken_data = {
#                         'hours': int(total_time_taken_in_seconds // 3600),
#                         'minutes': int((total_time_taken_in_seconds % 3600) // 60)
#                     }
#                     duration = f"{total_time_taken_data['hours']}:{total_time_taken_data['minutes']:02}"
#                     row.TotalDuration = duration
#                     row.save()

#         return JsonResponse("Updated", safe=False)





class GetAllTicketsApi(generics.ListAPIView):
    queryset =ProjectTask.objects.filter(TaskType='Ticket').order_by('-SortId')
    pagination_class = CustomPageNumberPagination
    serializer_class = ProjectTaskSerializer 
    def post(self, request, *args, **kwargs):
        try:
            filterData = JSONParser().parse(request)
            Keyword = filterData.get('SearchKeyword', '')
            if filterData['CompanyId']:
                project = Project.objects.filter(
                        CompanyId=filterData['CompanyId'],ActiveStatus=1)
                projectSerializer = ProjectSerializer(
                        project,many=True)
                projectId=[]
                for row in projectSerializer.data:
                    projectId.append(row['ProjectId'])
                self.queryset = self.queryset.filter(ProjectId__in=projectId)
            if len(filterData['TaskAssignedTo']):
                self.queryset = self.queryset.filter(TaskAssignedTo__in=filterData['TaskAssignedTo'])
            if len(filterData['TaskAssignedBy']):
                self.queryset = self.queryset.filter(TaskAssignedBy__in=filterData['TaskAssignedBy'])
            if len(filterData['ProjectId']):
                self.queryset = self.queryset.filter(ProjectId__in=filterData['ProjectId'])
                
            # Filter by Status
            if filterData['Status']:
                status = filterData['Status']
                if isinstance(status, int):
                    status = [status]
                self.queryset = self.queryset.filter(Status__in=status)
            # if filterData['Status']:
            #     status=filterData['Status']
            #     self.queryset = self.queryset.filter(Status__in=status)
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
        except:
            return JsonResponse("", safe=False)   




@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get Tickets by TaskAssignedTo",)
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
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get Tickets by TaskAssignedBy",)
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




def calculateNextScheduledDate(RepeatInterval="",Interval="",date= ""):
    
    if date:
        given_date=datetime.fromisoformat(date)
    else:
        given_date=datetime.now()
    day_of_week = int((given_date.weekday()+ 1))
    now = timezone.now()
    if RepeatInterval == 'daily':
        interval=Interval
        if day_of_week == 7:
            interval=interval+1
            next_Schduled_date = now + timedelta(days=interval)
            
            
        else:
            next_Schduled_date = now + timedelta(days=interval)
        
    elif RepeatInterval == 'weekly':
        interval=Interval
        if day_of_week == 7:
            interval=interval+1
            next_Schduled_date = now + timedelta(weeks=interval)
            
        else:
            next_Schduled_date = now + timedelta(weeks=interval)
            

    elif RepeatInterval == 'monthly':
        
        interval=Interval
        if day_of_week == 7:
            interval=interval+1
            next_Schduled_date = now + relativedelta(months=interval)
            
        else:
            next_Schduled_date = now + relativedelta(months=interval)
            
    elif RepeatInterval == 'yearly':
        interval = Interval
        if day_of_week == 7:
            interval=interval+1
            next_Schduled_date = now + relativedelta(years=interval)
        
        else:
            next_Schduled_date = now + relativedelta(years=interval)
    return next_Schduled_date
          





@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get My Task",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def GetallTaskTemplate(request,CompanyId=""):
    try:
        if request.method == 'GET':
            # project = Project.objects.filter(
            #             CompanyId=CompanyId)
            # projectSerializer = ProjectSerializer(
            #         project,many=True)
            # projectId=[]
            # for row in projectSerializer.data:
            #     projectId.append(row['ProjectId'])

            projectTask = ProjectTask.objects.filter(IsTemplate=1,CompanyId=CompanyId).order_by('-SortId')
            projectTaskSerializer = ProjectTaskSerializer(
                    projectTask,many=True)
            taskStatusName=[]
            for row in projectTaskSerializer.data:
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





class GetAllTemplatesByPagination(generics.ListAPIView):
    queryset =ProjectTask.objects.filter(IsTemplate=1).order_by('-SortId')
    pagination_class = CustomPageNumberPagination
    serializer_class = ProjectTaskSerializer 
    def post(self, request, *args, **kwargs):
        try:
            filterData = JSONParser().parse(request)
            Keyword = filterData.get('SearchKeyword', '')
            if filterData['CompanyId']:
                self.queryset = self.queryset.filter(CompanyId=filterData['CompanyId'])
            if Keyword:
                self.queryset = self.queryset.filter(Q(Title__icontains=Keyword)|Q(Description__icontains=Keyword))
            page = self.paginate_queryset(self.queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                data = []

                for row in serializer.data:
                    try:                      
                        taskStatus=TaskStatus.objects.get(StatusId=row['Status'])
                        taskStatusSerializer=TaskStatusSerializer(taskStatus)
                        row['StatusName']=taskStatusSerializer.data['Status']
                    except:
                        row['StatusName']=""
                    try:                      
                        templateType=TempleteType.objects.get(TempleteTypeId=row['TempleteType'])
                        templateTypeSerializer=TempleteTypeSerializer(templateType)
                        row['TempleteTypeName']=templateTypeSerializer.data['TempleteType']
                    except:
                        row['TempleteTypeName']=""

                    try:
                        try:
                            staff = Staff.objects.get(StaffId=row['TaskAssignedBy'])
                            staffSerializer = StaffSerializer(staff)
                            row['TaskAssignedByName'] = staffSerializer.data['StaffName']
                        except:
                            company = Company.objects.get(CompanyId=row['TaskAssignedBy'])
                            companySerializer = CompanySerializer(company)
                            row['TaskAssignedByName'] =companySerializer.data['CompanyName']
                    except:
                        row['TaskAssignedByName'] =""

                    try:
                        projectTaskFile = ProjectTaskFile.objects.filter(ProjectTaskId=row['ProjectTaskId'])
                        projectTaskFileSerializer = ProjectTaskFileSerializer(projectTaskFile,many=True)
                        row['ProjectTaskFiles']=projectTaskFileSerializer.data
                    except:
                        row['ProjectTaskFiles']=""
                    data.append(row)
                return self.get_paginated_response(data)
        except:
            return JsonResponse("", safe=False)




# class SaveProjectTaskFile(APIView):
#     parser_classes = (MultiPartParser, FormParser)
#     def post(self, request,  *args, **kwargs):
#         # try:
#                 Serializer = SaveProjectTaskFileSerializer(
#                     data=request.data)
#                 if Serializer.is_valid():
#                     Serializer.save()
#                     return JsonResponse(Serializer.data['ProjectTaskFileId'], safe=False)
#                 else:
#                     return JsonResponse("", safe=False)
#         # except:
#         #     return JsonResponse("", safe=False)     
                    
import os
import shutil

@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get My Task")
@api_view(['GET'])
def copy_image(request, ProjectTaskFileId=""):
    try:
       
        projecttaskFile = ProjectTaskFile.objects.get(ProjectTaskFileId=ProjectTaskFileId)
        source_relative_path = projecttaskFile.TaskFile.name
       
        source_path = os.path.join(settings.MEDIA_ROOT, source_relative_path)
        
        
        destination_folder = os.path.join(settings.MEDIA_ROOT, 'Template')
        # destination_path = os.path.join(destination_folder, 'image.jpg')
        destination_path = os.path.join(destination_folder, os.path.basename(source_relative_path))
        
      
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        shutil.copy2(source_path, destination_path)
        
        
        return JsonResponse(destination_path,safe=False)
    
    except:
        return JsonResponse("",safe=False)




from django.core.files.base import ContentFile
import base64
import uuid
@csrf_exempt
@swagger_auto_schema(method='POST', operation_description="NOTE: API for get My Task")
@api_view(['POST'])
def savecopy_image(request,):
    try:
        if request.method == 'POST':
            projectdata = JSONParser().parse(request)
            projecttaskFile = ProjectTaskFile.objects.get(ProjectTaskFileId=projectdata['ProjectTaskFileId'])
            
           
            if 'TaskFile' in projectdata:
                image_data = projectdata['TaskFile']
                
               
                if isinstance(image_data, str) and image_data.startswith('data:image'):
                    
                    format, imgstr = image_data.split(';base64,')
                    ext = format.split('/')[-1]  
                    image_data = ContentFile(base64.b64decode(imgstr), name=f"{uuid.uuid4()}.{ext}")
                
                projecttaskFile.TaskFile = image_data
                projecttaskFile.save()
                return JsonResponse("updated", safe=False)
            
            return JsonResponse("TaskFile not provided", safe=False)
    
    except ProjectTaskFile.DoesNotExist:
        return JsonResponse("ProjectTaskFile not found", safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, safe=False)
    




@csrf_exempt
@api_view(['GET'])
@retry(retries=3, delay=2)
def UpdateClientandCompanyInTask(request):
    try:
        if request.method == 'GET':
            project=Project.objects.all()
            projectSerializer=ProjectSerializer(project,many=True)
            for row in projectSerializer.data:
                company_id=row['CompanyId']
                client_id=row['ClientId']
                projectTask = ProjectTask.objects.filter(ProjectId=row['ProjectId'])
                for pro in projectTask:
                    pro.CompanyId=company_id
                    pro.ClientId=client_id
                    pro.save()
               
            return JsonResponse("updated", safe=False)
        else:
                return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    

@csrf_exempt
@api_view(['GET'])
def ProjectTaskTimingCalculation(request):
        # TaskTiming = ProjectTaskTiming.objects.get(ProjectTaskTimingId=ProjectTaskTimingId)
        projectTaskTiming = ProjectTaskTiming.objects.filter(Q(Duration__isnull=True)|Q(Duration=""))
        projectTaskTimingSerializer = ProjectTaskTimingSerializer(projectTaskTiming, many=True)
        total_duration_minutes = 0
        for row in projectTaskTiming:
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
        return JsonResponse("updated", safe=False)

        #     hours, minutes = map(int, duration.split(':'))
        #     total_duration_minutes += hours * 60 + minutes

        # total_duration_hours = total_duration_minutes // 60
        # total_duration_remaining_minutes = total_duration_minutes % 60
        # total_duration = f"{total_duration_hours}:{total_duration_remaining_minutes}"

        # projectTask = ProjectTask.objects.get(ProjectTaskId=ProjectTaskId)
        # projectTask.TotalDuration = total_duration
        # projectTask.save()



@csrf_exempt
@api_view(['GET'])
def ProjectTaskendatedurationCalculation(request):
    projectTasks=ProjectTask.objects.filter(Q(TotalDuration__isnull=True)|Q(TotalDuration="")).exclude(TaskType='Subtask')
    projectTaskSerializer=ProjectTaskSerializer(projectTasks,many=True)
    for row in projectTasks:
        projectTaskTiming = ProjectTaskTiming.objects.filter(ProjectTaskId=row.ProjectTaskId).order_by('-SortId')
        projectTaskTimingSerializer = ProjectTaskTimingSerializer(projectTaskTiming, many=True)
        if not projectTaskTiming.exists():
            continue
        total_duration_minutes = 0
        for row in projectTaskTiming:
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

        projectTask = ProjectTask.objects.get(ProjectTaskId=row.ProjectTaskId)
      
        projectTask.EndDate=projectTaskTimingSerializer.data[0]['EndDate']
        projectTask.TotalDuration = total_duration
        projectTask.save()
    return JsonResponse("updated", safe=False)

