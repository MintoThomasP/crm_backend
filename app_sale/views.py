from django.shortcuts import render
import os
from django.db.models import Q
import smtplib
from email.message import EmailMessage
import codecs
import os
from django.db.models import Max
from django.conf import settings 
# Create your views here.
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

from app_client.models import Client, ClientAddress
from app_client.serializers import ClientSerializer
from app_default.models import InvoiceStatus, PaymentMode
from app_default.serializers import InvoiceStatusSerializer
from app_default.views import retry
from app_project.models import Project
from app_project.serializers import ProjectSerializer
from app_sale.models import Invoice, InvoiceDocument, InvoiceItem, PaymentReceived, Quotation, QuotationFile, QuotationItem
from app_sale.serializers import InvoiceDocumentSerializer, InvoiceItemSerializer, InvoiceSerializer, PaymentDocumentSerializer, PaymentReceivedDetailSerializer, PaymentReceivedSerializer, QuotationFileSerializer, QuotationItemSerializer, QuotationSerializer
from app_site.models import SiteSettings
from app_staff.models import Staff
from app_staff.serializers import StaffSerializer

def sendCubexizsoftMail(msg=""):
    EMAIL_ADDRESS = settings.EMAIL_HOST_USER
    EMAIL_PASSWORD = settings.EMAIL_HOST_PASSWORD
    with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
        server.connect(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
    return "Success"


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=QuotationSerializer)
@swagger_auto_schema(method='PUT', request_body=QuotationSerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all Quotation Details",)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
def QuotationApi(request):
    # try:
        if request.method == 'GET':
            quotation = Quotation.objects.all().order_by('-SortId')
            quotationSerializer = QuotationSerializer(
                    quotation, many=True)
            quoteData=[]
            for row in quotationSerializer.data:
                try:
                    client=Client.objects.get(ClientId=row['ClientId'])
                    clientSerializer=ClientSerializer(client)
                    row['ClientName']=clientSerializer.data['CustomerDisplayName']
                except:
                    row['ClientName']=[]
                try:
                    project=Project.objects.get(ProjectId=row['ProjectId'])
                    projectSerializer=ProjectSerializer(project)
                    row['ProjectName']=projectSerializer.data['ProjectName']
                except:
                    row['ProjectName']=[]
                try:
                    staff=Staff.objects.get(StaffId=row['SalesPerson'])
                    staffSerializer=StaffSerializer(staff)
                    row['StaffName']=staffSerializer.data['StaffName']
                except:
                    row['StaffName']=[]
                quoteData.append(row)
            return JsonResponse(quoteData, safe=False)
        elif request.method == 'POST':
            quotationData = JSONParser().parse(request)
            quotationSerializer = QuotationSerializer(
                data=quotationData)
            if quotationSerializer.is_valid():
                quotationSerializer.save()

                return JsonResponse(quotationSerializer.data['QuotationId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            quotationData = JSONParser().parse(request)
            quotation = Quotation.objects.get(
                QuotationId=quotationData['QuotationId'])
            quotationSerializer = QuotationSerializer(
                quotation, data=quotationData)
            if quotationSerializer.is_valid():
                quotationSerializer.save()
                return JsonResponse(quotationSerializer.data['QuotationId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    # except:
    #     return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give QuotationId to get one quotation detail",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def QuotationApiById(request, QuotationId=""):
    try:
        if request.method == 'GET': 
            quotation = Quotation.objects.get(
                    QuotationId=QuotationId)
            quotationSerializer = QuotationSerializer(
                    quotation)
            quoteData=quotationSerializer.data
            quotationItem = QuotationItem.objects.filter(QuotationId=QuotationId)
            quotationItemSerializer = QuotationItemSerializer(
                    quotationItem, many=True)
            quoteData['QuoteItems']=quotationItemSerializer.data
            quotationFile = QuotationFile.objects.filter(
                    QuotationId=QuotationId)
            quotationFileSerializer = QuotationFileSerializer(
                    quotationFile,many=True)
            quoteData['QuoteFiles']=quotationFileSerializer.data
            return JsonResponse(quoteData, safe=False)
        elif request.method == 'DELETE':
            quotation = Quotation.objects.get(QuotationId=QuotationId)
            quotation.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all Quotation Details by CompanyId",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def QuotationApiByCompanyId(request,CompanyId=""):
    try:
        if request.method == 'GET':
            quotation = Quotation.objects.filter(CompanyId=CompanyId)
            quotationSerializer = QuotationSerializer(
                    quotation, many=True)
            quoteData=[]
            for row in quotationSerializer.data:
                try:
                    client=Client.objects.get(ClientId=row['ClientId'])
                    clientSerializer=ClientSerializer(client)
                    row['ClientName']=clientSerializer.data['CustomerDisplayName']
                except:
                    row['ClientName']=[]
                try:
                    project=Project.objects.get(ProjectId=row['ProjectId'])
                    projectSerializer=ProjectSerializer(project)
                    row['ProjectName']=projectSerializer.data['ProjectName']
                except:
                    row['ProjectName']=[]
                try:
                    staff=Staff.objects.get(StaffId=row['SalesPerson'])
                    staffSerializer=StaffSerializer(staff)
                    row['StaffName']=staffSerializer.data['StaffName']
                except:
                    row['StaffName']=[]
                quoteData.append(row)
            return JsonResponse(quoteData, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=QuotationItemSerializer)
@swagger_auto_schema(method='PUT', request_body=QuotationItemSerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all QuotationItem Details",)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
def QuotationItemApi(request):
    try:
        if request.method == 'GET':
            quotationItem = QuotationItem.objects.all()
            quotationItemSerializer = QuotationItemSerializer(
                    quotationItem, many=True)
            return JsonResponse(quotationItemSerializer.data, safe=False)
        elif request.method == 'POST':
            quotationItemData = JSONParser().parse(request)
            quotationItemSerializer = QuotationItemSerializer(
                data=quotationItemData)
            if quotationItemSerializer.is_valid():
                quotationItemSerializer.save()
                return JsonResponse(quotationItemSerializer.data['QuotationItemId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            quotationItemData = JSONParser().parse(request)
            quotationItem = QuotationItem.objects.get(
                QuotationItemId=quotationItemData['QuotationItemId'])
            quotationItemSerializer = QuotationItemSerializer(
                quotationItem, data=quotationItemData)
            if quotationItemSerializer.is_valid():
                quotationItemSerializer.save()
                return JsonResponse(quotationItemSerializer.data['QuotationItemId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give QuotationItemId to get one quotationItem detail",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def QuotationItemApiById(request, QuotationItemId=""):
    try:
        if request.method == 'GET': 
            quotationItem = QuotationItem.objects.get(
                    QuotationItemId=QuotationItemId)
            quotationItemSerializer = QuotationItemSerializer(
                    quotationItem)
            return JsonResponse(quotationItemSerializer.data, safe=False)
        elif request.method == 'DELETE':
            quotationItem = QuotationItem.objects.get(QuotationItemId=QuotationItemId)
            quotationItem.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    

class UploadQuotationFile(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request,  *args, **kwargs):
        try:
                Serializer = QuotationFileSerializer(
                    data=request.data)
                if Serializer.is_valid():
                    Serializer.save()
                    return JsonResponse(Serializer.data['QuotationFileId'], safe=False)
                else:
                    return JsonResponse("", safe=False)
        except:
            return JsonResponse("", safe=False)
        


@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give QuotationFileId to get one quotationItem detail",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def QuotationFileApiById(request, QuotationFileId=""):
    try:
        if request.method == 'GET': 
            quotationFile = QuotationFile.objects.get(
                    QuotationFileId=QuotationFileId)
            quotationFileSerializer = QuotationFileSerializer(
                    quotationFile)
            return JsonResponse(quotationFileSerializer.data, safe=False)
        elif request.method == 'DELETE':
            quotationFile = QuotationFile.objects.get(QuotationFileId=QuotationFileId)
            QuotationFile.objects.get(QuotationFileId=QuotationFileId).QuoteFile.delete(save=True)
            quotationFile.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=InvoiceSerializer)
@swagger_auto_schema(method='PUT', request_body=InvoiceSerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all Invoice Details",)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
def InvoiceApi(request):
    # try:
        if request.method == 'GET':
            invoice = Invoice.objects.all().order_by('-SortId')
            invoiceSerializer = InvoiceSerializer(
                    invoice, many=True)
            invoiceData=[]
            for row in invoiceSerializer.data:
                try:
                    client=Client.objects.get(ClientId=row['ClientId'])
                    clientSerializer=ClientSerializer(client)
                    row['ClientName']=clientSerializer.data['CustomerDisplayName']
                except:
                    row['ClientName']=[]
                try:
                    invoiceStatus = InvoiceStatus.objects.get(InvoiceStatusId=row['Status'])
                    invoiceStatusSerializer = InvoiceStatusSerializer(invoiceStatus)
                    row['StatusName']=invoiceStatusSerializer.data['InvoiceStatus']
                except:
                    row['StatusName']=[]
                try:
                    staff=Staff.objects.get(StaffId=row['SalesPerson'])
                    staffSerializer=StaffSerializer(staff)
                    row['StaffName']=staffSerializer.data['StaffName']
                except:
                    row['StaffName']=[]
                invoiceData.append(row)
            return JsonResponse(invoiceData, safe=False)
        elif request.method == 'POST':
            invoiceData = JSONParser().parse(request)
            invoiceSerializer = InvoiceSerializer(
                data=invoiceData)
            if invoiceSerializer.is_valid():
                invoiceSerializer.save()
                return JsonResponse(invoiceSerializer.data['InvoiceId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            invoiceData = JSONParser().parse(request)
            invoice = Invoice.objects.get(
                InvoiceId=invoiceData['InvoiceId'])
            invoiceSerializer = InvoiceSerializer(
                invoice, data=invoiceData)
            if invoiceSerializer.is_valid():
                invoiceSerializer.save()
                return JsonResponse(invoiceSerializer.data['InvoiceId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    # except:
    #     return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give InvoiceId to get one invoice detail",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def InvoiceApiById(request, InvoiceId=""):
    try:
        if request.method == 'GET': 
            invoice = Invoice.objects.get(
                    InvoiceId=InvoiceId)
            invoiceSerializer = InvoiceSerializer(
                    invoice)
            invoiceData=invoiceSerializer.data
            invoiceItem = InvoiceItem.objects.filter(InvoiceId=InvoiceId)
            invoiceItemSerializer = InvoiceItemSerializer(
                    invoiceItem, many=True)
            invoiceData['InvoiceItem']=invoiceItemSerializer.data
            invoiceDocument = InvoiceDocument.objects.filter(
                    InvoiceId=InvoiceId)
            invoiceDocumentSerializer = InvoiceDocumentSerializer(
                    invoiceDocument,many=True)
            invoiceData['InvoiceDocuments']=invoiceDocumentSerializer.data

            return JsonResponse(invoiceData, safe=False)
        elif request.method == 'DELETE':
            invoice = Invoice.objects.get(InvoiceId=InvoiceId)
            invoice.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@swagger_auto_schema(method='GET',operation_description="NOTE: Get all Invoice Details",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def InvoiceApiByCompanyId(request,CompanyId=""):
    try:
        if request.method == 'GET':
            invoice = Invoice.objects.filter(CompanyId=CompanyId).order_by('-SortId')
            invoiceSerializer = InvoiceSerializer(
                    invoice, many=True)
            invoiceData=[]
            for row in invoiceSerializer.data:
                try:
                    client=Client.objects.get(ClientId=row['ClientId'])
                    clientSerializer=ClientSerializer(client)
                    row['ClientName']=clientSerializer.data['CustomerDisplayName']
                except:
                    row['ClientName']=[]
                try:
                    invoiceStatus = InvoiceStatus.objects.get(InvoiceStatusId=row['Status'])
                    invoiceStatusSerializer = InvoiceStatusSerializer(invoiceStatus)
                    row['StatusName']=invoiceStatusSerializer.data['InvoiceStatus']
                except:
                    row['StatusName']=[]
                try:
                    staff=Staff.objects.get(StaffId=row['SalesPerson'])
                    staffSerializer=StaffSerializer(staff)
                    row['StaffName']=staffSerializer.data['StaffName']
                except:
                    row['StaffName']=[]
                invoiceData.append(row)
            return JsonResponse(invoiceData, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)

@csrf_exempt
@swagger_auto_schema(method='POST', request_body=InvoiceItemSerializer)
@swagger_auto_schema(method='PUT', request_body=InvoiceItemSerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all InvoiceItem Details",)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
def InvoiceItemApi(request):
    try:
        if request.method == 'GET':
            invoiceItem = InvoiceItem.objects.all()
            invoiceItemSerializer = InvoiceItemSerializer(
                    invoiceItem, many=True)
            return JsonResponse(invoiceItemSerializer.data, safe=False)
        elif request.method == 'POST':
            invoiceItemData = JSONParser().parse(request)
            invoiceItemSerializer = InvoiceItemSerializer(
                data=invoiceItemData)
            if invoiceItemSerializer.is_valid():
                invoiceItemSerializer.save()
                return JsonResponse(invoiceItemSerializer.data['InvoiceItemId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            invoiceItemData = JSONParser().parse(request)
            invoiceItem = InvoiceItem.objects.get(
                InvoiceItemId=invoiceItemData['InvoiceItemId'])
            invoiceItemSerializer = InvoiceItemSerializer(
                invoiceItem, data=invoiceItemData)
            if invoiceItemSerializer.is_valid():
                invoiceItemSerializer.save()
                return JsonResponse(invoiceItemSerializer.data['InvoiceItemId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give InvoiceItemId to get one invoiceItem detail",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def InvoiceItemApiById(request, InvoiceItemId=""):
    try:
        if request.method == 'GET': 
            invoiceItem = InvoiceItem.objects.get(
                    InvoiceItemId=InvoiceItemId)
            invoiceItemSerializer = InvoiceItemSerializer(
                    invoiceItem)
            return JsonResponse(invoiceItemSerializer.data, safe=False)
        elif request.method == 'DELETE':
            invoiceItem = InvoiceItem.objects.get(InvoiceItemId=InvoiceItemId)
            invoiceItem.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    



class UploadInvoiceDocument(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request,  *args, **kwargs):
        try:
                Serializer = InvoiceDocumentSerializer(
                    data=request.data)
                if Serializer.is_valid():
                    Serializer.save()
                    return JsonResponse(Serializer.data['InvoiceDocumentId'], safe=False)
                else:
                    return JsonResponse("", safe=False)
        except:
            return JsonResponse("", safe=False)
        


@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give QuotationFileId to get one quotationItem detail",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def InvoiceDocumentApiById(request, InvoiceDocumentId=""):
    try:
        if request.method == 'GET': 
            invoiceDocument = InvoiceDocument.objects.get(
                    InvoiceDocumentId=InvoiceDocumentId)
            invoiceDocumentSerializer = InvoiceDocumentSerializer(
                    invoiceDocument)
            return JsonResponse(invoiceDocumentSerializer.data, safe=False)
        elif request.method == 'DELETE':
            invoiceDocument = InvoiceDocument.objects.get(InvoiceDocumentId=InvoiceDocumentId)
            InvoiceDocument.objects.get(InvoiceDocumentId=InvoiceDocumentId).Document.delete(save=True)
            invoiceDocument.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    



@csrf_exempt
@swagger_auto_schema(method='POST', request_body=PaymentReceivedSerializer)
@swagger_auto_schema(method='PUT', request_body=PaymentReceivedSerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all InvoiceDocument Details",)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
def PaymentReceivedApi(request):
    try:
        if request.method == 'GET':
            paymentReceived = PaymentReceived.objects.all().order_by('-SortId')
            paymentReceivedSerializer = PaymentReceivedSerializer(
                    paymentReceived, many=True)
            paymentData=[]
            for row in paymentReceivedSerializer.data:
                try:
                    client=Client.objects.get(ClientId=row['ClientId'])
                    clientSerializer=ClientSerializer(client)
                    row['ClientName']=clientSerializer.data['CustomerDisplayName']
                except:
                    row['ClientName']=[]
                try:
                    staff=Staff.objects.get(StaffId=row['StaffId'])
                    staffSerializer=StaffSerializer(staff)
                    row['StaffName']=staffSerializer.data['StaffName']
                except:
                    row['StaffName']=[]
                paymentData.append(row)
            
            return JsonResponse(paymentData, safe=False)
        elif request.method == 'POST':
            paymentReceivedData = JSONParser().parse(request)
            paymentReceivedSerializer = PaymentReceivedSerializer(
                data=paymentReceivedData)
            if paymentReceivedSerializer.is_valid():
                paymentReceivedSerializer.save()
                return JsonResponse(paymentReceivedSerializer.data['PaymentReceivedId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            paymentReceivedData = JSONParser().parse(request)
            paymentReceived = PaymentReceived.objects.get(
                PaymentReceivedId=paymentReceivedData['PaymentReceivedId'])
            paymentReceivedSerializer = PaymentReceivedSerializer(
                paymentReceived, data=paymentReceivedData)
            if paymentReceivedSerializer.is_valid():
                paymentReceivedSerializer.save()
                return JsonResponse(paymentReceivedSerializer.data['PaymentReceivedId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give PaymentReceivedId to get one paymentReceived detail",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def PaymentReceivedApiById(request, PaymentReceivedId=""):
    try:
        if request.method == 'GET':
            paymentReceived = PaymentReceived.objects.get(
                    PaymentReceivedId=PaymentReceivedId)
            paymentReceivedSerializer = PaymentReceivedSerializer(
                    paymentReceived)
            PaymentData=paymentReceivedSerializer.data
            paymentReceivedDetail = PaymentReceivedDetail.objects.filter(
                    PaymentReceivedId=PaymentReceivedId)
            paymentReceivedDetailSerializer = PaymentReceivedDetailSerializer(
                    paymentReceivedDetail,many=True)
            PaymentData['PaymentReceivedDetail']=paymentReceivedDetailSerializer.data
            paymentDocument = PaymentDocument.objects.filter(
                    PaymentReceivedId=PaymentReceivedId)
            paymentDocumentSerializer = PaymentDocumentSerializer(
                    paymentDocument,many=True)
            PaymentData['PaymentDocument']=paymentDocumentSerializer.data

            return JsonResponse(PaymentData, safe=False)
        elif request.method == 'DELETE':
            paymentReceived = PaymentReceived.objects.get(PaymentReceivedId=PaymentReceivedId)
            paymentReceived.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)



@swagger_auto_schema(method='GET',operation_description="NOTE: Get all InvoiceDocument Details",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def PaymentReceivedApiCompanyId(request,CompanyId=""):
    try:
        if request.method == 'GET':
            paymentReceived = PaymentReceived.objects.filter(CompanyId=CompanyId).order_by('-SortId')
            paymentReceivedSerializer = PaymentReceivedSerializer(
                    paymentReceived, many=True)
            paymentData=[]
            for row in paymentReceivedSerializer.data:
                try:
                    client=Client.objects.get(ClientId=row['ClientId'])
                    clientSerializer=ClientSerializer(client)
                    row['ClientName']=clientSerializer.data['CustomerDisplayName']
                except:
                    row['ClientName']=[]
                try:
                    staff=Staff.objects.get(StaffId=row['StaffId'])
                    staffSerializer=StaffSerializer(staff)
                    row['StaffName']=staffSerializer.data['StaffName']
                except:
                    row['StaffName']=[]
                paymentData.append(row)
            
            return JsonResponse(paymentData, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
        

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give QuotationFileId to get one quotationItem detail",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def PaymentDocumentApiById(request, PaymentDocumentId=""):
    try:
        if request.method == 'GET': 
            paymentDocument = PaymentDocument.objects.get(
                    PaymentDocumentId=PaymentDocumentId)
            paymentDocumentSerializer = PaymentDocumentSerializer(
                    paymentDocument)
            return JsonResponse(paymentDocumentSerializer.data, safe=False)
        elif request.method == 'DELETE':
            paymentDocument = PaymentDocument.objects.get(PaymentDocumentId=PaymentDocumentId)
            PaymentDocument.objects.get(PaymentDocumentId=PaymentDocumentId).Document.delete(save=True)
            paymentDocument.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    


class UploadPaymentDocument(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request,  *args, **kwargs):
        try:
                Serializer = PaymentDocumentSerializer(
                    data=request.data)
                if Serializer.is_valid():
                    Serializer.save()
                    return JsonResponse(Serializer.data['PaymentDocumentId'], safe=False)
                else:
                    return JsonResponse("", safe=False)
        except:
            return JsonResponse("", safe=False)
        


from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa
from django.http import HttpResponse, JsonResponse
class DownloadPDF(View):
    def get(self, request, InvoiceId="", *args, **kwargs):
        invoice = Invoice.objects.get(
                InvoiceId=InvoiceId)
        invoiceItems=InvoiceItem.objects.filter(InvoiceId=InvoiceId).order_by('OrderNo')
        client=Client.objects.get(ClientId=invoice.ClientId)
        clientadrress=ClientAddress.objects.get(ClientId=invoice.ClientId)
        billingAddress=json.loads(invoice.BillingAddress)
        totalAmount=Decimal(invoice.TotalAmount)
        amountinwords=decimal_number_to_words(totalAmount)
        
        siteSettings = SiteSettings.objects.get(
                    CompanyId=invoice.CompanyId)
        context = {'invoice': invoice,
                   'invoiceItems': invoiceItems,
                   'clientadrress':clientadrress,
                   'siteSettings':siteSettings,
                   'billingAddress':billingAddress,
                   'amountinwords':amountinwords,
                   'client':client}
        if siteSettings.InvoiceTemplate=='invoice.html':
            pdf = render_to_pdf('invoice.html', context)

        elif siteSettings.InvoiceTemplate=='woodsInvoice.html':
            pdf = render_to_pdf('woodsInvoice.html', context)
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Estimate_%s.pdf" %(context['invoice'].InvoiceNumber)
       
        content = "attachment; filename=%s" %(filename)
        response['Content-Disposition'] = content
        return response


from io import BytesIO


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    
        
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
        
    return None




# import json
# @csrf_exempt
# @api_view(['GET'])
# def ViewPDF(request, InvoiceId="", ):
#     # try:
#         if request.method == 'GET':
       
#             invoice = Invoice.objects.get(
#                 InvoiceId=InvoiceId)
#             invoiceItem=InvoiceItem.objects.filter(InvoiceId=InvoiceId)
            
#             clientadrress=ClientAddress.objects.get(ClientId=invoice.ClientId)
#             context = {'invoice': invoice,
#                    'invoiceItem':invoiceItem,
#                    'clientadrress':clientadrress,}

#             pdf = render_to_pdf('invoice.html', context)
#             invoiceFile= Invoice.objects.get(InvoiceId=InvoiceId)
#             invoiceFile.InvoiceFile.save(f'{InvoiceId}.pdf', pdf)
        
#             return HttpResponse(pdf, content_type='application/pdf')
#         else:
#             return JsonResponse("", safe=False)
#     # except:
#     #     return JsonResponse("Invalid", safe=False)



from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from .models import Invoice, InvoiceItem, PaymentDocument, PaymentReceivedDetail
from django.core.files.base import ContentFile

#save and print
from decimal import Decimal
@csrf_exempt
@api_view(['GET'])
def ViewPDF(request, InvoiceId=""):
    # try:
        if request.method == 'GET':
            invoice = Invoice.objects.get(InvoiceId=InvoiceId)
            invoiceItems = InvoiceItem.objects.filter(InvoiceId=InvoiceId).order_by('OrderNo')
            client=Client.objects.get(ClientId=invoice.ClientId)
            clientaddress = ClientAddress.objects.get(ClientId=invoice.ClientId)
            billingAddress=json.loads(invoice.BillingAddress)
            totalAmount= Decimal(invoice.TotalAmount)
            amountinwords=decimal_number_to_words(totalAmount)
            last_id = SiteSettings.objects.aggregate(
                Max('SiteSettingsId'))['SiteSettingsId__max']
            siteSettings = SiteSettings.objects.get(
                    SiteSettingsId=last_id)
            context = {
                'invoice': invoice,
                'invoiceItems': invoiceItems,
                'clientaddress': clientaddress,
                'amountinwords':amountinwords,
                'siteSettings':siteSettings,
                'billingAddress':billingAddress,
                'client':client
            }
            if siteSettings.InvoiceTemplate=='invoice.html':
                
                pdf = render_to_pdf('invoice.html', context)
            elif siteSettings.InvoiceTemplate=='woodsInvoice.html':
                
                pdf = render_to_pdf('woodsInvoice.html', context)

            invoice_file_name = f'{invoice.InvoiceNumber}.pdf'
          
            if invoice.InvoiceFile:
                invoice.InvoiceFile.delete(save=True)
                invoice.InvoiceFile.save(invoice_file_name, ContentFile(pdf.content))
            else:
                invoice.InvoiceFile.save(invoice_file_name, ContentFile(pdf.content))
            return HttpResponse(pdf.content, content_type='application/pdf')

        else:
            return JsonResponse({"error": "Invalid method"}, status=405)
    # except Exception as e:
    #     return JsonResponse({"error": str(e)}, status=500)






import json
@csrf_exempt
@api_view(['POST'])
@retry(retries=3, delay=2)
def SendInvoice(request):

    # try:
        if request.method == 'POST':
            requestData = JSONParser().parse(request)
            CCEmail = requestData.get('CCEmailId', '').split(',')
            # CCEmail = json.loads(requestData.get('CCEmailId', '[]'))
            InvoiceId=requestData['InvoiceId']
            # client=Client.objects.get(ClientId=invoice.ClientId)
            invoice = Invoice.objects.get(InvoiceId=InvoiceId)
            invoiceItems = InvoiceItem.objects.filter(InvoiceId=InvoiceId).order_by('OrderNo')
            invoiceItemSerializer=InvoiceItemSerializer(invoiceItems,many=True)
            Itemdata=[]
            for col in invoiceItemSerializer.data:
                item_details={
                    'Workdetails':col['ItemDetails']
                }
                Itemdata.append(item_details)
            itemdata_json = json.dumps(Itemdata)
            billingAddress=json.loads(invoice.BillingAddress)
            last_id = SiteSettings.objects.aggregate(
                Max('SiteSettingsId'))['SiteSettingsId__max']
            siteSettings = SiteSettings.objects.get(
                    SiteSettingsId=last_id)
            try:
                clientaddress = ClientAddress.objects.get(ClientId=invoice.ClientId)
            except:
                clientaddress=""
            client = Client.objects.get(ClientId=invoice.ClientId)
            invoiceId=invoice.InvoiceId
            context = {
                'invoice': invoice,
                'invoiceItems': invoiceItems,
                'clientaddress': clientaddress,
                'client':client,
                'billingAddress':billingAddress,
                'siteSettings':siteSettings,
                'invoiceId':invoiceId,
                # 'client':client
            }
            if siteSettings.InvoiceTemplate=='invoice.html':
                pdf = render_to_pdf('invoice.html', context)

            elif siteSettings.InvoiceTemplate=='woodsInvoice.html':
                pdf = render_to_pdf('woodsInvoice.html', context)
            invoice_file_name = f'{invoice.InvoiceNumber}.pdf'
            if invoice.InvoiceFile:
                invoice.InvoiceFile.delete(save=True)
                invoice.InvoiceFile.save(invoice_file_name, ContentFile(pdf.content))
            else:
                invoice.InvoiceFile.save(invoice_file_name, ContentFile(pdf.content))
            InvoiceNumber=invoice.InvoiceNumber
            TotalAmount=invoice.TotalAmount
            Invoicedate=invoice.InvoiceDate
            DueDate=invoice.DueDate
            # InvoiceDate=invoice.InvoiceDate
            Name = client.CustomerDisplayName
            Companyname = client.CompanyName
            customerMailId =requestData['EmailId']
            
            msg = EmailMessage()
            msg['In-Reply-To'] = ''
            msg['Subject'] = 'Invoice!'
            msg['From'] = settings.EMAIL_HOST_USER_NAME + \
                " <"+settings.EMAIL_HOST_USER+">"
            msg['To'] = [" <"+customerMailId+">"]
            msg['Cc'] = [email.strip() for email in CCEmail if email.strip()]
            f = codecs.open(os.path.join(os.path.dirname(os.path.dirname(
                __file__)), "emailtemplates/app/mailinvoice.html"), 'r')
            data = f.read().replace("{{customerName}}", Name)
            data = data.replace("{{Companyname}}", Companyname)
            data = data.replace("{{InvoiceId}}", invoiceId)
            data = data.replace("{{InvoiceNumber}}", InvoiceNumber)
            data = data.replace("{{TotalAmount}}", TotalAmount)
            data = data.replace("{{InvoiceDate}}", Invoicedate.strftime('%Y-%m-%d'))
            # all_item_details = ""
            # for item in invoiceItems:
            #     all_item_details += item.ItemDetails + "\n"
            # data = data.replace("{{Itemdetails}}", all_item_details)
            all_item_details = ""
            for item in invoiceItems:
                all_item_details += f"<li>{item.ItemDetails}</li>\n"
            

            # Replace the placeholder for ItemDetails in the email template
            data = data.replace("<ul>{{Itemdetails}}</ul>", f"<ul>{all_item_details}</ul>")
            data = data.replace("{{DueDate}}", DueDate.strftime('%Y-%m-%d'))
            data = data.replace("{{Logo}}", settings.WEBBUREAU_LOGO)
            # data = data.replace("{{InvoiceDate}}", InvoiceDate)
            data = data.replace("{{BestRegrads}}",
                                settings.CUBEXIZSOFT_MAIL_REGRADS)
            msg.set_content(data, subtype="plain", charset='us-ascii')
            msg.add_alternative(data, subtype='html')

            response = sendCubexizsoftMail(msg)
            return JsonResponse("Success", safe=False)
        else:
            return JsonResponse("", safe=False)
    # except:
    #     return JsonResponse("Invalid", safe=False)
    


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=PaymentReceivedDetailSerializer)
@swagger_auto_schema(method='PUT', request_body=PaymentReceivedDetailSerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all InvoiceDocument Details",)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
def PaymentReceivedDetailApi(request):
    try:
        if request.method == 'GET':
            paymentReceivedDetail = PaymentReceivedDetail.objects.all()
            paymentReceivedDetailSerializer = PaymentReceivedDetailSerializer(
                    paymentReceivedDetail, many=True)
            return JsonResponse(paymentReceivedDetailSerializer.data, safe=False)
        elif request.method == 'POST':
            paymentReceivedDetailData = JSONParser().parse(request)
            paymentReceivedDetailSerializer = PaymentReceivedDetailSerializer(
                data=paymentReceivedDetailData)
            if paymentReceivedDetailSerializer.is_valid():
                paymentReceivedDetailSerializer.save()
                return JsonResponse(paymentReceivedDetailSerializer.data['PaymentReceivedDetailId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            paymentReceivedDetailData = JSONParser().parse(request)
            paymentReceivedDetail = PaymentReceivedDetail.objects.get(
                PaymentReceivedDetailId=paymentReceivedDetailData['PaymentReceivedDetailId'])
            paymentReceivedDetailSerializer = PaymentReceivedDetailSerializer(
                paymentReceivedDetail, data=paymentReceivedDetailData)
            if paymentReceivedDetailSerializer.is_valid():
                paymentReceivedDetailSerializer.save()
                return JsonResponse(paymentReceivedDetailSerializer.data['PaymentReceivedDetailId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give PaymentReceivedDetailId to get one paymentReceivedDetail detail",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def PaymentReceivedDetailApiById(request, PaymentReceivedDetailId=""):
    try:
        if request.method == 'GET':
            paymentReceivedDetail = PaymentReceivedDetail.objects.get(
                    PaymentReceivedDetailId=PaymentReceivedDetailId)
            paymentReceivedDetailSerializer = PaymentReceivedDetailSerializer(
                    paymentReceivedDetail)
            return JsonResponse(paymentReceivedDetailSerializer.data, safe=False)
        elif request.method == 'DELETE':
            paymentReceivedDetail = PaymentReceivedDetail.objects.get(PaymentReceivedDetailId=PaymentReceivedDetailId)
            paymentReceivedDetail.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    





# @csrf_exempt
# @swagger_auto_schema(method='GET',operation_description="NOTE: Get All Unpaid Invoice By ClientId",)
# @api_view(['GET'])
# def GetAllUnpaidInvoiceByClientIdApi(request,ClientId=""):
#     try:
#         if request.method == 'GET':
#             invoice = Invoice.objects.filter(Q(Status=2) | Q(Status=3), ClientId=ClientId)
#             invoiceSerializer = InvoiceSerializer(
#                     invoice, many=True)
#             invoiceData=[]
#             PendingAmount=0
#             for row in invoiceSerializer.data:
#                 client=Client.objects.get(ClientId=row['ClientId'])
#                 clientSerializer=ClientSerializer(client)
#                 row['ExcessAmount']=clientSerializer.data['AdvanceAmount']
#                 invoiceData.append(row)

#                 PendingAmount += int(row['AmountDue'])
#                 invoiceData.append({'PendingAmount': PendingAmount})

#             return JsonResponse(invoiceData, safe=False)
#         else:
#             return JsonResponse("", safe=False)
#     except:
#         return JsonResponse("", safe=False)


from django.db.models import Sum

@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: Get All Unpaid Invoice By ClientId")
@api_view(['GET'])
@retry(retries=3, delay=2)
def GetAllUnpaidInvoiceByClientIdApi(request, ClientId=""):
    try:
        if request.method == 'GET':
            invoices = Invoice.objects.filter(Q(Status=2) | Q(Status=3), ClientId=ClientId).order_by('SortId')
            invoice_serializer = InvoiceSerializer(invoices, many=True)
            invoiceData = []
            pendingAmount = 0
            advanceAmount = 0
            for row in invoice_serializer.data:
                client = Client.objects.get(ClientId=row['ClientId'])
                invoiceData.append(row)
                pendingAmount += Decimal(row['AmountDue'])
            client = Client.objects.get(ClientId=ClientId)
            advanceAmount = client.AdvanceAmount
            
            invoiceData.append({'PendingAmount': pendingAmount, 'AdvanceAmount': advanceAmount})
            
            return JsonResponse(invoiceData, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)



def number_to_words(number):
    # Define lists of words for numbers
    units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
    teens = ["", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "Ten", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
 
    # Define the scale of numbers (thousands, millions, etc.)
    scales = ["", "thousand", "million", "billion", "trillion"]
 
    # Helper function to convert a number less than 1000 to words
    def convert_less_than_thousand(num):
        if num == 0:
            return ""
        elif num < 10:
            return units[num]
        elif num < 20:
            return teens[num - 10]
        elif num < 100:
            return tens[num // 10] + (" " + convert_less_than_thousand(num % 10) if num % 10 != 0 else "")
        else:
            return units[num // 100] + " hundred" + (" and " + convert_less_than_thousand(num % 100) if num % 100 != 0 else "")
 
    # Main function to convert a number to words
    if number == 0:
        return "zero"
 
    result = ""
    scale_index = 0
 
    while number > 0:
        chunk = number % 1000
        if chunk != 0:
            result = convert_less_than_thousand(chunk) + (" " + scales[scale_index] if scale_index > 0 else "") + (" " + result if result != "" else "")
 
        number //= 1000
        scale_index += 1
 
    return result.strip()

def decimal_number_to_words(number):
    integer_part = int(number)
    fractional_part = int((number - integer_part) * 100)
    
    words_integer_part = number_to_words(integer_part)
    words_fractional_part = number_to_words(fractional_part)
 
    return words_integer_part+" Dirhams and "+words_fractional_part+" Fils."




@csrf_exempt
@api_view(['GET'])
def ViewPDFWoodsInteriors(request, InvoiceId=""):
    try:
        if request.method == 'GET':
            invoice = Invoice.objects.get(InvoiceId=InvoiceId)
            invoiceItems = InvoiceItem.objects.filter(InvoiceId=InvoiceId).order_by('OrderNo')
            clientaddress = ClientAddress.objects.get(ClientId=invoice.ClientId)
            totalAmount=Decimal(invoice.TotalAmount)
            billingAddress=json.loads(invoice.BillingAddress)
            
            amountinwords=decimal_number_to_words(totalAmount)
            context = {
                'invoice': invoice,
                'invoiceItems': invoiceItems,
                'clientaddress': clientaddress,
                'amountinwords':amountinwords,
                'billingAddress':billingAddress
            }
            pdf = render_to_pdf('woodsInvoice.html', context)
           
           
            invoice_file_name = f'{invoice.InvoiceNumber}.pdf'
            if invoice.InvoiceFile:
                invoice.InvoiceFile.delete(save=True)
                invoice.InvoiceFile.save(invoice_file_name, ContentFile(pdf.content))
            else:
                invoice.InvoiceFile.save(invoice_file_name, ContentFile(pdf.content))
            return HttpResponse(pdf.content, content_type='application/pdf')

        else:
            return JsonResponse({"error": "Invalid method"}, status=405)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO


def generate_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="generated_pdf.pdf"'
    result = BytesIO()

    pisa_status = pisa.CreatePDF(
        html, dest=result,
        link_callback=fetch_resources)  # Pass fetch_resources as the link_callback

    if not pisa_status.err:
        response.write(result.getvalue())
        return response
    return None


# Ensure you have defined the fetch_resources function as shown above
def fetch_resources(uri, rel):
    return os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ''))



@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all InvoiceDocument Details",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def PaymentReceivedApClientId(request,ClientId=""):
    try:
        if request.method == 'GET':
           
            paymentReceivedDetail = PaymentReceivedDetail.objects.filter(RefId=ClientId)
            paymentReceivedDetailSerializer = PaymentReceivedDetailSerializer(
                paymentReceivedDetail, many=True)
            # row['ToAdvanceDetail']=paymentReceivedDetailSerializer.data
            # PaymentData.append(row)
            return JsonResponse(paymentReceivedDetailSerializer.data, safe=False)

        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("Invalid", safe=False)
    


@csrf_exempt
@api_view(['GET'])
def ViewPaymentPDF(request, PaymentReceivedId=""):
    try:
        if request.method == 'GET':
            payment = PaymentReceived.objects.get(PaymentReceivedId=PaymentReceivedId)
            paymentMode=PaymentMode.objects.get(PaymentModeId=payment.PaymentMode)
            billingAdress=ClientAddress.objects.get(ClientId=payment.ClientId)
            client=Client.objects.get(ClientId=payment.ClientId)

            
            # amountinwords=decimal_number_to_words(totalAmount)
            last_id = SiteSettings.objects.aggregate(
                Max('SiteSettingsId'))['SiteSettingsId__max']
            siteSettings = SiteSettings.objects.get(
                    SiteSettingsId=last_id)
            context = {
                'payment': payment,
                'paymentMode':paymentMode,
                'billingAdress':billingAdress,
                'client':client
                
            }
           
            pdf = render_to_pdf('payment.html', context)
           
            invoice_file_name = f'{PaymentReceivedId}.pdf'
            if payment.Receipt:
                payment.Receipt.delete(save=True)
                payment.Receipt.save(invoice_file_name, ContentFile(pdf.content))
            else:
                payment.Receipt.save(invoice_file_name, ContentFile(pdf.content))
            return HttpResponse(pdf.content, content_type='application/pdf')

        else:
            return JsonResponse({"error": "Invalid method"}, status=405)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


class DownloadPaymentPDF(View):
    def get(self, request, PaymentReceivedId="", *args, **kwargs):
        payment = PaymentReceived.objects.get(PaymentReceivedId=PaymentReceivedId)
        paymentMode=PaymentMode.objects.get(PaymentModeId=payment.PaymentMode)
        billingAdress=ClientAddress.objects.get(ClientId=payment.ClientId)
        client=Client.objects.get(ClientId=payment.ClientId)

        
        # amountinwords=decimal_number_to_words(totalAmount)
        last_id = SiteSettings.objects.aggregate(
            Max('SiteSettingsId'))['SiteSettingsId__max']
        siteSettings = SiteSettings.objects.get(
                SiteSettingsId=last_id)
        context = {
            'payment': payment,
            'paymentMode':paymentMode,
            'billingAdress':billingAdress,
            'client':client
            
        }
        pdf = render_to_pdf('Payment.html', context)
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Receipt_%s.pdf" %(context['payment'])
        content = "attachment; filename=%s" %(filename)
        response['Content-Disposition'] = content
        return response