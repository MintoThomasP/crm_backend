from datetime import date, datetime,timedelta
from django.db import connection
from django.core.cache import cache
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
from app_company.models import Company, CompanyBankDetails, CompanyDocuments
from app_company.serializers import CompanyBankDetailsSerializer, CompanyDocumentsSerializer, CompanySerializer, SaveCompanyDocumentsSerializer, UploadCompanyDocumentsSerializer
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
            company = Company.objects.filter(ActiveStatus=1)
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
           
            company.ActiveStatus=0
            company.save()

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
    if request.method == 'GET':
        # cache_key = f"company_performance_{CompanyId}"
        # cached_data = cache.get(cache_key)
        # if cached_data:
        #     return JsonResponse(cached_data, safe=False)

            company = Company.objects.get(CompanyId=CompanyId)
            companySerializer = CompanySerializer(company)
            companyData = companySerializer.data
            

            projects = Project.objects.filter(CompanyId=CompanyId,ActiveStatus=1)
            projectSerializer = ProjectSerializer(projects, many=True)
            total_points_gain = 0
            total_count = 0

            work_status_count = {'Pending': 0, 'Performance': 0,'Sales':0}
            if projects.exists():  
                for project in projectSerializer.data:
                    currentMonthYear = date.today().strftime("%Y-%m")
                    year, month = map(int, currentMonthYear.split('-'))

                    # Get the last day of the current month
                    last_day_of_month = calendar.monthrange(year, month)[1]

                    startDate = f"{currentMonthYear}-01"
                    endDate = f"{currentMonthYear}-{last_day_of_month}"

                    start_date = datetime.strptime(startDate, '%Y-%m-%d')
                    end_date = datetime.strptime(endDate, '%Y-%m-%d')+ timedelta(days=1)

                    projectTasks = ProjectTask.objects.filter(CreatedDate__range=(start_date, end_date), ProjectId=project['ProjectId'])
                    projectTaskSerializer = ProjectTaskSerializer(projectTasks, many=True)
                    if projectTasks.exists(): 
                        for task in projectTaskSerializer.data:
                            if task['Status'] in ['7', '8', '9']:
                                total_points_gain += float(task['CompletionPoint'])
                                total_count += 1

                        if total_count > 0:
                            work_status_count['Performance'] = total_points_gain / total_count
                    projectTasks = ProjectTask.objects.filter(ProjectId=project['ProjectId'],TaskType='Task')
                    projectTaskSerializer = ProjectTaskSerializer(projectTasks, many=True)
                   
                    if projectTasks.exists(): 
                        for task in projectTaskSerializer.data:
                            if task['Status'] in ['1','2', '4', '5', '6', '10']:
                                work_status_count['Pending'] += 1

                    # else:
                       
                    #     work_status_count = {'Pending': 0, 'Performance': 0,'Sales':0}
            else:
               
                work_status_count = {'Pending': 0, 'Performance': 0,'Sales':0}

            companyData['DashboardData'] = work_status_count

            bestPerformer = AllStaffPerformancebyCompany(CompanyId)
            companyData['bestPerformer'] = "N/A"
            if bestPerformer:
                companyData['bestPerformer'] = max(bestPerformer, key=lambda ev: ev['Performance'])
           
            staff = Staff.objects.filter(CompanyId=CompanyId,Status=1)
            client = Client.objects.filter(CompanyId=CompanyId,ActiveStatus=1)

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
            
            
            
            sql="WITH RECURSIVE DateSeries AS ( SELECT CURDATE() - INTERVAL 30 DAY AS task_date UNION ALL SELECT task_date + INTERVAL 1 DAY FROM DateSeries WHERE task_date + INTERVAL 1 DAY <= CURDATE() ) SELECT DATE_FORMAT(ds.task_date, '%b %d') AS formatted_date, IFNULL(COUNT(t.ProjectTaskId), 0) AS total_completed_tasks FROM DateSeries ds LEFT JOIN app_project_projecttask t ON DATE(t.EndDate) = ds.task_date AND t.Status IN (7, 8, 9) AND CompanyId='"+CompanyId+"' WHERE ds.task_date BETWEEN CURDATE() - INTERVAL 30 DAY AND CURDATE() GROUP BY ds.task_date, t.CompanyId ORDER BY ds.task_date;"
            task_performance = connection.cursor()
            task_performance.execute(sql)
            field_names = [i[0] for i in task_performance.description]
            task_performance_data = []
            for task in task_performance.fetchall():
                j = 0
                task_data = {}
                for col in task:
                    if j < len(field_names):
                        task_data[str(field_names[j])] = col
                        j = j + 1
                task_performance_data.append(task_data)
            companyData['StaffPerformance']=task_performance_data
            
            
            sql="SELECT c.CustomerDisplayName, COALESCE(COUNT(t.ProjectTaskId), 0) AS total_completed_tasks FROM app_client_client c JOIN app_project_projecttask t ON c.ClientId = t.ClientId AND t.Status IN (7, 8, 9) AND t.EndDate >= CURDATE() - INTERVAL 60 DAY AND  t.CompanyId='"+CompanyId+"'  AND  c.CompanyId='"+CompanyId+"' GROUP BY c.ClientId ORDER BY total_completed_tasks DESC LIMIT 10;"
            
            task_performance = connection.cursor()
            task_performance.execute(sql)
            field_names = [i[0] for i in task_performance.description]
            task_performance_data = []
            for task in task_performance.fetchall():
                j = 0
                task_data = {}
                for col in task:
                    if j < len(field_names):
                        task_data[str(field_names[j])] = col
                        j = j + 1
                task_performance_data.append(task_data)
            companyData['ClientTouchpoint']=task_performance_data
            
            sql="WITH RECURSIVE date_series AS ( SELECT CURDATE() - INTERVAL 6 DAY AS DateValue UNION ALL SELECT DateValue + INTERVAL 1 DAY FROM date_series WHERE DateValue + INTERVAL 1 DAY <= CURDATE() ) SELECT DATE_FORMAT(ds.DateValue, '%a') AS DayOfWeek, ds.DateValue AS Date, COALESCE(SUM(TIMESTAMPDIFF(HOUR, t.MoveOutDateTime, t.MoveInDateTime)), 0) AS TotalWorkingHours FROM date_series ds LEFT JOIN app_staff_moveonregister t ON DATE(t.MoveInDateTime) = ds.DateValue LEFT JOIN app_staff_staff s ON t.StaffId = s.StaffId AND s.CompanyId='"+CompanyId+"'  GROUP BY ds.DateValue ORDER BY ds.DateValue;"
            task_performance = connection.cursor()
            task_performance.execute(sql)
            field_names = [i[0] for i in task_performance.description]
            task_performance_data = []
            for task in task_performance.fetchall():
                j = 0
                task_data = {}
                for col in task:
                    if j < len(field_names):
                        task_data[str(field_names[j])] = col
                        j = j + 1
                task_performance_data.append(task_data)
            companyData['7DayWorkingHours']=task_performance_data
            
            sql="SELECT DATE(d.days) AS `Date`, DATE_FORMAT(d.days, '%a') AS `DayName`, COALESCE(COUNT(t.ProjectTaskId), 0) AS `TotalCompletedTasks` FROM ( SELECT CURDATE() - INTERVAL n DAY AS days FROM ( SELECT 0 AS n UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 ) AS numbers ) AS d LEFT JOIN app_project_projecttask t ON DATE(t.CreatedDate) = DATE(d.days) AND t.Status IN (7, 8, 9) AND CompanyId='"+CompanyId+"' GROUP BY d.days ORDER BY d.days DESC;"
            task_performance = connection.cursor()
            task_performance.execute(sql)
            field_names = [i[0] for i in task_performance.description]
            task_performance_data = []
            for task in task_performance.fetchall():
                j = 0
                task_data = {}
                for col in task:
                    if j < len(field_names):
                        task_data[str(field_names[j])] = col
                        j = j + 1
                task_performance_data.append(task_data)
            companyData['7DayTaskCount']=task_performance_data
            
            
            sql="SELECT SUM(CASE WHEN ScheduledDeadline < CURDATE() THEN 1 ELSE 0 END) AS Overdue, SUM(CASE WHEN ScheduledDeadline = CURDATE() THEN 1 ELSE 0 END) AS Due, SUM(CASE WHEN ScheduledDeadline > CURDATE() THEN 1 ELSE 0 END) AS Upcoming, SUM(CASE WHEN ScheduledDeadline IS NULL THEN 1 ELSE 0 END) AS NoDeadline FROM app_project_projecttask WHERE Status IN (1, 2, 4, 5, 6, 10) AND CompanyId='"+CompanyId+"';"
            task_performance = connection.cursor()
            task_performance.execute(sql)
            field_names = [i[0] for i in task_performance.description]
            task_performance_data = []
            for task in task_performance.fetchall():
                j = 0
                task_data = {}
                for col in task:
                    if j < len(field_names):
                        task_data[str(field_names[j])] = col
                        j = j + 1
                task_performance_data.append(task_data)
            companyData['TaskDetails']=task_performance_data
            # cache.set(cache_key, companyData, 300)
            return JsonResponse(companyData, safe=False)
        
       
        
        # else:
        #     return JsonResponse("", safe=False)
    
    # except:
    #     return JsonResponse("", safe=False)



