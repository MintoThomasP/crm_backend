from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from app_client.models import Client, SupportTicket
from app_project.models import Project
from app_login.models import Login
from .models import ClientPortalAccess, ClientDocumentUpload, ServiceExpiryAlert
from .serializers import ClientPortalAccessSerializer, ClientDocumentUploadSerializer, ServiceExpiryAlertSerializer
from app_project.serializers import ProjectSerializer
from app_client.serializers import SupportTicketSerializer
import uuid

@api_view(['GET'])
def client_projects(request, client_id):
    projects = Project.objects.filter(ClientId=client_id)
    serializer = ProjectSerializer(projects, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def client_tickets(request, client_id):
    tickets = SupportTicket.objects.filter(ClientId=client_id)
    serializer = SupportTicketSerializer(tickets, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def client_portal_login(request):
    email = request.data.get('EmailId')
    password = request.data.get('Password')
    try:
        login_obj = Login.objects.get(EmailId=email, Password=password)
        access = ClientPortalAccess.objects.get(LoginId=login_obj.LoginId, IsActive=True)
        return Response({
            'token': 'client-token-' + str(uuid.uuid4()), 
            'ClientId': access.ClientId, 
            'UserId': login_obj.UserId
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': 'Invalid credentials or no portal access'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def client_dashboard_stats(request, client_id):
    active_projects = Project.objects.filter(ClientId=client_id).count()
    open_tickets = SupportTicket.objects.filter(ClientId=client_id, Status='open').count()
    
    return Response({
        'active_projects': active_projects,
        'pending_invoices': 0,
        'unpaid_balance': 0,
        'open_tickets': open_tickets
    }, status=status.HTTP_200_OK)

class ClientDocumentUploadViewSet(viewsets.ModelViewSet):
    queryset = ClientDocumentUpload.objects.all()
    serializer_class = ClientDocumentUploadSerializer

    def get_queryset(self):
        client_id = self.request.query_params.get('client_id')
        if client_id:
            return self.queryset.filter(ClientId=client_id)
        return self.queryset

class ServiceExpiryAlertViewSet(viewsets.ModelViewSet):
    queryset = ServiceExpiryAlert.objects.all()
    serializer_class = ServiceExpiryAlertSerializer
