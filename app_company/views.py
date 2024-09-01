from datetime import date, datetime
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
# Create your views here.
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

from app_basic.models import Designation, UserGroup
from app_category.models import Category, Report, ReportRefFile
from app_client.models import Client, ClientAddress, ClientDocuments, ClientOtherDetails, ContactPerson
from app_client.serializers import ClientSerializer
from app_company.models import Company, CompanyDocuments
from app_company.serializers import CompanyDocumentsSerializer, CompanySerializer, SaveCompanyDocumentsSerializer, UploadCompanyDocumentsSerializer
from app_credential.models import Credentials
from app_default.views import retry
from app_enquiry.models import Enquiry, FollowUp
from app_login.models import Login, LoginHistory
from app_notes.models import MeetingNoteDocument, MeetingNotes
from app_project.models import CommentFile, Comments, Project, ProjectTask, ProjectTaskFile, ProjectTaskTiming, TaskReviews
from app_project.serializers import ProjectSerializer, ProjectTaskSerializer
from app_sale.models import Invoice, InvoiceDocument, InvoiceItem, PaymentDocument, PaymentReceived, PaymentReceivedDetail, Quotation, QuotationFile, QuotationItem
from app_site.models import Notification, SiteSettings
from app_site.serializers import SiteSettingsSerializer
from app_staff.models import LeaveApplication, MoveOnRegister, SalarySlip, Staff, StaffDocuments, StaffGuardian
from app_staff.serializers import StaffSerializer
from app_staff.views import AllStaffPerformancebyCompany
from app_todo.models import Todo
@csrf_exempt
@swagger_auto_schema(method='POST', request_body=CompanySerializer,operation_description="NOTE: API for save Company")
@swagger_auto_schema(method='PUT', request_body=CompanySerializer,operation_description="NOTE: API for edit Company")
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all company",)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
def CompanyApi(request):
    try:
        if request.method == 'GET':
            company = Company.objects.all()
            companySerializer = CompanySerializer(
                    company, many=True)
            companyData=[]
            for row in companySerializer.data:
                try:
                    companyDocuments = CompanyDocuments.objects.filter(
                        CompanyId=row['CompanyId'])
                    companyDocumentsSerializer = CompanyDocumentsSerializer(
                        companyDocuments,many=True)
                    row['DocumentDetails']=companyDocumentsSerializer.data
                except:
                    row['DocumentDetails']=""
                companyData.append(row)
              

            return JsonResponse(companyData, safe=False)
        elif request.method == 'POST':
            companyData = JSONParser().parse(request)
            companySerializer = CompanySerializer(
                data=companyData)
            if companySerializer.is_valid():
                companySerializer.save()
                return JsonResponse(companySerializer.data['CompanyId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            companyData = JSONParser().parse(request)
            company = Company.objects.get(
                CompanyId=companyData['CompanyId'])
            companySerializer = CompanySerializer(
                company, data=companyData)
            if companySerializer.is_valid():
                companySerializer.save()
                return JsonResponse(companySerializer.data['CompanyId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get Company by CompanyId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete Company by CompanyId",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def CompanyApiById(request, CompanyId=""):
    try:
        if request.method == 'GET': 
            company = Company.objects.get(
                    CompanyId=CompanyId)
            companySerializer = CompanySerializer(
                    company)
            companyData=companySerializer.data
            try:
                companyDocuments = CompanyDocuments.objects.filter(
                    CompanyId=CompanyId)
                companyDocumentsSerializer = CompanyDocumentsSerializer(
                    companyDocuments,many=True)
                companyData['DocumentDetails']=companyDocumentsSerializer.data
            except:
                companyData['DocumentDetails']=""    
            return JsonResponse(companyData, safe=False)
        elif request.method == 'DELETE':
            company = Company.objects.get(CompanyId=CompanyId)
            company.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    



@csrf_exempt
@swagger_auto_schema(method='POST', request_body=CompanyDocumentsSerializer,operation_description="NOTE: API for save CompanyDocuments")
@swagger_auto_schema(method='PUT', request_body=CompanyDocumentsSerializer,operation_description="NOTE: API for edit CompanyDocuments")
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all company Documents",)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
def CompanyDocumentsApi(request):
    try:
        if request.method == 'GET':
            companyDocuments = CompanyDocuments.objects.all()
            companyDocumentsSerializer = CompanyDocumentsSerializer(
                    companyDocuments, many=True)
            return JsonResponse(companyDocumentsSerializer.data, safe=False)
        elif request.method == 'POST':
            companyDocumentsData = JSONParser().parse(request)
            companyDocumentsSerializer = SaveCompanyDocumentsSerializer(
                data=companyDocumentsData)
            if companyDocumentsSerializer.is_valid():
                companyDocumentsSerializer.save()
                return JsonResponse(companyDocumentsSerializer.data['CompanyDocumentId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            companyDocumentsData = JSONParser().parse(request)
            companyDocuments = CompanyDocuments.objects.get(
                CompanyDocumentId=companyDocumentsData['CompanyDocumentId'])
            companyDocumentsSerializer = SaveCompanyDocumentsSerializer(
                companyDocuments, data=companyDocumentsData)
            if companyDocumentsSerializer.is_valid():
                companyDocumentsSerializer.save()
                return JsonResponse(companyDocumentsSerializer.data['CompanyDocumentId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get companyDocumentsdetail by CompanyDocumentId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete companyDocuments by CompanyDocumentId",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def CompanyDocumentsApiById(request, CompanyDocumentId=""):
    try:
        if request.method == 'GET': 
            companyDocuments = CompanyDocuments.objects.get(
                    CompanyDocumentId=CompanyDocumentId)
            companyDocumentsSerializer = CompanyDocumentsSerializer(
                    companyDocuments)
            companyDocumentsData=companyDocumentsSerializer.data
            
            return JsonResponse(companyDocumentsData, safe=False)
        elif request.method == 'DELETE':
            companyDocuments = CompanyDocuments.objects.get(CompanyDocumentId=CompanyDocumentId)
            companyDocuments.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    




class UploadCompanyDocuments(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, CompanyDocumentId="", *args, **kwargs):
        try:

                companyDocuments = CompanyDocuments.objects.get(
                    CompanyDocumentId=CompanyDocumentId)
                try:
                    CompanyDocuments.objects.get(
                        CompanyDocumentId=CompanyDocumentId).Document.delete(save=True)
                except:
                    p = ""
                Serializer = UploadCompanyDocumentsSerializer(
                    companyDocuments, data=request.data)
                if Serializer.is_valid():
                    Serializer.save()
                    return JsonResponse("ok", safe=False)
                else:
                    return JsonResponse("", safe=False)
        except:
            return JsonResponse("", safe=False)
        




# @csrf_exempt
# @swagger_auto_schema(method='GET',operation_description="NOTE: API for get Company by CompanyId",)
# @api_view(['GET','DELETE'])
# @retry(retries=3, delay=2)
# def CompanyPerformanceById(request, CompanyId=""):
#     try:
#         if request.method == 'GET': 
#             company = Company.objects.get(
#                     CompanyId=CompanyId)
#             companySerializer = CompanySerializer(
#                     company)
#             companyData=companySerializer.data
#             work_status_count = {'Pending': 0, 'Performance': 0}
#             projects = Project.objects.filter(CompanyId=CompanyId)
#             projectSerializer = ProjectSerializer(projects, many=True)

            
#             total_points_gain = 0
#             total_count = 0

#             for project in projectSerializer.data:
#                 currentMonthYear=date.today().strftime("%Y-%m")
#                 startDate=f"{currentMonthYear}-1"
#                 endDate=f"{currentMonthYear}-31"
#                 start_date = datetime.strptime(startDate, '%Y-%m-%d')
#                 end_date = datetime.strptime(endDate, '%Y-%m-%d')

#                 projectTasks = ProjectTask.objects.filter(CreatedDate__range=(start_date,end_date),ProjectId=project['ProjectId'])
#                 projectTaskSerializer = ProjectTaskSerializer(projectTasks, many=True)
                
#                 work_status_count = {'Pending': 0, 'Performance': 0}
#                 for task in projectTaskSerializer.data:
                    
                    
#                     if task['Status'] in ['7', '8', '9']:
#                         total_points_gain += float(task['CompletionPoint'])
#                         total_count += 1
#                     if task['Status'] in ['1', '2', '10']:
#                         work_status_count['Pending'] += 1
                        
#                 companyData['DashboardData'] = work_status_count  
                
#                 if total_count > 0:
#                     work_status_count['Performance'] = total_points_gain / total_count
#                 bestPerformer=AllStaffPerformancebyCompany(CompanyId)
#                 companyData['bestPerformer']="N/A"
#                 if bestPerformer:
#                     companyData['bestPerformer'] = max(bestPerformer, key=lambda ev: ev['Performance'])
                
#             return JsonResponse(companyData, safe=False)
    
#         else:
#             return JsonResponse("", safe=False)
#     except:
#         return JsonResponse("", safe=False)
    
import calendar
@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get Company by CompanyId")
@api_view(['GET'])
@retry(retries=3, delay=2)
def CompanyPerformanceById(request, CompanyId=""):
    # try:
        if request.method == 'GET': 
            company = Company.objects.get(CompanyId=CompanyId)
            companySerializer = CompanySerializer(company)
            companyData = companySerializer.data
            work_status_count = {'Pending': 0, 'Performance': 0}

            projects = Project.objects.filter(CompanyId=CompanyId)
            projectSerializer = ProjectSerializer(projects, many=True)
            
            total_points_gain = 0
            total_count = 0

            if projects.exists():  
                for project in projectSerializer.data:
                    currentMonthYear = date.today().strftime("%Y-%m")
                    year, month = map(int, currentMonthYear.split('-'))

                    # Get the last day of the current month
                    last_day_of_month = calendar.monthrange(year, month)[1]

                    startDate = f"{currentMonthYear}-01"
                    endDate = f"{currentMonthYear}-{last_day_of_month}"

                    start_date = datetime.strptime(startDate, '%Y-%m-%d')
                    end_date = datetime.strptime(endDate, '%Y-%m-%d')

                    projectTasks = ProjectTask.objects.filter(CreatedDate__range=(start_date, end_date), ProjectId=project['ProjectId'])
                    projectTaskSerializer = ProjectTaskSerializer(projectTasks, many=True)
                    
                    if projectTasks.exists():  
                        for task in projectTaskSerializer.data:
                            if task['Status'] in ['7', '8', '9']:
                                total_points_gain += float(task['CompletionPoint'])
                                total_count += 1
                            if task['Status'] in ['1', '2', '10']:
                                work_status_count['Pending'] += 1

                        if total_count > 0:
                            work_status_count['Performance'] = total_points_gain / total_count
                    else:
                       
                        work_status_count = {'Pending': 0, 'Performance': 0}
            else:
               
                work_status_count = {'Pending': 0, 'Performance': 0}

            companyData['DashboardData'] = work_status_count

            bestPerformer = AllStaffPerformancebyCompany(CompanyId)
            companyData['bestPerformer'] = "N/A"
            if bestPerformer:
                companyData['bestPerformer'] = max(bestPerformer, key=lambda ev: ev['Performance'])
            # Fetch staff and clients in bulk
            staff = Staff.objects.filter(CompanyId=CompanyId)
            client = Client.objects.filter(CompanyId=CompanyId)

            # Serialize the data
            staff_count = staff.count()
            client_count = client.count()

            # Fetch site settings and serialize
            siteSettings = SiteSettings.objects.filter(CompanyId=CompanyId).first()
            siteSettings_data = SiteSettingsSerializer(siteSettings).data if siteSettings else {}

            # Determine flags for site settings and logo
            siteSettings_flag = bool(siteSettings_data.get('StaffCodePrefix'))
            logo_flag = bool(siteSettings_data.get('Logo'))

            # Compile the account completion data
            account_completion = {
                'Staff': staff_count,
                'Client': client_count,
                'SiteSettings': siteSettings_flag,
                'Logo': logo_flag
            }
            companyData['account_completion']=account_completion
            return JsonResponse(companyData, safe=False)
        
       
        
        else:
            return JsonResponse("", safe=False)
    
    # except:
    #     return JsonResponse("", safe=False)



@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get Company by CompanyId",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def DeleteCompanyDataByCompanyId(request, CompanyId=""):
    try:
        if request.method == 'GET':          
            category=Category.objects.filter(CompanyId=CompanyId)
            for cate in category:
                report=Report.objects.filter(CategoryId=cate.CategoryId)
                for rep in report:
                    reportRefFiles=ReportRefFile.objects.filter(ReportId=rep.ReportId)
                    for refFiles in reportRefFiles:
                        refFiles.ReportRefFile.delete(save=True)
                        refFiles.delete()
                    rep.delete()
                cate.delete()


            client=Client.objects.filter(CompanyId=CompanyId)
            for cli in client:
                clientOtherDetails=ClientOtherDetails.objects.filter(ClientId=cli.ClientId)
                for details in clientOtherDetails:
                    clientDocuments=ClientDocuments.objects.filter(ClientOtherDetailId=details.ClientOtherDetailId)
                    for clientdoc in clientDocuments:
                        clientdoc.Document.delete(save=True)
                        clientdoc.delete()
                    details.delete()
                
                clientAddress=ClientAddress.objects.filter(ClientId=cli.ClientId).delete()
                contactPerson=ContactPerson.objects.filter(ClientId=cli.ClientId).delete()
                cli.delete()
            

            credentials=Credentials.objects.filter(CompanyId=CompanyId).delete()

            enquiry=Enquiry.objects.filter(CompanyId=CompanyId)
            for enq in enquiry:
                followUp=FollowUp.objects.filter(EnquiryId=enq.EnquiryId).delete()
                enq.delete()


            notes=MeetingNotes.objects.filter(CompanyId=CompanyId)
            for note in notes:
                noteDocument=MeetingNoteDocument.objects.filter(MeetingNoteId=note.MeetingNoteId)
                for notedoc in noteDocument:
                    notedoc.Document.delete(save=True)
                    notedoc.delete()
                note.delete()

            project=Project.objects.filter(CompanyId=CompanyId)
            for proj in project:
                projectTask=ProjectTask.objects.filter(ProjectId=proj.ProjectId)
                for task in projectTask:
                    projectTaskTiming=ProjectTaskTiming.objects.filter(ProjectTaskId=task.ProjectTaskId).delete()
                    projectTaskFile=ProjectTaskFile.objects.filter(ProjectTaskId=task.ProjectTaskId)
                    for file in projectTaskFile:
                        file.TaskFile.delete(save=True)
                        file.delete()
                    TaskReviews.objects.filter(ProjectTaskId=task.ProjectTaskId).delete()

                    comments=Comments.objects.filter(ProjectTaskId=task.ProjectTaskId)
                    for com in comments:
                        commentFile=CommentFile.objects.filter(CommentId=com.CommentId)
                        for comfile in commentFile:
                            comfile.CommentFile.delete(save=True)
                            comfile.delete()
                        com.delete()
                    task.delete()
                proj.delete()
            
            quotation=Quotation.objects.filter(CompanyId=CompanyId)
            for quot in quotation:
                QuotationItem.objects.filter(QuotationId=quot.QuotationId).delete()
                quotationFile=QuotationFile.objects.filter(QuotationId=quot.QuotationId)
                for quotfile in quotationFile:
                    quotfile.QuoteFile.delete(save=True)
                    quotfile.delete()
                quot.delete()

            invoice=Invoice.objects.filter(CompanyId=CompanyId)
            for inv in invoice:
                InvoiceItem.objects.filter(InvoiceId=inv.InvoiceId).delete()
                invoiceDocument=InvoiceDocument.objects.filter(InvoiceId=inv.InvoiceId)
                for invfile in invoiceDocument:
                    invfile.Document.delete(save=True)
                    invfile.delete()
                inv.delete()


            paymentReceived=PaymentReceived.objects.filter(CompanyId=CompanyId)
            for payment in paymentReceived:
                PaymentReceivedDetail.objects.filter(PaymentReceivedId=payment.PaymentReceivedId).delete()
                paymentDocument=PaymentDocument.objects.filter(PaymentReceivedId=payment.PaymentReceivedId)
                for payfile in paymentDocument:
                    payfile.Document.delete(save=True)
                    payfile.delete()
                payment.delete()

            staff=Staff.objects.filter(CompanyId=CompanyId)
            for user in staff:
                StaffGuardian.objects.filter(StaffId=user.StaffId).delete()
                LeaveApplication.objects.filter(StaffId=user.StaffId).delete()
                SalarySlip.objects.filter(StaffId=user.StaffId).delete()
                MoveOnRegister.objects.filter(StaffId=user.StaffId).delete()
                staffdocuments=StaffDocuments.objects.filter(StaffId=user.StaffId)
                for staffdoc in staffdocuments:
                    staffdoc.Document.delete(save=True)
                    staffdoc.delete()
                notification=Notification.objects.filter(FromUser=user.StaffId).delete()
                Todo.objects.filter(UserId=user.StaffId).delete()
                Login.objects.filter(UserId=user.StaffId).delete()
                LoginHistory.objects.filter(UserId=user.StaffId).delete()
                user.delete()
            Designation.objects.filter(CompanyId=CompanyId).delete()
            UserGroup.objects.filter(CompanyId=CompanyId).delete()
            return JsonResponse("Deleted Successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
            








