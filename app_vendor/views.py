from django.shortcuts import render

# Create your views here.
from datetime import date
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from app_vendor.models import Vendor, VendorAddress, VendorBankDetails, VendorContactPerson, VendorDocuments, VendorBill
from app_vendor.serializers import VendorAddressSerializer, VendorBankDetailsSerializer, VendorContactPersonSerializer, VendorDocumentsSerializer, VendorSerializer, VendorBillSerializer
from datetime import datetime
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from app_basic.models import Country, State
from app_basic.serializers import CountrySerializer, StateSerializer
from app_default.views import retry
from app_project.views import CustomPageNumberPagination
from rest_framework import generics
from django.db.models import Q
from django.db import transaction   

@csrf_exempt
@swagger_auto_schema(method='POST', request_body=VendorSerializer,operation_description="NOTE: API for save Vendor")
@swagger_auto_schema(method='PUT', request_body=VendorSerializer,operation_description="NOTE: API for edit Vendor")
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all vendor by company id",)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
def VendorApi(request,CompanyId=""):
    try:
        if request.method == 'GET':
            vendor = Vendor.objects.filter(ActiveStatus=1,CompanyId=CompanyId)
            vendorSerializer = VendorSerializer(
                    vendor, many=True)
            return JsonResponse(vendorSerializer.data, safe=False)
        elif request.method == 'POST':
            vendorData = JSONParser().parse(request)
            vendorSerializer = VendorSerializer(
                data=vendorData)
            if vendorSerializer.is_valid():
                vendorSerializer.save()
                return JsonResponse(vendorSerializer.data['VendorId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            vendorData = JSONParser().parse(request)
            vendor = Vendor.objects.get(
                VendorId=vendorData['VendorId'])
            vendorSerializer = VendorSerializer(
                vendor, data=vendorData)
            if vendorSerializer.is_valid():
                vendorSerializer.save()
                return JsonResponse(vendorSerializer.data['VendorId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get Vendor by VendorId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete Vendor by VendorId",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def VendorApiById(request, VendorId=""):
    try:
        if request.method == 'GET': 
            vendor = Vendor.objects.get(
                    VendorId=VendorId)
            vendorSerializer = VendorSerializer(
                    vendor)
            vendorData=vendorSerializer.data
            vendorDocuments=VendorDocuments.objects.filter(VendorId=VendorId)
            vendorDocumentsSerializer = VendorDocumentsSerializer(
                    vendorDocuments,many=True)
            vendorData['VendorDocuments']=vendorDocumentsSerializer.data
               
            vendorAddress = VendorAddress.objects.filter(VendorId=VendorId)
            vendorAddressSerializer = VendorAddressSerializer(
                    vendorAddress, many=True)
            vendorData['VendorAddress']=vendorAddressSerializer.data
            contactPerson = VendorContactPerson.objects.filter(VendorId=VendorId)
            contactPersonSerializer = VendorContactPersonSerializer(
                    contactPerson, many=True)
            vendorData['ContactPersons']=contactPersonSerializer.data
            return JsonResponse(vendorData, safe=False)
        elif request.method == 'DELETE':
            vendor = Vendor.objects.get(VendorId=VendorId)
            vendor.ActiveStatus=0
            vendor.save()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get Vendor by CompanyId",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def VendorByCompanyId(request, CompanyId=""):
    try:
        if request.method == 'GET':
            BATCH_SIZE = 100
            vendor = Vendor.objects.filter(
                    CompanyId=CompanyId,ActiveStatus=1)
            total_vendor=vendor.count()
            all_serialized_data = []
            for i in range(0, total_vendor, BATCH_SIZE):
                with transaction.atomic():
                    batch_tasks = vendor[i:i+BATCH_SIZE]
                    serializer = VendorSerializer(batch_tasks, many=True)
                    serialized_data = serializer.data
                    all_serialized_data.extend(serialized_data)
            return JsonResponse(all_serialized_data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


class VendorApiByCompanyId(generics.ListAPIView):
    queryset =Vendor.objects.filter(ActiveStatus=1).order_by('-SortId')
    pagination_class = CustomPageNumberPagination
    serializer_class = VendorSerializer 
    def post(self, request, *args, **kwargs):
        try:
            filterData = JSONParser().parse(request)
            Keyword = filterData.get('SearchKeyword', '')
            if filterData['CompanyId']:
                self.queryset = self.queryset.filter(CompanyId=filterData['CompanyId'])

            if Keyword:
                self.queryset = self.queryset.filter(Q(CustomerDisplayName__icontains=Keyword)|Q(CompanyName__icontains=Keyword))
            page = self.paginate_queryset(self.queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
        except:
            return JsonResponse("", safe=False)



    


class UploadVendorDocument(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request,  *args, **kwargs):
        try:
                Serializer = VendorDocumentsSerializer(
                    data=request.data)
                if Serializer.is_valid():
                    Serializer.save()
                    return JsonResponse(Serializer.data['VendorDocumentId'], safe=False)
                else:
                    return JsonResponse("", safe=False)
        except:
            return JsonResponse("", safe=False)





@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get VendorDocument by VendorDocumentId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete VendorDocument by VendorDocumentId",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def VendorDocumentApiById(request, VendorDocumentId=""):
    try:
        if request.method == 'GET': 
            vendorDocuments = VendorDocuments.objects.get(
                    VendorDocumentId=VendorDocumentId)
            vendorDocumentsSerializer = VendorDocumentsSerializer(
                    vendorDocuments)
            return JsonResponse(vendorDocumentsSerializer.data, safe=False)
        elif request.method == 'DELETE':
            vendorDocuments = VendorDocuments.objects.get(VendorDocumentId=VendorDocumentId)
            VendorDocuments.objects.get(VendorDocumentId=VendorDocumentId).Document.delete(save=True)
            vendorDocuments.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=VendorAddressSerializer,operation_description="NOTE: API for save VendorAddress")
@swagger_auto_schema(method='PUT', request_body=VendorAddressSerializer,operation_description="NOTE: API for edit VendorAddress")
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all VendorAddress",)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
def VendorAddressApi(request):
    try:
        if request.method == 'GET':
            vendorAddress = VendorAddress.objects.all()
            vendorAddressSerializer = VendorAddressSerializer(
                    vendorAddress, many=True)
            return JsonResponse(vendorAddressSerializer.data, safe=False)
        elif request.method == 'POST':
            vendorAddressData = JSONParser().parse(request)
            vendorAddressSerializer = VendorAddressSerializer(
                data=vendorAddressData)
            if vendorAddressSerializer.is_valid():
                vendorAddressSerializer.save()
                return JsonResponse(vendorAddressSerializer.data['VendorAddressId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            vendorAddressData = JSONParser().parse(request)
            vendorAddress = VendorAddress.objects.get(
                VendorAddressId=vendorAddressData['VendorAddressId'])
            vendorAddressSerializer = VendorAddressSerializer(
                vendorAddress, data=vendorAddressData)
            if vendorAddressSerializer.is_valid():
                vendorAddressSerializer.save()
                return JsonResponse(vendorAddressSerializer.data['VendorAddressId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get vendorAddress by VendorAddressId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete vendorAddress by VendorAddressId",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def VendorAddressApiById(request, VendorAddressId=""):
    try:
        if request.method == 'GET': 
            vendorAddress = VendorAddress.objects.get(
                    VendorAddressId=VendorAddressId)
            vendorAddressSerializer = VendorAddressSerializer(
                    vendorAddress)
            return JsonResponse(vendorAddressSerializer.data, safe=False)
        elif request.method == 'DELETE':
            vendorAddress = VendorAddress.objects.get(VendorAddressId=VendorAddressId)
            vendorAddress.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get VendorAddress by VendorId",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def VendorAddressApiByVendorId(request, VendorId=""):
    try:
        if request.method == 'GET': 
            vendorAddress = VendorAddress.objects.filter(
                    VendorId=VendorId)
            vendorAddressSerializer = VendorAddressSerializer(
                    vendorAddress,many=True)
            vendorData=[]
            for row in vendorAddressSerializer.data:
                country=Country.objects.get(CountryId=row['Country'])
                countrySerializer=CountrySerializer(country)
                row['CountryName']=countrySerializer.data['Country']
                try:
                    state=State.objects.get(StateId=row['State'])
                    stateSerializer=StateSerializer(state)
                    row['StateName']=stateSerializer.data['State']
                except:
                    row['StateName']=[]
                vendorData.append(row)

            return JsonResponse(vendorData, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    



@csrf_exempt
@swagger_auto_schema(method='POST', request_body=VendorContactPersonSerializer,operation_description="NOTE: API for save ContactPerson")
@swagger_auto_schema(method='PUT', request_body=VendorContactPersonSerializer,operation_description="NOTE: API for edit ContactPerson")
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get all ContactPerson",)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
def ContactPersonApi(request):
    try:
        if request.method == 'GET':
            contactPerson = VendorContactPerson.objects.all()
            contactPersonSerializer = VendorContactPersonSerializer(
                    contactPerson, many=True)
            return JsonResponse(contactPersonSerializer.data, safe=False)
        elif request.method == 'POST':
            contactPersonData = JSONParser().parse(request)
            contactPersonSerializer = VendorContactPersonSerializer(
                data=contactPersonData)
            if contactPersonSerializer.is_valid():
                contactPersonSerializer.save()
                return JsonResponse(contactPersonSerializer.data['ContactPersonId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            contactPersonData = JSONParser().parse(request)
            contactPerson = VendorContactPerson.objects.get(
                ContactPersonId=contactPersonData['ContactPersonId'])
            contactPersonSerializer = VendorContactPersonSerializer(
                contactPerson, data=contactPersonData)
            if contactPersonSerializer.is_valid():
                contactPersonSerializer.save()
                return JsonResponse(contactPersonSerializer.data['ContactPersonId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get ContactPerson by ContactPersonId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete ContactPerson by ContactPersonId",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def ContactPersonApiById(request, ContactPersonId=""):
    try:
        if request.method == 'GET': 
            contactPerson = VendorContactPerson.objects.get(
                    ContactPersonId=ContactPersonId)
            contactPersonSerializer = VendorContactPersonSerializer(
                    contactPerson)
            return JsonResponse(contactPersonSerializer.data, safe=False)
        elif request.method == 'DELETE':
            contactPerson = VendorContactPerson.objects.get(ContactPersonId=ContactPersonId)
            contactPerson.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    





@csrf_exempt
@swagger_auto_schema(method='POST', request_body=VendorBankDetailsSerializer,operation_description="NOTE: API for save VendorBankDetails")
@swagger_auto_schema(method='PUT', request_body=VendorBankDetailsSerializer,operation_description="NOTE: API for edit VendorBankDetails")
@api_view(['POST','PUT'])
@retry(retries=3, delay=2)
def VendorBankDetailsApi(request):
    try:
        if request.method == 'POST':
            vendorBankDetailsData = JSONParser().parse(request)
            vendorBankDetailsSerializer = VendorBankDetailsSerializer(
                data=vendorBankDetailsData)
            if vendorBankDetailsData['PrimaryAccount']==True:
                vendorBankDetails=VendorBankDetails.objects.filter(PrimaryAccount=1,VendorId=vendorBankDetailsData['VendorId'])
                for bank in vendorBankDetails:
                    bank.PrimaryAccount=False
                    bank.save()
            if vendorBankDetailsSerializer.is_valid():
                vendorBankDetailsSerializer.save()
                vendorBankDetails = VendorBankDetails.objects.filter(VendorId=vendorBankDetailsData['VendorId'])
                if len(vendorBankDetails)==1:
                    for row in vendorBankDetails:
                        row.PrimaryAccount=True
                        row.save()
                return JsonResponse(vendorBankDetailsSerializer.data['BankDetailId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            vendorBankDetailsData = JSONParser().parse(request)
            vendorBankDetails = VendorBankDetails.objects.get(
                BankDetailId=vendorBankDetailsData['BankDetailId'])
            vendorBankDetailsSerializer = VendorBankDetailsSerializer(
                vendorBankDetails, data=vendorBankDetailsData)
            if vendorBankDetailsData['PrimaryAccount']==True:
                vendorBankDetails=VendorBankDetails.objects.filter(PrimaryAccount=1,VendorId=vendorBankDetailsData['VendorId'])
                for bank in vendorBankDetails:
                    bank.PrimaryAccount=False
                    bank.save()
            if vendorBankDetailsSerializer.is_valid():
                vendorBankDetailsSerializer.save()
                return JsonResponse(vendorBankDetailsSerializer.data['BankDetailId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get VendorBankDetails by VendorBankDetailsId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete VendorBankDetails by VendorBankDetailsId",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def VendorBankDetailsApiById(request, BankDetailId=""):
    try:
        if request.method == 'GET': 
            vendorBankDetails = VendorBankDetails.objects.get(
                    BankDetailId=BankDetailId)
            vendorBankDetailsSerializer = VendorBankDetailsSerializer(
                    vendorBankDetails)
            return JsonResponse(vendorBankDetailsSerializer.data, safe=False)
        elif request.method == 'DELETE':
            vendorBankDetails = VendorBankDetails.objects.get(BankDetailId=BankDetailId)
            vendorBankDetails.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    



@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get VendorBankDetails by VendorId",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def VendorBankDetailsApiByVendorId(request, VendorId=""):
    try:
        if request.method == 'GET': 
            vendorBankDetails = VendorBankDetails.objects.filter(
                    VendorId=VendorId)
            vendorBankDetailsSerializer = VendorBankDetailsSerializer(
                vendorBankDetails,many=True)
            return JsonResponse(vendorBankDetailsSerializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


def get_next_bill_number(company_id):
    from app_vendor.models import VendorBill
    bills = VendorBill.objects.filter(CompanyId=company_id, BillNumber__startswith='BILL-')
    max_num = 0
    for b in bills:
        try:
            num_part = int(b.BillNumber.split('-')[-1])
            if num_part > max_num:
                max_num = num_part
        except (ValueError, IndexError):
            pass
    next_num = max_num + 1
    return f"BILL-{next_num:07d}"


def post_vendor_bill_journal_entries(bill):
    from app_accounting.signals import get_or_create_default_accounts
    from app_accounting.models import Account, JournalEntry, JournalItem
    from django.db import transaction

    company_id = bill.CompanyId
    if not company_id:
        return

    accounts = get_or_create_default_accounts(company_id)
    ap_account = accounts.get('2100')
    if not ap_account:
        ap_account, _ = Account.objects.get_or_create(
            Code='2100',
            CompanyId=company_id,
            defaults={'Name': 'Accounts Payable', 'Type': 'Liability', 'IsCashOrBank': False}
        )

    vendor_name = ""
    if bill.VendorId:
        try:
            v = Vendor.objects.get(VendorId=bill.VendorId)
            vendor_name = v.VendorDisplayName or v.CompanyName or ""
        except Vendor.DoesNotExist:
            pass

    ref_num = bill.BillNumber
    narration = f"Vendor Bill {bill.BillNumber} from {vendor_name} - {bill.Description or ''}"

    with transaction.atomic():
        journal_entry, entry_created = JournalEntry.objects.get_or_create(
            ReferenceNumber=ref_num,
            Source='vendor_bill',
            CompanyId=company_id,
            defaults={
                'Date': bill.Date or datetime.now().strftime('%Y-%m-%d'),
                'Narration': narration
            }
        )

        if not entry_created:
            JournalItem.objects.filter(JournalEntryId=journal_entry.JournalEntryId).delete()
            journal_entry.Date = bill.Date or journal_entry.Date
            journal_entry.Narration = narration
            journal_entry.save()

        bill.JournalEntryId = journal_entry.JournalEntryId

        # Debit Expense / Purchase Account (bill.AccountId)
        JournalItem.objects.create(
            JournalEntryId=journal_entry.JournalEntryId,
            AccountId=bill.AccountId,
            Debit=f"{float(bill.Amount or 0.0):.2f}",
            Credit="0.00",
            VendorId=bill.VendorId
        )

        # Credit Accounts Payable (2100)
        JournalItem.objects.create(
            JournalEntryId=journal_entry.JournalEntryId,
            AccountId=ap_account.AccountId,
            Debit="0.00",
            Credit=f"{float(bill.Amount or 0.0):.2f}",
            VendorId=bill.VendorId
        )


def post_vendor_bill_payment_journal_entries(bill):
    from app_accounting.signals import get_or_create_default_accounts
    from app_accounting.models import Account, JournalEntry, JournalItem
    from django.db import transaction

    company_id = bill.CompanyId
    if not company_id or not bill.IsPaid or not bill.PaymentAccountId:
        return

    accounts = get_or_create_default_accounts(company_id)
    ap_account = accounts.get('2100')
    if not ap_account:
        ap_account, _ = Account.objects.get_or_create(
            Code='2100',
            CompanyId=company_id,
            defaults={'Name': 'Accounts Payable', 'Type': 'Liability', 'IsCashOrBank': False}
        )

    vendor_name = ""
    if bill.VendorId:
        try:
            v = Vendor.objects.get(VendorId=bill.VendorId)
            vendor_name = v.VendorDisplayName or v.CompanyName or ""
        except Vendor.DoesNotExist:
            pass

    ref_num = f"VPAY-{bill.BillNumber}"
    narration = f"Payment for Vendor Bill {bill.BillNumber} to {vendor_name}"

    with transaction.atomic():
        journal_entry, entry_created = JournalEntry.objects.get_or_create(
            ReferenceNumber=ref_num,
            Source='vendor_payment',
            CompanyId=company_id,
            defaults={
                'Date': bill.PaymentDate or datetime.now().strftime('%Y-%m-%d'),
                'Narration': narration
            }
        )

        if not entry_created:
            JournalItem.objects.filter(JournalEntryId=journal_entry.JournalEntryId).delete()
            journal_entry.Date = bill.PaymentDate or journal_entry.Date
            journal_entry.Narration = narration
            journal_entry.save()

        bill.PaymentJournalEntryId = journal_entry.JournalEntryId

        # Debit Accounts Payable (2100)
        JournalItem.objects.create(
            JournalEntryId=journal_entry.JournalEntryId,
            AccountId=ap_account.AccountId,
            Debit=f"{float(bill.Amount or 0.0):.2f}",
            Credit="0.00",
            VendorId=bill.VendorId
        )

        # Credit Cash/Bank Account (bill.PaymentAccountId)
        JournalItem.objects.create(
            JournalEntryId=journal_entry.JournalEntryId,
            AccountId=bill.PaymentAccountId,
            Debit="0.00",
            Credit=f"{float(bill.Amount or 0.0):.2f}",
            VendorId=bill.VendorId
        )


@csrf_exempt
@api_view(['GET', 'POST'])
def VendorBillApi(request):
    if request.method == 'GET':
        bills = VendorBill.objects.all().order_by('-SortId')
        serializer = VendorBillSerializer(bills, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = request.POST.dict() if request.POST else (JSONParser().parse(request) if request.body else {})
        company_id = data.get('CompanyId')
        if company_id:
            data['BillNumber'] = get_next_bill_number(company_id)

        serializer = VendorBillSerializer(data=data)
        if serializer.is_valid():
            bill = serializer.save()
            if 'BillFile' in request.FILES:
                bill.BillFile = request.FILES['BillFile']
                bill.save()
            post_vendor_bill_journal_entries(bill)
            bill.save()
            return JsonResponse(bill.BillId, safe=False)
        return JsonResponse(serializer.errors, status=400)


@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def VendorBillApiById(request, BillId=""):
    try:
        bill = VendorBill.objects.get(BillId=BillId)
    except VendorBill.DoesNotExist:
        return JsonResponse("Vendor Bill not found", status=404)

    if request.method == 'GET':
        serializer = VendorBillSerializer(bill)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'PUT':
        data = request.POST.dict() if request.POST else (JSONParser().parse(request) if request.body else {})
        serializer = VendorBillSerializer(bill, data=data, partial=True)
        if serializer.is_valid():
            bill = serializer.save()
            if 'BillFile' in request.FILES:
                bill.BillFile = request.FILES['BillFile']
                bill.save()
            post_vendor_bill_journal_entries(bill)
            if bill.IsPaid:
                post_vendor_bill_payment_journal_entries(bill)
            bill.save()
            return JsonResponse(bill.BillId, safe=False)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        with transaction.atomic():
            if bill.JournalEntryId:
                JournalItem.objects.filter(JournalEntryId=bill.JournalEntryId).delete()
                JournalEntry.objects.filter(JournalEntryId=bill.JournalEntryId).delete()
            if bill.PaymentJournalEntryId:
                JournalItem.objects.filter(JournalEntryId=bill.PaymentJournalEntryId).delete()
                JournalEntry.objects.filter(JournalEntryId=bill.PaymentJournalEntryId).delete()
            bill.delete()
        return JsonResponse("Deleted successfully", safe=False)


@csrf_exempt
@api_view(['GET'])
def VendorBillByCompanyId(request, CompanyId=""):
    bills = VendorBill.objects.filter(CompanyId=CompanyId).order_by('-Date', '-BillNumber')
    serializer = VendorBillSerializer(bills, many=True)
    return JsonResponse(serializer.data, safe=False)


@csrf_exempt
@api_view(['POST'])
def PayVendorBill(request, BillId=""):
    try:
        bill = VendorBill.objects.get(BillId=BillId)
    except VendorBill.DoesNotExist:
        return JsonResponse("Vendor Bill not found", status=404)

    data = JSONParser().parse(request)
    bill.IsPaid = True
    bill.PaymentDate = data.get('PaymentDate', datetime.now().strftime('%Y-%m-%d'))
    bill.PaymentAccountId = data.get('PaymentAccountId')
    post_vendor_bill_payment_journal_entries(bill)
    bill.save()
    return JsonResponse(bill.BillId, safe=False)


@csrf_exempt
@api_view(['GET'])
def VendorLedgerApi(request, VendorId=""):
    try:
        from app_accounting.models import JournalItem, JournalEntry
        from app_accounting.views import get_attachment_url_for_journal_entry, resolve_reference_number

        # Fetch items chronologically (ASC: oldest to newest) to compute running balances from opening balance
        items = JournalItem.objects.filter(VendorId=VendorId).order_by('SortId')
        ledger_items = []
        running_balance = 0.0

        for item in items:
            try:
                entry = JournalEntry.objects.get(JournalEntryId=item.JournalEntryId)
                entry_date = entry.Date
                ref_num = resolve_reference_number(entry)
                source = entry.Source
                narration = entry.Narration
                attachment_url = get_attachment_url_for_journal_entry(entry)
            except JournalEntry.DoesNotExist:
                entry_date = ""
                ref_num = ""
                source = ""
                narration = ""
                attachment_url = ""

            # Exclude reimbursement payouts (internal company repayment to staff)
            if source == 'expense_claim_repay' or (ref_num and ref_num.startswith('REIMB-')):
                continue

            raw_debit = float(item.Debit or "0.00")
            raw_credit = float(item.Credit or "0.00")

            if source == 'expense_claim':
                # Skip credit clearing line from DB query to prevent duplicate processing
                if raw_credit > 0:
                    continue
                
                amount = raw_debit if raw_debit > 0 else raw_credit
                if amount <= 0:
                    continue

                # 1. Vendor Expense / Bill (Credit column)
                c1 = amount
                d1 = 0.0
                running_balance += (c1 - d1)
                ledger_items.append({
                    "Date": entry_date,
                    "ReferenceNumber": ref_num,
                    "Source": source,
                    "Narration": narration,
                    "AttachmentUrl": attachment_url,
                    "Debit": f"{d1:.2f}",
                    "Credit": f"{c1:.2f}",
                    "RunningBalance": f"{running_balance:.2f}"
                })

                # 2. Paid out-of-pocket by employee to Vendor (Debit column)
                c2 = 0.0
                d2 = amount
                running_balance += (c2 - d2)
                ledger_items.append({
                    "Date": entry_date,
                    "ReferenceNumber": ref_num,
                    "Source": source,
                    "Narration": f"{narration} (Paid Out-of-Pocket)",
                    "AttachmentUrl": attachment_url,
                    "Debit": f"{d2:.2f}",
                    "Credit": f"{c2:.2f}",
                    "RunningBalance": f"{running_balance:.2f}"
                })
                continue
            elif source == 'expense':
                # Direct expense: Expense account debit line = Vendor Bill (Credit column),
                # Cash/Bank credit line = Vendor Payment (Debit column)
                if raw_debit > 0:
                    debit = 0.0
                    credit = raw_debit
                else:
                    debit = raw_credit
                    credit = 0.0
            else:
                debit = raw_debit
                credit = raw_credit

            running_balance += (credit - debit)

            ledger_items.append({
                "Date": entry_date,
                "ReferenceNumber": ref_num,
                "Source": source,
                "Narration": narration,
                "AttachmentUrl": attachment_url,
                "Debit": f"{debit:.2f}",
                "Credit": f"{credit:.2f}",
                "RunningBalance": f"{running_balance:.2f}"
            })

        # Reverse for DESC display order (newest at top, oldest at bottom)
        ledger_items.reverse()

        opening_bal = 0.00
        try:
            v = Vendor.objects.get(VendorId=VendorId)
            vendor_name = v.VendorDisplayName or v.CompanyName or "Vendor"
        except Vendor.DoesNotExist:
            vendor_name = "Vendor"

        closing_bal = running_balance

        return JsonResponse({
            "VendorId": VendorId,
            "VendorName": vendor_name,
            "OpeningBalance": f"{opening_bal:.2f}",
            "ClosingBalance": f"{closing_bal:.2f}",
            "LedgerItems": ledger_items
        }, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)