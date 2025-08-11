from datetime import datetime
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from app_firebase.models import DeviceToken
from app_firebase.serailizers import DeviceTokenSerializer
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from app_company.models import Company
from app_company.serializers import CompanySerializer
from app_default.models import UserType
from app_default.serializers import UserTypeSerializer
from app_default.views import retry
from app_login.models import Login, LoginHistory
from django.contrib.auth import logout
from django.shortcuts import redirect
from app_login.serializers import LoginAuthSerializer, LoginHistorySerializer, LoginSaveSerializer, LoginSerializer, LoginUpdateSerializer
from app_project.models import ProjectTask, ProjectTaskTiming
from app_project.serializers import ProjectTaskSerializer, ProjectTaskTimingSerializer
from app_staff.models import Staff
from app_staff.serializers import StaffSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from django.db.models import Q
# Create your views here.

from datetime import datetime, timedelta, timezone


@csrf_exempt
@swagger_auto_schema(method='PUT', request_body=LoginSaveSerializer, operation_description="NOTE: API for edit Login")
@swagger_auto_schema(method='POST', request_body=LoginSaveSerializer, operation_description="NOTE: API for save Login")
@api_view(['POST', 'PUT'])
@retry(retries=3, delay=2)
def CreateLoginApi(request):
    if request.method == 'POST':
        userLogin_data = JSONParser().parse(request)
        userLogin_serializer = LoginSaveSerializer(data=userLogin_data)
        if userLogin_serializer.is_valid():
            userLogin_serializer.save()
            return JsonResponse("Add successfully", safe=False)
        return JsonResponse("Failed to add", safe=False)
    elif request.method == 'PUT':
        userLoginData = JSONParser().parse(request)
        userLogin = Login.objects.get(
            LoginId=userLoginData['LoginId'])
        logSerializer = LoginSaveSerializer(
            userLogin, data=userLoginData)
        if logSerializer.is_valid():
            logSerializer.save()

            return JsonResponse("Update successfully", safe=False)
        return JsonResponse("Failed to Update", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get login details by UserId",)
@swagger_auto_schema(method='DELETE', operation_description="NOTE: API for delete login details by UserId",)
@api_view(['GET', 'DELETE'])
@retry(retries=3, delay=2)
def UserLoginApiById(request, UserId=""):
    try:
        if request.method == 'GET':
            userLogin = Login.objects.get(UserId=UserId)
            userLoginSerializer = LoginSerializer(userLogin)
            return JsonResponse(userLoginSerializer.data, safe=False)
        elif request.method == 'DELETE':
            userLogin = Login.objects.get(UserId=UserId)
            userLogin.delete()
            return JsonResponse("Deleted successfully", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=LoginAuthSerializer, operation_description="NOTE: API for Login, payload { EmailId, Password}")
@swagger_auto_schema(method='PUT', request_body=LoginUpdateSerializer, operation_description="NOTE: API for Update Login by EmailId and UserType")
@api_view(['POST', 'PUT'])
@retry(retries=3, delay=2)
def loginApi(request):
    try:
        if request.method == 'POST':
            login_data = JSONParser().parse(request)
            Data = []
            try:
                login = Login.objects.get(
                    EmailId=login_data['EmailId'], Password=login_data['Password'])
                login_serializer = LoginAuthSerializer(login)

                UserData = []
                if not login_serializer.data:
                    login = Login.objects.filter(
                        EmailId=login_data['EmailId'])
                    login_serializer = LoginAuthSerializer(login, many=True)
                    if not login_serializer.data:
                        Data.append('FAILED')
                        Data.append(
                            'Please check the username/password and try again.')
                    else:
                        Data.append('FAILED')
                        Data.append(login_serializer.data[0])
                else:
                    userType = UserType.objects.get(
                        UserTypeId=login_serializer.data['UserType'])
                    userType_serializer = UserTypeSerializer(userType)
                    status = ""
                    message = ""

                    if userType_serializer.data['UserType'] == 'Team' or userType_serializer.data['UserType'] == 'Admin' or userType_serializer.data['UserType'] == 'Super Admin':
                        staff = Staff.objects.get(
                            StaffId=login_serializer.data['UserId'])

                        staff_serializer = StaffSerializer(staff)
                        if staff_serializer.data['Status'] != 1:
                            status = "FAILED"
                            message = 'Your account has been blocked. Please contact administrator.'
                        else:
                            status = "SUCCESS"
                            message = 'Successfully logged in'
                            UserData = staff_serializer.data
                    elif userType_serializer.data['UserType'] == 'Company':
                        company = Company.objects.get(
                            CompanyId=login_serializer.data['UserId'])

                        company_serializer = CompanySerializer(company)
                        # if staff_serializer.data['Status'] == -1:
                        #     status="FAILED"
                        #     message='Your account has been blocked. Please contact administrator.'
                        # else:
                        status = "SUCCESS"
                        message = 'Successfully logged in'
                        UserData = company_serializer.data
                    else:
                        status = "SUCCESS"
                        message = 'Successfully logged in'

                    Data.append(status)
                    Data.append(login_serializer.data)
                    Data.append(message)
                Data.append(UserData)
                return JsonResponse(Data, safe=False)
            except:
                Data.append('FAILED')
                Data.append(
                    'Please check the username/password and try again.')
                return JsonResponse(Data, safe=False)
        elif request.method == 'PUT':
            login_data = JSONParser().parse(request)
            login = Login.objects.get(
                EmailId=login_data['EmailId'], UserType=login_data['UserType'])
            login_serializer = LoginUpdateSerializer(login, data=login_data)
            if login_serializer.is_valid():
                login_serializer.save()
                return JsonResponse("Update successfully", safe=False)
            return JsonResponse("Failed to Update", safe=False)
    except:
        return JsonResponse("Failed", safe=False)


@csrf_exempt
@swagger_auto_schema(method='POST', operation_description="NOTE: API for Update UserType")
@api_view(['POST'])
@retry(retries=3, delay=2)
def UpdateUserTypeApi(request, pk=""):
    try:
        if request.method == 'POST':
            login_data = JSONParser().parse(request)
            try:
                login = Login.objects.get(UserId=login_data['UserId'])
                try:
                    user_type = UserType.objects.get(
                        UserTypeId=login_data['UserType'])

                    login.UserType = user_type
                    login.save()
                    return JsonResponse("Updated", safe=False)
                except:
                    return JsonResponse("UserType not found", safe=False)
            except:
                return JsonResponse("UserId not found", safe=False)
    except Exception as e:
        return JsonResponse(str(e), safe=False)


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=LoginHistorySerializer, operation_description="NOTE: API for save LoginHistory")
@swagger_auto_schema(method='PUT', request_body=LoginHistorySerializer, operation_description="NOTE: API for edit LoginHistory")
@swagger_auto_schema(method='GET', operation_description="NOTE: API for Get all LoginHistory Details",)
@api_view(['GET', 'POST', 'PUT'])
@retry(retries=3, delay=2)
def LoginHistoryApi(request):
    try:
        if request.method == 'GET':
            loginHistory = LoginHistory.objects.all().order_by('-SortId')
            loginHistorySerializer = LoginHistorySerializer(
                loginHistory, many=True)
            return JsonResponse(loginHistorySerializer.data, safe=False)
        elif request.method == 'POST':
            loginHistoryData = JSONParser().parse(request)
            loginHistorySerializer = LoginHistorySerializer(
                data=loginHistoryData)
            try:
                loginHistoryOld = LoginHistory.objects.get(Q(Q(LogoutTime__isnull=True) | Q(
                    LogoutTime='')) & Q(UserId=loginHistoryData['UserId']))
                loginHistoryOld.LogoutTime = loginHistoryData['LoginTime']
                loginHistoryOld.save()
            except:
                p = ""
            if loginHistorySerializer.is_valid():
                loginHistorySerializer.save()

                UserId = loginHistoryData['UserId']
                Token = loginHistoryData['Token']
                UserType = loginHistoryData['UserType']
                if Token:
                    obj, created = DeviceToken.objects.update_or_create(
                        Token=Token,
                        defaults={'UserId': UserId,
                                  'Active': True, 'UserType': UserType}
                    )
                # login = Login.objects.get(UserId=loginHistoryData['UserId'])
                # login.Token = loginHistoryData['Token']
                # login.save()
                return JsonResponse(loginHistorySerializer.data['LoginHistoryId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            loginHistoryData = JSONParser().parse(request)
            loginHistory = LoginHistory.objects.get(
                LoginHistoryId=loginHistoryData['LoginHistoryId'])
            loginHistorySerializer = LoginHistorySerializer(
                loginHistory, data=loginHistoryData)
            if loginHistorySerializer.is_valid():
                loginHistorySerializer.save()
                try:
                    deviceToken = DeviceToken.objects.get(
                        Token=loginHistoryData['Token'])
                    if deviceToken:
                        deviceToken.Active = False
                        deviceToken.save()
                except:
                    p = ""
                try:
                    login = Login.objects.get(UserId=loginHistory.UserId)
                    login.Token = ""
                    login.save()
                except:
                    p = ""
                try:
                    projectTask = ProjectTask.objects.filter(
                        TaskAssignedTo=loginHistoryData['UserId'])
                    projectTaskSerializer = ProjectTaskSerializer(
                        projectTask, many=True)
                    for row in projectTaskSerializer.data:
                        taskTimings = ProjectTaskTiming.objects.filter(
                            Q(EndDate__isnull=True) | Q(EndDate=""),
                            ProjectTaskId=row['ProjectTaskId']
                        )

                        for taskTiming in taskTimings:
                            taskTiming.EndDate = loginHistoryData['LogoutTime']
                            taskTiming.save()
                        projectTask = ProjectTask.objects.get(
                            ProjectTaskId=row['ProjectTaskId'])
                        if projectTask.Status == '2':
                            projectTask.Status = 10
                            projectTask.EndDate = loginHistoryData['LogoutTime']
                            projectTask.save()
                except:
                    p = ""
                return JsonResponse(loginHistorySerializer.data['LoginHistoryId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get loginHistory by LoginHistoryId",)
@swagger_auto_schema(method='DELETE', operation_description="NOTE: API for delete loginHistory by LoginHistoryId",)
@api_view(['GET', 'DELETE'])
@retry(retries=3, delay=2)
def LoginHistoryApiById(request, LoginHistoryId=""):
    try:
        if request.method == 'GET':
            loginHistory = LoginHistory.objects.get(
                LoginHistoryId=LoginHistoryId)
            loginHistorySerializer = LoginHistorySerializer(
                loginHistory)
            return JsonResponse(loginHistorySerializer.data, safe=False)
        elif request.method == 'DELETE':
            loginHistory = LoginHistory.objects.get(
                LoginHistoryId=LoginHistoryId)
            loginHistory.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get loginHistory by UserId",)
@api_view(['GET', 'DELETE'])
@retry(retries=3, delay=2)
def LoginHistoryApiByUserId(request, UserId=""):
    try:
        if request.method == 'GET':
            loginHistory = LoginHistory.objects.filter(
                UserId=UserId)
            loginHistorySerializer = LoginHistorySerializer(
                loginHistory, many=True)
            return JsonResponse(loginHistorySerializer.data, safe=False)

        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


# @csrf_exempt
# @swagger_auto_schema(method='POST', request_body=LoginAuthSerializer,operation_description="NOTE: API for Login by using Token. payload { Token,UserId}")
# @api_view(['POST'])
# @retry(retries=3, delay=2)
# def loginByTokenApi(request):
#     # try:
#         if request.method == 'POST':
#             login_data = JSONParser().parse(request)
#             # try:
#             login = Login.objects.filter(
#                 Token=login_data['Token'],UserId=login_data['UserId'])
#             # except:
#             #     return JsonResponse("FAILED",safe=False)

#             Data = []
#             login_serializer = LoginAuthSerializer(login,many=True)

#             UserData = []
#             if not login_serializer.data:
#                 login = Login.objects.filter(
#                     EmailId=login_data['Token'],UserId=login_data['UserId'])
#                 login_serializer = LoginAuthSerializer(login, many=True)
#                 if not login_serializer.data:
#                     Data.append('FAILED')
#                     Data.append(
#                         'Please check the username/password and try again.')
#                 else:
#                     Data.append('FAILED')
#                     Data.append(login_serializer.data[0])
#             else:
#                 userType = UserType.objects.get(UserTypeId=login_serializer.data['UserType'])
#                 userType_serializer = UserTypeSerializer(userType)
#                 status=""
#                 message=""
#                 if userType_serializer.data['UserType'] == 'Team' or userType_serializer.data['UserType'] == 'Admin' or userType_serializer.data['UserType'] == 'Super Admin':
#                     staff = Staff.objects.get(
#                         StaffId=login_serializer.data['UserId'])

#                     staff_serializer = StaffSerializer(staff)
#                     # if staff_serializer.data['Status'] == -1:
#                     #     status="FAILED"
#                     #     message='Your account has been blocked. Please contact administrator.'
#                     # else:
#                     status="SUCCESS"
#                     message='Successfully logged in'
#                     UserData = staff_serializer.data
#                 elif userType_serializer.data['UserType'] == 'Company':
#                     company = Company.objects.get(
#                         CompanyId=login_serializer.data['UserId'])

#                     company_serializer = CompanySerializer(company)
#                     # if staff_serializer.data['Status'] == -1:
#                     #     status="FAILED"
#                     #     message='Your account has been blocked. Please contact administrator.'
#                     # else:
#                     status="SUCCESS"
#                     message='Successfully logged in'
#                     UserData = company_serializer.data
#                 else:
#                     status="SUCCESS"
#                     message='Successfully logged in'

#                 Data.append(status)
#                 Data.append(login_serializer.data)
#                 Data.append(message)
#             Data.append(UserData)
#             return JsonResponse(Data, safe=False)
#         else:
#             return JsonResponse("", safe=False)
#     # except:
#     #     return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=LoginAuthSerializer, operation_description="NOTE: API for Login, payload { EmailId, Password}")
@api_view(['POST'])
@retry(retries=3, delay=2)
def loginByTokenApi(request):
    try:
        if request.method == 'POST':
            login_data = JSONParser().parse(request)
            Data = []
            try:
                deviceToken = DeviceToken.objects.get(
                    Token=login_data['Token'], UserId=login_data['UserId'])
                deviceTokenSerializer = DeviceTokenSerializer(deviceToken)

                if deviceTokenSerializer.data:
                    login = Login.objects.get(
                        UserId=deviceTokenSerializer.data['UserId'])
                    login_serializer = LoginAuthSerializer(deviceToken)

                    UserData = []
                    if not login_serializer.data:
                        login = Login.objects.filter(
                            Token=login_data['Token'])
                        login_serializer = LoginAuthSerializer(
                            login, many=True)
                        if not login_serializer.data:
                            Data.append('FAILED')
                            Data.append(
                                'Please check the username/password and try again.')
                        else:
                            Data.append('FAILED')
                            Data.append(login_serializer.data[0])
                    else:
                        userType = UserType.objects.get(
                            UserTypeId=login_serializer.data['UserType'])
                        userType_serializer = UserTypeSerializer(userType)
                        status = ""
                        message = ""

                        if userType_serializer.data['UserType'] == 'Team' or userType_serializer.data['UserType'] == 'Admin' or userType_serializer.data['UserType'] == 'Super Admin':
                            staff = Staff.objects.get(
                                StaffId=login_serializer.data['UserId'])

                            staff_serializer = StaffSerializer(staff)
                            if staff_serializer.data['Status'] != 1:
                                status = "FAILED"
                                message = 'Your account has been blocked. Please contact administrator.'
                            else:
                                status = "SUCCESS"
                                message = 'Successfully logged in'
                                UserData = staff_serializer.data
                        elif userType_serializer.data['UserType'] == 'Company':
                            company = Company.objects.get(
                                CompanyId=login_serializer.data['UserId'])

                            company_serializer = CompanySerializer(company)

                            status = "SUCCESS"
                            message = 'Successfully logged in'
                            UserData = company_serializer.data
                        else:
                            status = "SUCCESS"
                            message = 'Successfully logged in'

                        Data.append(status)
                        Data.append(login_serializer.data)
                        Data.append(message)
                    Data.append(UserData)
                    return JsonResponse(Data, safe=False)
                else:
                    Data.append('FAILED')
                    Data.append(
                        'Please check the username/password and try again.')
            except:
                Data.append('FAILED')
                Data.append(
                    'Please check the username/password and try again.')
                return JsonResponse(Data, safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for auto logout",)
@api_view(['GET'])
def AutoLogout(request, UserId=""):
    try:
        if request.method == 'GET':
            loginHistory = LoginHistory.objects.filter(
                Q(LogoutTime__isnull=True) | Q(LogoutTime=""))
            loginHistorySerializer = LoginHistorySerializer(
                loginHistory, many=True)
            for row in loginHistory:
                logout_time = datetime.now(timezone.utc)
                timezone_offset = timedelta(hours=5, minutes=30)
                logout_time = logout_time.astimezone(timezone(timezone_offset))
                formatted_logout_time = logout_time.strftime(
                    '%Y-%m-%dT%H:%M:%S%z')
                formatted_logout_time = formatted_logout_time[:-
                                                              2] + ':' + formatted_logout_time[-2:]
                row.LogoutTime = formatted_logout_time
                row.save()
                login = Login.objects.get(LoginId=row.LoginId)
                login.Token = ""
                login.save()

            return JsonResponse("updated", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@api_view(['GET'])
def CheckEmptyLogout(request, UserId=""):
    try:
        if request.method == 'GET':
            loginHistory = LoginHistory.objects.filter(
                Q(LogoutTime__isnull=True) | Q(LogoutTime=""), UserId=UserId)
            loginHistorySerializer = LoginHistorySerializer(
                loginHistory, many=True)
            return JsonResponse(loginHistorySerializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


def currentTime():
    logout_time = datetime.now(timezone.utc)
    timezone_offset = timedelta(hours=5, minutes=30)
    logout_time = logout_time.astimezone(timezone(timezone_offset))
    formatted_logout_time = logout_time.strftime('%Y-%m-%dT%H:%M:%S%z')
    formatted_logout_time = formatted_logout_time[:-
                                                  2] + ':' + formatted_logout_time[-2:]
    LogoutTime = formatted_logout_time
    return LogoutTime
