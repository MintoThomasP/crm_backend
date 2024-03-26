from django.shortcuts import render
import os
import smtplib
from email.message import EmailMessage
import codecs
import os
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
from app_sale.models import Invoice, InvoiceDocument, InvoiceItem, PaymentReceived, Quotation, QuotationFile, QuotationItem
from app_sale.serializers import InvoiceDocumentSerializer, InvoiceItemSerializer, InvoiceSerializer, PaymentReceivedSerializer, QuotationFileSerializer, QuotationItemSerializer, QuotationSerializer

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
def QuotationApi(request):
    try:
        if request.method == 'GET':
            quotation = Quotation.objects.all().order_by('-SortId')
            quotationSerializer = QuotationSerializer(
                    quotation, many=True)
            return JsonResponse(quotationSerializer.data, safe=False)
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
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give QuotationId to get one quotation detail",)
@api_view(['GET','DELETE'])
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
    



@csrf_exempt
@swagger_auto_schema(method='POST', request_body=QuotationItemSerializer)
@swagger_auto_schema(method='PUT', request_body=QuotationItemSerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all QuotationItem Details",)
@api_view(['GET','POST','PUT'])
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
def InvoiceApi(request):
    try:
        if request.method == 'GET':
            invoice = Invoice.objects.all().order_by('-SortId')
            invoiceSerializer = InvoiceSerializer(
                    invoice, many=True)
            return JsonResponse(invoiceSerializer.data, safe=False)
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
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give InvoiceId to get one invoice detail",)
@api_view(['GET','DELETE'])
def InvoiceApiById(request, InvoiceId=""):
    try:
        if request.method == 'GET': 
            invoice = Invoice.objects.get(
                    InvoiceId=InvoiceId)
            invoiceSerializer = InvoiceSerializer(
                    invoice)
            return JsonResponse(invoiceSerializer.data, safe=False)
        elif request.method == 'DELETE':
            invoice = Invoice.objects.get(InvoiceId=InvoiceId)
            invoice.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='POST', request_body=InvoiceItemSerializer)
@swagger_auto_schema(method='PUT', request_body=InvoiceItemSerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all InvoiceItem Details",)
@api_view(['GET','POST','PUT'])
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
def PaymentReceivedApi(request):
    try:
        if request.method == 'GET':
            quotationItem = PaymentReceived.objects.all()
            quotationItemSerializer = PaymentReceivedSerializer(
                    quotationItem, many=True)
            return JsonResponse(quotationItemSerializer.data, safe=False)
        elif request.method == 'POST':
            quotationItemData = JSONParser().parse(request)
            quotationItemSerializer = PaymentReceivedSerializer(
                data=quotationItemData)
            if quotationItemSerializer.is_valid():
                quotationItemSerializer.save()

                return JsonResponse(quotationItemSerializer.data['PaymentReceivedId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            quotationItemData = JSONParser().parse(request)
            quotationItem = PaymentReceived.objects.get(
                PaymentReceivedId=quotationItemData['PaymentReceivedId'])
            quotationItemSerializer = PaymentReceivedSerializer(
                quotationItem, data=quotationItemData)
            if quotationItemSerializer.is_valid():
                quotationItemSerializer.save()
                return JsonResponse(quotationItemSerializer.data['PaymentReceivedId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give PaymentReceivedId to get one quotationItem detail",)
@api_view(['GET','DELETE'])
def PaymentReceivedApiById(request, PaymentReceivedId=""):
    try:
        if request.method == 'GET': 
            quotationItem = PaymentReceived.objects.get(
                    PaymentReceivedId=PaymentReceivedId)
            quotationItemSerializer = PaymentReceivedSerializer(
                    quotationItem)
            return JsonResponse(quotationItemSerializer.data, safe=False)
        elif request.method == 'DELETE':
            quotationItem = PaymentReceived.objects.get(PaymentReceivedId=PaymentReceivedId)
            quotationItem.delete()
            return JsonResponse("Deleted successfully", safe=False)
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
        invoiceItem=InvoiceItem.objects.filter(InvoiceId=InvoiceId)
        clientadrress=ClientAddress.objects.get(ClientId=invoice.ClientId)
        context = {'invoice': invoice,
                   'invoiceItem':invoiceItem,
                   'clientadrress':clientadrress,}
        pdf = render_to_pdf('invoice.html', context)
      

        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Estimate_%s.pdf" %(context['invoice'])
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
from .models import Invoice, InvoiceItem
from django.core.files.base import ContentFile

#save and print

@csrf_exempt
@api_view(['GET'])
def ViewPDF(request, InvoiceId=""):
    try:
        if request.method == 'GET':
            invoice = Invoice.objects.get(InvoiceId=InvoiceId)
            invoiceItems = InvoiceItem.objects.filter(InvoiceId=InvoiceId)
            clientaddress = ClientAddress.objects.get(ClientId=invoice.ClientId)
            context = {
                'invoice': invoice,
                'invoiceItems': invoiceItems,
                'clientaddress': clientaddress,
            }
            pdf = render_to_pdf('invoice.html', context)
            invoice_file_name = f'{InvoiceId}.pdf'
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






import json
@csrf_exempt
@api_view(['POST'])
def SendInvoice(request):

    # try:
        if request.method == 'POST':
            requestData = JSONParser().parse(request)
            # CCEmail = requestData.get('CCEmailId', '').split(',')
            CCEmail = json.loads(requestData.get('CCEmailId', '[]'))
            InvoiceId=requestData['InvoiceId']

            invoice = Invoice.objects.get(InvoiceId=InvoiceId)
            invoiceItems = InvoiceItem.objects.filter(InvoiceId=InvoiceId)
            clientaddress = ClientAddress.objects.get(ClientId=invoice.ClientId)
            client = Client.objects.get(ClientId=invoice.ClientId)
            context = {
                'invoice': invoice,
                'invoiceItems': invoiceItems,
                'clientaddress': clientaddress,
                'client':client
            }
            pdf = render_to_pdf('invoice.html', context)
            invoice_file_name = f'{InvoiceId}.pdf'
            if invoice.InvoiceFile:
                invoice.InvoiceFile.delete(save=True)
                invoice.InvoiceFile.save(invoice_file_name, ContentFile(pdf.content))
            else:
                invoice.InvoiceFile.save(invoice_file_name, ContentFile(pdf.content))
            InvoiceNumber=invoice.InvoiceNumber
            TotalAmount=invoice.TotalAmount
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
            data = data.replace("{{InvoiceNumber}}", InvoiceNumber)
            data = data.replace("{{TotalAmount}}", TotalAmount)
            # data = data.replace("{{InvoiceDate}}", InvoiceDate)
            data = data.replace("{{BestRegrads}}",
                                settings.CUBEXIZSOFT_MAIL_REGRADS)
            msg.set_content(data, subtype="plain", charset='us-ascii')
            msg.add_alternative(data, subtype='html')

            response = sendCubexizsoftMail(msg)
            # hashlib.sha1(repr(OTPCODE).encode('utf-8')).hexdigest()
            return JsonResponse("Success", safe=False)
        else:
            return JsonResponse("", safe=False)
    # except:
    #     return JsonResponse("Invalid", safe=False)