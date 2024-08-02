from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from app_client.models import Client
from app_client.serializers import ClientSerializer
from app_default.models import MeetingType
from app_default.serializers import MeetingTypeSerializer
from app_default.views import retry
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from django.utils import timezone
from app_notes.models import MeetingNoteDocument, MeetingNotes
from app_notes.serializers import MeetingNoteDocumentSerializer, MeetingNotesSerializer
from app_project.views import CustomPageNumberPagination
from app_staff.models import Staff
from app_staff.serializers import StaffSerializer
from rest_framework import generics
from django.db.models import Q
from datetime import datetime, timedelta
from django.utils import timezone
# Create your views here.


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=MeetingNotesSerializer)
@swagger_auto_schema(method='PUT', request_body=MeetingNotesSerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all MeetingNotes Details",)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
def MeetingNotesApi(request):
    try:
        if request.method == 'GET':
            meetingNotes = MeetingNotes.objects.all().order_by('-SortId')
            meetingNotesSerializer = MeetingNotesSerializer(
                    meetingNotes, many=True)
            return JsonResponse(meetingNotesSerializer.data, safe=False)
        elif request.method == 'POST':
            meetingNotesData = JSONParser().parse(request)
            meetingNotesSerializer = MeetingNotesSerializer(
                data=meetingNotesData)
            if meetingNotesSerializer.is_valid():
                meetingNotesSerializer.save()

                return JsonResponse(meetingNotesSerializer.data['MeetingNoteId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            meetingNotesData = JSONParser().parse(request)
            meetingNotes = MeetingNotes.objects.get(
                MeetingNoteId=meetingNotesData['MeetingNoteId'])
            meetingNotesSerializer = MeetingNotesSerializer(
                meetingNotes, data=meetingNotesData)
            if meetingNotesSerializer.is_valid():
                meetingNotesSerializer.save()
                return JsonResponse(meetingNotesSerializer.data['MeetingNoteId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give MeetingNotesId to get one meetingNotes detail",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def MeetingNotesApiById(request, MeetingNoteId=""):
    try:
        if request.method == 'GET': 
            meetingNotes = MeetingNotes.objects.get(
                    MeetingNoteId=MeetingNoteId)
            meetingNotesSerializer = MeetingNotesSerializer(
                    meetingNotes)
            noteData=meetingNotesSerializer.data
            try:
                meetingDocument=MeetingNoteDocument.objects.filter(MeetingNoteId=MeetingNoteId)
                meetingDocumentSerializer=MeetingNoteDocumentSerializer(meetingDocument,many=True)
                noteData['MeetingDocuments']=meetingDocumentSerializer.data
            except:
                noteData['MeetingDocuments']=""
            return JsonResponse(noteData, safe=False)
        elif request.method == 'DELETE':
            meetingNotes = MeetingNotes.objects.get(MeetingNoteId=MeetingNoteId)
            MeetingNoteDocument.objects.filter(
                        MeetingNoteId=MeetingNoteId).delete()
            meetingNotes.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    


class UploadMeetingNoteDocument(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request,  *args, **kwargs):
        try:
                Serializer = MeetingNoteDocumentSerializer(
                    data=request.data)
                if Serializer.is_valid():
                    Serializer.save()
                    return JsonResponse(Serializer.data['MeetingNoteDocumentId'], safe=False)
                else:
                    return JsonResponse("", safe=False)
        except:
            return JsonResponse("", safe=False)
        

@csrf_exempt
@api_view(['DELETE'])
@retry(retries=3, delay=2)
def DeleteMeetingDocument(request, MeetingNoteDocumentId=""):
    try:

        if request.method == 'DELETE':
            
            meetingNotes=MeetingNoteDocument.objects.get(
                        MeetingNoteDocumentId=MeetingNoteDocumentId)
            MeetingNoteDocument.objects.get(
                        MeetingNoteDocumentId=MeetingNoteDocumentId).Document.delete(save=True)
            meetingNotes.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
from rest_framework.pagination import PageNumberPagination  
class CustomNotesPagination(PageNumberPagination):
    page_size = 10 # Adjust the page size as needed
    page_size_query_param = 'page_size'  

class MeetingNotesApiByCompanyId(generics.ListAPIView):
    queryset =MeetingNotes.objects.all()
    pagination_class = CustomNotesPagination
    serializer_class = MeetingNotesSerializer 
    def post(self, request, *args, **kwargs):
        filterData = JSONParser().parse(request)
        
        Keyword = filterData.get('SearchKeyword', '')
        if Keyword:
            self.queryset = self.queryset.filter(Q(Title__icontains=Keyword)|Q(Description__icontains=Keyword))
        if filterData['CompanyId']:
            self.queryset = self.queryset.filter(CompanyId=filterData['CompanyId'])
        if filterData['CreatedBy']:
            self.queryset = self.queryset.filter(CreatedBy=filterData['CreatedBy'])
            
        if filterData['MeetingType']:
            self.queryset = self.queryset.filter(MeetingType=filterData['MeetingType'])
        if filterData['ParticipatedBy']:
            self.queryset = self.queryset.filter(TeamParticipants__icontains=filterData['ParticipatedBy'])
        if filterData['StartDate'] and filterData['EndDate']:
            # start_date=datetime.strptime(filterData['StartDate'], '%Y-%m-%d').date()
            # end_date=datetime.strptime(filterData['EndDate'], '%Y-%m-%d').date()
            start_date = timezone.datetime.strptime(filterData['StartDate'], '%Y-%m-%d').date()
            end_date = (timezone.datetime.strptime(filterData['EndDate'], '%Y-%m-%d') + timezone.timedelta(days=1)).date()
            print(start_date)
            self.queryset = self.queryset.filter(CreatedDate__range=(start_date,end_date))
            print(self.queryset)
        page = self.paginate_queryset(self.queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = []

            for row in serializer.data:
                try:
                    staff=Staff.objects.get(StaffId=row['CreatedBy'])
                    staffSerializer=StaffSerializer(staff)
                    row['CreatedByName']=staffSerializer.data['StaffName']
                except:
                    row['CreatedByName']=""
                try:
                    meetingType=MeetingType.objects.get(MeetingTypeId=row['MeetingType'])
                    meetingTypeSerializer=MeetingTypeSerializer(meetingType)
                    row['MeetingTypevalue']=meetingTypeSerializer.data['MeetingType']
                except:
                    row['MeetingTypevalue']=""
                try:
                    client=Client.objects.get(ClientId=row['ClientId'])
                    clientSerializer=ClientSerializer(client)
                    row['ClientName']=clientSerializer.data['CustomerDisplayName']
                except:
                    row['ClientName']=""
                try:
                    meetingDocument=MeetingNoteDocument.objects.filter(MeetingNoteId=row['MeetingNoteId'])
                    meetingDocumentSerializer=MeetingNoteDocumentSerializer(meetingDocument,many=True)
                    row['MeetingDocuments']=meetingDocumentSerializer.data
                except:
                    row['MeetingDocuments']=""
                data.append(row)

            return self.get_paginated_response(data)
        

from datetime import datetime
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all MeetingNotes Details",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def UpdateCreatedDateinMeetingNotes(request):
    try:
        if request.method == 'GET':
            meetingNotes = MeetingNotes.objects.all().order_by('-SortId')
            meetingNotesSerializer = MeetingNotesSerializer(
                    meetingNotes, many=True)
            for row in meetingNotes:
                parsed_datetime=datetime.strptime(row.StartTime, '%Y-%m-%dT%H:%M')
                
                formatted_datetime = parsed_datetime.strftime('%Y-%m-%dT%H:%M:%S%z')
               
                
                row.CreatedDate=formatted_datetime
                row.save()
               
                
            return JsonResponse("date changed", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)