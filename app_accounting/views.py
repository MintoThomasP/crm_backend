from rest_framework.decorators import api_view, parser_classes
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from django.db import transaction
from django.db.models import Q
from app_accounting.models import Account, JournalEntry, JournalItem, Expense, ExpenseClaim
from app_accounting.serializers import AccountSerializer, JournalEntrySerializer, JournalItemSerializer, ExpenseSerializer, ExpenseClaimSerializer
from app_client.models import Client
from app_client.serializers import ClientSerializer
from app_staff.models import Staff


def format_media_url(file_field):
    if not file_field or not hasattr(file_field, 'name') or not file_field.name:
        return ""
    name = str(file_field.name).lstrip('/')
    if name.startswith('media/'):
        return name
    return f"media/{name}"


def get_attachment_url_for_journal_entry(entry):
    if not entry or not entry.Source:
        return ""

    source = (entry.Source or "").lower()

    if source == 'invoice':
        from app_sale.models import Invoice, InvoiceDocument
        inv = None
        if entry.ReferenceNumber:
            inv = Invoice.objects.filter(
                Q(InvoiceNumber=entry.ReferenceNumber) | Q(InvoiceId=entry.ReferenceNumber)
            ).first()
        
        if not inv and entry.Narration:
            import re
            match = re.search(r'Invoice\s+#?([A-Za-z0-9\-]+)', entry.Narration, re.IGNORECASE)
            if match:
                inv_ref = match.group(1)
                inv = Invoice.objects.filter(
                    Q(InvoiceNumber=inv_ref) | Q(InvoiceId=inv_ref)
                ).first()

        if inv:
            # 1. Check InvoiceFile in Invoice table
            if inv.InvoiceFile and hasattr(inv.InvoiceFile, 'name') and inv.InvoiceFile.name:
                return format_media_url(inv.InvoiceFile)
            # 2. Check Document in InvoiceDocument table
            inv_doc = InvoiceDocument.objects.filter(InvoiceId=inv.InvoiceId).first()
            if inv_doc and inv_doc.Document and hasattr(inv_doc.Document, 'name') and inv_doc.Document.name:
                return format_media_url(inv_doc.Document)
            # 3. Fallback to view generated PDF
            return f"api-sale/ViewPDF/{inv.InvoiceId}"

    elif source == 'payment':
        from app_sale.models import PaymentReceived, PaymentDocument
        pay = None
        if entry.ReferenceNumber:
            pay = PaymentReceived.objects.filter(
                Q(PaymentNumber=entry.ReferenceNumber) | Q(ReferenceNumber=entry.ReferenceNumber) | Q(PaymentReceivedId=entry.ReferenceNumber)
            ).first()

        if not pay and entry.Narration:
            import re
            match = re.search(r'Payment Received\s+#?([A-Za-z0-9\-]+)', entry.Narration, re.IGNORECASE)
            if match:
                pay_ref = match.group(1)
                pay = PaymentReceived.objects.filter(
                    Q(PaymentNumber=pay_ref) | Q(ReferenceNumber=pay_ref) | Q(PaymentReceivedId=pay_ref)
                ).first()

        if pay:
            # 1. Check Receipt in PaymentReceived table
            if pay.Receipt and hasattr(pay.Receipt, 'name') and pay.Receipt.name:
                return format_media_url(pay.Receipt)
            # 2. Check Document in PaymentDocument table
            pay_doc = PaymentDocument.objects.filter(PaymentReceivedId=pay.PaymentReceivedId).first()
            if pay_doc and pay_doc.Document and hasattr(pay_doc.Document, 'name') and pay_doc.Document.name:
                return format_media_url(pay_doc.Document)
            # 3. Fallback to view generated Payment PDF
            return f"api-sale/ViewPaymentPDF/{pay.PaymentReceivedId}"

    elif source == 'expense':
        from app_accounting.models import Expense
        exp = None
        if entry.ReferenceNumber:
            exp = Expense.objects.filter(
                Q(ExpenseNumber=entry.ReferenceNumber) | Q(ExpenseId=entry.ReferenceNumber)
            ).first()

        if exp and hasattr(exp, 'Receipt') and exp.Receipt and hasattr(exp.Receipt, 'name') and exp.Receipt.name:
            return format_media_url(exp.Receipt)

    elif source in ['expense_claim', 'expense_claim_repay']:
        from app_accounting.models import ExpenseClaim
        claim = ExpenseClaim.objects.filter(
            Q(ExpenseJournalEntryId=entry.JournalEntryId) |
            Q(ReimbursementJournalEntryId=entry.JournalEntryId) |
            Q(ClaimNumber=entry.ReferenceNumber)
        ).first()

        if claim and claim.Receipt and hasattr(claim.Receipt, 'name') and claim.Receipt.name:
            return format_media_url(claim.Receipt)

    elif source in ['vendor_bill', 'vendor_payment']:
        from app_vendor.models import VendorBill
        bill = VendorBill.objects.filter(
            Q(JournalEntryId=entry.JournalEntryId) |
            Q(PaymentJournalEntryId=entry.JournalEntryId) |
            Q(BillNumber=entry.ReferenceNumber)
        ).first()

        if bill and bill.BillFile and hasattr(bill.BillFile, 'name') and bill.BillFile.name:
            return format_media_url(bill.BillFile)

    return ""


