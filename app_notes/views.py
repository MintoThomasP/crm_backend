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
from app_staff.models import Staff
from app_staff.serializers import StaffSerializer
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
    

@csrf_exempt
@api_view(['POST'])
@retry(retries=3, delay=2)
def MeetingNotesApiByCompanyId(request):
    # try:
        if request.method == 'POST': 
            meetingNotesData = JSONParser().parse(request)
           
            if meetingNotesData['StartDate'] and  meetingNotesData['EndDate']:
                start_date = timezone.datetime.strptime(meetingNotesData['StartDate'], '%Y-%m-%d').date()
                print(start_date)
                end_date = (timezone.datetime.strptime(meetingNotesData['EndDate'], '%Y-%m-%d') + timezone.timedelta(days=1)).date()
                meetingNotes = MeetingNotes.objects.filter(
                        CompanyId=meetingNotesData['CompanyId'],CreatedDate__range=(start_date,end_date))
            else:
                meetingNotes = MeetingNotes.objects.filter(
                        CompanyId=meetingNotesData['CompanyId'])
            meetingNotesSerializer = MeetingNotesSerializer(
                    meetingNotes,many=True)
            noteData=[]
            for row in meetingNotesSerializer.data:
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
                noteData.append(row)

            return JsonResponse(noteData, safe=False)
        else:
            return JsonResponse("", safe=False)
    # except:
    #     return JsonResponse("", safe=False)