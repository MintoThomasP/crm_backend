from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from app_default.models import UserType
from app_default.serializers import UserTypeSerializer
from app_login.models import Login, LoginHistory
from django.contrib.auth import logout
from django.shortcuts import redirect
from app_login.serializers import LoginAuthSerializer, LoginHistorySerializer, LoginSaveSerializer, LoginSerializer, LoginUpdateSerializer
from app_staff.models import Staff
from app_staff.serializers import StaffSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
# Create your views here.




@csrf_exempt
@swagger_auto_schema(method='PUT', request_body=LoginSaveSerializer)
@swagger_auto_schema(method='POST', request_body=LoginSaveSerializer)
@api_view(['POST','PUT'])
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
            userLoginId=userLoginData['LoginId'])
        logSerializer = LoginSaveSerializer(
            userLogin, data=userLoginData)
        if logSerializer.is_valid():
            logSerializer.save()
            return JsonResponse("Update successfully", safe=False)
        return JsonResponse("Failed to Update", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: get login details by UserId",)
@api_view(['GET','DELETE'])
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
@swagger_auto_schema(method='POST', request_body=LoginAuthSerializer)
@swagger_auto_schema(method='PUT', request_body=LoginUpdateSerializer)
@api_view(['POST','PUT'])
def loginApi(request):
    # try:
        if request.method == 'POST':
            login_data = JSONParser().parse(request)
            login = Login.objects.get(
                EmailId=login_data['EmailId'], Password=login_data['Password'])
            Data = []
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
                userType = UserType.objects.get(UserTypeId=login_serializer.data['UserType'])
                userType_serializer = UserTypeSerializer(userType)
                status=""
                message=""
                if userType_serializer.data['UserType'] == 'Staff' or userType_serializer.data['UserType'] == 'Admin':
                    staff = Staff.objects.get(
                        StaffId=login_serializer.data['UserId'])
                    staff_serializer = StaffSerializer(staff)
                    # if staff_serializer.data['Status'] == -1:
                    #     status="FAILED"
                    #     message='Your account has been blocked. Please contact administrator.'
                    # else:
                    status="SUCCESS"
                    message='Successfully logged in'
                    UserData = staff_serializer.data
                else:
                    status="SUCCESS"
                    message='Successfully logged in'
                    
                Data.append(status)
                Data.append(login_serializer.data)
                Data.append(message)
            Data.append(UserData)
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
    # except:
    #     return JsonResponse("", safe=False)
        


@csrf_exempt
@api_view(['POST'])
def UpdateUserTypeApi(request, pk=""):
    try:
        if request.method == 'POST':
            login_data = JSONParser().parse(request)
            try:
                login = Login.objects.get(UserId=login_data['UserId'])
                try:
                    user_type = UserType.objects.get(UserTypeId=login_data['UserType']) 
                   
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
@swagger_auto_schema(method='POST', request_body=LoginHistorySerializer)
@swagger_auto_schema(method='PUT', request_body=LoginHistorySerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all LoginHistory Details",)
@api_view(['GET','POST','PUT'])
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
            if loginHistorySerializer.is_valid():
                loginHistorySerializer.save()
                
                login = Login.objects.get(UserId=loginHistoryData['UserId'])
                login.Token = loginHistoryData['Token']
                login.save()
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
                return JsonResponse(loginHistorySerializer.data['LoginHistoryId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give LoginHistoryId to get one loginHistory detail",)
@api_view(['GET','DELETE'])
def LoginHistoryApiById(request, LoginHistoryId=""):
    try:
        if request.method == 'GET': 
            loginHistory = LoginHistory.objects.get(
                    LoginHistoryId=LoginHistoryId)
            loginHistorySerializer = LoginHistorySerializer(
                    loginHistory)
            return JsonResponse(loginHistorySerializer.data, safe=False)
        elif request.method == 'DELETE':
            loginHistory = LoginHistory.objects.get(LoginHistoryId=LoginHistoryId)
            loginHistory.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    



@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give UserId to get one loginHistory detail",)
@api_view(['GET','DELETE'])
def LoginHistoryApiByUserId(request, UserId=""):
    try:
        if request.method == 'GET': 
            loginHistory = LoginHistory.objects.filter(
                    UserId=UserId)
            loginHistorySerializer = LoginHistorySerializer(
                    loginHistory,many=True)
            return JsonResponse(loginHistorySerializer.data, safe=False)
        
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)