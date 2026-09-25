from django.templatetags.static import static
from django.http import HttpResponse
from django.db.models import Sum
import json
from datetime import datetime
from decimal import Decimal
from django.core.files.base import ContentFile
from .models import Invoice, InvoiceItem, PaymentDocument, PaymentReceivedDetail
from io import BytesIO
from django.http import HttpResponse, JsonResponse
from xhtml2pdf import pisa
from django.views import View
from django.template.loader import get_template
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Case, When, F, DecimalField
from django.shortcuts import render
import os
import re
from rest_framework import generics
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
from app_client.serializers import ClientAddressSerializer, ClientSerializer
from app_company.models import Company
from app_default.models import InvoiceStatus, PaymentMode
from app_basic.models import Country, State
from app_default.serializers import InvoiceStatusSerializer
from app_basic.serializers import CountrySerializer, StateSerializer
from app_default.views import retry
from app_project.models import Project
from app_project.serializers import ProjectSerializer

from app_sale.models import Invoice, InvoiceDocument, InvoiceItem, PaymentReceived, Quotation, QuotationFile, QuotationItem
from app_sale.serializers import InvoiceDocumentSerializer, InvoiceItemSerializer, InvoiceSerializer, PaymentDocumentSerializer, PaymentReceivedDetailSerializer, PaymentReceivedSerializer, QuotationFileSerializer, QuotationItemSerializer, QuotationSerializer
from app_site.models import SiteSettings
from app_site.serializers import SiteSettingsSerializer
from app_staff.models import Staff
from app_staff.serializers import StaffSerializer
from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size = 40  # Adjust the page size as needed
    page_size_query_param = 'page_size'


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
@swagger_auto_schema(method='POST', request_body=QuotationSerializer, operation_description="NOTE: API for save Quotation")
@swagger_auto_schema(method='PUT', request_body=QuotationSerializer, operation_description="NOTE: API for edit Quotation")
@swagger_auto_schema(method='GET', operation_description="NOTE: Get all Quotation Details",)
@api_view(['GET', 'POST', 'PUT'])
@retry(retries=3, delay=2)
def QuotationApi(request):
    # try:
    if request.method == 'GET':
        quotation = Quotation.objects.all().order_by('-SortId')
        quotationSerializer = QuotationSerializer(
            quotation, many=True)
        quoteData = []
        for row in quotationSerializer.data:
            try:
                client = Client.objects.get(ClientId=row['ClientId'])
                clientSerializer = ClientSerializer(client)
                row['ClientName'] = clientSerializer.data['CustomerDisplayName']
            except:
                row['ClientName'] = []
            try:
                project = Project.objects.get(ProjectId=row['ProjectId'])
                projectSerializer = ProjectSerializer(project)
                row['ProjectName'] = projectSerializer.data['ProjectName']
            except:
                row['ProjectName'] = []
            try:
                staff = Staff.objects.get(StaffId=row['SalesPerson'])
                staffSerializer = StaffSerializer(staff)
                row['StaffName'] = staffSerializer.data['StaffName']
            except:
                row['StaffName'] = []
            quoteData.append(row)
        return JsonResponse(quoteData, safe=False)
    elif request.method == 'POST':
        quotationData = JSONParser().parse(request)
        quotationSerializer = QuotationSerializer(
            data=quotationData)
        if quotationSerializer.is_valid():
            quotationSerializer.save()
            return JsonResponse(quotationSerializer.data['QuotationId'], safe=False)
        return JsonResponse(quotationSerializer.errors, status=400, safe=False)
    elif request.method == 'PUT':
        quotationData = JSONParser().parse(request)
        quotation = Quotation.objects.get(
            QuotationId=quotationData['QuotationId'])
        quotationSerializer = QuotationSerializer(
            quotation, data=quotationData)
        if quotationSerializer.is_valid():
            quotationSerializer.save()
            return JsonResponse(quotationSerializer.data['QuotationId'], safe=False)
        return JsonResponse(quotationSerializer.errors, status=400, safe=False)
    else:
        return JsonResponse("", safe=False)
    # except:
    #     return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get Quotation by QuotationId",)
@swagger_auto_schema(method='DELETE', operation_description="NOTE: API for delete Quotation by QuotationId",)
@api_view(['GET', 'DELETE'])
@retry(retries=3, delay=2)
def QuotationApiById(request, QuotationId=""):
    try:
        if request.method == 'GET':
            quotation = Quotation.objects.get(
                QuotationId=QuotationId)
            quotationSerializer = QuotationSerializer(
                quotation)
            quoteData = quotationSerializer.data

            if quoteData.get('QuoteDate'):
                try:
                    quoteData['QuoteDate'] = datetime.strptime(
                        quoteData['QuoteDate'], '%d %b %Y').strftime('%Y-%m-%d')
                except:
                    try:
                        quoteData['QuoteDate'] = datetime.strptime(
                            quoteData['QuoteDate'], '%Y-%m-%d').strftime('%Y-%m-%d')
                    except:
                        pass

            if quoteData.get('ExpiryDate'):
                try:
                    quoteData['ExpiryDate'] = datetime.strptime(
                        quoteData['ExpiryDate'], '%d %b %Y').strftime('%Y-%m-%d')
                except:
                    try:
                        quoteData['ExpiryDate'] = datetime.strptime(
                            quoteData['ExpiryDate'], '%Y-%m-%d').strftime('%Y-%m-%d')
                    except:
                        pass

            quotationItem = QuotationItem.objects.filter(
                QuotationId=QuotationId).order_by('OrderNo', 'SortId')
            quotationItemSerializer = QuotationItemSerializer(
                quotationItem, many=True)
            quoteData['QuoteItems'] = quotationItemSerializer.data
            quotationFile = QuotationFile.objects.filter(
                QuotationId=QuotationId)
            quotationFileSerializer = QuotationFileSerializer(
                quotationFile, many=True)
            quoteData['QuoteFiles'] = quotationFileSerializer.data
            return JsonResponse(quoteData, safe=False)
        elif request.method == 'DELETE':
            quotation = Quotation.objects.get(QuotationId=QuotationId)
            quotation.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


class QuotationApiByCompanyId(generics.ListAPIView):
    queryset = Quotation.objects.filter(Q(IsLatest=True) | Q(IsLatest__isnull=True)).order_by('-SortId')
    pagination_class = CustomPagination
    serializer_class = QuotationSerializer

    def post(self, request, *args, **kwargs):
        try:
            self.queryset = Quotation.objects.filter(Q(IsLatest=True) | Q(IsLatest__isnull=True)).order_by('-SortId')
            filterData = JSONParser().parse(request)
            Keyword = filterData.get('SearchKeyword', '')
            if filterData.get('CompanyId'):
                self.queryset = self.queryset.filter(
                    CompanyId=filterData['CompanyId'])
            if Keyword:
                self.queryset = self.queryset.filter(
                    Q(Subject__icontains=Keyword) | Q(QuotationNumber__icontains=Keyword))
            page = self.paginate_queryset(self.queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                data = []

                for row in serializer.data:
                    try:
                        client = Client.objects.get(ClientId=row['ClientId'])
                        clientSerializer = ClientSerializer(client)
                        row['ClientName'] = clientSerializer.data['CustomerDisplayName']
                    except:
                        row['ClientName'] = []
                    try:
                        project = Project.objects.get(
                            ProjectId=row['ProjectId'])
                        projectSerializer = ProjectSerializer(project)
                        row['ProjectName'] = projectSerializer.data['ProjectName']
                    except:
                        row['ProjectName'] = []
                    try:
                        staff = Staff.objects.get(StaffId=row['SalesPerson'])
                        staffSerializer = StaffSerializer(staff)
                        row['StaffName'] = staffSerializer.data['StaffName']
                    except:
                        row['StaffName'] = []
                    data.append(row)
                return self.get_paginated_response(data)
        except:
            return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=QuotationItemSerializer, operation_description="NOTE: API for save QuotationItem")