@api_view(['GET', 'POST'])
def AccountApi(request):
    if request.method == 'GET':
        accounts = Account.objects.all().order_by('-SortId')
        serializer = AccountSerializer(accounts, many=True)
        return JsonResponse(serializer.data, safe=False)
    
    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = AccountSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data['AccountId'], safe=False)
        return JsonResponse("Failed to add Account", safe=False, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
def AccountApiById(request, AccountId=""):
    try:
        account = Account.objects.get(AccountId=AccountId)
    except Account.DoesNotExist:
        return JsonResponse("Account does not exist", safe=False, status=404)

    if request.method == 'GET':
        serializer = AccountSerializer(account)
        return JsonResponse(serializer.data, safe=False)
    
    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = AccountSerializer(account, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data['AccountId'], safe=False)
        return JsonResponse("Failed to update Account", safe=False, status=400)
    
    elif request.method == 'DELETE':
        account.delete()
        return JsonResponse("Deleted successfully", safe=False)


@api_view(['GET'])
def AccountByCompanyId(request, CompanyId=""):
    from app_accounting.signals import get_or_create_default_accounts
    get_or_create_default_accounts(CompanyId)
    accounts = Account.objects.filter(CompanyId=CompanyId).order_by('Code')
    serializer = AccountSerializer(accounts, many=True)
    return JsonResponse(serializer.data, safe=False)



def resolve_reference_number(entry):
    if not entry or not entry.ReferenceNumber:
        return ""

    ref_num = entry.ReferenceNumber
    source = (entry.Source or "").lower()

    if source == 'expense':
        exp = Expense.objects.filter(
            Q(ExpenseNumber=ref_num) | Q(ExpenseId=ref_num)
        ).first()
        if exp and exp.ExpenseNumber:
            return exp.ExpenseNumber
    elif source in ['expense_claim', 'expense_claim_repay']:
        claim = ExpenseClaim.objects.filter(
            Q(ExpenseJournalEntryId=entry.JournalEntryId) |
            Q(ReimbursementJournalEntryId=entry.JournalEntryId) |
            Q(ClaimNumber=ref_num) |
            Q(ExpenseClaimId=ref_num)
        ).first()
        if claim and claim.ClaimNumber:
            if source == 'expense_claim_repay':
                return f"REIMB-{claim.ClaimNumber}" if not ref_num.startswith('REIMB-') else ref_num
            return claim.ClaimNumber
        elif ref_num.startswith('EXP-CLAIM-'):
            return ref_num.replace('EXP-CLAIM-', '')
    elif source == 'invoice':
        from app_sale.models import Invoice
        inv = Invoice.objects.filter(
            Q(InvoiceNumber=ref_num) | Q(InvoiceId=ref_num)
        ).first()
        if inv and inv.InvoiceNumber:
            return inv.InvoiceNumber
    elif source == 'payment':
        from app_sale.models import PaymentReceived
        pay = PaymentReceived.objects.filter(
            Q(PaymentNumber=ref_num) | Q(ReferenceNumber=ref_num) | Q(PaymentReceivedId=ref_num)
        ).first()
        if pay and pay.PaymentNumber:
            return pay.PaymentNumber

    return ref_num


def get_invoice_info_for_journal_entry(entry):
    if not entry or not entry.Source:
        return "", ""

    source = (entry.Source or "").lower()
    from app_sale.models import Invoice, InvoiceDocument, PaymentReceived, PaymentReceivedDetail
    import re

    inv = None

    if source == 'invoice':
        if entry.ReferenceNumber:
            inv = Invoice.objects.filter(
                Q(InvoiceNumber=entry.ReferenceNumber) | Q(InvoiceId=entry.ReferenceNumber)
            ).first()
        if not inv and entry.Narration:
            match = re.search(r'Invoice\s+#?([A-Za-z0-9\-]+)', entry.Narration, re.IGNORECASE)
            if match:
                inv_ref = match.group(1)
                inv = Invoice.objects.filter(
                    Q(InvoiceNumber=inv_ref) | Q(InvoiceId=inv_ref)
                ).first()

    elif source == 'payment':
        pay = None
        if entry.ReferenceNumber:
            pay = PaymentReceived.objects.filter(
                Q(PaymentNumber=entry.ReferenceNumber) | Q(ReferenceNumber=entry.ReferenceNumber) | Q(PaymentReceivedId=entry.ReferenceNumber)
            ).first()
        if not pay and entry.Narration:
            match = re.search(r'Payment Received\s+#?([A-Za-z0-9\-]+)', entry.Narration, re.IGNORECASE)
            if match:
                pay_ref = match.group(1)
                pay = PaymentReceived.objects.filter(
                    Q(PaymentNumber=pay_ref) | Q(ReferenceNumber=pay_ref) | Q(PaymentReceivedId=pay_ref)
                ).first()

        if pay:
            details = PaymentReceivedDetail.objects.filter(PaymentReceivedId=pay.PaymentReceivedId)
            for detail in details:
                if detail.RefId:
                    inv = Invoice.objects.filter(Q(InvoiceId=detail.RefId) | Q(InvoiceNumber=detail.RefId)).first()
                    if inv:
                        break
        
        # If still not found, check if Narration references an Invoice number
        if not inv and entry.Narration:
            match = re.search(r'(INV-[0-9A-Za-z\-]+|Invoice\s+#?[0-9A-Za-z\-]+)', entry.Narration, re.IGNORECASE)
            if match:
                raw_ref = match.group(1).replace('Invoice', '').replace('#', '').strip()
                inv = Invoice.objects.filter(Q(InvoiceNumber=raw_ref) | Q(InvoiceId=raw_ref)).first()

    if inv:
        inv_num = inv.InvoiceNumber or inv.InvoiceId
        inv_url = ""
        if inv.InvoiceFile and hasattr(inv.InvoiceFile, 'name') and inv.InvoiceFile.name:
            inv_url = format_media_url(inv.InvoiceFile)
        else:
            inv_doc = InvoiceDocument.objects.filter(InvoiceId=inv.InvoiceId).first()
            if inv_doc and inv_doc.Document and hasattr(inv_doc.Document, 'name') and inv_doc.Document.name:
                inv_url = format_media_url(inv_doc.Document)
            else:
                inv_url = f"api-sale/ViewPDF/{inv.InvoiceId}"
        return inv_num, inv_url

    return "", ""


@api_view(['GET'])
def JournalItemByAccountId(request, AccountId=""):
    # Fetch all items for this Account
    items = JournalItem.objects.filter(AccountId=AccountId).order_by('SortId')
    
    # Enrich each JournalItem with JournalEntry information (Date, ReferenceNumber, Source, Narration, AttachmentUrl, InvoiceAttachmentUrl)
    enriched_items = []
    for item in items:
        item_data = JournalItemSerializer(item).data
        try:
            entry = JournalEntry.objects.get(JournalEntryId=item.JournalEntryId)
            item_data['Date'] = entry.Date
            item_data['ReferenceNumber'] = resolve_reference_number(entry)
            item_data['Source'] = entry.Source
            item_data['Narration'] = entry.Narration
            item_data['AttachmentUrl'] = get_attachment_url_for_journal_entry(entry)
            inv_num, inv_url = get_invoice_info_for_journal_entry(entry)
            item_data['InvoiceNumber'] = inv_num
            item_data['InvoiceAttachmentUrl'] = inv_url
        except JournalEntry.DoesNotExist:
            item_data['Date'] = ""
            item_data['ReferenceNumber'] = ""
            item_data['Source'] = ""
            item_data['Narration'] = ""
            item_data['AttachmentUrl'] = ""
            item_data['InvoiceNumber'] = ""
            item_data['InvoiceAttachmentUrl'] = ""
            
        client_id = item.ClientId
        if not client_id and entry and entry.Source == 'payment':
            from app_sale.models import PaymentReceived
            pay = PaymentReceived.objects.filter(Q(PaymentNumber=entry.ReferenceNumber) | Q(PaymentReceivedId=entry.ReferenceNumber)).first()
            if pay:
                client_id = pay.ClientId
        if not client_id and entry and entry.Source == 'invoice':
            from app_sale.models import Invoice
            inv = Invoice.objects.filter(Q(InvoiceNumber=entry.ReferenceNumber) | Q(InvoiceId=entry.ReferenceNumber)).first()
            if inv:
                client_id = inv.ClientId

        if client_id:
            try:
                client = Client.objects.get(ClientId=client_id)
                item_data['ClientName'] = client.CustomerDisplayName
                item_data['ClientId'] = client_id
            except:
                item_data['ClientName'] = ""
                item_data['ClientId'] = client_id
        else:
            item_data['ClientName'] = ""
            item_data['ClientId'] = ""

        staff_id = getattr(item, 'StaffId', None)
        if not staff_id and entry and entry.Source == 'expense':
            from app_accounting.models import Expense
            exp = Expense.objects.filter(
                Q(ExpenseNumber=entry.ReferenceNumber) |
                Q(ExpenseId=entry.ReferenceNumber) |
                Q(Narration=entry.Narration)
            ).first()
            if exp and exp.StaffId:
                staff_id = exp.StaffId
                try:
                    JournalItem.objects.filter(JournalEntryId=entry.JournalEntryId).update(StaffId=staff_id)
                except:
                    pass

        if not staff_id and entry and entry.Source in ['expense_claim', 'expense_claim_repay']:
            from app_accounting.models import ExpenseClaim
            claim = ExpenseClaim.objects.filter(
                Q(ExpenseJournalEntryId=entry.JournalEntryId) |
                Q(ReimbursementJournalEntryId=entry.JournalEntryId) |
                Q(ClaimNumber=entry.ReferenceNumber)
            ).first()
            if claim and claim.StaffId:
                staff_id = claim.StaffId
                try:
                    JournalItem.objects.filter(JournalEntryId=entry.JournalEntryId).update(StaffId=staff_id)
                except:
                    pass

        if staff_id:
            try:
                staff = Staff.objects.get(StaffId=staff_id)
                item_data['StaffName'] = staff.StaffName or ""
                item_data['StaffId'] = staff_id
            except:
                item_data['StaffName'] = ""
                item_data['StaffId'] = staff_id
        else:
            item_data['StaffName'] = ""
            item_data['StaffId'] = ""

        vendor_id = getattr(item, 'VendorId', None)
        if not vendor_id and entry and entry.Source == 'expense':
            from app_accounting.models import Expense
            exp = Expense.objects.filter(
                Q(ExpenseNumber=entry.ReferenceNumber) |
                Q(ExpenseId=entry.ReferenceNumber) |
                Q(Narration=entry.Narration)
            ).first()
            if exp and exp.VendorId:
                vendor_id = exp.VendorId
                try:
                    JournalItem.objects.filter(JournalEntryId=entry.JournalEntryId).update(VendorId=vendor_id)
                except:
                    pass

        if not vendor_id and entry and entry.Source in ['expense_claim', 'expense_claim_repay']:
            from app_accounting.models import ExpenseClaim
            claim = ExpenseClaim.objects.filter(
                Q(ExpenseJournalEntryId=entry.JournalEntryId) |
                Q(ReimbursementJournalEntryId=entry.JournalEntryId) |
                Q(ClaimNumber=entry.ReferenceNumber)
            ).first()
            if claim and claim.VendorId:
                vendor_id = claim.VendorId
                try:
                    JournalItem.objects.filter(JournalEntryId=entry.JournalEntryId).update(VendorId=vendor_id)
                except:
                    pass

        if vendor_id:
            try:
                from app_vendor.models import Vendor
                v = Vendor.objects.get(VendorId=vendor_id)
                item_data['VendorName'] = v.VendorDisplayName or v.CompanyName or ""
                item_data['VendorId'] = vendor_id
            except:
                item_data['VendorName'] = ""
                item_data['VendorId'] = vendor_id
        else:
            item_data['VendorName'] = ""
            item_data['VendorId'] = ""

        enriched_items.append(item_data)
        
    # Sort in ascending order of Date, then SortId
    enriched_items.sort(key=lambda x: (x.get('Date') or '', x.get('SortId') or ''))
    return JsonResponse(enriched_items, safe=False)


from datetime import datetime

def safe_float(val):
    try:
        return float(val) if val else 0.0
    except ValueError:
        return 0.0

def parse_date(date_str):
    if not date_str:
        return None
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d', '%d-%m-%Y'):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            pass
    return None

@api_view(['GET'])
def CashBookByCompanyId(request, CompanyId=""):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    start_date_obj = parse_date(start_date)
    end_date_obj = parse_date(end_date)
    
    # Fetch all Accounts for this Company that are marked as Cash or Bank
    cash_bank_accounts = Account.objects.filter(CompanyId=CompanyId, IsCashOrBank=True)
    account_ids = [acc.AccountId for acc in cash_bank_accounts]
    
    # Fetch all JournalItems for these Accounts
    items = JournalItem.objects.filter(AccountId__in=account_ids).order_by('SortId')
    
    opening_balance = 0.0
    period_items = []
    
    for item in items:
        try:
            entry = JournalEntry.objects.get(JournalEntryId=item.JournalEntryId)
            entry_date = entry.Date
        except JournalEntry.DoesNotExist:
            entry_date = None
            
        entry_date_obj = parse_date(entry_date)
        
        debit_val = safe_float(item.Debit)
        credit_val = safe_float(item.Credit)
        
        if start_date_obj and entry_date_obj and entry_date_obj < start_date_obj:
            opening_balance += (debit_val - credit_val)
            continue
            
        if end_date_obj and entry_date_obj and entry_date_obj > end_date_obj:
            continue
            
        # Enrich with JournalEntry info
        item_data = JournalItemSerializer(item).data
        try:
            account = Account.objects.get(AccountId=item.AccountId)
            item_data['AccountName'] = account.Name
            item_data['AccountCode'] = account.Code
        except Account.DoesNotExist:
            item_data['AccountName'] = ""
            item_data['AccountCode'] = ""
            
        if entry_date:
            item_data['Date'] = entry.Date
            item_data['ReferenceNumber'] = resolve_reference_number(entry)
            item_data['Source'] = entry.Source
            item_data['Narration'] = entry.Narration
            item_data['AttachmentUrl'] = get_attachment_url_for_journal_entry(entry)
            inv_num, inv_url = get_invoice_info_for_journal_entry(entry)
            item_data['InvoiceNumber'] = inv_num
            item_data['InvoiceAttachmentUrl'] = inv_url
            
            # Resolve Contra Account
            other_items = JournalItem.objects.filter(JournalEntryId=item.JournalEntryId).exclude(JournalItemId=item.JournalItemId)
            non_cb_items = []
            for o_item in other_items:
                try:
                    acc = Account.objects.get(AccountId=o_item.AccountId)
                    if not acc.IsCashOrBank:
                        non_cb_items.append((o_item, acc))
                except Account.DoesNotExist:
                    pass
            
            if not non_cb_items:
                for o_item in other_items:
                    try:
                        acc = Account.objects.get(AccountId=o_item.AccountId)
                        non_cb_items.append((o_item, acc))
                    except Account.DoesNotExist:
                        pass
                        
            if len(non_cb_items) == 1:
                item_data['ContraAccountName'] = non_cb_items[0][1].Name
                item_data['ContraAccountCode'] = non_cb_items[0][1].Code
            elif len(non_cb_items) > 1:
                if entry.Source == 'payment':
                    ar_item = next((x for x in non_cb_items if x[1].Code == '1200'), None)
                    if ar_item:
                        item_data['ContraAccountName'] = ar_item[1].Name
                        item_data['ContraAccountCode'] = ar_item[1].Code
                    else:
                        item_data['ContraAccountName'] = "Multiple Accounts"
                        item_data['ContraAccountCode'] = "Split"
                else:
                    item_data['ContraAccountName'] = ", ".join([x[1].Name for x in non_cb_items if x[1].Name])
                    item_data['ContraAccountCode'] = ", ".join([x[1].Code for x in non_cb_items if x[1].Code])
            else:
                item_data['ContraAccountName'] = ""
                item_data['ContraAccountCode'] = ""
                
            # Get Bank Charges for payment received
            if entry.Source == 'payment':
                charges_item = next((x for x in non_cb_items if x[1].Code == '6150'), None)
                if charges_item:
                    item_data['BankCharges'] = charges_item[0].Debit
                else:
                    item_data['BankCharges'] = "0.00"
            else:
                item_data['BankCharges'] = "0.00"
        else:
            item_data['Date'] = ""
            item_data['ReferenceNumber'] = ""
            item_data['Source'] = ""
            item_data['Narration'] = ""
            item_data['ContraAccountName'] = ""
            item_data['ContraAccountCode'] = ""
            item_data['BankCharges'] = "0.00"
            item_data['InvoiceNumber'] = ""
            item_data['InvoiceAttachmentUrl'] = ""
            
        client_id = item.ClientId
        if not client_id and entry_date and entry.Source == 'payment':
            from app_sale.models import PaymentReceived
            pay = PaymentReceived.objects.filter(Q(PaymentNumber=entry.ReferenceNumber) | Q(PaymentReceivedId=entry.ReferenceNumber)).first()
            if pay:
                client_id = pay.ClientId
        if not client_id and entry_date and entry.Source == 'invoice':
            from app_sale.models import Invoice
            inv = Invoice.objects.filter(Q(InvoiceNumber=entry.ReferenceNumber) | Q(InvoiceId=entry.ReferenceNumber)).first()
            if inv:
                client_id = inv.ClientId

        if client_id:
            try:
                client = Client.objects.get(ClientId=client_id)
                item_data['ClientName'] = client.CustomerDisplayName
                item_data['ClientId'] = client_id
            except:
                item_data['ClientName'] = ""
                item_data['ClientId'] = client_id
        else:
            item_data['ClientName'] = ""
            item_data['ClientId'] = ""

        staff_id = getattr(item, 'StaffId', None)
        if not staff_id and entry_date and entry.Source == 'expense':
            from app_accounting.models import Expense
            exp = Expense.objects.filter(Q(ExpenseNumber=entry.ReferenceNumber) | Q(ExpenseId=entry.ReferenceNumber)).first()
            if exp:
                staff_id = getattr(exp, 'StaffId', None)
        if not staff_id and entry_date and entry.Source in ['expense_claim', 'expense_claim_repay']:
            from app_accounting.models import ExpenseClaim
            claim = ExpenseClaim.objects.filter(
                Q(ExpenseJournalEntryId=entry.JournalEntryId) |
                Q(ReimbursementJournalEntryId=entry.JournalEntryId) |
                Q(ClaimNumber=entry.ReferenceNumber)
            ).first()
            if claim:
                staff_id = claim.StaffId

        if staff_id:
            try:
                staff = Staff.objects.get(StaffId=staff_id)
                item_data['StaffName'] = staff.StaffName or ""
                item_data['StaffId'] = staff_id
            except:
                item_data['StaffName'] = ""
                item_data['StaffId'] = staff_id
        else:
            item_data['StaffName'] = ""
            item_data['StaffId'] = ""
            
        period_items.append(item_data)
        
    # Sort in ascending order of Date, then SortId
    period_items.sort(key=lambda x: (x.get('Date') or '', x.get('SortId') or ''))
    
    closing_balance = opening_balance
    for item in period_items:
        closing_balance += (safe_float(item.get('Debit')) - safe_float(item.get('Credit')))
        
    # Return structured dict if date range parameters exist, else return raw list for backward compatibility
    if start_date or end_date:
        return JsonResponse({
            "opening_balance": f"{opening_balance:.2f}",
            "closing_balance": f"{closing_balance:.2f}",
            "items": period_items
        }, safe=False)
    else:
        return JsonResponse(period_items, safe=False)


@api_view(['POST'])
def SyncLedger(request):
    try:
        from app_sale.models import Invoice, PaymentReceived
        from app_accounting.models import Expense
        from app_accounting.signals import create_invoice_journal_entry, create_payment_journal_entry, create_expense_journal_entry
        
        invoices = Invoice.objects.all()
        for invoice in invoices:
            create_invoice_journal_entry(sender=Invoice, instance=invoice, created=True)
            
        payments = PaymentReceived.objects.all()
        for payment in payments:
            create_payment_journal_entry(sender=PaymentReceived, instance=payment, created=True)
            
        expenses = Expense.objects.all()
        for expense in expenses:
            create_expense_journal_entry(sender=Expense, instance=expense, created=True)
            
        return JsonResponse({"message": "Successfully synchronized ledger and cash book using existing records"}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


from app_accounting.models import Expense
from app_accounting.serializers import ExpenseSerializer
import re

def get_next_expense_number(company_id):
    expenses = Expense.objects.filter(CompanyId=company_id, ExpenseNumber__startswith='EXP-')
    max_num = 0
    for exp in expenses:
        match = re.match(r'^EXP-(\d+)$', exp.ExpenseNumber or '')
        if match:
            num = int(match.group(1))
            if num > max_num:
                max_num = num
    next_num = max_num + 1
    return f"EXP-{next_num:07d}"


@api_view(['GET'])
def NextExpenseNumber(request, CompanyId=""):
    return JsonResponse({"NextExpenseNumber": get_next_expense_number(CompanyId)}, safe=False)


@api_view(['GET', 'POST'])
def ExpenseApi(request):
    if request.method == 'GET':
        expenses = Expense.objects.all().order_by('Date', 'ExpenseNumber')
        serializer = ExpenseSerializer(expenses, many=True)
        return JsonResponse(serializer.data, safe=False)
    
    elif request.method == 'POST':
        data = JSONParser().parse(request)
        company_id = data.get('CompanyId')
        if company_id:
            data['ExpenseNumber'] = get_next_expense_number(company_id)
        serializer = ExpenseSerializer(data=data)
        if serializer.is_valid():
            exp_obj = serializer.save()
            from app_accounting.signals import create_expense_journal_entry
            create_expense_journal_entry(sender=Expense, instance=exp_obj, created=True)
            return JsonResponse(serializer.data['ExpenseId'], safe=False)
        return JsonResponse("Failed to add Expense", safe=False, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
def ExpenseApiById(request, ExpenseId=""):
    try:
        expense = Expense.objects.get(ExpenseId=ExpenseId)
    except Expense.DoesNotExist:
        return JsonResponse("Expense does not exist", safe=False, status=404)

    if request.method == 'GET':
        serializer = ExpenseSerializer(expense)
        return JsonResponse(serializer.data, safe=False)
    
    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = ExpenseSerializer(expense, data=data, partial=True)
        if serializer.is_valid():
            exp_obj = serializer.save()
            from app_accounting.signals import create_expense_journal_entry
            create_expense_journal_entry(sender=Expense, instance=exp_obj, created=False)
            return JsonResponse(serializer.data['ExpenseId'], safe=False)
        return JsonResponse("Failed to update Expense", safe=False, status=400)
    
    elif request.method == 'DELETE':
        with transaction.atomic():
            ref_num = expense.ExpenseNumber if expense.ExpenseNumber else expense.ExpenseId
            entries = JournalEntry.objects.filter(Source='expense', ReferenceNumber__in=[ref_num, expense.ExpenseId])
            for entry in entries:
                JournalItem.objects.filter(JournalEntryId=entry.JournalEntryId).delete()
                entry.delete()
            expense.delete()
        return JsonResponse("Deleted successfully", safe=False)


@api_view(['GET'])
def ExpenseByCompanyId(request, CompanyId=""):
    expenses = Expense.objects.filter(CompanyId=CompanyId).order_by('Date', 'ExpenseNumber')
    enriched_expenses = []
    for exp in expenses:
        data = ExpenseSerializer(exp).data
        try:
            account = Account.objects.get(AccountId=exp.AccountId)
            data['AccountName'] = account.Name
            data['AccountCode'] = account.Code
        except Account.DoesNotExist:
            data['AccountName'] = ""
            data['AccountCode'] = ""
            
        try:
            payment_account = Account.objects.get(AccountId=exp.PaymentAccountId)
            data['PaymentAccountName'] = payment_account.Name
            data['PaymentAccountCode'] = payment_account.Code
        except Account.DoesNotExist:
            data['PaymentAccountName'] = ""
            data['PaymentAccountCode'] = ""

        if exp.StaffId:
            try:
                from app_staff.models import Staff
                staff = Staff.objects.get(StaffId=exp.StaffId)
                data['StaffName'] = staff.StaffName or ""
            except:
                data['StaffName'] = ""
        else:
            data['StaffName'] = ""

        if exp.VendorId:
            try:
                from app_vendor.models import Vendor
                vendor = Vendor.objects.get(VendorId=exp.VendorId)
                data['VendorName'] = vendor.VendorDisplayName or vendor.CompanyName or ""
            except:
                data['VendorName'] = ""
        else:
            data['VendorName'] = ""

        enriched_expenses.append(data)

    return JsonResponse(enriched_expenses, safe=False)


def get_next_claim_number(company_id):
    claims = ExpenseClaim.objects.filter(CompanyId=company_id, ClaimNumber__startswith='CLM-')
    max_num = 0
    for clm in claims:
        match = re.match(r'^CLM-(\d+)$', clm.ClaimNumber or '')
        if match:
            num = int(match.group(1))
            if num > max_num:
                max_num = num
    next_num = max_num + 1
    return f"CLM-{next_num:07d}"


def post_claim_journal_entries(claim):
    from app_accounting.signals import get_or_create_default_accounts
    company_id = claim.CompanyId
    if not company_id:
        return

    accounts = get_or_create_default_accounts(company_id)
    clearing_account = accounts.get('2300')
    if not clearing_account:
        clearing_account, _ = Account.objects.get_or_create(
            Code='2300',
            CompanyId=company_id,
            defaults={'Name': 'Due to Directors / Expense Clearing', 'Type': 'Liability', 'IsCashOrBank': False}
        )

    staff_name = ""
    if claim.StaffId:
        try:
            staff = Staff.objects.get(StaffId=claim.StaffId)
            staff_name = staff.StaffName or ""
        except Staff.DoesNotExist:
            pass

    ref_num = f"EXP-CLAIM-{claim.ClaimNumber}"
    narration = f"Expense Claim {claim.ClaimNumber} paid out-of-pocket by {staff_name} - {claim.Description or ''}"

    with transaction.atomic():
        journal_entry, entry_created = JournalEntry.objects.get_or_create(
            ReferenceNumber=ref_num,
            Source='expense_claim',
            CompanyId=company_id,
            defaults={
                'Date': claim.Date or datetime.now().strftime('%Y-%m-%d'),
                'Narration': narration
            }
        )

        if not entry_created:
            JournalItem.objects.filter(JournalEntryId=journal_entry.JournalEntryId).delete()
            journal_entry.Date = claim.Date or journal_entry.Date
            journal_entry.Narration = narration
            journal_entry.save()

        claim.ExpenseJournalEntryId = journal_entry.JournalEntryId

        # Debit Expense Account
        JournalItem.objects.create(
            JournalEntryId=journal_entry.JournalEntryId,
            AccountId=claim.AccountId,
            Debit=f"{float(claim.Amount or 0.0):.2f}",
            Credit="0.00",
            StaffId=claim.StaffId,
            VendorId=claim.VendorId
        )

        # Credit Liability clearing account (Staff clearing account, no VendorId)
        JournalItem.objects.create(
            JournalEntryId=journal_entry.JournalEntryId,
            AccountId=clearing_account.AccountId,
            Debit="0.00",
            Credit=f"{float(claim.Amount or 0.0):.2f}",
            StaffId=claim.StaffId
        )


def post_reimbursement_journal_entries(claim):
    from app_accounting.signals import get_or_create_default_accounts
    company_id = claim.CompanyId
    if not company_id or not claim.IsReimbursed or not claim.ReimbursementAccountId:
        return

    accounts = get_or_create_default_accounts(company_id)
    clearing_account = accounts.get('2300')
    if not clearing_account:
        clearing_account, _ = Account.objects.get_or_create(
            Code='2300',
            CompanyId=company_id,
            defaults={'Name': 'Due to Directors / Expense Clearing', 'Type': 'Liability', 'IsCashOrBank': False}
        )

    staff_name = ""
    if claim.StaffId:
        try:
            staff = Staff.objects.get(StaffId=claim.StaffId)
            staff_name = staff.StaffName or ""
        except Staff.DoesNotExist:
            pass

    ref_num = f"REIMB-{claim.ClaimNumber}"
    narration = f"Reimbursement of Claim {claim.ClaimNumber} to {staff_name}"

    with transaction.atomic():
        journal_entry, entry_created = JournalEntry.objects.get_or_create(
            ReferenceNumber=ref_num,
            Source='expense_claim_repay',
            CompanyId=company_id,
            defaults={
                'Date': claim.ReimbursementDate or datetime.now().strftime('%Y-%m-%d'),
                'Narration': narration
            }
        )

        if not entry_created:
            JournalItem.objects.filter(JournalEntryId=journal_entry.JournalEntryId).delete()
            journal_entry.Date = claim.ReimbursementDate or journal_entry.Date
            journal_entry.Narration = narration
            journal_entry.save()

        claim.ReimbursementJournalEntryId = journal_entry.JournalEntryId

        # Debit Liability clearing account
        JournalItem.objects.create(
            JournalEntryId=journal_entry.JournalEntryId,
            AccountId=clearing_account.AccountId,
            Debit=f"{float(claim.Amount or 0.0):.2f}",
            Credit="0.00",
            StaffId=claim.StaffId
        )

        # Credit Selected Cash/Bank Account
        JournalItem.objects.create(
            JournalEntryId=journal_entry.JournalEntryId,
            AccountId=claim.ReimbursementAccountId,
            Debit="0.00",
            Credit=f"{float(claim.Amount or 0.0):.2f}",
            StaffId=claim.StaffId
        )


@api_view(['GET', 'POST'])
def ExpenseClaimApi(request):
    if request.method == 'GET':
        claims = ExpenseClaim.objects.all().order_by('-SortId')
        serializer = ExpenseClaimSerializer(claims, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        company_id = data.get('CompanyId')
        if company_id:
            data['ClaimNumber'] = get_next_claim_number(company_id)
        
        serializer = ExpenseClaimSerializer(data=data)
        if serializer.is_valid():
            claim = serializer.save()
            post_claim_journal_entries(claim)
            claim.save()
            return JsonResponse(claim.ExpenseClaimId, safe=False)
        return JsonResponse("Failed to add Expense Claim", safe=False, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
def ExpenseClaimApiById(request, ExpenseClaimId=""):
    try:
        claim = ExpenseClaim.objects.get(ExpenseClaimId=ExpenseClaimId)
    except ExpenseClaim.DoesNotExist:
        return JsonResponse("Expense Claim does not exist", safe=False, status=404)

    if request.method == 'GET':
        serializer = ExpenseClaimSerializer(claim)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = ExpenseClaimSerializer(claim, data=data, partial=True)
        if serializer.is_valid():
            claim = serializer.save()
            post_claim_journal_entries(claim)
            if claim.IsReimbursed:
                post_reimbursement_journal_entries(claim)
            else:
                if claim.ReimbursementJournalEntryId:
                    JournalItem.objects.filter(JournalEntryId=claim.ReimbursementJournalEntryId).delete()
                    JournalEntry.objects.filter(JournalEntryId=claim.ReimbursementJournalEntryId).delete()
                    claim.ReimbursementJournalEntryId = None
            claim.save()
            return JsonResponse(claim.ExpenseClaimId, safe=False)
        return JsonResponse("Failed to update Expense Claim", safe=False, status=400)

    elif request.method == 'DELETE':
        with transaction.atomic():
            if claim.ExpenseJournalEntryId:
                JournalItem.objects.filter(JournalEntryId=claim.ExpenseJournalEntryId).delete()
                JournalEntry.objects.filter(JournalEntryId=claim.ExpenseJournalEntryId).delete()
            if claim.ReimbursementJournalEntryId:
                JournalItem.objects.filter(JournalEntryId=claim.ReimbursementJournalEntryId).delete()
                JournalEntry.objects.filter(JournalEntryId=claim.ReimbursementJournalEntryId).delete()
            claim.delete()
        return JsonResponse("Deleted successfully", safe=False)


@api_view(['GET'])
def ExpenseClaimByCompanyId(request, CompanyId=""):
    claims = ExpenseClaim.objects.filter(CompanyId=CompanyId).order_by('-Date', '-ClaimNumber')
    enriched_claims = []
    for claim in claims:
        data = ExpenseClaimSerializer(claim).data
        try:
            account = Account.objects.get(AccountId=claim.AccountId)
            data['AccountName'] = account.Name
            data['AccountCode'] = account.Code
        except Account.DoesNotExist:
            data['AccountName'] = ""
            data['AccountCode'] = ""

        try:
            if claim.ReimbursementAccountId:
                reimb_acc = Account.objects.get(AccountId=claim.ReimbursementAccountId)
                data['ReimbursementAccountName'] = reimb_acc.Name
                data['ReimbursementAccountCode'] = reimb_acc.Code
            else:
                data['ReimbursementAccountName'] = ""
                data['ReimbursementAccountCode'] = ""
        except Account.DoesNotExist:
            data['ReimbursementAccountName'] = ""
            data['ReimbursementAccountCode'] = ""

        try:
            if claim.StaffId:
                staff = Staff.objects.get(StaffId=claim.StaffId)
                data['StaffName'] = staff.StaffName
            else:
                data['StaffName'] = ""
        except Staff.DoesNotExist:
            data['StaffName'] = ""

        try:
            if claim.VendorId:
                from app_vendor.models import Vendor
                v = Vendor.objects.get(VendorId=claim.VendorId)
                data['VendorName'] = v.VendorDisplayName or v.CompanyName or ""
            else:
                data['VendorName'] = ""
        except:
            data['VendorName'] = ""

        enriched_claims.append(data)

    return JsonResponse(enriched_claims, safe=False)


@api_view(['POST'])
def ExpenseClaimReimburse(request, ExpenseClaimId=""):
    try:
        claim = ExpenseClaim.objects.get(ExpenseClaimId=ExpenseClaimId)
    except ExpenseClaim.DoesNotExist:
        return JsonResponse("Expense Claim does not exist", safe=False, status=404)

    data = JSONParser().parse(request)
    reimbursement_account_id = data.get('ReimbursementAccountId')
    reimbursement_date = data.get('ReimbursementDate')

    if not reimbursement_account_id or not reimbursement_date:
        return JsonResponse("ReimbursementAccountId and ReimbursementDate are required", safe=False, status=400)

    claim.IsReimbursed = True
    claim.ReimbursementAccountId = reimbursement_account_id
    claim.ReimbursementDate = reimbursement_date
    post_reimbursement_journal_entries(claim)
    claim.save()

    return JsonResponse(claim.ExpenseClaimId, safe=False)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def ExpenseClaimUploadReceipt(request, ExpenseClaimId=""):
    try:
        claim = ExpenseClaim.objects.get(ExpenseClaimId=ExpenseClaimId)
    except ExpenseClaim.DoesNotExist:
        return JsonResponse("Expense Claim does not exist", safe=False, status=404)

    file_obj = request.FILES.get('Receipt')
    if not file_obj:
        return JsonResponse("No receipt file provided", safe=False, status=400)

    claim.Receipt = file_obj
    claim.save()

    return JsonResponse("Uploaded successfully", safe=False)


@api_view(['GET', 'POST'])

def JournalEntryApi(request):
    if request.method == 'GET':
        company_id = request.GET.get('CompanyId') or request.query_params.get('CompanyId')
        if company_id:
            entries = JournalEntry.objects.filter(CompanyId=company_id, Source='manual').order_by('Date', 'SortId')
        else:
            entries = JournalEntry.objects.filter(Source='manual').order_by('Date', 'SortId')
        
        enriched_entries = []
        for entry in entries:
            data = JournalEntrySerializer(entry).data
            items = JournalItem.objects.filter(JournalEntryId=entry.JournalEntryId)
            
            # Enrich items with AccountName, AccountCode, ClientName
            enriched_items = []
            for item in items:
                item_data = JournalItemSerializer(item).data
                try:
                    acc = Account.objects.get(AccountId=item.AccountId)
                    item_data['AccountName'] = acc.Name
                    item_data['AccountCode'] = acc.Code
                except Account.DoesNotExist:
                    item_data['AccountName'] = ""
                    item_data['AccountCode'] = ""
                
                try:
                    if item.ClientId:
                        client = Client.objects.get(ClientId=item.ClientId)
                        item_data['ClientName'] = client.CustomerDisplayName
                    else:
                        item_data['ClientName'] = ""
                except:
                    item_data['ClientName'] = ""
                enriched_items.append(item_data)
                
            data['Items'] = enriched_items
            enriched_entries.append(data)
        return JsonResponse(enriched_entries, safe=False)
        
    elif request.method == 'POST':
        data = JSONParser().parse(request)
        
        # Expected payload:
        # {
        #   "JournalEntryId": "optional-for-edit",
        #   "CompanyId": "...",
        #   "Date": "YYYY-MM-DD",
        #   "ReferenceNumber": "...",
        #   "Narration": "...",
        #   "Items": [
        #     { "AccountId": "...", "Debit": "100.00", "Credit": "0.00", "ClientId": "..." },
        #     { "AccountId": "...", "Debit": "0.00", "Credit": "100.00", "ClientId": "..." }
        #   ]
        # }
        
        items_data = data.get('Items', [])
        if not items_data or len(items_data) < 2:
            return JsonResponse("At least two journal items are required", safe=False, status=400)
            
        total_debit = 0.0
        total_credit = 0.0
        for item in items_data:
            try:
                total_debit += float(item.get('Debit') or 0.0)
                total_credit += float(item.get('Credit') or 0.0)
            except ValueError:
                return JsonResponse("Invalid debit or credit amount format", safe=False, status=400)
                
        if abs(total_debit - total_credit) > 0.001:
            return JsonResponse(f"Journal entry is not balanced. Total Debits ({total_debit:.2f}) must equal Total Credits ({total_credit:.2f})", safe=False, status=400)
            
        if total_debit <= 0:
            return JsonResponse("Amount must be greater than 0", safe=False, status=400)
            
        # Save JournalEntry
        je_id = data.get('JournalEntryId')
        if je_id:
            try:
                entry = JournalEntry.objects.get(JournalEntryId=je_id)
                entry.Date = data.get('Date')
                entry.ReferenceNumber = data.get('ReferenceNumber')
                entry.Narration = data.get('Narration')
                entry.CompanyId = data.get('CompanyId')
                entry.save()
            except JournalEntry.DoesNotExist:
                return JsonResponse("Journal entry not found", safe=False, status=404)
        else:
            entry = JournalEntry.objects.create(
                Date=data.get('Date'),
                ReferenceNumber=data.get('ReferenceNumber'),
                Narration=data.get('Narration'),
                Source='manual',
                CompanyId=data.get('CompanyId')
            )
            
        # Delete existing items if editing
        JournalItem.objects.filter(JournalEntryId=entry.JournalEntryId).delete()
        
        # Create new items
        for item in items_data:
            JournalItem.objects.create(
                JournalEntryId=entry.JournalEntryId,
                AccountId=item.get('AccountId'),
                Debit=f"{float(item.get('Debit') or 0.0):.2f}",
                Credit=f"{float(item.get('Credit') or 0.0):.2f}",
                ClientId=item.get('ClientId') or None
            )
            
        return JsonResponse(entry.JournalEntryId, safe=False, status=200)

@api_view(['GET', 'DELETE'])
def JournalEntryApiById(request, JournalEntryId=""):
    try:
        entry = JournalEntry.objects.get(JournalEntryId=JournalEntryId)
    except JournalEntry.DoesNotExist:
        return JsonResponse("Journal entry not found", safe=False, status=404)
        
    if request.method == 'GET':
        data = JournalEntrySerializer(entry).data
        items = JournalItem.objects.filter(JournalEntryId=entry.JournalEntryId)
        
        # Enrich items
        enriched_items = []
        for item in items:
            item_data = JournalItemSerializer(item).data
            try:
                acc = Account.objects.get(AccountId=item.AccountId)
                item_data['AccountName'] = acc.Name
                item_data['AccountCode'] = acc.Code
            except Account.DoesNotExist:
                item_data['AccountName'] = ""
                item_data['AccountCode'] = ""
            
            try:
                if item.ClientId:
                    client = Client.objects.get(ClientId=item.ClientId)
                    item_data['ClientName'] = client.CustomerDisplayName
                else:
                    item_data['ClientName'] = ""
            except:
                item_data['ClientName'] = ""
            enriched_items.append(item_data)
            
        data['Items'] = enriched_items
        return JsonResponse(data, safe=False)
        
    elif request.method == 'DELETE':
        JournalItem.objects.filter(JournalEntryId=entry.JournalEntryId).delete()
        entry.delete()
        return JsonResponse("Deleted successfully", safe=False)


@api_view(['GET'])
def ExportCashBook(request, CompanyId=""):
    print("ExportCashBook VIEW REACHED! CompanyId:", CompanyId)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    export_format = request.GET.get('export_format', request.GET.get('format', 'pdf')).lower()
    
    start_date_obj = parse_date(start_date)
    end_date_obj = parse_date(end_date)
    
    # Fetch all Accounts for this Company that are marked as Cash or Bank
    cash_bank_accounts = Account.objects.filter(CompanyId=CompanyId, IsCashOrBank=True)
    account_ids = [acc.AccountId for acc in cash_bank_accounts]
    
    # Fetch all JournalItems for these Accounts
    items = JournalItem.objects.filter(AccountId__in=account_ids).order_by('SortId')
    
    opening_balance = 0.0
    period_items = []
    
    for item in items:
        try:
            entry = JournalEntry.objects.get(JournalEntryId=item.JournalEntryId)
            entry_date = entry.Date
        except JournalEntry.DoesNotExist:
            entry_date = None
            
        entry_date_obj = parse_date(entry_date)
        
        debit_val = safe_float(item.Debit)
        credit_val = safe_float(item.Credit)
        
        if start_date_obj and entry_date_obj and entry_date_obj < start_date_obj:
            opening_balance += (debit_val - credit_val)
            continue
            
        if end_date_obj and entry_date_obj and entry_date_obj > end_date_obj:
            continue
            
        # Get Contra account
        other_items = JournalItem.objects.filter(JournalEntryId=item.JournalEntryId).exclude(JournalItemId=item.JournalItemId)
        non_cb_items = []
        for o_item in other_items:
            try:
                acc = Account.objects.get(AccountId=o_item.AccountId)
                if not acc.IsCashOrBank:
                    non_cb_items.append((o_item, acc))
            except Account.DoesNotExist:
                pass
        
        if not non_cb_items:
            for o_item in other_items:
                try:
                    acc = Account.objects.get(AccountId=o_item.AccountId)
                    non_cb_items.append((o_item, acc))
                except Account.DoesNotExist:
                    pass
                    
        client_name = ""
        if item.ClientId:
            client = Client.objects.filter(ClientId=item.ClientId).first()
            if client:
                client_name = client.CustomerDisplayName

        # Check for Bank Charges
        bank_charges = 0.0
        if entry_date and entry.Source == 'payment':
            charges_item = next((x for x in non_cb_items if x[1].Code == '6150'), None)
            if charges_item:
                bank_charges = safe_float(charges_item[0].Debit)
                
        if entry_date and entry.Source == 'payment' and bank_charges > 0.0:
            # 1. Gross Cash Addition Row
            ar_item = next((x for x in non_cb_items if x[1].Code == '1200'), None)
            contra_name = ar_item[1].Name if ar_item else "Accounts Receivable"
            contra_code = ar_item[1].Code if ar_item else "1200"
            gross_debit = debit_val + bank_charges
            
            period_items.append({
                'Date': entry_date,
                'ReferenceNumber': entry.ReferenceNumber,
                'Source': entry.Source,
                'Narration': f"{entry.Narration} (Gross Receipt)",
                'Debit': f"{gross_debit:.2f}",
                'Credit': "0.00",
                'SortId': item.SortId,
                'ContraAccountName': contra_name,
                'ContraAccountCode': contra_code,
                'ClientName': client_name,
            })
            
            # 2. Bank Charges Deduction Row
            period_items.append({
                'Date': entry_date,
                'ReferenceNumber': entry.ReferenceNumber,
                'Source': entry.Source,
                'Narration': f"{entry.Narration} (Bank Charges)",
                'Debit': "0.00",
                'Credit': f"{bank_charges:.2f}",
                'SortId': item.SortId,
                'ContraAccountName': "Bank Charges",
                'ContraAccountCode': "6150",
                'ClientName': "",
            })
        else:
            contra_name = ""
            contra_code = ""
            if len(non_cb_items) == 1:
                contra_name = non_cb_items[0][1].Name
                contra_code = non_cb_items[0][1].Code
            elif len(non_cb_items) > 1:
                if entry_date and entry.Source == 'payment':
                    ar_item = next((x for x in non_cb_items if x[1].Code == '1200'), None)
                    if ar_item:
                        contra_name = ar_item[1].Name
                        contra_code = ar_item[1].Code
                    else:
                        contra_name = "Multiple Accounts"
                        contra_code = "Split"
                else:
                    contra_name = ", ".join([x[1].Name for x in non_cb_items if x[1].Name])
                    contra_code = ", ".join([x[1].Code for x in non_cb_items if x[1].Code])
                    
            period_items.append({
                'Date': entry_date or "",
                'ReferenceNumber': entry.ReferenceNumber if entry_date else "",
                'Source': entry.Source if entry_date else "",
                'Narration': entry.Narration if entry_date else "",
                'Debit': f"{debit_val:.2f}",
                'Credit': f"{credit_val:.2f}",
                'SortId': item.SortId,
                'ContraAccountName': contra_name,
                'ContraAccountCode': contra_code,
                'ClientName': client_name,
            })
            
    # Sort: Date, SortId, then Debit row first
    period_items.sort(key=lambda x: (
        x.get('Date') or '',
        x.get('SortId') or '',
        0 if safe_float(x.get('Debit')) > 0 else 1
    ))
    
    closing_balance = opening_balance
    running_balance = opening_balance
    for i in range(len(period_items)):
        row = period_items[i]
        deb = safe_float(row['Debit'])
        crd = safe_float(row['Credit'])
        running_balance += (deb - crd)
        row['RunningBalance'] = f"{running_balance:.2f}"
    closing_balance = running_balance
    
    # Fetch company header info
    company_name = "CRM Cash Book Report"
    try:
        from app_company.models import Company
        company = Company.objects.filter(CompanyId=CompanyId).first()
        if company and company.CompanyName:
            company_name = company.CompanyName
    except:
        pass
        
    period_str = f"{start_date or 'Beginning'} to {end_date or 'Present'}"
    
    currency_type = 'INR'
    try:
        from app_site.models import SiteSettings
        siteSettings = SiteSettings.objects.filter(CompanyId=CompanyId).first()
        if siteSettings and siteSettings.CurrencyType:
            currency_type = siteSettings.CurrencyType.strip().upper()
    except:
        pass

    import datetime
    import calendar
    
    def parse_dt(d_str):
        if not d_str:
            return None
        for fmt in ('%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y'):
            try:
                return datetime.datetime.strptime(d_str.strip(), fmt).date()
            except ValueError:
                continue
        return None
        
    start_dt = parse_dt(start_date)
    end_dt = parse_dt(end_date)
    
    if not start_dt and not end_dt:
        suffix = "All"
    elif start_dt and not end_dt:
        suffix = f"from_{start_dt.strftime('%Y%m%d')}"
    elif not start_dt and end_dt:
        suffix = f"to_{end_dt.strftime('%Y%m%d')}"
    else:
        last_day = calendar.monthrange(start_dt.year, start_dt.month)[1]
        if start_dt.year == end_dt.year and start_dt.month == end_dt.month and start_dt.day == 1 and end_dt.day == last_day:
            suffix = f"Monthly_{start_dt.strftime('%B')}_{start_dt.year}"
        elif start_dt.month == 4 and start_dt.day == 1 and end_dt.month == 3 and end_dt.day == 31 and end_dt.year == start_dt.year + 1:
            fy_start = str(start_dt.year)[2:]
            fy_end = str(end_dt.year)[2:]
            suffix = f"FY{fy_start}-{fy_end}"
        elif start_dt.year == end_dt.year and start_dt.day == 1:
            if start_dt.month == 1 and end_dt.month == 3 and end_dt.day == 31:
                suffix = f"Quarterly_Q1_{start_dt.year}"
            elif start_dt.month == 4 and end_dt.month == 6 and end_dt.day == 30:
                suffix = f"Quarterly_Q2_{start_dt.year}"
            elif start_dt.month == 7 and end_dt.month == 9 and end_dt.day == 30:
                suffix = f"Quarterly_Q3_{start_dt.year}"
            elif start_dt.month == 10 and end_dt.month == 12 and end_dt.day == 31:
                suffix = f"Quarterly_Q4_{start_dt.year}"
            else:
                suffix = f"{start_dt.strftime('%Y%m%d')}_to_{end_dt.strftime('%Y%m%d')}"
        else:
            suffix = f"{start_dt.strftime('%Y%m%d')}_to_{end_dt.strftime('%Y%m%d')}"
            
    filename = f"Cash_Book_{suffix}"
    
    if export_format == 'excel':
        import openpyxl
        from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
        from django.http import HttpResponse
            
        if currency_type == 'INR':
            excel_format = '#,##,##0.00;(#,##,##0.00);"-"'
        else:
            excel_format = '#,##0.00;(#,##0.00);"-"'

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Cash Book"
        
        title_font = Font(name="Arial", size=16, bold=True, color="1E3A8A")
        subtitle_font = Font(name="Arial", size=11, italic=True, color="4B5563")
        header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
        bold_font = Font(name="Arial", size=11, bold=True)
        regular_font = Font(name="Arial", size=10)
        
        header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
        summary_fill = PatternFill(start_color="F3F4F6", end_color="F3F4F6", fill_type="solid")
        
        thin_border = Border(
            left=Side(style='thin', color="D1D5DB"),
            right=Side(style='thin', color="D1D5DB"),
            top=Side(style='thin', color="D1D5DB"),
            bottom=Side(style='thin', color="D1D5DB")
        )
        double_bottom_border = Border(
            top=Side(style='thin', color="9CA3AF"),
            bottom=Side(style='double', color="1E3A8A")
        )
        
        ws.merge_cells("A1:I1")
        ws["A1"] = company_name
        ws["A1"].font = title_font
        ws["A1"].alignment = Alignment(horizontal="center")
        
        ws.merge_cells("A2:I2")
        ws["A2"] = f"Period: {period_str}"
        ws["A2"].font = subtitle_font
        ws["A2"].alignment = Alignment(horizontal="center")
        
        ws.merge_cells("A3:I3")
        ws["A3"] = "Note: All financial figures and transaction amounts are represented in Indian Rupees (INR)."
        ws["A3"].font = Font(name="Arial", size=10, italic=True, color="4B5563")
        ws["A3"].alignment = Alignment(horizontal="left")
        
        ws.append([]) # Row 4 empty
        
        ws.append(["Opening Balance", "", "", "", "", "", "", "", opening_balance])
        ws.merge_cells(f"A5:H5")
        ws["A5"].font = bold_font
        ws["I5"].font = bold_font
        ws["I5"].alignment = Alignment(horizontal="right")
        ws["I5"].number_format = excel_format
        ws["A5"].fill = summary_fill
        ws["I5"].fill = summary_fill
        
        headers = ["#", "Date", "Reference", "Account", "Narration", "Client", "Receipt (Dr)", "Payment (Cr)", "Running Balance"]
        ws.append(headers)
        header_row = 6
        for col_idx, h in enumerate(headers, 1):
            cell = ws.cell(row=header_row, column=col_idx)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="left" if col_idx <= 6 else "right")
            
        current_row = 7
        for idx, row in enumerate(period_items, 1):
            debit_val = safe_float(row['Debit'])
            credit_val = safe_float(row['Credit'])
            bal_val = safe_float(row['RunningBalance'])
            
            ws.append([
                idx,
                row['Date'],
                row['ReferenceNumber'],
                f"{row['ContraAccountCode']} - {row['ContraAccountName']}" if row['ContraAccountCode'] else row['ContraAccountName'],
                row['Narration'],
                row.get('ClientName', '') or '-',
                debit_val,
                credit_val,
                bal_val
            ])
            for col_idx in range(1, 10):
                cell = ws.cell(row=current_row, column=col_idx)
                cell.font = regular_font
                cell.border = thin_border
                cell.alignment = Alignment(horizontal="left" if col_idx <= 6 else "right")
                if col_idx in (7, 8, 9):
                    cell.number_format = excel_format
            current_row += 1
            
        ws.append(["Closing Balance", "", "", "", "", "", "", "", closing_balance])
        ws.merge_cells(f"A{current_row}:H{current_row}")
        ws[f"A{current_row}"].font = bold_font
        ws[f"I{current_row}"].font = bold_font
        ws[f"I{current_row}"].alignment = Alignment(horizontal="right")
        ws[f"I{current_row}"].number_format = excel_format
        ws[f"A{current_row}"].border = double_bottom_border
        ws[f"I{current_row}"].border = double_bottom_border
        ws[f"A{current_row}"].fill = summary_fill
        ws[f"I{current_row}"].fill = summary_fill
        
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = openpyxl.utils.get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 3, 12)
            
        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
        wb.save(response)
        return response
        
    else:
        from django.http import HttpResponse
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_RIGHT
        
        def format_raw_currency(value, currency_code):
            if value is None or value == '':
                value = 0.0
            try:
                num = float(value)
            except (ValueError, TypeError):
                return ''
            
            is_negative = num < 0
            abs_num = abs(num)
            fixed_num = f"{abs_num:.2f}"
            parts = fixed_num.split('.')
            integer_part = parts[0]
            decimal_part = parts[1]
            
            code = (currency_code or '').strip().upper()
            
            if code == 'INR':
                if len(integer_part) <= 3:
                    formatted_integer = integer_part
                else:
                    last_three = integer_part[-3:]
                    remaining = integer_part[:-3]
                    chunks = []
                    while len(remaining) > 0:
                        chunks.insert(0, remaining[-2:])
                        remaining = remaining[:-2]
                    formatted_integer = ','.join(chunks) + ',' + last_three
                return f"{'-' if is_negative else ''}{formatted_integer}.{decimal_part}"
                
            elif code == 'EUR':
                chunks = []
                remaining = integer_part
                while len(remaining) > 0:
                    chunks.insert(0, remaining[-3:])
                    remaining = remaining[:-3]
                formatted_integer = '.'.join(chunks)
                return f"{'-' if is_negative else ''}{formatted_integer},{decimal_part}"
                
            else:
                chunks = []
                remaining = integer_part
                while len(remaining) > 0:
                    chunks.insert(0, remaining[-3:])
                    remaining = remaining[:-3]
                formatted_integer = ','.join(chunks)
                return f"{'-' if is_negative else ''}{formatted_integer}.{decimal_part}"

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
        
        doc = SimpleDocTemplate(response, pagesize=landscape(letter), rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        story = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=18,
            textColor=colors.HexColor("#1e3a8a"),
            spaceAfter=6
        )
        subtitle_style = ParagraphStyle(
            'DocSub',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=10,
            textColor=colors.HexColor("#4b5563"),
            spaceAfter=8
        )
        note_style = ParagraphStyle(
            'DocNote',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=9,
            textColor=colors.HexColor("#4b5563"),
            spaceAfter=15
        )
        cell_style = ParagraphStyle(
            'CellText',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            leading=10
        )
        cell_style_right = ParagraphStyle(
            'CellTextRight',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            leading=10,
            alignment=TA_RIGHT
        )
        cell_bold = ParagraphStyle(
            'CellBold',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            leading=10
        )
        cell_bold_right = ParagraphStyle(
            'CellBoldRight',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            leading=10,
            alignment=TA_RIGHT
        )
        header_cell_style = ParagraphStyle(
            'HeaderCell',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=11,
            textColor=colors.white
        )
        header_cell_style_right = ParagraphStyle(
            'HeaderCellRight',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=11,
            textColor=colors.white,
            alignment=TA_RIGHT
        )
        
        story.append(Paragraph(company_name, title_style))
        story.append(Paragraph(f"Cash Book Statement &mdash; Period: {period_str}", subtitle_style))
        story.append(Paragraph("Note: All financial figures and transaction amounts are represented in Indian Rupees (INR).", note_style))
        
        col_widths = [30, 65, 65, 105, 175, 100, 60, 60, 60]
        
        table_data = []
        table_data.append([
            Paragraph("#", header_cell_style),
            Paragraph("Date", header_cell_style),
            Paragraph("Reference", header_cell_style),
            Paragraph("Account", header_cell_style),
            Paragraph("Narration", header_cell_style),
            Paragraph("Client", header_cell_style),
            Paragraph("Receipt (Dr)", header_cell_style_right),
            Paragraph("Payment (Cr)", header_cell_style_right),
            Paragraph("Running Balance", header_cell_style_right)
        ])
        
        table_data.append([
            Paragraph("<b>Opening Balance</b>", cell_bold),
            "", "", "", "", "", "", "",
            Paragraph(f"<b>{format_raw_currency(opening_balance, currency_type)}</b>", cell_bold_right)
        ])
        
        for idx, row in enumerate(period_items, 1):
            debit_val = safe_float(row['Debit'])
            credit_val = safe_float(row['Credit'])
            running_val = safe_float(row['RunningBalance'])
            
            debit_str = format_raw_currency(debit_val, currency_type) if debit_val > 0 else "-"
            credit_str = format_raw_currency(credit_val, currency_type) if credit_val > 0 else "-"
            running_str = format_raw_currency(running_val, currency_type)
            
            table_data.append([
                Paragraph(str(idx), cell_style),
                Paragraph(row['Date'], cell_style),
                Paragraph(row['ReferenceNumber'], cell_style),
                Paragraph(f"{row['ContraAccountCode']} - {row['ContraAccountName']}" if row['ContraAccountCode'] else row['ContraAccountName'], cell_style),
                Paragraph(row['Narration'], cell_style),
                Paragraph(row.get('ClientName', '') or '-', cell_style),
                Paragraph(debit_str, cell_style_right),
                Paragraph(credit_str, cell_style_right),
                Paragraph(running_str, cell_style_right)
            ])
            
        table_data.append([
            Paragraph("<b>Closing Balance</b>", cell_bold),
            "", "", "", "", "", "", "",
            Paragraph(f"<b>{format_raw_currency(closing_balance, currency_type)}</b>", cell_bold_right)
        ])
        
        t = Table(table_data, colWidths=col_widths, repeatRows=1)
        t_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
            
            ('SPAN', (0, 1), (7, 1)),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor("#f3f4f6")),
            ('ALIGN', (8, 1), (8, 1), 'RIGHT'),
            
            ('SPAN', (0, -1), (7, -1)),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#f3f4f6")),
            ('ALIGN', (8, -1), (8, -1), 'RIGHT'),
            
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ])
        t.setStyle(t_style)
        story.append(t)
        
        doc.build(story)
        return response