@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get Company by CompanyId",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def DeleteCompanyDataByCompanyId(request, CompanyId=""):
    try:
        if request.method == 'GET':          
            company = Company.objects.get(CompanyId=CompanyId)
            companyDocuments=CompanyDocuments.objects.filter(CompanyId=CompanyId)
            for compdoc in companyDocuments:
                compdoc.Document.delete(save=True)
                compdoc.delete
            login=Login.objects.get(UserId=CompanyId)
            login.delete

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


            client=Client.objects.filter(CompanyId=CompanyId,ActiveStatus=1)
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

            project=Project.objects.filter(CompanyId=CompanyId,ActiveStatus=1)
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

            staff=Staff.objects.filter(CompanyId=CompanyId,Status=1)
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
            company.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
            






@csrf_exempt
@swagger_auto_schema(method='POST', request_body=CompanyBankDetailsSerializer,operation_description="NOTE: API for save CompanyBankDetails")
@swagger_auto_schema(method='PUT', request_body=CompanyBankDetailsSerializer,operation_description="NOTE: API for edit CompanyBankDetails")
@api_view(['POST','PUT'])
@retry(retries=3, delay=2)
def CompanyBankDetailsApi(request):
    try:
        if request.method == 'POST':
            companyBankDetailsData = JSONParser().parse(request)
            companyBankDetailsSerializer = CompanyBankDetailsSerializer(
                data=companyBankDetailsData)
            if companyBankDetailsData['PrimaryAccount']==True:
                companyBankDetails=CompanyBankDetails.objects.filter(PrimaryAccount=1,CompanyId=companyBankDetailsData['CompanyId'])
                for bank in companyBankDetails:
                    bank.PrimaryAccount=False
                    bank.save()
            if companyBankDetailsSerializer.is_valid():
                companyBankDetailsSerializer.save()
                companyBankDetails = CompanyBankDetails.objects.filter(CompanyId=companyBankDetailsData['CompanyId'])
                if len(companyBankDetails)==1:
                    for row in companyBankDetails:
                        row.PrimaryAccount=True
                        row.save()
                
                return JsonResponse(companyBankDetailsSerializer.data['BankDetailId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            companyBankDetailsData = JSONParser().parse(request)
            companyBankDetails = CompanyBankDetails.objects.get(
                BankDetailId=companyBankDetailsData['BankDetailId'])
            companyBankDetailsSerializer = CompanyBankDetailsSerializer(
                companyBankDetails, data=companyBankDetailsData)
            if companyBankDetailsData['PrimaryAccount']==True:
                companyBankDetails=CompanyBankDetails.objects.filter(PrimaryAccount=1,CompanyId=companyBankDetailsData['CompanyId'])
                for bank in companyBankDetails:
                    bank.PrimaryAccount=False
                    bank.save()
            if companyBankDetailsSerializer.is_valid():
                companyBankDetailsSerializer.save()
                
                return JsonResponse(companyBankDetailsSerializer.data['BankDetailId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get CompanyBankDetails by CompanyBankDetailsId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete CompanyBankDetails by CompanyBankDetailsId",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def CompanyBankDetailsApiById(request, BankDetailId=""):
    try:
        if request.method == 'GET': 
            companyBankDetails = CompanyBankDetails.objects.get(
                    BankDetailId=BankDetailId)
            companyBankDetailsSerializer = CompanyBankDetailsSerializer(
                    companyBankDetails)
            return JsonResponse(companyBankDetailsSerializer.data, safe=False)
        elif request.method == 'DELETE':
            companyBankDetails = CompanyBankDetails.objects.get(BankDetailId=BankDetailId)
            companyBankDetails.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    



@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get CompanyBankDetails by CompanyId",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def CompanyBankDetailsApiByCompanyId(request, CompanyId=""):
    try:
        if request.method == 'GET': 
            companyBankDetails = CompanyBankDetails.objects.filter(
                    CompanyId=CompanyId)
            companyBankDetailsSerializer = CompanyBankDetailsSerializer(
                companyBankDetails,many=True)
            return JsonResponse(companyBankDetailsSerializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)



# from twilio.rest import Client
# @csrf_exempt
# @swagger_auto_schema(method='GET',operation_description="API for get CompanyBankDetails by CompanyId",)
# @api_view(['GET'])
# def SendWhatsappmessage(request):
#     account_sid = 'REMOVED_TWILIO_SID'
#     auth_token = 'REMOVED_TWILIO_TOKEN'
#     client = Client(account_sid, auth_token)

    
#     try:
       
#         message = client.messages.create(
#             body='Hello, this is a test message from Python!',
#             from_='whatsapp:+14155238886', 
#             to='whatsapp:+919526864524'
#         )
       
       
#         return JsonResponse({
#             "status": "sent",
#             "message_sid": message.sid,
#             "date_created": str(message.date_created),
#             "to": message.to,
#             "from": message.from_,
#             "body": message.body
#         }, safe=False)

#     except Exception as e:
#         return JsonResponse({"status": "failed", "error": str(e)}, safe=False)



# import pywhatkit
# @csrf_exempt
# @api_view(['GET'])
# def SendWhatsappmessage(request):
#     myobj = datetime.now()
#     hour=myobj.hour
#     minute=myobj.minute + 1
#     pywhatkit.sendwhatmsg('+919526844444','Test taw4a 4ya55',hour,minute)
#     return JsonResponse("ok",safe=False)
    


# from django.shortcuts import redirect
# @csrf_exempt
# def SendWhatsappmessage(request):
#     phone_number = '+919526864524'  
#     message = 'Hello from Django!' 
#     whatsapp_url = f"https://wa.me/{phone_number[1:]}?text={message.replace(' ', '%20')}"
#     return redirect(whatsapp_url)


@csrf_exempt
@api_view(['GET'])
@retry(retries=3, delay=2)
def get_dashboard_analytics_api(request, CompanyId=""):
    try:
        cache_key = f"dashboard_analytics_{CompanyId}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return JsonResponse(cached_data, safe=False)

        # 1. Sales Pipeline Metrics
        invoices = Invoice.objects.filter(CompanyId=CompanyId)
        quotations = Quotation.objects.filter(CompanyId=CompanyId)
        
        total_invoices_val = 0.0
        for inv in invoices:
            try:
                total_invoices_val += float(inv.TotalAmount or 0.0)
            except:
                pass
                
        total_quotes_val = 0.0
        for q in quotations:
            try:
                total_quotes_val += float(q.TotalAmount or 0.0)
            except:
                pass

        sales_metrics = {
            "invoice_count": invoices.count(),
            "invoice_volume": f"{total_invoices_val:.2f}",
            "quotation_count": quotations.count(),
            "quotation_volume": f"{total_quotes_val:.2f}"
        }

        # 2. Finance Metrics (Cash Flow & Aging Receivables)
        inflow = 0.0
        outflow = 0.0
        with connection.cursor() as cursor:
            sql = """
                SELECT COALESCE(SUM(CAST(ji.Debit AS DECIMAL(15,2))), 0) AS Inflow, 
                       COALESCE(SUM(CAST(ji.Credit AS DECIMAL(15,2))), 0) AS Outflow 
                FROM app_accounting_journalitem ji 
                JOIN app_accounting_account a ON ji.AccountId = a.AccountId 
                WHERE a.IsCashOrBank = 1 AND a.CompanyId = %s
            """
            cursor.execute(sql, [CompanyId])
            row = cursor.fetchone()
            if row:
                inflow = float(row[0])
                outflow = float(row[1])

        # Aging Receivables calculation
        current_date_str = date.today().strftime("%Y-%m-%d")
        aging_current = 0.0
        aging_30 = 0.0
        aging_60 = 0.0
        aging_over_60 = 0.0

        for inv in invoices:
            if not inv.AmountDue:
                continue
            try:
                amount_due = float(inv.AmountDue)
                if amount_due <= 0.0:
                    continue
                if not inv.DueDate:
                    aging_current += amount_due
                    continue
                
                due_dt = datetime.strptime(inv.DueDate, "%Y-%m-%d").date()
                today_dt = date.today()
                diff_days = (today_dt - due_dt).days

                if diff_days <= 0:
                    aging_current += amount_due
                elif diff_days <= 30:
                    aging_30 += amount_due
                elif diff_days <= 60:
                    aging_60 += amount_due
                else:
                    aging_over_60 += amount_due
            except:
                pass

        finance_metrics = {
            "cash_flow": {
                "inflow": f"{inflow:.2f}",
                "outflow": f"{outflow:.2f}",
                "net": f"{(inflow - outflow):.2f}"
            },
            "receivables_aging": {
                "current": f"{aging_current:.2f}",
                "1_30_days": f"{aging_30:.2f}",
                "31_60_days": f"{aging_60:.2f}",
                "over_60_days": f"{aging_over_60:.2f}"
            }
        }

        # 3. Customer Dashboard Metrics
        clients_count = Client.objects.filter(CompanyId=CompanyId, ActiveStatus=1).count()
        enquiries_count = Enquiry.objects.filter(CompanyId=CompanyId).count()
        followups_count = FollowUp.objects.filter(CompanyId=CompanyId).count()

        customer_metrics = {
            "active_clients": clients_count,
            "total_enquiries": enquiries_count,
            "total_followups": followups_count
        }

        # 4. Calendar Timeline Widget Feeds
        calendar_events = []
        # Due Invoices
        for inv in invoices:
            try:
                amount_due = float(inv.AmountDue or 0.0)
                if amount_due > 0.0 and inv.DueDate:
                    calendar_events.append({
                        "id": inv.InvoiceId,
                        "title": f"Invoice Due: {inv.InvoiceNumber or 'N/A'}",
                        "date": inv.DueDate,
                        "type": "invoice_due",
                        "amount": f"{amount_due:.2f}"
                    })
            except:
                pass

        # Project Task Deadlines
        tasks = ProjectTask.objects.filter(CompanyId=CompanyId, Status__in=[1, 2, 4, 5, 6, 10])
        for t in tasks:
            if t.ScheduledDeadline:
                try:
                    deadline_str = t.ScheduledDeadline
                    if isinstance(deadline_str, (date, datetime)):
                        deadline_str = deadline_str.strftime("%Y-%m-%d")
                    else:
                        deadline_str = str(deadline_str)[:10]
                    calendar_events.append({
                        "id": t.ProjectTaskId,
                        "title": f"Task: {t.TaskName or 'N/A'}",
                        "date": deadline_str,
                        "type": "task_deadline",
                        "priority": "normal"
                    })
                except:
                    pass

        # Sort calendar by date
        calendar_events = sorted(calendar_events, key=lambda x: x['date'])[:15]

        analytics_data = {
            "sales": sales_metrics,
            "finance": finance_metrics,
            "customer": customer_metrics,
            "calendar": calendar_events
        }

        cache.set(cache_key, analytics_data, 300)
        return JsonResponse(analytics_data, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, safe=False)