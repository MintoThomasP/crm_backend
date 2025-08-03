from rest_framework.pagination import PageNumberPagination
from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from app_client.models import Client
from app_client.serializers import ClientSerializer
from app_company.models import Company
from app_company.serializers import CompanySerializer
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
@swagger_auto_schema(method='POST', request_body=MeetingNotesSerializer, operation_description="NOTE: API for save MeetingNotes")
@swagger_auto_schema(method='PUT', request_body=MeetingNotesSerializer, operation_description="NOTE: API for edit MeetingNotes")
@swagger_auto_schema(method='GET', operation_description="NOTE: API for Get all MeetingNotes",)
@api_view(['GET', 'POST', 'PUT'])
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
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get MeetingNotes by MeetingNotesId",)
@swagger_auto_schema(method='DELETE', operation_description="NOTE: API for delete MeetingNotes by MeetingNotesId",)
@api_view(['GET', 'DELETE'])
@retry(retries=3, delay=2)
def MeetingNotesApiById(request, MeetingNoteId=""):
    try:
        if request.method == 'GET':
            meetingNotes = MeetingNotes.objects.get(
                MeetingNoteId=MeetingNoteId)
            meetingNotesSerializer = MeetingNotesSerializer(
                meetingNotes)
            noteData = meetingNotesSerializer.data
            try:
                meetingDocument = MeetingNoteDocument.objects.filter(
                    MeetingNoteId=MeetingNoteId)
                meetingDocumentSerializer = MeetingNoteDocumentSerializer(
                    meetingDocument, many=True)
                noteData['MeetingDocuments'] = meetingDocumentSerializer.data
            except:
                noteData['MeetingDocuments'] = ""
            return JsonResponse(noteData, safe=False)
        elif request.method == 'DELETE':
            meetingNotes = MeetingNotes.objects.get(
                MeetingNoteId=MeetingNoteId)
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
@swagger_auto_schema(method='DELETE', operation_description="NOTE: API for delete MeetingNoteDocument by MeetingNoteDocumentId",)
@api_view(['DELETE'])
@retry(retries=3, delay=2)
def DeleteMeetingDocument(request, MeetingNoteDocumentId=""):
    try:

        if request.method == 'DELETE':

            meetingNotes = MeetingNoteDocument.objects.get(
                MeetingNoteDocumentId=MeetingNoteDocumentId)
            MeetingNoteDocument.objects.get(
                MeetingNoteDocumentId=MeetingNoteDocumentId).Document.delete(save=True)
            meetingNotes.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


class CustomNotesPagination(PageNumberPagination):
    page_size = 40  # Adjust the page size as needed
    page_size_query_param = 'page_size'


class MeetingNotesApiByCompanyId(generics.ListAPIView):
    queryset = MeetingNotes.objects.all().order_by('-SortId')
    pagination_class = CustomNotesPagination
    serializer_class = MeetingNotesSerializer

    def post(self, request, *args, **kwargs):
        try:
            filterData = JSONParser().parse(request)
    #         : [[]],
    #   ClientId: [[]],
    #   FromDate: "",
    #   ToDate: "",
    #   ParticipatedBy: [[]],
    #   CreatedBy
            try:
                Keyword = filterData.get('SearchKeyword', '')
                if Keyword:
                    self.queryset = self.queryset.filter(
                        Q(Title__icontains=Keyword) | Q(Description__icontains=Keyword))
            except:
                p = ""
            try:
                if filterData['CompanyId']:
                    self.queryset = self.queryset.filter(
                        CompanyId=filterData['CompanyId'])
            except:
                p = ""
            try:
                if filterData['CreatedBy']:
                    self.queryset = self.queryset.filter(
                        CreatedBy__in=filterData['CreatedBy'])

            except:
                p = ""
            try:
                if filterData['MeetingType']:
                    self.queryset = self.queryset.filter(
                        MeetingType__in=filterData['MeetingType'])
            except:
                p = ""
            # try:
            #     if filterData['ParticipatedBy']:
            #         self.queryset = self.queryset.filter(TeamParticipants__icontains=filterData['ParticipatedBy'])
            # except:
            #     p=""
            try:
                if filterData['FromDate'] and filterData['ToDate']:
                    # start_date=datetime.strptime(filterData['FromDate'], '%Y-%m-%d').date()
                    # end_date=datetime.strptime(filterData['ToDate'], '%Y-%m-%d').date()
                    start_date = timezone.datetime.strptime(
                        filterData['FromDate'], '%Y-%m-%d').date()
                    end_date = (timezone.datetime.strptime(
                        filterData['ToDate'], '%Y-%m-%d') + timezone.timedelta(days=1)).date()

                    self.queryset = self.queryset.filter(
                        CreatedDate__range=(start_date, end_date))
            except:
                p = ""

            page = self.paginate_queryset(self.queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                data = []

                for row in serializer.data:
                    try:
                        try:
                            staff = Staff.objects.get(StaffId=row['CreatedBy'])
                            staffSerializer = StaffSerializer(staff)
                            row['CreatedByName'] = staffSerializer.data['StaffName']
                        except:
                            company = Company.objects.get(
                                CompanyId=row['CreatedBy'])
                            companySerializer = CompanySerializer(company)
                            row['CreatedByName'] = companySerializer.data['CompanyName']
                    except:
                        row['CreatedByName'] = ""
                    try:
                        meetingType = MeetingType.objects.get(
                            MeetingTypeId=row['MeetingType'])
                        meetingTypeSerializer = MeetingTypeSerializer(
                            meetingType)
                        row['MeetingTypevalue'] = meetingTypeSerializer.data['MeetingType']
                    except:
                        row['MeetingTypevalue'] = ""
                    try:
                        client = Client.objects.get(ClientId=row['ClientId'])
                        clientSerializer = ClientSerializer(client)
                        row['ClientName'] = clientSerializer.data['CustomerDisplayName']
                    except:
                        row['ClientName'] = ""
                    try:
                        meetingDocument = MeetingNoteDocument.objects.filter(
                            MeetingNoteId=row['MeetingNoteId'])
                        meetingDocumentSerializer = MeetingNoteDocumentSerializer(
                            meetingDocument, many=True)
                        row['MeetingDocuments'] = meetingDocumentSerializer.data
                    except:
                        row['MeetingDocuments'] = ""
                    data.append(row)

                return self.get_paginated_response(data)
        except:
            return JsonResponse("", safe=False)
