from django.shortcuts import render
from django.http.response import JsonResponse
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from app_login.models import Login
from app_client.models import Client, SupportTicket, ClientDocuments
from app_project.models import Project, ProjectDocument, ProjectService
from app_sale.models import Quotation, Invoice, PaymentReceived
import uuid

class ClientLoginView(APIView):
    def post(self, request):
        data = JSONParser().parse(request)
        email = data.get('EmailId')
        password = data.get('Password')
        try:
            # Login lookup
            login_entry = Login.objects.get(EmailId=email, Password=password)
            # Find the client
            client = Client.objects.get(ClientId=login_entry.UserId)
            
            client_data = {
                'ClientId': client.ClientId,
                'FirstName': client.FirstName,
                'LastName': client.LastName,
                'CompanyName': client.CompanyName,
                'EmailId': client.EmailId,
                'Phone1': client.Phone1,
            }
            return JsonResponse({'status': 'SUCCESS', 'client': client_data}, safe=False)
        except Exception as e:
            return JsonResponse({'status': 'FAILED', 'message': 'Invalid credentials or client not found'}, safe=False)

class ClientProjectListView(APIView):
    def get(self, request):
        client_id = request.GET.get('client_id')
        if not client_id:
            return JsonResponse({'status': 'FAILED', 'message': 'Client ID required'}, safe=False)
        
        projects = Project.objects.filter(ClientId=client_id)
        project_list = []
        for p in projects:
            project_list.append({
                'ProjectId': p.ProjectId,
                'ProjectName': p.ProjectName,
                'StartDate': p.StartDate,
                'EndDate': p.EndDate,
                'Status': p.Status.Status if p.Status else 'Unknown',
            })
        return JsonResponse({'status': 'SUCCESS', 'data': project_list}, safe=False)

class ClientProjectDetailView(APIView):
    def get(self, request, project_id):
        client_id = request.GET.get('client_id')
        try:
            project = Project.objects.get(ProjectId=project_id, ClientId=client_id)
            
            # Quotes
            quotes = list(Quotation.objects.filter(ProjectId=project_id).values('QuotationId', 'QuotationNumber', 'TotalAmount', 'ApprovalStatus', 'QuoteDate'))
            # Invoices
            # Note: Invoice model might not have ProjectId, but maybe ClientId. Let's assume it has ClientId and we filter.
            invoices = list(Invoice.objects.filter(ClientId=client_id).values('InvoiceId', 'InvoiceNumber', 'TotalAmount', 'AmountDue', 'Status', 'DueDate'))
            # Payments
            payments = list(PaymentReceived.objects.filter(ClientId=client_id).values('PaymentReceivedId', 'AmountReceived', 'PaymentDate', 'PaymentMode'))
            # Documents
            docs = list(ProjectDocument.objects.filter(ProjectId=project_id).values('ProjectDocumentId', 'DocumentName', 'Document', 'UploadDate', 'UploadedBy'))
            # Services
            services = list(ProjectService.objects.filter(ProjectId=project_id).values('ProjectServiceId', 'ServiceName', 'ExpiryDate', 'Cost'))
            # Tickets
            tickets = list(SupportTicket.objects.filter(ProjectId=project_id).values('TicketId', 'Subject', 'Status', 'Priority'))
            
            data = {
                'ProjectId': project.ProjectId,
                'ProjectName': project.ProjectName,
                'Description': project.Description,
                'StartDate': project.StartDate,
                'quotes': quotes,
                'invoices': invoices,
                'payments': payments,
                'documents': docs,
                'services': services,
                'tickets': tickets
            }
            return JsonResponse({'status': 'SUCCESS', 'data': data}, safe=False)
        except Exception as e:
            return JsonResponse({'status': 'FAILED', 'message': str(e)}, safe=False)

class ProjectDocumentUploadView(APIView):
    def post(self, request, project_id):
        client_id = request.POST.get('client_id')
        file = request.FILES.get('document')
        doc_name = request.POST.get('document_name', 'Uploaded File')
        
        if not file:
            return JsonResponse({'status': 'FAILED', 'message': 'No file provided'}, safe=False)
            
        try:
            doc = ProjectDocument.objects.create(
                ProjectId=project_id,
                ClientId=client_id,
                DocumentName=doc_name,
                Document=file,
                UploadedBy='Client'
            )
            return JsonResponse({'status': 'SUCCESS', 'message': 'Document uploaded'}, safe=False)
        except Exception as e:
            return JsonResponse({'status': 'FAILED', 'message': str(e)}, safe=False)

class ClientTicketCreateView(APIView):
    def post(self, request):
        data = JSONParser().parse(request)
        try:
            ticket = SupportTicket.objects.create(
                ClientId=data.get('client_id'),
                ProjectId=data.get('project_id'),
                Subject=data.get('subject'),
                Priority=data.get('priority', 'medium'),
                Status='open'
            )
            return JsonResponse({'status': 'SUCCESS', 'message': 'Ticket created'}, safe=False)
        except Exception as e:
            return JsonResponse({'status': 'FAILED', 'message': str(e)}, safe=False)