@swagger_auto_schema(method='PUT', request_body=QuotationItemSerializer, operation_description="NOTE: API for edit QuotationItem")
@swagger_auto_schema(method='GET', operation_description="NOTE: API for Get all QuotationItem Details")
@api_view(['GET', 'POST', 'PUT'])
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
            return JsonResponse(quotationItemSerializer.errors, status=400, safe=False)
        elif request.method == 'PUT':
            quotationItemData = JSONParser().parse(request)
            item_id = quotationItemData.get('QuotationItemId')
            if item_id and QuotationItem.objects.filter(QuotationItemId=item_id).exists():
                quotationItem = QuotationItem.objects.get(QuotationItemId=item_id)
                quotationItemSerializer = QuotationItemSerializer(
                    quotationItem, data=quotationItemData)
            else:
                quotationItemSerializer = QuotationItemSerializer(
                    data=quotationItemData)
            if quotationItemSerializer.is_valid():
                quotationItemSerializer.save()
                return JsonResponse(quotationItemSerializer.data['QuotationItemId'], safe=False)
            return JsonResponse(quotationItemSerializer.errors, status=400, safe=False)
        else:
            return JsonResponse("", safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500, safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get quotationItem by QuotationItemId",)
@swagger_auto_schema(method='DELETE', operation_description="NOTE: API for delete quotationItem by QuotationItemId",)
@api_view(['GET', 'DELETE'])
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
            quotationItem = QuotationItem.objects.get(
                QuotationItemId=QuotationItemId)
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
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get QuotationFile by QuotationFileId",)
@swagger_auto_schema(method='DELETE', operation_description="NOTE: API for delete QuotationFile by QuotationFileId",)
@api_view(['GET', 'DELETE'])
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
            quotationFile = QuotationFile.objects.get(
                QuotationFileId=QuotationFileId)
            QuotationFile.objects.get(
                QuotationFileId=QuotationFileId).QuoteFile.delete(save=True)
            quotationFile.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


def check_credit_limit(client_id, new_invoice_amount, current_invoice_id=None):
    from app_client.models import Client
    from app_accounting.models import Account, JournalItem, JournalEntry

    try:
        if not client_id:
            return True, ""
        client = Client.objects.filter(ClientId=client_id).first()
        if not client or not client.CreditLimitEnforced:
            return True, ""

        try:
            limit = float(client.CreditLimit or "0.00")
        except ValueError:
            limit = 0.0

        if limit <= 0.0:
            return True, ""

        # Accounts Receivable code is '1200'
        accounts = Account.objects.filter(Code='1200')
        account_ids = [acc.AccountId for acc in accounts]

        # Calculate current outstanding balance (Debits - Credits)
        items = JournalItem.objects.filter(ClientId=client_id, AccountId__in=account_ids)

        if current_invoice_id:
            # Exclude journal items associated with the invoice being updated
            from app_sale.models import Invoice
            inv = Invoice.objects.filter(InvoiceId=current_invoice_id).first()
            ref_nums = [current_invoice_id]
            if inv and inv.InvoiceNumber:
                ref_nums.append(inv.InvoiceNumber)
            exclude_entry_ids = list(JournalEntry.objects.filter(
                ReferenceNumber__in=ref_nums,
                Source='invoice'
            ).values_list('JournalEntryId', flat=True))
            if exclude_entry_ids:
                items = items.exclude(JournalEntryId__in=exclude_entry_ids)

        outstanding_balance = 0.0
        for item in items:
            outstanding_balance += (float(item.Debit or "0.00") - float(item.Credit or "0.00"))

        try:
            new_amount = float(new_invoice_amount or "0.00")
        except ValueError:
            new_amount = 0.0

        if outstanding_balance + new_amount > limit:
            return False, f"Credit limit of {limit:.2f} exceeded. Current outstanding balance is {outstanding_balance:.2f}, and this invoice is {new_amount:.2f} (Total: {(outstanding_balance + new_amount):.2f})."
        return True, ""
    except Exception as e:
        # Fail-open in production to prevent user workflow block on system error
        return True, ""


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=InvoiceSerializer, operation_description="NOTE: API for save Invoice")
@swagger_auto_schema(method='PUT', request_body=InvoiceSerializer, operation_description="NOTE: API for edit Invoice")
@swagger_auto_schema(method='GET', operation_description="NOTE: API for Get all Invoice Details",)
@api_view(['GET', 'POST', 'PUT'])
@retry(retries=3, delay=2)
def InvoiceApi(request):
    try:
        from app_client.models import Client
        from app_client.serializers import ClientSerializer
        from app_staff.models import Staff
        from app_staff.serializers import StaffSerializer
        from app_default.models import InvoiceStatus
        from app_default.serializers import InvoiceStatusSerializer

        if request.method == 'GET':
            invoice = Invoice.objects.all().order_by('-SortId')
            invoiceSerializer = InvoiceSerializer(
                invoice, many=True)
            invoiceData = []
            for row in invoiceSerializer.data:
                try:
                    client = Client.objects.get(ClientId=row['ClientId'])
                    clientSerializer = ClientSerializer(client)
                    row['ClientName'] = clientSerializer.data['CustomerDisplayName']
                except:
                    row['ClientName'] = []
                try:
                    invoiceStatus = InvoiceStatus.objects.get(
                        InvoiceStatusId=row['Status'])
                    invoiceStatusSerializer = InvoiceStatusSerializer(
                        invoiceStatus)
                    row['StatusName'] = invoiceStatusSerializer.data['InvoiceStatus']
                except:
                    row['StatusName'] = []
                try:
                    staff = Staff.objects.get(StaffId=row['SalesPerson'])
                    staffSerializer = StaffSerializer(staff)
                    row['StaffName'] = staffSerializer.data['StaffName']
                except:
                    row['StaffName'] = []
                invoiceData.append(row)
            return JsonResponse(invoiceData, safe=False)
        elif request.method == 'POST':
            invoiceData = JSONParser().parse(request)
            client_id = invoiceData.get('ClientId')
            total_amount = invoiceData.get('TotalAmount', '0.00')

            allowed, msg = check_credit_limit(client_id, total_amount)
            if not allowed:
                return JsonResponse({"error": msg}, status=400)

            invoiceSerializer = InvoiceSerializer(
                data=invoiceData)
            if invoiceSerializer.is_valid():
                invoiceSerializer.save()
                return JsonResponse(invoiceSerializer.data['InvoiceId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            invoiceData = JSONParser().parse(request)
            client_id = invoiceData.get('ClientId')
            total_amount = invoiceData.get('TotalAmount', '0.00')
            invoice_id = invoiceData.get('InvoiceId')

            allowed, msg = check_credit_limit(client_id, total_amount, current_invoice_id=invoice_id)
            if not allowed:
                return JsonResponse({"error": msg}, status=400)

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
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get Invoice by InvoiceId",)
@swagger_auto_schema(method='DELETE', operation_description="NOTE: API for delete Invoice by InvoiceId",)
@api_view(['GET', 'DELETE'])
@retry(retries=3, delay=2)
def InvoiceApiById(request, InvoiceId=""):
    # try:
    if request.method == 'GET':
        invoice = Invoice.objects.get(
            InvoiceId=InvoiceId)
        invoiceSerializer = InvoiceSerializer(
            invoice)
        invoiceData = invoiceSerializer.data
        try:
            invoiceData['InvoiceDate'] = datetime.strptime(
                invoiceData['InvoiceDate'], '%d %b %Y')
        except:
            invoiceData['InvoiceDate'] = datetime.strptime(
                invoiceData['InvoiceDate'], '%Y-%m-%d')
        invoiceData['InvoiceDate'] = invoiceData['InvoiceDate'].strftime(
            '%Y-%m-%d')

        try:
            invoiceData['DueDate'] = datetime.strptime(
                invoiceData['DueDate'], '%d %b %Y')
        except:
            invoiceData['DueDate'] = datetime.strptime(
                invoiceData['DueDate'], '%Y-%m-%d')
        invoiceData['DueDate'] = invoiceData['DueDate'].strftime('%Y-%m-%d')

        invoiceItem = InvoiceItem.objects.filter(InvoiceId=InvoiceId)
        invoiceItemSerializer = InvoiceItemSerializer(
            invoiceItem, many=True)
        invoiceData['InvoiceItem'] = invoiceItemSerializer.data
        invoiceDocument = InvoiceDocument.objects.filter(
            InvoiceId=InvoiceId)
        invoiceDocumentSerializer = InvoiceDocumentSerializer(
            invoiceDocument, many=True)
        invoiceData['InvoiceDocuments'] = invoiceDocumentSerializer.data

        return JsonResponse(invoiceData, safe=False)
    elif request.method == 'DELETE':
        invoice = Invoice.objects.get(InvoiceId=InvoiceId)
        invoice.delete()
        return JsonResponse("Deleted successfully", safe=False)
    else:
        return JsonResponse("", safe=False)

    # except:
    #     return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get Invoice summery",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def invoice_summary_view(request, CompanyId=""):
    current_date = timezone.now().date()

    total_receivable_amount = 0
    current_amount = 0
    due_1_15_days = 0
    due_16_30_days = 0
    due_31_45_days = 0
    due_above_45_days = 0
    try:
        # Calculate the current date

        # Initialize totals

        # Define past date ranges
        past_15_days = current_date - timedelta(days=15)
        past_30_days = current_date - timedelta(days=30)
        past_45_days = current_date - timedelta(days=45)

        # Filter only Unpaid and Partially Paid invoices
        queryset = Invoice.objects.filter(
            CompanyId=CompanyId, Status__in=[2, 3])

        for invoice in queryset:
            # Parse DueDate
            due_date = parse_due_date(invoice.DueDate)
            amount_due = float(invoice.AmountDue) or 0

            # Aggregate total receivable amount
            total_receivable_amount += amount_due

            # Categorize each invoice into the appropriate range
            if due_date >= current_date:
                current_amount += amount_due
            elif past_15_days <= due_date < current_date:
                due_1_15_days += amount_due
            elif past_30_days <= due_date < past_15_days:
                due_16_30_days += amount_due
            elif past_45_days <= due_date < past_30_days:
                due_31_45_days += amount_due
            elif due_date < past_45_days:
                due_above_45_days += amount_due

        totals = {
            "total_receivable_amount": total_receivable_amount,
            "current_amount": current_amount,
            "due_1_15_days": due_1_15_days,
            "due_16_30_days": due_16_30_days,
            "due_31_45_days": due_31_45_days,
            "due_above_45_days": due_above_45_days,
        }
        totals = {
            "current_date": current_date,        "total_receivable_amount": totals.get("total_receivable_amount") or 0,
            "current_amount": totals.get("current_amount") or 0,
            "due_1_15_days": totals.get("due_1_15_days") or 0,
            "due_16_30_days": totals.get("due_16_30_days") or 0,
            "due_31_45_days": totals.get("due_31_45_days") or 0,
            "due_above_45_days": totals.get("due_above_45_days") or 0,
        }
        return JsonResponse(totals, safe=False)
    except:

        return JsonResponse({
            "current_date": current_date,        "total_receivable_amount":  0,
            "current_amount":  0,
            "due_1_15_days": 0,
            "due_16_30_days":  0,
            "due_31_45_days":  0,
            "due_above_45_days": 0,
        }, safe=False)


def parse_due_date(due_date_str):
    return datetime.strptime(due_date_str, "%d %b %Y").date()


class InvoiceApiByCompanyId(generics.ListAPIView):
    queryset = Invoice.objects.all().order_by('-OrderNumber')
    pagination_class = CustomPagination
    serializer_class = InvoiceSerializer

    def post(self, request, *args, **kwargs):
        try:
            filterData = JSONParser().parse(request)
            if filterData['CompanyId']:
                self.queryset = self.queryset.filter(
                    CompanyId=filterData['CompanyId'])
            page = self.paginate_queryset(self.queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                data = []

                for row in serializer.data:
                    try:
                        client = Client.objects.get(ClientId=row['ClientId'])
                        clientSerializer = ClientSerializer(client)
                        row['ClientName'] = clientSerializer.data['CustomerDisplayName']
                    except:
                        row['ClientName'] = []
                    try:
                        invoiceStatus = InvoiceStatus.objects.get(
                            InvoiceStatusId=row['Status'])
                        invoiceStatusSerializer = InvoiceStatusSerializer(
                            invoiceStatus)
                        row['StatusName'] = invoiceStatusSerializer.data['InvoiceStatus']
                    except:
                        row['StatusName'] = []
                    try:
                        staff = Staff.objects.get(StaffId=row['SalesPerson'])
                        staffSerializer = StaffSerializer(staff)
                        row['StaffName'] = staffSerializer.data['StaffName']
                    except:
                        row['StaffName'] = []
                    data.append(row)
                return self.get_paginated_response(data)
        except:
            return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=InvoiceItemSerializer, operation_description="NOTE: API for save InvoiceItem")
@swagger_auto_schema(method='PUT', request_body=InvoiceItemSerializer, operation_description="NOTE: API for edit InvoiceItem")
@swagger_auto_schema(method='GET', operation_description="NOTE:API for Get all InvoiceItem Details",)
@api_view(['GET', 'POST', 'PUT'])
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
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get InvoiceItem by InvoiceItemId",)
@swagger_auto_schema(method='DELETE', operation_description="NOTE: API for delete InvoiceItem by InvoiceItemId",)
@api_view(['GET', 'DELETE'])
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
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get InvoiceDocument by InvoiceDocumentId",)
@swagger_auto_schema(method='DELETE', operation_description="NOTE: API for delete InvoiceDocument by InvoiceDocumentId",)
@api_view(['GET', 'DELETE'])
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
            invoiceDocument = InvoiceDocument.objects.get(
                InvoiceDocumentId=InvoiceDocumentId)
            InvoiceDocument.objects.get(
                InvoiceDocumentId=InvoiceDocumentId).Document.delete(save=True)
            invoiceDocument.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=PaymentReceivedSerializer, operation_description="NOTE: API for save PaymentReceived")
@swagger_auto_schema(method='PUT', request_body=PaymentReceivedSerializer, operation_description="NOTE: API for edit PaymentReceived")
@swagger_auto_schema(method='GET', operation_description="NOTE: API for Get all PaymentReceived",)
@api_view(['GET', 'POST', 'PUT'])
@retry(retries=3, delay=2)
def PaymentReceivedApi(request):
    try:
        if request.method == 'GET':
            paymentReceived = PaymentReceived.objects.all().order_by('-SortId')
            paymentReceivedSerializer = PaymentReceivedSerializer(
                paymentReceived, many=True)
            paymentData = []
            for row in paymentReceivedSerializer.data:
                try:
                    client = Client.objects.get(ClientId=row['ClientId'])
                    clientSerializer = ClientSerializer(client)
                    row['ClientName'] = clientSerializer.data['CustomerDisplayName']
                except:
                    row['ClientName'] = []
                try:
                    staff = Staff.objects.get(StaffId=row['StaffId'])
                    staffSerializer = StaffSerializer(staff)
                    row['StaffName'] = staffSerializer.data['StaffName']
                except:
                    row['StaffName'] = []
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
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get paymentReceived by PaymentReceivedId",)
@swagger_auto_schema(method='DELETE', operation_description="NOTE: API for delete paymentReceived by PaymentReceivedId",)
@api_view(['GET', 'DELETE'])
@retry(retries=3, delay=2)
def PaymentReceivedApiById(request, PaymentReceivedId=""):
    try:
        if request.method == 'GET':
            paymentReceived = PaymentReceived.objects.get(
                PaymentReceivedId=PaymentReceivedId)
            paymentReceivedSerializer = PaymentReceivedSerializer(
                paymentReceived)
            PaymentData = paymentReceivedSerializer.data
            paymentReceivedDetail = PaymentReceivedDetail.objects.filter(
                PaymentReceivedId=PaymentReceivedId)
            paymentReceivedDetailSerializer = PaymentReceivedDetailSerializer(
                paymentReceivedDetail, many=True)
            PaymentData['PaymentReceivedDetail'] = paymentReceivedDetailSerializer.data
            paymentDocument = PaymentDocument.objects.filter(
                PaymentReceivedId=PaymentReceivedId)
            paymentDocumentSerializer = PaymentDocumentSerializer(
                paymentDocument, many=True)
            PaymentData['PaymentDocument'] = paymentDocumentSerializer.data

            return JsonResponse(PaymentData, safe=False)
        elif request.method == 'DELETE':
            paymentReceived = PaymentReceived.objects.get(
                PaymentReceivedId=PaymentReceivedId)
            paymentReceived.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


class PaymentReceivedApiCompanyId(generics.ListAPIView):
    queryset = PaymentReceived.objects.all().order_by('-SortId')
    pagination_class = CustomPagination
    serializer_class = PaymentReceivedSerializer

    def post(self, request, *args, **kwargs):
        try:
            filterData = JSONParser().parse(request)
            if filterData['CompanyId']:
                self.queryset = self.queryset.filter(
                    CompanyId=filterData['CompanyId'])
            page = self.paginate_queryset(self.queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                data = []

                for row in serializer.data:
                    try:
                        client = Client.objects.get(ClientId=row['ClientId'])
                        clientSerializer = ClientSerializer(client)
                        row['ClientName'] = clientSerializer.data['CustomerDisplayName']
                    except:
                        row['ClientName'] = []
                    try:
                        staff = Staff.objects.get(StaffId=row['StaffId'])
                        staffSerializer = StaffSerializer(staff)
                        row['StaffName'] = staffSerializer.data['StaffName']
                    except:
                        row['StaffName'] = []
                    data.append(row)
                return self.get_paginated_response(data)
        except:
            return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get PaymentDocument by PaymentDocumentId",)
@swagger_auto_schema(method='DELETE', operation_description="NOTE: API for delete PaymentDocument by PaymentDocumentId",)
@api_view(['GET', 'DELETE'])
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
            paymentDocument = PaymentDocument.objects.get(
                PaymentDocumentId=PaymentDocumentId)
            PaymentDocument.objects.get(
                PaymentDocumentId=PaymentDocumentId).Document.delete(save=True)
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


class DownloadPDF(View):
    def get(self, request, InvoiceId="", *args, **kwargs):
        invoice = Invoice.objects.get(
            InvoiceId=InvoiceId)
        invoiceItems = InvoiceItem.objects.filter(
            InvoiceId=InvoiceId).order_by('OrderNo')
        client = Client.objects.get(ClientId=invoice.ClientId)
        company = Company.objects.get(CompanyId=invoice.CompanyId)
        clientadrress = ClientAddress.objects.get(ClientId=invoice.ClientId)
        billingAddress = json.loads(invoice.BillingAddress)
        totalAmount = Decimal(invoice.TotalAmount)
        HalfTax = float(invoice.TaxPercentage) / 2
        HalfTaxAmount = float(invoice.TaxAmount) / 2
        siteSettings = SiteSettings.objects.get(CompanyId=invoice.CompanyId)
        currencyType = siteSettings.CurrencyType

        amountinwords = decimal_number_to_words(totalAmount, currencyType)
        # amountinwords=decimal_number_to_words(totalAmount)

        try:
            siteSettings = SiteSettings.objects.get(
                CompanyId=invoice.CompanyId)
            siteSettingsSerializer = SiteSettingsSerializer(siteSettings)
            logo = os.path.join(settings.BASE_DIR) + \
                siteSettingsSerializer.data['Logo']
        except:
            logo = ""
        context = {'invoice': invoice,
                   'invoiceItems': invoiceItems,
                   'clientadrress': clientadrress,
                   'siteSettings': siteSettings,
                   'billingAddress': billingAddress,
                   'amountinwords': amountinwords,
                   'company': company,
                   'client': client,
                   'HalfTax': HalfTax,
                   'HalfTaxAmount': HalfTaxAmount,
                   'logo': logo}
        if siteSettings.InvoiceTemplate == 'invoice.html':
            pdf = render_to_pdf('invoice.html', context)

        elif siteSettings.InvoiceTemplate == 'woodsInvoice.html':
            pdf = render_to_pdf('woodsInvoice.html', context)
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "%s.pdf" % (context['invoice'].InvoiceNumber)

        content = "attachment; filename=%s" % (filename)
        response['Content-Disposition'] = content
        return response


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()

    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
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


# save and print


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for view invoice PDF",)
@api_view(['GET'])
def ViewPDF(request, InvoiceId=""):
    try:
        if request.method == 'GET':
            invoice = Invoice.objects.get(InvoiceId=InvoiceId)
            invoiceItems = InvoiceItem.objects.filter(
                InvoiceId=InvoiceId).order_by('OrderNo')
            company = Company.objects.get(CompanyId=invoice.CompanyId)
            client = Client.objects.get(ClientId=invoice.ClientId)
            clientaddress = ClientAddress.objects.get(
                ClientId=invoice.ClientId)
            billingAddress = json.loads(invoice.BillingAddress)
            totalAmount = Decimal(invoice.TotalAmount)
            siteSettings = SiteSettings.objects.get(
                CompanyId=invoice.CompanyId)
            currencyType = siteSettings.CurrencyType

            HalfTax = float(invoice.TaxPercentage) / 2
            HalfTaxAmount = float(invoice.TaxAmount) / 2
            amountinwords = decimal_number_to_words(totalAmount, currencyType)
            # amountinwords=decimal_number_to_words(totalAmount)
            try:
                siteSettings = SiteSettings.objects.get(
                    CompanyId=invoice.CompanyId)
                siteSettingsSerializer = SiteSettingsSerializer(siteSettings)
                logo = os.path.join(settings.BASE_DIR) + \
                    siteSettingsSerializer.data['Logo']

            except:
                logo = ""

            bankAccount = ""
            if invoice.AddBankAccount == True:
                bankAccount = siteSettings.BankAccount
            else:
                bankAccount = ""

            try:
                InvoiceDate = datetime.strptime(
                    invoice.InvoiceDate, '%Y-%m-%d')

                # Format the date in '25 Mar 2024' format
                invoice.InvoiceDate = InvoiceDate.strftime('%d %b %Y')

            except:
                p = ""
            try:
                DueDate = datetime.strptime(invoice.DueDate, '%Y-%m-%d')

                # Format the date in '25 Mar 2024' format
                invoice.DueDate = DueDate.strftime('%d %b %Y')
            except:
                p = ""
            context = {
                'invoice': invoice,
                'invoiceItems': invoiceItems,
                'clientaddress': clientaddress,
                'logo': logo,
                'amountinwords': amountinwords,
                'siteSettings': siteSettings,
                'billingAddress': billingAddress,
                'client': client,
                'company': company,
                'bankAccount': bankAccount,
                'HalfTax': HalfTax,
                'HalfTaxAmount': HalfTaxAmount
            }
            if siteSettings.InvoiceTemplate == 'invoice.html':

                pdf = render_to_pdf('invoice.html', context)
            elif siteSettings.InvoiceTemplate == 'woodsInvoice.html':

                pdf = render_to_pdf('woodsInvoice.html', context)

            filename = "%s.pdf" % (context['invoice'].InvoiceNumber)

            if invoice.InvoiceFile:
                invoice.InvoiceFile.delete(save=True)
                invoice.InvoiceFile.save(filename, ContentFile(pdf.content))
            else:
                invoice.InvoiceFile.save(filename, ContentFile(pdf.content))
            return HttpResponse(pdf.content, content_type='application/pdf')

        else:
            return JsonResponse({"error": "Invalid method"}, status=405)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@swagger_auto_schema(method='POST', operation_description="NOTE: API for send invoice by email. paylaod {CCEmailId,InvoiceId,EmailId }",)
@api_view(['POST'])
@retry(retries=3, delay=2)
def SendInvoice(request):

    try:
        if request.method == 'POST':
            requestData = JSONParser().parse(request)
            CCEmail = requestData.get('CCEmailId', '').split(',')
            # CCEmail = json.loads(requestData.get('CCEmailId', '[]'))
            InvoiceId = requestData['InvoiceId']
            # client=Client.objects.get(ClientId=invoice.ClientId)
            invoice = Invoice.objects.get(InvoiceId=InvoiceId)
            company = Company.objects.get(CompanyId=invoice.CompanyId)
            invoiceItems = InvoiceItem.objects.filter(
                InvoiceId=InvoiceId).order_by('OrderNo')
            invoiceItemSerializer = InvoiceItemSerializer(
                invoiceItems, many=True)
            Itemdata = []
            for col in invoiceItemSerializer.data:
                item_details = {
                    'Workdetails': col['ItemDetails']
                }
                Itemdata.append(item_details)
            itemdata_json = json.dumps(Itemdata)
            billingAddress = json.loads(invoice.BillingAddress)
            try:
                siteSettings = SiteSettings.objects.get(
                    CompanyId=invoice.CompanyId)
                siteSettingsSerializer = SiteSettingsSerializer(siteSettings)
                logo = os.path.join(settings.BASE_DIR) + \
                    siteSettingsSerializer.data['Logo']
            except:
                logo = ""
            try:
                clientaddress = ClientAddress.objects.get(
                    ClientId=invoice.ClientId)
            except:
                clientaddress = ""
            client = Client.objects.get(ClientId=invoice.ClientId)
            invoiceId = invoice.InvoiceId
            context = {
                'invoice': invoice,
                'invoiceItems': invoiceItems,
                'clientaddress': clientaddress,
                'client': client,
                'billingAddress': billingAddress,
                'siteSettings': siteSettings,
                'invoiceId': invoiceId,
                'logo': logo,
                'company': company
                # 'client':client
            }
            if siteSettings.InvoiceTemplate == 'invoice.html':
                pdf = render_to_pdf('invoice.html', context)

            elif siteSettings.InvoiceTemplate == 'woodsInvoice.html':
                pdf = render_to_pdf('woodsInvoice.html', context)
            invoice_file_name = f'{invoice.InvoiceNumber}.pdf'
            if invoice.InvoiceFile:
                invoice.InvoiceFile.delete(save=True)
                invoice.InvoiceFile.save(
                    invoice_file_name, ContentFile(pdf.content))
            else:
                invoice.InvoiceFile.save(
                    invoice_file_name, ContentFile(pdf.content))
            InvoiceNumber = invoice.InvoiceNumber
            TotalAmount = invoice.TotalAmount
            Invoicedate = invoice.InvoiceDate
            DueDate = invoice.DueDate
            # InvoiceDate=invoice.InvoiceDate
            Name = client.CustomerDisplayName
            Companyname = client.CompanyName
            customerMailId = requestData['EmailId']

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
            data = data.replace("{{InvoiceDate}}", Invoicedate)
            # data = data.replace("{{logo}}", logo)
            # all_item_details = ""
            # for item in invoiceItems:
            #     all_item_details += item.ItemDetails + "\n"
            # data = data.replace("{{Itemdetails}}", all_item_details)
            all_item_details = ""
            for item in invoiceItems:
                all_item_details += f"<li>{item.ItemDetails}</li>\n"

            # Replace the placeholder for ItemDetails in the email template
            data = data.replace(
                "<ul>{{Itemdetails}}</ul>", f"<ul>{all_item_details}</ul>")
            data = data.replace("{{DueDate}}", DueDate)
            data = data.replace("{{InvoiceDate}}", Invoicedate)

            msg.set_content(data, subtype="plain", charset='us-ascii')
            msg.add_alternative(data, subtype='html')

            response = sendCubexizsoftMail(msg)
            return JsonResponse("Success", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=PaymentReceivedDetailSerializer, operation_description="NOTE: API for save PaymentReceivedDetail")
@swagger_auto_schema(method='PUT', request_body=PaymentReceivedDetailSerializer, operation_description="NOTE: API for edit PaymentReceivedDetail")
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get all PaymentReceivedDetail",)
@api_view(['GET', 'POST', 'PUT'])
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
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get PaymentReceivedDetail by PaymentReceivedDetailId",)
@swagger_auto_schema(method='DELETE', operation_description="NOTE: API for delete PaymentReceivedDetail by PaymentReceivedDetailId",)
@api_view(['GET', 'DELETE'])
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
            paymentReceivedDetail = PaymentReceivedDetail.objects.get(
                PaymentReceivedDetailId=PaymentReceivedDetailId)
            paymentReceivedDetail.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE:API for Get All Unpaid Invoice By ClientId")
@api_view(['GET'])
@retry(retries=3, delay=2)
def GetAllUnpaidInvoiceByClientIdApi(request, ClientId=""):
    try:
        if request.method == 'GET':
            invoices = Invoice.objects.filter(Q(Status=2) | Q(
                Status=3), ClientId=ClientId).order_by('SortId')
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

            invoiceData.append(
                {'PendingAmount': pendingAmount, 'AdvanceAmount': advanceAmount})

            return JsonResponse(invoiceData, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


def number_to_words(number):
    # Define lists of words for numbers
    units = ["", "One", "Two", "Three", "Four",
             "Five", "Six", "Seven", "Eight", "Nine"]
    teens = ["", "Eleven", "Twelve", "Thirteen", "Fourteen",
             "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "Ten", "Twenty", "Thirty", "Forty",
            "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]

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
            result = convert_less_than_thousand(
                chunk) + (" " + scales[scale_index] if scale_index > 0 else "") + (" " + result if result != "" else "")

        number //= 1000
        scale_index += 1

    return result.strip()


def decimal_number_to_words(number, currencyType):
    integer_part = int(number)
    fractional_part = int((number - integer_part) * 100)

    words_integer_part = number_to_words(integer_part)
    words_fractional_part = number_to_words(fractional_part)
    if currencyType == 'INR':
        if fractional_part > 0:
            Amount = words_integer_part + " Rupees and " + words_fractional_part + " Paisa."
        else:
            Amount = words_integer_part + " Rupees only."
    elif currencyType == 'AED':
        if fractional_part > 0:
            Amount = words_integer_part + " Dirhams and " + words_fractional_part + " Fils."
        else:
            Amount = words_integer_part + " Dirhams only."

    return Amount


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE:API for view woodsinteriors invoice PDF")
@api_view(['GET'])
def ViewPDFWoodsInteriors(request, InvoiceId=""):
    try:
        if request.method == 'GET':
            invoice = Invoice.objects.get(InvoiceId=InvoiceId)
            invoiceItems = InvoiceItem.objects.filter(
                InvoiceId=InvoiceId).order_by('OrderNo')
            clientaddress = ClientAddress.objects.get(
                ClientId=invoice.ClientId)
            totalAmount = Decimal(invoice.TotalAmount)
            billingAddress = json.loads(invoice.BillingAddress)
            siteSettings = SiteSettings.objects.get(
                CompanyId=invoice.CompanyId)
            currencyType = siteSettings.CurrencyType

            amountinwords = decimal_number_to_words(totalAmount, currencyType)
            context = {
                'invoice': invoice,
                'invoiceItems': invoiceItems,
                'clientaddress': clientaddress,
                'amountinwords': amountinwords,
                'billingAddress': billingAddress
            }
            pdf = render_to_pdf('woodsInvoice.html', context)

            invoice_file_name = f'{invoice.InvoiceNumber}.pdf'
            if invoice.InvoiceFile:
                invoice.InvoiceFile.delete(save=True)
                invoice.InvoiceFile.save(
                    invoice_file_name, ContentFile(pdf.content))
            else:
                invoice.InvoiceFile.save(
                    invoice_file_name, ContentFile(pdf.content))
            return HttpResponse(pdf.content, content_type='application/pdf')

        else:
            return JsonResponse({"error": "Invalid method"}, status=405)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


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
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get PaymentReceivedDetail by ClientId",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def PaymentReceivedApClientId(request, ClientId=""):
    try:
        if request.method == 'GET':

            paymentReceivedDetail = PaymentReceivedDetail.objects.filter(
                RefId=ClientId)
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
@swagger_auto_schema(method='GET', operation_description="NOTE: API for View payment PDF",)
@api_view(['GET'])
def ViewPaymentPDF(request, PaymentReceivedId=""):
    try:
        if request.method == 'GET':
            payment = PaymentReceived.objects.get(
                PaymentReceivedId=PaymentReceivedId)
            paymentMode = PaymentMode.objects.get(
                PaymentModeId=payment.PaymentMode)
            company = Company.objects.get(CompanyId=payment.CompanyId)
            billingAdress = ClientAddress.objects.get(
                ClientId=payment.ClientId)
            billingAdressSerializer = ClientAddressSerializer(billingAdress)
            billingaddressdata = billingAdressSerializer.data
            try:
                country = Country.objects.get(CountryId=billingAdress.Country)
                countrySerializer = CountrySerializer(country)
                billingaddressdata['CountryName'] = countrySerializer.data['Country']
            except:
                billingaddressdata['CountryName'] = ""
            try:
                state = State.objects.get(StateId=billingAdress.State)
                stateSerializer = StateSerializer(state)
                billingaddressdata['StateName'] = stateSerializer.data['State']
            except:
                billingaddressdata['StateName'] = ""

            client = Client.objects.get(ClientId=payment.ClientId)

            # amountinwords=decimal_number_to_words(totalAmount)
            siteSettings = None
            try:
                siteSettings = SiteSettings.objects.get(
                    CompanyId=payment.CompanyId)
                siteSettingsSerializer = SiteSettingsSerializer(siteSettings)
                logo = os.path.join(settings.BASE_DIR) + \
                    siteSettingsSerializer.data['Logo']
            except:
                logo = ""

            context = {
                'payment': payment,
                'paymentDate': datetime.strptime(payment.PaymentDate, '%Y-%m-%d').strftime('%B %d, %Y'),
                'company': company,
                'paymentMode': paymentMode,
                'billingaddressdata': billingaddressdata,
                'client': client,
                'logo': logo,
                'siteSettings': siteSettings
            }

            pdf = render_to_pdf('payment.html', context)

            invoice_file_name = f'{PaymentReceivedId}.pdf'
            if payment.Receipt:
                payment.Receipt.delete(save=True)
                payment.Receipt.save(
                    invoice_file_name, ContentFile(pdf.content))
            else:
                payment.Receipt.save(
                    invoice_file_name, ContentFile(pdf.content))
            return HttpResponse(pdf.content, content_type='application/pdf')

        else:
            return JsonResponse({"error": "Invalid method"}, status=405)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


class DownloadPaymentPDF(View):
    def get(self, request, PaymentReceivedId="", *args, **kwargs):
        payment = PaymentReceived.objects.get(
            PaymentReceivedId=PaymentReceivedId)
        company = Company.objects.get(CompanyId=payment.CompanyId)
        paymentMode = PaymentMode.objects.get(
            PaymentModeId=payment.PaymentMode)
        billingAdress = ClientAddress.objects.get(ClientId=payment.ClientId)
        client = Client.objects.get(ClientId=payment.ClientId)

        # amountinwords=decimal_number_to_words(totalAmount)
        siteSettings = None
        try:
            siteSettings = SiteSettings.objects.get(
                CompanyId=payment.CompanyId)
            siteSettingsSerializer = SiteSettingsSerializer(siteSettings)
            logo = os.path.join(settings.BASE_DIR) + \
                siteSettingsSerializer.data['Logo']
        except:
            logo = ""
        context = {
            'payment': payment,
            'paymentMode': paymentMode,
            'billingAdress': billingAdress,
            'client': client,
            'company': company,
            'logo': logo,
            'siteSettings': siteSettings
        }
        pdf = render_to_pdf('Payment.html', context)
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Receipt_%s.pdf" % (context['payment'])
        content = "attachment; filename=%s" % (filename)
        response['Content-Disposition'] = content
        return response


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for View payment PDF",)
@api_view(['GET'])
def ViewQuotationPDF(request, QuotationId=""):
    # try:
    if request.method == 'GET':
        quote = Quotation.objects.get(QuotationId=QuotationId)
        invoiceItems = QuotationItem.objects.filter(
            QuotationId=QuotationId).order_by('OrderNo', 'SortId')
        try:
            company = Company.objects.get(CompanyId=quote.CompanyId)
        except:
            company = Company.objects.first()

        client = Client.objects.get(ClientId=quote.ClientId)
        try:
            clientaddress = ClientAddress.objects.get(ClientId=quote.ClientId)
            try:
                country = Country.objects.get(CountryId=clientaddress.Country)
                countrySerializer = CountrySerializer(country)
                clientaddress.Country = countrySerializer.data['Country']
            except:
                clientaddress.Country = ""
        except:
            clientaddress = type('Addr', (object,), {
                'Address1': '',
                'Address2': '',
                'Country': ''
            })()

        totalAmount = Decimal(quote.TotalAmount)
        try:
            siteSettings = SiteSettings.objects.get(CompanyId=quote.CompanyId)
        except:
            siteSettings = SiteSettings.objects.first()

        if not siteSettings:
            siteSettings = type('Settings', (object,), {
                'CurrencyType': 'INR',
                'QuotationPrefix': 'QT-',
                'Logo': '',
                'BankAccount': ''
            })()

        currencyType = siteSettings.CurrencyType
        amountinwords = decimal_number_to_words(totalAmount, currencyType)

        try:
            logo = os.path.join(settings.BASE_DIR) + siteSettings.Logo
        except:
            logo = ""

        try:
            QuoteDate = datetime.strptime(quote.QuoteDate, '%Y-%m-%d')

            # Format the date in '25 Mar 2024' format
            quote.QuoteDate = QuoteDate.strftime('%d %b %Y')

        except:
            p = ""
        try:
            ExpiryDate = datetime.strptime(quote.ExpiryDate, '%Y-%m-%d')

            # Format the date in '25 Mar 2024' format
            quote.ExpiryDate = ExpiryDate.strftime('%d %b %Y')
        except:
            p = ""

        logo_url = request.build_absolute_uri(static('images/line.webp'))
        other_image_url = request.build_absolute_uri(
            static('images/round.webp'))
        bankAccount = ""
        if quote.AddBankAccount and siteSettings and siteSettings.BankAccount:
            bankAccount = siteSettings.BankAccount

        context = {
            'quote': quote,
            'invoiceItems': invoiceItems,
            'clientaddress': clientaddress,
            'logo': logo,
            'amountinwords': amountinwords,
            'siteSettings': siteSettings,
            'bankAccount': bankAccount,
            'logo_url': logo_url,
            'other_image_url': other_image_url,
            'client': client,
            'company': company,
        }

        template_src = 'quotation.html'
        if quote.TemplateName == 'modern':
            template_src = 'quotation_modern.html'
        elif quote.TemplateName == 'classic':
            template_src = 'quotation_classic.html'

        pdf = render_to_pdf(template_src, context)

        invoice_file_name = f'{quote.QuotationNumber}.pdf'

        if quote.QuotationFile:
            quote.QuotationFile.delete(save=True)
            quote.QuotationFile.save(
                invoice_file_name, ContentFile(pdf.content))
        response = HttpResponse(pdf.content, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{invoice_file_name}"'
        return response

    else:
        return JsonResponse({"error": "Invalid method"}, status=405)


@csrf_exempt
@api_view(['POST'])
def ApproveQuotationAndCreateTasks(request):
    try:
        data = JSONParser().parse(request)
        quotation_id = data.get('QuotationId')
        task_assigned_by = data.get('TaskAssignedBy', '')
        tasks_data = data.get('tasks', [])
        
        quote = Quotation.objects.get(QuotationId=quotation_id)
        quote.ApprovalStatus = 'approved'
        quote.save()

        from app_project.models import ProjectTask
        from app_default.models import TaskStatus
        
        default_status = TaskStatus.objects.first()
        status_id = str(default_status.StatusId) if default_status else "1"

        created_tasks = []
        for item in tasks_data:
            task_title = item.get('ItemName') or item.get('Title') or "Quotation Task"
            task_duration = str(item.get('Duration') or '0:10')
            assigned_to = str(item.get('TaskAssignedTo') or '')
            deadline = item.get('ScheduledDeadline') or quote.ExpiryDate or datetime.now().strftime('%Y-%m-%dT%H:%M')
            desc = item.get('Description') or f"Task created from Quotation {quote.QuotationNumber}"

            new_task = ProjectTask.objects.create(
                ProjectId=quote.ProjectId or "",
                ClientId=quote.ClientId or "",
                CompanyId=quote.CompanyId or "",
                Title=task_title,
                Description=desc,
                Duration=task_duration,
                Status=status_id,
                TaskAssignedTo=assigned_to,
                TaskAssignedBy=task_assigned_by or quote.SalesPerson or "",
                ScheduledDeadline=deadline,
                RefId=quote.QuotationId,
                TaskType='Quotation',
                CreatedDate=datetime.now().strftime('%Y-%m-%d')
            )
            created_tasks.append(new_task.ProjectTaskId)

        return JsonResponse({
            "message": "Quotation approved and tasks created successfully",
            "quotation_id": quote.QuotationId,
            "created_tasks_count": len(created_tasks),
            "task_ids": created_tasks
        }, status=200, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400, safe=False)


@csrf_exempt
@api_view(['POST'])
def ReviseQuotation(request):
    try:
        data = JSONParser().parse(request)
        quotation_id = data.get('QuotationId')
        current_quote = Quotation.objects.get(QuotationId=quotation_id)
        
        root_quote_id = current_quote.ParentQuotationId or current_quote.QuotationId
        
        # Archive current quote
        current_quote.IsLatest = False
        current_quote.ApprovalStatus = 'revised'
        current_quote.save()

        # Next version number
        new_version = current_quote.VersionNumber + 1
        base_quote_num = re.sub(r'-V\d+$', '', current_quote.QuotationNumber or 'QUO')
        new_quotation_number = f"{base_quote_num}-V{new_version}"

        # Create new revision in draft state
        new_quote = Quotation.objects.create(
            ClientId=current_quote.ClientId,
            CompanyId=current_quote.CompanyId,
            QuotationNumber=new_quotation_number,
            ReferenceNumber=current_quote.ReferenceNumber,
            QuoteDate=datetime.now().strftime('%Y-%m-%d'),
            ExpiryDate=current_quote.ExpiryDate,
            SalesPerson=current_quote.SalesPerson,
            ProjectId=current_quote.ProjectId,
            Subject=current_quote.Subject,
            CustomerNotes=current_quote.CustomerNotes,
            TermsNConditions=current_quote.TermsNConditions,
            SubTotalAmount=current_quote.SubTotalAmount,
            TotalAmount=current_quote.TotalAmount,
            VersionNumber=new_version,
            ApprovalStatus='draft',
            TemplateName=current_quote.TemplateName,
            QuotationType=current_quote.QuotationType,
            Summary=current_quote.Summary,
            PaymentTerms=current_quote.PaymentTerms,
            SummaryTitle=current_quote.SummaryTitle,
            WorkBreakdownTitle=current_quote.WorkBreakdownTitle,
            NotesTitle=current_quote.NotesTitle,
            PaymentTermsTitle=current_quote.PaymentTermsTitle,
            TermsTitle=current_quote.TermsTitle,
            AddBankAccount=current_quote.AddBankAccount,
            BankAccountTitle=current_quote.BankAccountTitle,
            ParentQuotationId=root_quote_id,
            IsLatest=True
        )

        items = QuotationItem.objects.filter(QuotationId=current_quote.QuotationId).order_by('OrderNo', 'SortId')
        for item in items:
            QuotationItem.objects.create(
                QuotationId=new_quote.QuotationId,
                ItemName=item.ItemName,
                Quantity=item.Quantity,
                Rate=item.Rate,
                DiscountPercent=item.DiscountPercent,
                Amount=item.Amount,
                OrderNo=item.OrderNo
            )

        return JsonResponse({
            "message": "Quotation revised successfully",
            "new_quotation_id": new_quote.QuotationId,
            "version_number": new_quote.VersionNumber,
            "quotation_number": new_quote.QuotationNumber
        }, status=200, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400, safe=False)


@csrf_exempt
@api_view(['GET'])
def GetQuotationRevisions(request, QuotationId=""):
    try:
        quote = Quotation.objects.get(QuotationId=QuotationId)
        root_id = quote.ParentQuotationId or quote.QuotationId
        
        revisions = Quotation.objects.filter(
            Q(QuotationId=root_id) | Q(ParentQuotationId=root_id)
        ).order_by('VersionNumber')

        rev_data = []
        for r in revisions:
            rev_data.append({
                "QuotationId": r.QuotationId,
                "QuotationNumber": r.QuotationNumber,
                "VersionNumber": r.VersionNumber,
                "ApprovalStatus": r.ApprovalStatus,
                "TotalAmount": r.TotalAmount,
                "QuoteDate": r.QuoteDate,
                "ExpiryDate": r.ExpiryDate,
                "IsLatest": r.IsLatest,
                "InvoiceId": r.InvoiceId,
                "CreatedDate": r.SortId.strftime('%d %b %Y %H:%M') if r.SortId else ""
            })
        return JsonResponse(rev_data, status=200, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400, safe=False)


@csrf_exempt
@api_view(['GET'])
def CheckQuotationTasksStatus(request, QuotationId=""):
    try:
        from app_project.models import ProjectTask
        from app_default.models import TaskStatus

        tasks = ProjectTask.objects.filter(RefId=QuotationId, TaskType='Quotation')
        total_tasks = tasks.count()
        completed_tasks = 0
        task_list = []

        for t in tasks:
            status_name = ""
            is_completed = False
            try:
                ts = TaskStatus.objects.get(StatusId=t.Status)
                status_name = ts.Status
                if "completed" in status_name.lower() or "done" in status_name.lower() or "verified" in status_name.lower() or str(ts.Point) == "100":
                    is_completed = True
            except:
                status_name = str(t.Status)

            if is_completed:
                completed_tasks += 1

            task_list.append({
                "ProjectTaskId": t.ProjectTaskId,
                "Title": t.Title,
                "Duration": t.Duration,
                "Status": t.Status,
                "StatusName": status_name,
                "TaskAssignedTo": t.TaskAssignedTo,
                "ScheduledDeadline": t.ScheduledDeadline,
                "IsCompleted": is_completed
            })

        all_completed = (total_tasks > 0 and completed_tasks == total_tasks)

        return JsonResponse({
            "QuotationId": QuotationId,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "all_completed": all_completed,
            "tasks": task_list
        }, status=200, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400, safe=False)


@csrf_exempt
@api_view(['POST'])
def ConvertQuotationToInvoice(request):
    try:
        data = JSONParser().parse(request)
        quotation_id = data.get('QuotationId')
        quote = Quotation.objects.get(QuotationId=quotation_id)

        if quote.InvoiceId and Invoice.objects.filter(InvoiceId=quote.InvoiceId).exists():
            inv = Invoice.objects.get(InvoiceId=quote.InvoiceId)
            return JsonResponse({
                "message": "Quotation already converted to Invoice",
                "invoice_id": inv.InvoiceId,
                "invoice_number": inv.InvoiceNumber
            }, status=200, safe=False)

        from app_site.models import SiteSettings
        invoice_prefix = "INV-"
        try:
            settings = SiteSettings.objects.get(CompanyId=quote.CompanyId)
            if settings.InvoicePrefix:
                invoice_prefix = settings.InvoicePrefix
        except:
            pass

        last_invoice = Invoice.objects.filter(CompanyId=quote.CompanyId).order_by('-SortId').first()
        if last_invoice and last_invoice.InvoiceNumber:
            try:
                num_part = int(re.findall(r'\d+', last_invoice.InvoiceNumber)[-1])
                next_num = num_part + 1
            except:
                next_num = Invoice.objects.filter(CompanyId=quote.CompanyId).count() + 1
        else:
            next_num = 1
        
        invoice_number = f"{invoice_prefix}{str(next_num).zfill(4)}"

        order_num = 1
        if last_invoice and last_invoice.OrderNumber:
            order_num = (last_invoice.OrderNumber or 0) + 1

        new_invoice = Invoice.objects.create(
            ClientId=quote.ClientId,
            CompanyId=quote.CompanyId,
            ProjectId=quote.ProjectId,
            SalesPerson=quote.SalesPerson,
            InvoiceNumber=invoice_number,
            OrderNumber=order_num,
            InvoiceDate=quote.QuoteDate or datetime.now().strftime('%d %b %Y'),
            DueDate=quote.ExpiryDate or datetime.now().strftime('%d %b %Y'),
            Subject=quote.Subject,
            CustomerNotes=quote.CustomerNotes,
            TermsNConditions=quote.TermsNConditions,
            SubTotalAmount=quote.SubTotalAmount or "0.00",
            TotalAmount=quote.TotalAmount or "0.00",
            AmountDue=quote.TotalAmount or "0.00",
            Status=1,
            AddBankAccount=quote.AddBankAccount
        )

        items = QuotationItem.objects.filter(QuotationId=quote.QuotationId).order_by('OrderNo', 'SortId')
        for item in items:
            InvoiceItem.objects.create(
                InvoiceId=new_invoice.InvoiceId,
                ItemName=item.ItemName,
                Quantity=item.Quantity or "1",
                Rate=item.Rate or "0",
                DiscountPercent=item.DiscountPercent or "0",
                Amount=item.Amount or "0",
                OrderNo=item.OrderNo
            )

        quote.ApprovalStatus = 'invoiced'
        quote.InvoiceId = new_invoice.InvoiceId
        quote.save()

        return JsonResponse({
            "message": "Quotation converted to Invoice successfully",
            "invoice_id": new_invoice.InvoiceId,
            "invoice_number": new_invoice.InvoiceNumber
        }, status=200, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400, safe=False)


@csrf_exempt
@api_view(['POST'])
def CancelQuotation(request, QuotationId=""):
    try:
        quote = Quotation.objects.get(QuotationId=QuotationId)
        quote.ApprovalStatus = 'cancelled'
        quote.save()
        return JsonResponse({
            "message": "Quotation cancelled successfully",
            "quotation_id": quote.QuotationId,
            "status": quote.ApprovalStatus
        }, status=200, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400, safe=False)


    # except Exception as e:
    #     return JsonResponse({"error": str(e)}, status=500)
