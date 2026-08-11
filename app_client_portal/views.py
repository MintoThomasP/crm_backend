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
from app_default.models import UserType
import uuid

@api_view(['POST'])
def generate_portal_access(request):
    client_id = request.data.get('ClientId')
    email = request.data.get('EmailId')
    password = request.data.get('Password')
    
    if not all([client_id, email, password]):
        return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        user_type, _ = UserType.objects.get_or_create(UserType='Client')
        
        login_obj, created = Login.objects.get_or_create(
            UserId=client_id,
            EmailId=email,
            defaults={'Password': password, 'UserType': user_type, 'Status': 1}
        )
        
        if not created:
            login_obj.Password = password
            login_obj.save()
            
        access_obj, created = ClientPortalAccess.objects.get_or_create(
            ClientId=client_id,
            LoginId=login_obj.LoginId,
            defaults={'IsActive': True}
        )
        
        if not created:
            access_obj.IsActive = True
            access_obj.save()
            
        return Response({'message': 'Portal access created successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
