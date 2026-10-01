from rest_framework.decorators import api_view, parser_classes
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from django.db import transaction
from django.db.models import Q
import calendar
from app_accounting.models import (
    Account, JournalEntry, JournalItem, Expense, ExpenseClaim,
    EmployeeLoan, EmployeeLoanRepayment, PayrollEntry
)
from app_accounting.serializers import (
    AccountSerializer, JournalEntrySerializer, JournalItemSerializer,
    ExpenseSerializer, ExpenseClaimSerializer, EmployeeLoanSerializer,
    EmployeeLoanRepaymentSerializer, PayrollEntrySerializer
)
from app_client.models import Client
from app_client.serializers import ClientSerializer
from app_staff.models import Staff, SalarySlip
from app_basic.models import Designation


def format_media_url(file_field):
    if not file_field or not hasattr(file_field, 'name') or not file_field.name:
        return ""
    name = str(file_field.name).lstrip('/')
    if name.startswith('media/'):
        return name
    return f"media/{name}"


def get_designation_map():
    try:
        return {d.DesignationId: d.Designation for d in Designation.objects.all() if d.Designation}
    except Exception:
        return {}


def resolve_designation_name(designation_val, desig_map=None):
    if not designation_val:
        return ""
    if desig_map is None:
        desig_map = get_designation_map()
    if designation_val in desig_map:
        return desig_map[designation_val]
    val_str = str(designation_val).strip()
    import re
    if re.match(r'^[0-9a-fA-F\-]{32,36}$', val_str):
        return ""
    return val_str


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

    elif source in ['employee_loan_disbursement', 'employee_loan']:
        from app_accounting.models import EmployeeLoan
        loan = EmployeeLoan.objects.filter(
            Q(DisbursementJournalEntryId=entry.JournalEntryId) |
            Q(LoanNumber=entry.ReferenceNumber)
        ).first()
        if loan and loan.Receipt and hasattr(loan.Receipt, 'name') and loan.Receipt.name:
            return format_media_url(loan.Receipt)

    elif source in ['employee_loan_repayment', 'employee_loan_repay']:
        from app_accounting.models import EmployeeLoanRepayment
        repay = EmployeeLoanRepayment.objects.filter(
            Q(JournalEntryId=entry.JournalEntryId) |
            Q(RepaymentNumber=entry.ReferenceNumber)
        ).first()
        if repay and repay.Receipt and hasattr(repay.Receipt, 'name') and repay.Receipt.name:
            return format_media_url(repay.Receipt)

    elif source in ['payroll_salary', 'payroll']:
        from app_accounting.models import PayrollEntry
        payroll = PayrollEntry.objects.filter(
            Q(JournalEntryId=entry.JournalEntryId) |
            Q(ReferenceNumber=entry.ReferenceNumber)
        ).first()
        if payroll and payroll.Receipt and hasattr(payroll.Receipt, 'name') and payroll.Receipt.name:
            return format_media_url(payroll.Receipt)

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
    elif source in ['employee_loan_disbursement', 'employee_loan']:
        from app_accounting.models import EmployeeLoan
        loan = EmployeeLoan.objects.filter(
            Q(DisbursementJournalEntryId=entry.JournalEntryId) |
            Q(LoanNumber=ref_num) |
            Q(EmployeeLoanId=ref_num)
        ).first()
        if loan and loan.LoanNumber:
            return loan.LoanNumber
        elif ref_num.startswith('LOAN-'):
            return ref_num.replace('LOAN-', '')
    elif source in ['employee_loan_repayment', 'employee_loan_repay']:
        from app_accounting.models import EmployeeLoanRepayment
        repay = EmployeeLoanRepayment.objects.filter(
            Q(JournalEntryId=entry.JournalEntryId) |
            Q(RepaymentNumber=ref_num) |
            Q(RepaymentId=ref_num)
        ).first()
        if repay and repay.RepaymentNumber:
            return repay.RepaymentNumber
        elif ref_num.startswith('REPAY-'):
            return ref_num.replace('REPAY-', '')
        elif ref_num.startswith('LRP-'):
            return ref_num
    elif source in ['payroll_salary', 'payroll']:
        from app_accounting.models import PayrollEntry
        payroll = PayrollEntry.objects.filter(
            Q(JournalEntryId=entry.JournalEntryId) |
            Q(ReferenceNumber=ref_num) |
            Q(PayrollId=ref_num)
        ).first()
        if payroll and payroll.ReferenceNumber:
            return payroll.ReferenceNumber
        return ref_num

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

        if not staff_id and entry and entry.Source in ['employee_loan_disbursement', 'employee_loan']:
            from app_accounting.models import EmployeeLoan
            loan = EmployeeLoan.objects.filter(
                Q(DisbursementJournalEntryId=entry.JournalEntryId) |
                Q(LoanNumber=entry.ReferenceNumber) |
                Q(EmployeeLoanId=entry.ReferenceNumber)
            ).first()
            if loan and loan.StaffId:
                staff_id = loan.StaffId
                try:
                    JournalItem.objects.filter(JournalEntryId=entry.JournalEntryId).update(StaffId=staff_id)
                except:
                    pass

        if not staff_id and entry and entry.Source in ['employee_loan_repayment', 'employee_loan_repay']:
            from app_accounting.models import EmployeeLoanRepayment, EmployeeLoan
            repay = EmployeeLoanRepayment.objects.filter(
                Q(JournalEntryId=entry.JournalEntryId) |
                Q(RepaymentNumber=entry.ReferenceNumber) |
                Q(RepaymentId=entry.ReferenceNumber)
            ).first()
            if repay and repay.EmployeeLoanId:
                loan = EmployeeLoan.objects.filter(EmployeeLoanId=repay.EmployeeLoanId).first()
                if loan and loan.StaffId:
                    staff_id = loan.StaffId
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

        if not staff_id and entry_date and entry.Source in ['employee_loan_disbursement', 'employee_loan']:
            from app_accounting.models import EmployeeLoan
            loan = EmployeeLoan.objects.filter(
                Q(DisbursementJournalEntryId=entry.JournalEntryId) |
                Q(LoanNumber=entry.ReferenceNumber) |
                Q(EmployeeLoanId=entry.ReferenceNumber)
            ).first()
            if loan:
                staff_id = loan.StaffId

        if not staff_id and entry_date and entry.Source in ['employee_loan_repayment', 'employee_loan_repay']:
            from app_accounting.models import EmployeeLoanRepayment, EmployeeLoan
            repay = EmployeeLoanRepayment.objects.filter(
                Q(JournalEntryId=entry.JournalEntryId) |
                Q(RepaymentNumber=entry.ReferenceNumber) |
                Q(RepaymentId=entry.ReferenceNumber)
            ).first()
            if repay and repay.EmployeeLoanId:
                loan = EmployeeLoan.objects.filter(EmployeeLoanId=repay.EmployeeLoanId).first()
                if loan:
                    staff_id = loan.StaffId

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


def generate_next_loan_number(company_id):
    loans = EmployeeLoan.objects.filter(CompanyId=company_id, LoanNumber__startswith='LN-')
    max_num = 0
    for l in loans:
        match = re.match(r'^LN-(\d+)$', l.LoanNumber or '')
        if match:
            num = int(match.group(1))
            if num > max_num:
                max_num = num
    next_num = max_num + 1
    return f"LN-{next_num:07d}"


def generate_next_repayment_number(company_id):
    reps = EmployeeLoanRepayment.objects.filter(CompanyId=company_id, RepaymentNumber__startswith='LRP-')
    max_num = 0
    for r in reps:
        match = re.match(r'^LRP-(\d+)$', r.RepaymentNumber or '')
        if match:
            num = int(match.group(1))
            if num > max_num:
                max_num = num
    next_num = max_num + 1
    return f"LRP-{next_num:07d}"


def post_loan_disbursement_journal_entries(loan):
    from app_accounting.signals import get_or_create_default_accounts
    company_id = loan.CompanyId
    if not company_id:
        return

    accounts = get_or_create_default_accounts(company_id)
    loan_account = accounts.get('1300')
    if not loan_account:
        loan_account, _ = Account.objects.get_or_create(
            Code='1300',
            CompanyId=company_id,
            defaults={'Name': 'Employee Loans & Advances', 'Type': 'Asset', 'IsCashOrBank': False}
        )

    loan.LoanAccountId = loan_account.AccountId

    staff_name = ""
    if loan.StaffId:
        try:
            staff = Staff.objects.get(StaffId=loan.StaffId)
            staff_name = staff.StaffName or ""
        except Staff.DoesNotExist:
            pass

    ref_num = f"LOAN-{loan.LoanNumber}" if loan.LoanNumber else f"LOAN-{loan.EmployeeLoanId}"
    narration = f"Loan Disbursement {loan.LoanNumber or ''} to {staff_name}"
    if loan.Narration:
        narration += f" - {loan.Narration}"

    with transaction.atomic():
        journal_entry, entry_created = JournalEntry.objects.get_or_create(
            ReferenceNumber=ref_num,
            Source='employee_loan_disbursement',
            CompanyId=company_id,
            defaults={
                'Date': loan.LoanDate or datetime.now().strftime('%Y-%m-%d'),
                'Narration': narration
            }
        )

        if not entry_created:
            JournalItem.objects.filter(JournalEntryId=journal_entry.JournalEntryId).delete()
            journal_entry.Date = loan.LoanDate or journal_entry.Date
            journal_entry.Narration = narration
            journal_entry.save()

        loan.DisbursementJournalEntryId = journal_entry.JournalEntryId

        principal_val = float(loan.PrincipalAmount or 0.0)

        # Debit 1300 - Employee Loans & Advances (Asset)
        JournalItem.objects.create(
            JournalEntryId=journal_entry.JournalEntryId,
            AccountId=loan_account.AccountId,
            Debit=f"{principal_val:.2f}",
            Credit="0.00",
            StaffId=loan.StaffId
        )

        # Credit Selected Cash/Bank Disbursement Account
        if loan.DisbursementAccountId:
            JournalItem.objects.create(
                JournalEntryId=journal_entry.JournalEntryId,
                AccountId=loan.DisbursementAccountId,
                Debit="0.00",
                Credit=f"{principal_val:.2f}",
                StaffId=loan.StaffId
            )


def post_loan_repayment_journal_entries(repayment, loan):
    from app_accounting.signals import get_or_create_default_accounts
    company_id = repayment.CompanyId or loan.CompanyId
    if not company_id:
        return

    accounts = get_or_create_default_accounts(company_id)
    loan_account = accounts.get('1300')
    if not loan_account:
        loan_account, _ = Account.objects.get_or_create(
            Code='1300',
            CompanyId=company_id,
            defaults={'Name': 'Employee Loans & Advances', 'Type': 'Asset', 'IsCashOrBank': False}
        )

    interest_income_acc = accounts.get('4100')
    if not interest_income_acc:
        interest_income_acc, _ = Account.objects.get_or_create(
            Code='4100',
            CompanyId=company_id,
            defaults={'Name': 'Interest Income from Staff Loans', 'Type': 'Revenue', 'IsCashOrBank': False}
        )

    staff_name = ""
    if loan.StaffId:
        try:
            staff = Staff.objects.get(StaffId=loan.StaffId)
            staff_name = staff.StaffName or ""
        except Staff.DoesNotExist:
            pass

    ref_num = f"REPAY-{repayment.RepaymentNumber}" if repayment.RepaymentNumber else f"REPAY-{repayment.RepaymentId}"
    narration = f"Loan Repayment {repayment.RepaymentNumber or ''} for Loan {loan.LoanNumber or ''} by {staff_name}"
    if repayment.Narration:
        narration += f" - {repayment.Narration}"

    total_amount = float(repayment.Amount or 0.0)
    principal_comp = float(repayment.PrincipalComponent or 0.0)
    interest_comp = float(repayment.InterestComponent or 0.0)

    if principal_comp == 0.0 and interest_comp == 0.0 and total_amount > 0.0:
        principal_comp = total_amount

    with transaction.atomic():
        journal_entry, entry_created = JournalEntry.objects.get_or_create(
            ReferenceNumber=ref_num,
            Source='employee_loan_repayment',
            CompanyId=company_id,
            defaults={
                'Date': repayment.RepaymentDate or datetime.now().strftime('%Y-%m-%d'),
                'Narration': narration
            }
        )

        if not entry_created:
            JournalItem.objects.filter(JournalEntryId=journal_entry.JournalEntryId).delete()
            journal_entry.Date = repayment.RepaymentDate or journal_entry.Date
            journal_entry.Narration = narration
            journal_entry.save()

        repayment.JournalEntryId = journal_entry.JournalEntryId

        # Debit Cash/Bank Payment Account
        if repayment.PaymentAccountId:
            JournalItem.objects.create(
                JournalEntryId=journal_entry.JournalEntryId,
                AccountId=repayment.PaymentAccountId,
                Debit=f"{total_amount:.2f}",
                Credit="0.00",
                StaffId=loan.StaffId
            )

        # Credit 1300 - Employee Loans & Advances
        if principal_comp > 0:
            JournalItem.objects.create(
                JournalEntryId=journal_entry.JournalEntryId,
                AccountId=loan_account.AccountId,
                Debit="0.00",
                Credit=f"{principal_comp:.2f}",
                StaffId=loan.StaffId
            )

        # Credit 4100 - Interest Income (if any)
        if interest_comp > 0:
            JournalItem.objects.create(
                JournalEntryId=journal_entry.JournalEntryId,
                AccountId=interest_income_acc.AccountId,
                Debit="0.00",
                Credit=f"{interest_comp:.2f}",
                StaffId=loan.StaffId
            )


def recalculate_loan_balance(loan):
    repayments = EmployeeLoanRepayment.objects.filter(EmployeeLoanId=loan.EmployeeLoanId)
    total_repaid = sum(float(r.Amount or 0.0) for r in repayments)
    principal_amount = float(loan.PrincipalAmount or 0.0)
    total_payable = float(loan.TotalAmountPayable or principal_amount)
    if total_payable <= 0:
        total_payable = principal_amount
    outstanding = max(0.0, total_payable - total_repaid)

    loan.TotalRepaid = f"{total_repaid:.2f}"
    loan.OutstandingBalance = f"{outstanding:.2f}"
    if outstanding <= 0.01 and total_repaid > 0:
        loan.Status = 'Closed'
    elif loan.Status == 'Closed' and outstanding > 0.01:
        loan.Status = 'Active'
    loan.save()
    return loan


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


@api_view(['GET'])
def NextLoanNumber(request, CompanyId=""):
    return JsonResponse(generate_next_loan_number(CompanyId), safe=False)


@api_view(['GET'])
def NextRepaymentNumber(request, CompanyId=""):
    return JsonResponse(generate_next_repayment_number(CompanyId), safe=False)


@api_view(['GET', 'POST'])
def EmployeeLoanApi(request):
    if request.method == 'GET':
        company_id = request.GET.get('CompanyId') or request.query_params.get('CompanyId')
        if company_id:
            loans = EmployeeLoan.objects.filter(CompanyId=company_id).order_by('-SortId')
        else:
            loans = EmployeeLoan.objects.all().order_by('-SortId')
        serializer = EmployeeLoanSerializer(loans, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        company_id = data.get('CompanyId', '')
        if not data.get('LoanNumber') and company_id:
            data['LoanNumber'] = generate_next_loan_number(company_id)

        principal = float(data.get('PrincipalAmount') or 0.0)
        repayment_type = data.get('RepaymentType', 'flexible')
        interest_type = data.get('InterestType', 'zero_interest')
        interest_rate = float(data.get('InterestRate') or 0.0)
        installment_count = max(1, int(float(data.get('InstallmentCount') or 1)))

        if interest_type == 'zero_interest':
            total_interest = 0.0
            data['InterestRate'] = '0.00'
        else:
            if repayment_type == 'installment':
                total_interest = principal * (interest_rate / 100.0) * (installment_count / 12.0)
            else:
                total_interest = principal * (interest_rate / 100.0)

        total_payable = principal + total_interest
        installment_amount = total_payable / installment_count if repayment_type == 'installment' else 0.0

        data['TotalInterest'] = f"{total_interest:.2f}"
        data['TotalAmountPayable'] = f"{total_payable:.2f}"
        data['InstallmentAmount'] = f"{installment_amount:.2f}"
        data['TotalRepaid'] = "0.00"
        data['OutstandingBalance'] = f"{total_payable:.2f}"
        data['Status'] = 'Active'

        serializer = EmployeeLoanSerializer(data=data)
        if serializer.is_valid():
            loan = serializer.save()
            post_loan_disbursement_journal_entries(loan)
            loan.save()
            return JsonResponse(loan.EmployeeLoanId, safe=False)
        return JsonResponse("Failed to create Employee Loan", safe=False, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
def EmployeeLoanApiById(request, EmployeeLoanId=""):
    try:
        loan = EmployeeLoan.objects.get(EmployeeLoanId=EmployeeLoanId)
    except EmployeeLoan.DoesNotExist:
        return JsonResponse("Employee Loan does not exist", safe=False, status=404)

    if request.method == 'GET':
        serializer = EmployeeLoanSerializer(loan)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        principal = float(data.get('PrincipalAmount') or loan.PrincipalAmount or 0.0)
        repayment_type = data.get('RepaymentType') or loan.RepaymentType or 'flexible'
        interest_type = data.get('InterestType') or loan.InterestType or 'zero_interest'
        interest_rate = float(data.get('InterestRate') if data.get('InterestRate') is not None else (loan.InterestRate or 0.0))
        installment_count = max(1, int(float(data.get('InstallmentCount') or loan.InstallmentCount or 1)))

        if interest_type == 'zero_interest':
            total_interest = 0.0
            data['InterestRate'] = '0.00'
        else:
            if repayment_type == 'installment':
                total_interest = principal * (interest_rate / 100.0) * (installment_count / 12.0)
            else:
                total_interest = principal * (interest_rate / 100.0)

        total_payable = principal + total_interest
        installment_amount = total_payable / installment_count if repayment_type == 'installment' else 0.0

        data['TotalInterest'] = f"{total_interest:.2f}"
        data['TotalAmountPayable'] = f"{total_payable:.2f}"
        data['InstallmentAmount'] = f"{installment_amount:.2f}"

        serializer = EmployeeLoanSerializer(loan, data=data, partial=True)
        if serializer.is_valid():
            loan = serializer.save()
            post_loan_disbursement_journal_entries(loan)
            recalculate_loan_balance(loan)
            return JsonResponse(loan.EmployeeLoanId, safe=False)
        return JsonResponse("Failed to update Employee Loan", safe=False, status=400)

    elif request.method == 'DELETE':
        with transaction.atomic():
            # Delete loan repayments
            repayments = EmployeeLoanRepayment.objects.filter(EmployeeLoanId=loan.EmployeeLoanId)
            for rep in repayments:
                if rep.JournalEntryId:
                    JournalItem.objects.filter(JournalEntryId=rep.JournalEntryId).delete()
                    JournalEntry.objects.filter(JournalEntryId=rep.JournalEntryId).delete()
            repayments.delete()

            # Delete disbursement journal entries
            if loan.DisbursementJournalEntryId:
                JournalItem.objects.filter(JournalEntryId=loan.DisbursementJournalEntryId).delete()
                JournalEntry.objects.filter(JournalEntryId=loan.DisbursementJournalEntryId).delete()

            loan.delete()
        return JsonResponse("Employee Loan deleted successfully", safe=False)


@api_view(['GET'])
def EmployeeLoanByCompanyId(request, CompanyId=""):
    loans = EmployeeLoan.objects.filter(CompanyId=CompanyId).order_by('-SortId')
    enriched_loans = []

    for loan in loans:
        data = EmployeeLoanSerializer(loan).data
        if loan.Receipt and hasattr(loan.Receipt, 'name') and loan.Receipt.name:
            data['ReceiptUrl'] = format_media_url(loan.Receipt)
        else:
            data['ReceiptUrl'] = ""

        try:
            if loan.DisbursementAccountId:
                account = Account.objects.get(AccountId=loan.DisbursementAccountId)
                data['DisbursementAccountName'] = account.Name
                data['DisbursementAccountCode'] = account.Code
            else:
                data['DisbursementAccountName'] = ""
                data['DisbursementAccountCode'] = ""
        except Account.DoesNotExist:
            data['DisbursementAccountName'] = ""
            data['DisbursementAccountCode'] = ""

        try:
            if loan.StaffId:
                staff = Staff.objects.get(StaffId=loan.StaffId)
                data['StaffName'] = staff.StaffName or ""
                data['StaffDesignation'] = resolve_designation_name(staff.Designation)
                data['StaffEmail'] = staff.EmailId or ""
                data['StaffPhone'] = staff.PhoneNumber or ""
                data['StaffPhoto'] = format_media_url(staff.ProfilePhoto) if (staff.ProfilePhoto and hasattr(staff.ProfilePhoto, 'name') and staff.ProfilePhoto.name) else ""
            else:
                data['StaffName'] = ""
                data['StaffDesignation'] = ""
                data['StaffEmail'] = ""
                data['StaffPhone'] = ""
                data['StaffPhoto'] = ""
        except Staff.DoesNotExist:
            data['StaffName'] = ""
            data['StaffDesignation'] = ""
            data['StaffEmail'] = ""
            data['StaffPhone'] = ""
            data['StaffPhoto'] = ""

        repayments = EmployeeLoanRepayment.objects.filter(EmployeeLoanId=loan.EmployeeLoanId)
        data['RepaymentsCount'] = repayments.count()

        enriched_loans.append(data)

    return JsonResponse(enriched_loans, safe=False)


@api_view(['GET'])
def EmployeeLoanByStaffId(request, StaffId=""):
    loans = EmployeeLoan.objects.filter(StaffId=StaffId).order_by('-SortId')
    enriched_loans = []

    for loan in loans:
        data = EmployeeLoanSerializer(loan).data
        if loan.Receipt and hasattr(loan.Receipt, 'name') and loan.Receipt.name:
            data['ReceiptUrl'] = format_media_url(loan.Receipt)
        else:
            data['ReceiptUrl'] = ""

        try:
            if loan.DisbursementAccountId:
                account = Account.objects.get(AccountId=loan.DisbursementAccountId)
                data['DisbursementAccountName'] = account.Name
                data['DisbursementAccountCode'] = account.Code
            else:
                data['DisbursementAccountName'] = ""
                data['DisbursementAccountCode'] = ""
        except Account.DoesNotExist:
            data['DisbursementAccountName'] = ""
            data['DisbursementAccountCode'] = ""

        repayments = EmployeeLoanRepayment.objects.filter(EmployeeLoanId=loan.EmployeeLoanId).order_by('-SortId')
        repay_list = []
        for r in repayments:
            r_data = EmployeeLoanRepaymentSerializer(r).data
            if r.Receipt and hasattr(r.Receipt, 'name') and r.Receipt.name:
                r_data['ReceiptUrl'] = format_media_url(r.Receipt)
            else:
                r_data['ReceiptUrl'] = ""
            try:
                if r.PaymentAccountId:
                    acc = Account.objects.get(AccountId=r.PaymentAccountId)
                    r_data['PaymentAccountName'] = acc.Name
                    r_data['PaymentAccountCode'] = acc.Code
            except:
                r_data['PaymentAccountName'] = ""
                r_data['PaymentAccountCode'] = ""
            repay_list.append(r_data)

        data['Repayments'] = repay_list
        data['RepaymentsCount'] = len(repay_list)
        enriched_loans.append(data)

    return JsonResponse(enriched_loans, safe=False)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def EmployeeLoanUploadReceipt(request, EmployeeLoanId=""):
    try:
        loan = EmployeeLoan.objects.get(EmployeeLoanId=EmployeeLoanId)
    except EmployeeLoan.DoesNotExist:
        return JsonResponse("Employee Loan does not exist", safe=False, status=404)

    file_obj = request.FILES.get('Receipt')
    if not file_obj:
        return JsonResponse("No receipt file provided", safe=False, status=400)

    loan.Receipt = file_obj
    loan.save()
    return JsonResponse("Uploaded successfully", safe=False)


@api_view(['POST'])
def EmployeeLoanRepaymentApi(request):
    data = JSONParser().parse(request)
    loan_id = data.get('EmployeeLoanId')
    try:
        loan = EmployeeLoan.objects.get(EmployeeLoanId=loan_id)
    except EmployeeLoan.DoesNotExist:
        return JsonResponse("Employee Loan does not exist", safe=False, status=404)

    company_id = data.get('CompanyId') or loan.CompanyId
    data['CompanyId'] = company_id
    data['StaffId'] = loan.StaffId

    if not data.get('RepaymentNumber') and company_id:
        data['RepaymentNumber'] = generate_next_repayment_number(company_id)

    total_amount = float(data.get('Amount') or 0.0)
    principal_comp = float(data.get('PrincipalComponent') or 0.0)
    interest_comp = float(data.get('InterestComponent') or 0.0)

    if principal_comp == 0.0 and interest_comp == 0.0 and total_amount > 0.0:
        if loan.InterestType == 'interest_bearing' and float(loan.TotalInterest or 0) > 0:
            tot_payable = float(loan.TotalAmountPayable or loan.PrincipalAmount or 1.0)
            tot_int = float(loan.TotalInterest or 0.0)
            int_ratio = tot_int / tot_payable if tot_payable > 0 else 0.0
            interest_comp = total_amount * int_ratio
            principal_comp = total_amount - interest_comp
        else:
            principal_comp = total_amount
            interest_comp = 0.0

    data['PrincipalComponent'] = f"{principal_comp:.2f}"
    data['InterestComponent'] = f"{interest_comp:.2f}"

    serializer = EmployeeLoanRepaymentSerializer(data=data)
    if serializer.is_valid():
        repayment = serializer.save()
        post_loan_repayment_journal_entries(repayment, loan)
        repayment.save()
        recalculate_loan_balance(loan)
        return JsonResponse(repayment.RepaymentId, safe=False)
    return JsonResponse("Failed to record Repayment", safe=False, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
def EmployeeLoanRepaymentApiById(request, RepaymentId=""):
    try:
        repayment = EmployeeLoanRepayment.objects.get(RepaymentId=RepaymentId)
    except EmployeeLoanRepayment.DoesNotExist:
        return JsonResponse("Repayment does not exist", safe=False, status=404)

    try:
        loan = EmployeeLoan.objects.get(EmployeeLoanId=repayment.EmployeeLoanId)
    except EmployeeLoan.DoesNotExist:
        loan = None

    if request.method == 'GET':
        serializer = EmployeeLoanRepaymentSerializer(repayment)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = EmployeeLoanRepaymentSerializer(repayment, data=data, partial=True)
        if serializer.is_valid():
            repayment = serializer.save()
            if loan:
                post_loan_repayment_journal_entries(repayment, loan)
                recalculate_loan_balance(loan)
            return JsonResponse(repayment.RepaymentId, safe=False)
        return JsonResponse("Failed to update Repayment", safe=False, status=400)

    elif request.method == 'DELETE':
        with transaction.atomic():
            if repayment.JournalEntryId:
                JournalItem.objects.filter(JournalEntryId=repayment.JournalEntryId).delete()
                JournalEntry.objects.filter(JournalEntryId=repayment.JournalEntryId).delete()
            repayment.delete()
            if loan:
                recalculate_loan_balance(loan)
        return JsonResponse("Repayment deleted successfully", safe=False)


@api_view(['GET'])
def EmployeeLoanRepaymentsByLoanId(request, EmployeeLoanId=""):
    repayments = EmployeeLoanRepayment.objects.filter(EmployeeLoanId=EmployeeLoanId).order_by('-SortId')
    enriched = []
    for r in repayments:
        data = EmployeeLoanRepaymentSerializer(r).data
        if r.Receipt and hasattr(r.Receipt, 'name') and r.Receipt.name:
            data['ReceiptUrl'] = format_media_url(r.Receipt)
        else:
            data['ReceiptUrl'] = ""

        try:
            if r.PaymentAccountId:
                account = Account.objects.get(AccountId=r.PaymentAccountId)
                data['PaymentAccountName'] = account.Name
                data['PaymentAccountCode'] = account.Code
            else:
                data['PaymentAccountName'] = ""
                data['PaymentAccountCode'] = ""
        except Account.DoesNotExist:
            data['PaymentAccountName'] = ""
            data['PaymentAccountCode'] = ""

        try:
            if r.StaffId:
                staff = Staff.objects.get(StaffId=r.StaffId)
                data['StaffName'] = staff.StaffName or ""
            else:
                data['StaffName'] = ""
        except Staff.DoesNotExist:
            data['StaffName'] = ""

        enriched.append(data)

    return JsonResponse(enriched, safe=False)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def EmployeeLoanRepaymentUploadReceipt(request, RepaymentId=""):
    try:
        repay = EmployeeLoanRepayment.objects.get(RepaymentId=RepaymentId)
    except EmployeeLoanRepayment.DoesNotExist:
        return JsonResponse("Repayment does not exist", safe=False, status=404)

    file_obj = request.FILES.get('Receipt')
    if not file_obj:
        return JsonResponse("No receipt file provided", safe=False, status=400)

    repay.Receipt = file_obj
    repay.save()
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


# ==========================================
# SALARY / PAYROLL PROCESSING ENDPOINTS
# ==========================================

def rollback_payroll_entry(payroll_entry):
    if not payroll_entry:
        return
    with transaction.atomic():
        # 1. Rollback and delete loan repayments
        if payroll_entry.RepaymentIds:
            repay_ids = [r.strip() for r in payroll_entry.RepaymentIds.split(',') if r.strip()]
            for r_id in repay_ids:
                repay = EmployeeLoanRepayment.objects.filter(RepaymentId=r_id).first()
                if repay:
                    if repay.EmployeeLoanId:
                        loan = EmployeeLoan.objects.filter(EmployeeLoanId=repay.EmployeeLoanId).first()
                        if loan:
                            repaid_amount = safe_float(repay.PrincipalComponent or repay.Amount)
                            new_total_repaid = max(0.0, safe_float(loan.TotalRepaid) - repaid_amount)
                            new_outstanding = safe_float(loan.OutstandingBalance) + repaid_amount
                            loan.TotalRepaid = f"{new_total_repaid:.2f}"
                            loan.OutstandingBalance = f"{new_outstanding:.2f}"
                            loan.Status = 'Active'
                            loan.save()
                    repay.delete()

        # 2. Rollback and delete journal entry and items
        if payroll_entry.JournalEntryId:
            JournalItem.objects.filter(JournalEntryId=payroll_entry.JournalEntryId).delete()
            JournalEntry.objects.filter(JournalEntryId=payroll_entry.JournalEntryId).delete()

        if payroll_entry.ReferenceNumber:
            entries = JournalEntry.objects.filter(
                ReferenceNumber=payroll_entry.ReferenceNumber,
                Source='payroll_salary',
                CompanyId=payroll_entry.CompanyId
            )
            for e in entries:
                JournalItem.objects.filter(JournalEntryId=e.JournalEntryId).delete()
                e.delete()


@api_view(['GET'])
def SalaryOverview(request, CompanyId=""):
    company_id = CompanyId or request.GET.get('CompanyId') or request.query_params.get('CompanyId', '')
    month_val = request.GET.get('Month') or request.query_params.get('Month')
    year_val = request.GET.get('Year') or request.query_params.get('Year')

    now = datetime.now()
    default_month = 12 if now.month == 1 else now.month - 1
    default_year = now.year - 1 if now.month == 1 else now.year

    try:
        month = int(month_val) if month_val else default_month
    except:
        month = default_month

    try:
        year = int(year_val) if year_val else default_year
    except:
        year = default_year

    staff_query = Staff.objects.filter(Status=1)
    if company_id:
        staff_query = staff_query.filter(CompanyId=company_id)
    staff_list = staff_query.order_by('StaffName')

    payroll_entries = PayrollEntry.objects.filter(
        PayrollMonth=month,
        PayrollYear=year
    )
    if company_id:
        payroll_entries = payroll_entries.filter(CompanyId=company_id)
    payroll_map = {p.StaffId: p for p in payroll_entries}
    legacy_slips = SalarySlip.objects.filter(Year=year, Month=month, StaffId__in=[st.StaffId for st in staff_list])
    legacy_slip_map = {s.StaffId: s for s in legacy_slips}

    from app_accounting.signals import get_or_create_default_accounts
    if company_id:
        get_or_create_default_accounts(company_id)
    bank_accounts = Account.objects.filter(IsCashOrBank=True)
    if company_id:
        bank_accounts = bank_accounts.filter(CompanyId=company_id)
    bank_account_list = AccountSerializer(bank_accounts, many=True).data

    overview_rows = []
    total_gross = 0.0
    total_deductions = 0.0
    total_net = 0.0
    processed_count = 0
    pending_count = 0

    desig_map = get_designation_map()

    for staff in staff_list:
        p_entry = payroll_map.get(staff.StaffId)
        s_slip = legacy_slip_map.get(staff.StaffId)

        active_loans = EmployeeLoan.objects.filter(
            StaffId=staff.StaffId,
            Status='Active'
        )
        if company_id:
            active_loans = active_loans.filter(CompanyId=company_id)

        loan_details = []
        total_loan_outstanding = 0.0
        suggested_loan_deduction = 0.0

        for loan in active_loans:
            out_bal = safe_float(loan.OutstandingBalance)
            inst_amt = safe_float(loan.InstallmentAmount)
            total_loan_outstanding += out_bal
            if loan.RepaymentType == 'installment' and inst_amt > 0:
                suggested_loan_deduction += min(inst_amt, out_bal)
            else:
                suggested_loan_deduction += out_bal

            loan_details.append({
                'EmployeeLoanId': loan.EmployeeLoanId,
                'LoanNumber': loan.LoanNumber or '',
                'PrincipalAmount': loan.PrincipalAmount or '0.00',
                'OutstandingBalance': loan.OutstandingBalance or '0.00',
                'InstallmentAmount': loan.InstallmentAmount or '0.00',
                'RepaymentType': loan.RepaymentType or 'flexible'
            })

        base_salary = safe_float(staff.Salary)

        if p_entry:
            processed_count += 1
            gross = safe_float(p_entry.GrossSalary)
            deduction = safe_float(p_entry.AdvanceDeduction)
            net = safe_float(p_entry.NetSalary)
            status = p_entry.Status or 'Paid'
            payment_date = p_entry.PaymentDate or ''
            payment_account_id = p_entry.PaymentAccountId or ''
            payment_mode = p_entry.PaymentMode or 'Bank Transfer'
            ref_num = p_entry.ReferenceNumber or ''
            payroll_id = p_entry.PayrollId
            narration = p_entry.Narration or ''
        elif s_slip:
            processed_count += 1
            gross = safe_float(s_slip.GrossPay or s_slip.BasicPay)
            deduction = 0.0
            net = gross
            status = 'Paid'
            payment_date = s_slip.SortId.strftime('%Y-%m-%d') if s_slip.SortId else f"{year}-{month:02d}-01"
            payment_account_id = ''
            payment_mode = 'Bank Transfer'
            ref_num = f"SLIP-{year}{month:02d}-{staff.StaffCode}" if staff.StaffCode else f"SLIP-{year}{month:02d}"
            payroll_id = s_slip.SalarySlipId
            narration = f"Salary Slip for {calendar.month_name[month]} {year}"
        else:
            pending_count += 1
            gross = base_salary
            deduction = min(suggested_loan_deduction, gross)
            net = max(0.0, gross - deduction)
            status = 'Pending'
            payment_date = now.strftime('%Y-%m-%d')
            payment_account_id = bank_accounts.first().AccountId if bank_accounts.exists() else ''
            payment_mode = 'Bank Transfer'
            ref_num = f"SAL-{year}{month:02d}-{staff.StaffCode}" if staff.StaffCode else f"SAL-{year}{month:02d}"
            payroll_id = ''
            narration = f"Salary for {calendar.month_name[month]} {year}"

        total_gross += gross
        total_deductions += deduction
        total_net += net

        photo_url = format_media_url(staff.ProfilePhoto) if hasattr(staff, 'ProfilePhoto') else ''

        overview_rows.append({
            'StaffId': staff.StaffId,
            'StaffCode': staff.StaffCode or '',
            'StaffName': staff.StaffName or '',
            'Designation': resolve_designation_name(staff.Designation, desig_map),
            'ProfilePhoto': photo_url,
            'BankAccount': staff.BankAccount or '',
            'BaseSalary': f"{base_salary:.2f}",
            'GrossSalary': f"{gross:.2f}",
            'OutstandingLoanBalance': f"{total_loan_outstanding:.2f}",
            'SuggestedDeduction': f"{suggested_loan_deduction:.2f}",
            'AdvanceDeduction': f"{deduction:.2f}",
            'NetSalary': f"{net:.2f}",
            'ActiveLoans': loan_details,
            'Status': status,
            'PaymentDate': payment_date,
            'PaymentAccountId': payment_account_id,
            'PaymentMode': payment_mode,
            'ReferenceNumber': ref_num,
            'PayrollId': payroll_id,
            'Narration': narration
        })

    return JsonResponse({
        'Month': month,
        'Year': year,
        'MonthName': calendar.month_name[month],
        'CompanyId': company_id,
        'BankAccounts': bank_account_list,
        'Summary': {
            'TotalStaffCount': len(staff_list),
            'ProcessedCount': processed_count,
            'PendingCount': pending_count,
            'TotalGross': f"{total_gross:.2f}",
            'TotalAdvanceDeduction': f"{total_deductions:.2f}",
            'TotalNetPayout': f"{total_net:.2f}"
        },
        'StaffList': overview_rows
    }, safe=False)


@api_view(['GET', 'POST'])
def PayrollApi(request):
    if request.method == 'GET':
        company_id = request.GET.get('CompanyId') or request.query_params.get('CompanyId')
        month = request.GET.get('Month') or request.query_params.get('Month')
        year = request.GET.get('Year') or request.query_params.get('Year')

        entries = PayrollEntry.objects.all().order_by('-SortId')
        if company_id:
            entries = entries.filter(CompanyId=company_id)
        if month:
            entries = entries.filter(PayrollMonth=int(month))
        if year:
            entries = entries.filter(PayrollYear=int(year))

        serializer = PayrollEntrySerializer(entries, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        company_id = data.get('CompanyId', '')
        month = int(data.get('Month', datetime.now().month))
        year = int(data.get('Year', datetime.now().year))
        payment_date = data.get('PaymentDate') or datetime.now().strftime('%Y-%m-%d')
        default_account_id = data.get('PaymentAccountId', '')
        default_mode = data.get('PaymentMode', 'Bank Transfer')

        # Check if batch items or single item
        staff_items = data.get('StaffList')
        if not staff_items:
            # Single item POST
            staff_items = [{
                'StaffId': data.get('StaffId'),
                'GrossSalary': data.get('GrossSalary'),
                'AdvanceDeduction': data.get('AdvanceDeduction'),
                'NetSalary': data.get('NetSalary'),
                'PaymentAccountId': data.get('PaymentAccountId') or default_account_id,
                'PaymentMode': data.get('PaymentMode') or default_mode,
                'PaymentDate': data.get('PaymentDate') or payment_date,
                'Narration': data.get('Narration', '')
            }]

        from app_accounting.signals import get_or_create_default_accounts
        accounts = get_or_create_default_accounts(company_id) if company_id else {}
        salary_expense_acc = accounts.get('6010')
        if not salary_expense_acc and company_id:
            salary_expense_acc, _ = Account.objects.get_or_create(
                Code='6010',
                CompanyId=company_id,
                defaults={'Name': 'Salaries Expense', 'Type': 'Expense', 'IsCashOrBank': False}
            )

        loan_asset_acc = accounts.get('1300')
        if not loan_asset_acc and company_id:
            loan_asset_acc, _ = Account.objects.get_or_create(
                Code='1300',
                CompanyId=company_id,
                defaults={'Name': 'Employee Loans & Advances', 'Type': 'Asset', 'IsCashOrBank': False}
            )

        processed_entries = []

        with transaction.atomic():
            for item in staff_items:
                staff_id = item.get('StaffId')
                if not staff_id:
                    continue

                staff = Staff.objects.filter(StaffId=staff_id).first()
                if not staff:
                    continue

                staff_code = staff.StaffCode or staff.StaffId[:6]
                gross_salary = safe_float(item.get('GrossSalary', staff.Salary))
                advance_deduction = safe_float(item.get('AdvanceDeduction', 0.0))
                net_salary = safe_float(item.get('NetSalary', gross_salary - advance_deduction))
                item_pay_acc = item.get('PaymentAccountId') or default_account_id
                item_pay_mode = item.get('PaymentMode') or default_mode
                item_pay_date = item.get('PaymentDate') or payment_date
                item_narration = item.get('Narration') or f"Salary for {calendar.month_name[month]} {year} - {staff.StaffName}"
                ref_num = f"SAL-{year}{month:02d}-{staff_code}"

                # 1. Rollback previous entry if exists
                existing_entry = PayrollEntry.objects.filter(
                    CompanyId=company_id,
                    StaffId=staff_id,
                    PayrollMonth=month,
                    PayrollYear=year
                ).first()
                if existing_entry:
                    rollback_payroll_entry(existing_entry)
                    existing_entry.delete()

                # 2. Process advance deduction against active loans
                repayment_ids = []
                if advance_deduction > 0:
                    active_loans = EmployeeLoan.objects.filter(
                        StaffId=staff_id,
                        Status='Active'
                    )
                    if company_id:
                        active_loans = active_loans.filter(CompanyId=company_id)
                    active_loans = active_loans.order_by('SortId')

                    remaining_deduction = advance_deduction
                    for loan in active_loans:
                        if remaining_deduction <= 0:
                            break
                        loan_outstanding = safe_float(loan.OutstandingBalance)
                        if loan_outstanding <= 0:
                            continue

                        deduct_for_this_loan = min(remaining_deduction, loan_outstanding)
                        repay_num = generate_next_repayment_number(company_id) if company_id else f"LRP-{datetime.now().strftime('%Y%m%d%H%M%S')}"

                        repayment = EmployeeLoanRepayment.objects.create(
                            RepaymentNumber=repay_num,
                            EmployeeLoanId=loan.EmployeeLoanId,
                            StaffId=staff_id,
                            CompanyId=company_id,
                            RepaymentDate=item_pay_date,
                            PaymentAccountId=item_pay_acc,
                            Amount=f"{deduct_for_this_loan:.2f}",
                            PrincipalComponent=f"{deduct_for_this_loan:.2f}",
                            InterestComponent="0.00",
                            PaymentMode='Salary Deduction',
                            ReferenceNumber=ref_num,
                            Narration=f"Salary Deduction for {calendar.month_name[month]} {year}"
                        )
                        repayment_ids.append(str(repayment.RepaymentId))

                        new_total_repaid = safe_float(loan.TotalRepaid) + deduct_for_this_loan
                        new_outstanding = max(0.0, loan_outstanding - deduct_for_this_loan)
                        loan.TotalRepaid = f"{new_total_repaid:.2f}"
                        loan.OutstandingBalance = f"{new_outstanding:.2f}"
                        if new_outstanding <= 0.001:
                            loan.Status = 'Closed'
                        loan.save()

                        remaining_deduction -= deduct_for_this_loan

                # 3. Create Double-Entry Journal Entry
                journal_entry = JournalEntry.objects.create(
                    Date=item_pay_date,
                    ReferenceNumber=ref_num,
                    Source='payroll_salary',
                    Narration=item_narration,
                    CompanyId=company_id
                )

                # Leg 1: Debit Salaries Expense (6010) with Gross Salary
                if salary_expense_acc:
                    JournalItem.objects.create(
                        JournalEntryId=str(journal_entry.JournalEntryId),
                        AccountId=salary_expense_acc.AccountId,
                        Debit=f"{gross_salary:.2f}",
                        Credit="0.00",
                        StaffId=staff_id
                    )

                # Leg 2: Credit Employee Loans & Advances (1300) with Advance Deduction
                if advance_deduction > 0 and loan_asset_acc:
                    JournalItem.objects.create(
                        JournalEntryId=str(journal_entry.JournalEntryId),
                        AccountId=loan_asset_acc.AccountId,
                        Debit="0.00",
                        Credit=f"{advance_deduction:.2f}",
                        StaffId=staff_id
                    )

                # Leg 3: Credit Bank/Cash Account with Net Salary
                if net_salary > 0 and item_pay_acc:
                    JournalItem.objects.create(
                        JournalEntryId=str(journal_entry.JournalEntryId),
                        AccountId=item_pay_acc,
                        Debit="0.00",
                        Credit=f"{net_salary:.2f}",
                        StaffId=staff_id
                    )

                # 4. Create PayrollEntry Record
                payroll_entry = PayrollEntry.objects.create(
                    CompanyId=company_id,
                    StaffId=staff_id,
                    PayrollMonth=month,
                    PayrollYear=year,
                    PaymentDate=item_pay_date,
                    GrossSalary=f"{gross_salary:.2f}",
                    AdvanceDeduction=f"{advance_deduction:.2f}",
                    NetSalary=f"{net_salary:.2f}",
                    PaymentAccountId=item_pay_acc,
                    PaymentMode=item_pay_mode,
                    ReferenceNumber=ref_num,
                    JournalEntryId=str(journal_entry.JournalEntryId),
                    RepaymentIds=",".join([str(r) for r in repayment_ids]),
                    Status='Paid',
                    Narration=item_narration
                )

                processed_entries.append(str(payroll_entry.PayrollId))

        return JsonResponse({
            'Status': 'Success',
            'Message': f"Processed salary for {len(processed_entries)} staff member(s)",
            'PayrollIds': processed_entries
        }, safe=False)


@api_view(['GET', 'DELETE'])
def PayrollApiById(request, PayrollId=""):
    try:
        entry = PayrollEntry.objects.get(PayrollId=PayrollId)
        is_legacy = False
    except PayrollEntry.DoesNotExist:
        try:
            entry = SalarySlip.objects.get(SalarySlipId=PayrollId)
            is_legacy = True
        except SalarySlip.DoesNotExist:
            return JsonResponse("Payroll entry not found", safe=False, status=404)

    if request.method == 'GET':
        if not is_legacy:
            serializer = PayrollEntrySerializer(entry)
            data = serializer.data
            if entry.StaffId:
                staff = Staff.objects.filter(StaffId=entry.StaffId).first()
                if staff:
                    data['StaffName'] = staff.StaffName or ''
                    data['StaffCode'] = staff.StaffCode or ''
                    data['Designation'] = resolve_designation_name(staff.Designation)
                    data['ProfilePhoto'] = format_media_url(staff.ProfilePhoto) if hasattr(staff, 'ProfilePhoto') else ''
                    data['BankAccount'] = staff.BankAccount or ''
            data['MonthName'] = calendar.month_name[entry.PayrollMonth] if 1 <= entry.PayrollMonth <= 12 else ''
            data['PeriodDisplay'] = f"{data['MonthName']} {entry.PayrollYear}"
            return JsonResponse(data, safe=False)
        else:
            staff = Staff.objects.filter(StaffId=entry.StaffId).first()
            m_name = calendar.month_name[entry.Month] if 1 <= entry.Month <= 12 else ''
            gross_val = safe_float(entry.GrossPay or entry.BasicPay)
            pay_date = entry.SortId.strftime('%Y-%m-%d') if entry.SortId else f"{entry.Year}-{entry.Month:02d}-01"
            data = {
                'PayrollId': entry.SalarySlipId,
                'StaffId': entry.StaffId,
                'StaffName': staff.StaffName if staff else '',
                'StaffCode': staff.StaffCode if staff else '',
                'Designation': resolve_designation_name(staff.Designation) if staff else '',
                'ProfilePhoto': format_media_url(staff.ProfilePhoto) if (staff and hasattr(staff, 'ProfilePhoto')) else '',
                'BankAccount': entry.BankAccount or (staff.BankAccount if staff else ''),
                'PayrollMonth': entry.Month,
                'PayrollYear': entry.Year,
                'MonthName': m_name,
                'PeriodDisplay': f"{m_name} {entry.Year}",
                'GrossSalary': f"{gross_val:.2f}",
                'AdvanceDeduction': '0.00',
                'NetSalary': f"{gross_val:.2f}",
                'PaymentDate': pay_date,
                'PaymentAccountId': '',
                'PaymentAccountName': '',
                'PaymentAccountCode': '',
                'PaymentMode': 'Bank Transfer',
                'ReferenceNumber': f"SLIP-{entry.Year}{entry.Month:02d}-{staff.StaffCode}" if (staff and staff.StaffCode) else f"SLIP-{entry.Year}{entry.Month:02d}",
                'Status': 'Paid',
                'Narration': f"Salary Slip for {m_name} {entry.Year}",
                'ReceiptUrl': '',
                'IsLegacySlip': True,
                'BasicPay': f"{safe_float(entry.BasicPay):.2f}",
                'ConveyanceAllowance': f"{safe_float(entry.ConveyanceAllowance):.2f}",
                'MedicalAllowance': f"{safe_float(entry.MedicalAllowance):.2f}",
                'OtherAllowance': f"{safe_float(entry.OtherAllowance):.2f}",
                'AppreciationBonus': f"{safe_float(entry.AppreciationBonus):.2f}",
                'TotalWorkingDays': entry.TotalWorkingDays or 0,
                'PaidDays': safe_float(entry.PaidDays or 0),
                'LOP': safe_float(entry.LOP or 0),
            }
            return JsonResponse(data, safe=False)

    elif request.method == 'DELETE':
        with transaction.atomic():
            if not is_legacy:
                rollback_payroll_entry(entry)
                entry.delete()
            else:
                entry.delete()
        return JsonResponse("Payroll entry rolled back and deleted successfully", safe=False)


@api_view(['GET'])
def PayrollByCompanyId(request, CompanyId=""):
    company_id = CompanyId or request.GET.get('CompanyId') or request.query_params.get('CompanyId', '')
    period_type = (request.GET.get('PeriodType') or request.query_params.get('PeriodType') or 'month').lower()
    month_val = request.GET.get('Month') or request.query_params.get('Month')
    quarter_val = request.GET.get('Quarter') or request.query_params.get('Quarter')
    half_val = request.GET.get('HalfYear') or request.query_params.get('HalfYear')
    year_val = request.GET.get('Year') or request.query_params.get('Year')
    staff_id = request.GET.get('StaffId') or request.query_params.get('StaffId')

    now = datetime.now()
    default_month = 12 if now.month == 1 else now.month - 1
    default_year = now.year - 1 if now.month == 1 else now.year

    try:
        year = int(year_val) if year_val else default_year
    except:
        year = default_year

    try:
        month = int(month_val) if month_val else default_month
    except:
        month = default_month

    try:
        quarter = int(quarter_val) if quarter_val else ((month - 1) // 3 + 1)
    except:
        quarter = 1

    try:
        half_year = int(half_val) if half_val else (1 if month <= 6 else 2)
    except:
        half_year = 1

    entries = PayrollEntry.objects.filter(CompanyId=company_id).order_by('-PayrollYear', '-PayrollMonth', '-SortId')

    staff_query = Staff.objects.all()
    if company_id:
        staff_query = staff_query.filter(CompanyId=company_id)
    company_staff_ids = [s.StaffId for s in staff_query]

    slips = SalarySlip.objects.filter(StaffId__in=company_staff_ids).order_by('-Year', '-Month', '-SortId')

    if period_type in ['month', 'monthly']:
        entries = entries.filter(PayrollYear=year, PayrollMonth=month)
        slips = slips.filter(Year=year, Month=month)
        period_label = f"{calendar.month_name[month]} {year}"
    elif period_type in ['quarter', 'quarterly']:
        q_map = {1: [1, 2, 3], 2: [4, 5, 6], 3: [7, 8, 9], 4: [10, 11, 12]}
        months = q_map.get(quarter, [1, 2, 3])
        entries = entries.filter(PayrollYear=year, PayrollMonth__in=months)
        slips = slips.filter(Year=year, Month__in=months)
        period_label = f"Quarter {quarter} ({calendar.month_abbr[months[0]]} - {calendar.month_abbr[months[-1]]}) {year}"
    elif period_type in ['half_year', 'half', 'half_yearly']:
        h_map = {1: [1, 2, 3, 4, 5, 6], 2: [7, 8, 9, 10, 11, 12]}
        months = h_map.get(half_year, [1, 2, 3, 4, 5, 6])
        entries = entries.filter(PayrollYear=year, PayrollMonth__in=months)
        slips = slips.filter(Year=year, Month__in=months)
        period_label = f"Half Year {half_year} ({calendar.month_abbr[months[0]]} - {calendar.month_abbr[months[-1]]}) {year}"
    elif period_type in ['full_year', 'year', 'yearly']:
        entries = entries.filter(PayrollYear=year)
        slips = slips.filter(Year=year)
        period_label = f"Full Year {year}"
    else:
        period_label = "All Processed Salaries"

    if staff_id:
        entries = entries.filter(StaffId=staff_id)
        slips = slips.filter(StaffId=staff_id)

    staff_dict = {s.StaffId: s for s in Staff.objects.all()}
    desig_map = get_designation_map()
    acc_dict = {a.AccountId: a for a in Account.objects.filter(CompanyId=company_id)}

    results = []
    total_gross = 0.0
    total_ded = 0.0
    total_net = 0.0

    existing_keys = set((e.StaffId, e.PayrollYear, e.PayrollMonth) for e in entries)

    for entry in entries:
        d = PayrollEntrySerializer(entry).data
        st = staff_dict.get(entry.StaffId)
        if st:
            d['StaffName'] = st.StaffName or ''
            d['StaffCode'] = st.StaffCode or ''
            d['Designation'] = resolve_designation_name(st.Designation, desig_map)
            d['ProfilePhoto'] = format_media_url(st.ProfilePhoto) if hasattr(st, 'ProfilePhoto') else ''
            d['BankAccount'] = st.BankAccount or ''

        acc = acc_dict.get(entry.PaymentAccountId)
        if acc:
            d['PaymentAccountName'] = acc.Name or ''
            d['PaymentAccountCode'] = acc.Code or ''

        d['MonthName'] = calendar.month_name[entry.PayrollMonth] if 1 <= entry.PayrollMonth <= 12 else ''
        d['PeriodDisplay'] = f"{d['MonthName']} {entry.PayrollYear}"
        d['ReceiptUrl'] = format_media_url(entry.Receipt) if hasattr(entry, 'Receipt') else ''
        d['IsLegacySlip'] = False

        gross_val = safe_float(entry.GrossSalary)
        ded_val = safe_float(entry.AdvanceDeduction)
        net_val = safe_float(entry.NetSalary)

        total_gross += gross_val
        total_ded += ded_val
        total_net += net_val

        results.append(d)

    for s_slip in slips:
        if (s_slip.StaffId, s_slip.Year, s_slip.Month) not in existing_keys:
            st = staff_dict.get(s_slip.StaffId)
            gross_val = safe_float(s_slip.GrossPay or s_slip.BasicPay)
            ded_val = 0.0
            net_val = gross_val
            m_name = calendar.month_name[s_slip.Month] if 1 <= s_slip.Month <= 12 else ''
            pay_date = s_slip.SortId.strftime('%Y-%m-%d') if s_slip.SortId else f"{s_slip.Year}-{s_slip.Month:02d}-01"

            results.append({
                'PayrollId': s_slip.SalarySlipId,
                'CompanyId': company_id,
                'StaffId': s_slip.StaffId,
                'StaffName': st.StaffName if st else '',
                'StaffCode': st.StaffCode if st else '',
                'Designation': resolve_designation_name(st.Designation, desig_map) if st else '',
                'ProfilePhoto': format_media_url(st.ProfilePhoto) if (st and hasattr(st, 'ProfilePhoto')) else '',
                'BankAccount': s_slip.BankAccount or (st.BankAccount if st else ''),
                'PayrollMonth': s_slip.Month,
                'PayrollYear': s_slip.Year,
                'MonthName': m_name,
                'PeriodDisplay': f"{m_name} {s_slip.Year}",
                'GrossSalary': f"{gross_val:.2f}",
                'AdvanceDeduction': '0.00',
                'NetSalary': f"{net_val:.2f}",
                'PaymentDate': pay_date,
                'PaymentAccountId': '',
                'PaymentAccountName': '',
                'PaymentAccountCode': '',
                'PaymentMode': 'Bank Transfer',
                'ReferenceNumber': f"SLIP-{s_slip.Year}{s_slip.Month:02d}-{st.StaffCode}" if (st and st.StaffCode) else f"SLIP-{s_slip.Year}{s_slip.Month:02d}",
                'Status': 'Paid',
                'Narration': f"Salary Slip for {m_name} {s_slip.Year}",
                'ReceiptUrl': '',
                'IsLegacySlip': True,
                'BasicPay': f"{safe_float(s_slip.BasicPay):.2f}",
                'ConveyanceAllowance': f"{safe_float(s_slip.ConveyanceAllowance):.2f}",
                'MedicalAllowance': f"{safe_float(s_slip.MedicalAllowance):.2f}",
                'OtherAllowance': f"{safe_float(s_slip.OtherAllowance):.2f}",
                'AppreciationBonus': f"{safe_float(s_slip.AppreciationBonus):.2f}",
                'TotalWorkingDays': s_slip.TotalWorkingDays or 0,
                'PaidDays': safe_float(s_slip.PaidDays or 0),
                'LOP': safe_float(s_slip.LOP or 0),
            })
            total_gross += gross_val
            total_ded += ded_val
            total_net += net_val

    results.sort(key=lambda x: (int(x.get('PayrollYear') or 0), int(x.get('PayrollMonth') or 0), str(x.get('PaymentDate') or '')), reverse=True)

    return JsonResponse({
        'PeriodType': period_type,
        'PeriodLabel': period_label,
        'Year': year,
        'Month': month,
        'Quarter': quarter,
        'HalfYear': half_year,
        'Summary': {
            'TotalCount': len(results),
            'TotalGross': f"{total_gross:.2f}",
            'TotalAdvanceDeduction': f"{total_ded:.2f}",
            'TotalNetPayout': f"{total_net:.2f}"
        },
        'Results': results
    }, safe=False)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def PayrollUploadReceipt(request, PayrollId=""):
    try:
        entry = PayrollEntry.objects.get(PayrollId=PayrollId)
    except PayrollEntry.DoesNotExist:
        return JsonResponse("Payroll entry not found", safe=False, status=404)

    receipt_file = request.FILES.get('Receipt')
    if not receipt_file:
        return JsonResponse("No receipt file provided", safe=False, status=400)

    entry.Receipt = receipt_file
    entry.save()
    return JsonResponse({'Status': 'Success', 'ReceiptUrl': format_media_url(entry.Receipt)}, safe=False)


@api_view(['GET'])
def ExportPayrollSheet(request, CompanyId=""):
    period_type = (request.GET.get('PeriodType') or request.query_params.get('PeriodType') or 'month').lower()
    month_val = request.GET.get('Month') or request.query_params.get('Month')
    quarter_val = request.GET.get('Quarter') or request.query_params.get('Quarter')
    half_val = request.GET.get('HalfYear') or request.query_params.get('HalfYear')
    year_val = request.GET.get('Year') or request.query_params.get('Year')
    staff_id = request.GET.get('StaffId') or request.query_params.get('StaffId')

    now = datetime.now()
    try:
        year = int(year_val) if year_val else now.year
    except:
        year = now.year

    try:
        month = int(month_val) if month_val else now.month
    except:
        month = now.month

    try:
        quarter = int(quarter_val) if quarter_val else ((month - 1) // 3 + 1)
    except:
        quarter = 1

    try:
        half_year = int(half_val) if half_val else (1 if month <= 6 else 2)
    except:
        half_year = 1

    payroll_entries = PayrollEntry.objects.filter(CompanyId=CompanyId).order_by('PayrollYear', 'PayrollMonth', 'SortId')

    staff_query = Staff.objects.all()
    if CompanyId:
        staff_query = staff_query.filter(CompanyId=CompanyId)
    company_staff_ids = [s.StaffId for s in staff_query]

    slips = SalarySlip.objects.filter(StaffId__in=company_staff_ids).order_by('Year', 'Month', 'SortId')

    if period_type in ['month', 'monthly']:
        payroll_entries = payroll_entries.filter(PayrollYear=year, PayrollMonth=month)
        slips = slips.filter(Year=year, Month=month)
        period_label = f"{calendar.month_name[month]} {year}"
        filename = f"Payroll_Sheet_{calendar.month_name[month]}_{year}"
    elif period_type in ['quarter', 'quarterly']:
        q_map = {1: [1, 2, 3], 2: [4, 5, 6], 3: [7, 8, 9], 4: [10, 11, 12]}
        months = q_map.get(quarter, [1, 2, 3])
        payroll_entries = payroll_entries.filter(PayrollYear=year, PayrollMonth__in=months)
        slips = slips.filter(Year=year, Month__in=months)
        period_label = f"Quarter {quarter} ({calendar.month_abbr[months[0]]} - {calendar.month_abbr[months[-1]]}) {year}"
        filename = f"Payroll_Sheet_Q{quarter}_{year}"
    elif period_type in ['half_year', 'half', 'half_yearly']:
        h_map = {1: [1, 2, 3, 4, 5, 6], 2: [7, 8, 9, 10, 11, 12]}
        months = h_map.get(half_year, [1, 2, 3, 4, 5, 6])
        payroll_entries = payroll_entries.filter(PayrollYear=year, PayrollMonth__in=months)
        slips = slips.filter(Year=year, Month__in=months)
        period_label = f"Half Year {half_year} ({calendar.month_abbr[months[0]]} - {calendar.month_abbr[months[-1]]}) {year}"
        filename = f"Payroll_Sheet_H{half_year}_{year}"
    elif period_type in ['full_year', 'year', 'yearly']:
        payroll_entries = payroll_entries.filter(PayrollYear=year)
        slips = slips.filter(Year=year)
        period_label = f"Full Year {year}"
        filename = f"Payroll_Sheet_FullYear_{year}"
    else:
        period_label = "All Processed Salaries"
        filename = f"Payroll_Sheet_All_{year}"

    if staff_id:
        payroll_entries = payroll_entries.filter(StaffId=staff_id)
        slips = slips.filter(StaffId=staff_id)

    staff_dict = {s.StaffId: s for s in Staff.objects.all()}
    desig_map = get_designation_map()
    acc_dict = {a.AccountId: a for a in Account.objects.filter(CompanyId=CompanyId)}

    company_name = "Company Payroll"
    try:
        from app_company.models import Company
        comp = Company.objects.filter(CompanyId=CompanyId).first()
        if comp and comp.CompanyName:
            company_name = comp.CompanyName
    except:
        pass

    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from django.http import HttpResponse

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Payroll Sheet"

    title_font = Font(name="Arial", size=16, bold=True, color="1E3A8A")
    subtitle_font = Font(name="Arial", size=11, italic=True, color="4B5563")
    header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
    bold_font = Font(name="Arial", size=11, bold=True)
    regular_font = Font(name="Arial", size=10)

    header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    summary_fill = PatternFill(start_color="F3F4F6", end_color="F3F4F6", fill_type="solid")

    ws.merge_cells("A1:I1")
    ws["A1"] = company_name
    ws["A1"].font = title_font
    ws["A1"].alignment = Alignment(horizontal="center")

    ws.merge_cells("A2:I2")
    ws["A2"] = f"Salary Sheet &mdash; {period_label}"
    ws["A2"].font = subtitle_font
    ws["A2"].alignment = Alignment(horizontal="center")

    ws.append([])

    headers = ["#", "Period", "Staff Code", "Staff Name", "Designation", "Payment Date", "Gross Salary (₹)", "Advance Deduction (₹)", "Net Payout (₹)"]
    ws.append(headers)
    header_row = 4
    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=header_row, column=col_idx)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="left" if col_idx <= 6 else "right")

    tot_gross = 0.0
    tot_ded = 0.0
    tot_net = 0.0

    existing_keys = set((e.StaffId, e.PayrollYear, e.PayrollMonth) for e in payroll_entries)

    export_rows = []
    for entry in payroll_entries:
        st = staff_dict.get(entry.StaffId)
        st_name = st.StaffName if st else "Staff"
        st_code = st.StaffCode if st else ""
        st_desig = resolve_designation_name(st.Designation, desig_map) if st else ""

        g = safe_float(entry.GrossSalary)
        d = safe_float(entry.AdvanceDeduction)
        n = safe_float(entry.NetSalary)

        m_name = calendar.month_abbr[entry.PayrollMonth] if 1 <= entry.PayrollMonth <= 12 else ''
        p_str = f"{m_name} {entry.PayrollYear}"

        export_rows.append({
            'Year': entry.PayrollYear,
            'Month': entry.PayrollMonth,
            'Date': entry.PaymentDate,
            'Data': [p_str, st_code, st_name, st_desig, entry.PaymentDate, g, d, n],
            'g': g, 'd': d, 'n': n
        })

    for s_slip in slips:
        if (s_slip.StaffId, s_slip.Year, s_slip.Month) not in existing_keys:
            st = staff_dict.get(s_slip.StaffId)
            st_name = st.StaffName if st else "Staff"
            st_code = st.StaffCode if st else ""
            st_desig = resolve_designation_name(st.Designation, desig_map) if st else ""

            g = safe_float(s_slip.GrossPay or s_slip.BasicPay)
            d = 0.0
            n = g

            m_name = calendar.month_abbr[s_slip.Month] if 1 <= s_slip.Month <= 12 else ''
            p_str = f"{m_name} {s_slip.Year}"
            pay_date = s_slip.SortId.strftime('%Y-%m-%d') if s_slip.SortId else f"{s_slip.Year}-{s_slip.Month:02d}-01"

            export_rows.append({
                'Year': s_slip.Year,
                'Month': s_slip.Month,
                'Date': pay_date,
                'Data': [p_str, st_code, st_name, st_desig, pay_date, g, d, n],
                'g': g, 'd': d, 'n': n
            })

    export_rows.sort(key=lambda x: (int(x['Year'] or 0), int(x['Month'] or 0), str(x['Date'] or '')))

    current_row = 5
    for idx, r_item in enumerate(export_rows, 1):
        tot_gross += r_item['g']
        tot_ded += r_item['d']
        tot_net += r_item['n']

        ws.append([idx] + r_item['Data'])

        for c_idx in range(1, 10):
            c = ws.cell(row=current_row, column=c_idx)
            c.font = regular_font
            if c_idx >= 7:
                c.alignment = Alignment(horizontal="right")
                c.number_format = '#,##,##0.00'
        current_row += 1

    ws.append(["Total", "", "", "", "", "", tot_gross, tot_ded, tot_net])
    ws.merge_cells(f"A{current_row}:F{current_row}")
    for c_idx in range(1, 10):
        c = ws.cell(row=current_row, column=c_idx)
        c.font = bold_font
        c.fill = summary_fill
        if c_idx >= 7:
            c.alignment = Alignment(horizontal="right")
            c.number_format = '#,##,##0.00'

    # Column widths
    ws.column_dimensions['A'].width = 6
    ws.column_dimensions['B'].width = 14
    ws.column_dimensions['C'].width = 14
    ws.column_dimensions['D'].width = 24
    ws.column_dimensions['E'].width = 20
    ws.column_dimensions['F'].width = 14
    ws.column_dimensions['G'].width = 18
    ws.column_dimensions['H'].width = 22
    ws.column_dimensions['I'].width = 18

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
    wb.save(response)
    return response


@api_view(['GET'])
def StaffExpenseCandidates(request, CompanyId=""):
    company_id = CompanyId or request.GET.get('CompanyId') or request.query_params.get('CompanyId', '')
    staff_id = request.GET.get('StaffId') or request.query_params.get('StaffId')
    search_q = (request.GET.get('Search') or request.query_params.get('Search') or '').strip().lower()
    from_date = request.GET.get('FromDate') or request.query_params.get('FromDate')
    to_date = request.GET.get('ToDate') or request.query_params.get('ToDate')

    # Get all staff
    staff_query = Staff.objects.all()
    if company_id:
        staff_query = staff_query.filter(CompanyId=company_id)
    staff_dict = {s.StaffId: s for s in staff_query}
    staff_name_map = {s.StaffName.lower(): s.StaffId for s in staff_query if s.StaffName}

    # Fetch candidate expenses
    exp_query = Expense.objects.all()
    if company_id:
        exp_query = exp_query.filter(CompanyId=company_id)

    if from_date:
        exp_query = exp_query.filter(Date__gte=from_date)
    if to_date:
        exp_query = exp_query.filter(Date__lte=to_date)

    exp_list = exp_query.order_by('-Date', '-ExpenseNumber')

    # Preload existing loans to check conversion status
    loans = EmployeeLoan.objects.all()
    if company_id:
        loans = loans.filter(CompanyId=company_id)

    converted_exp_ids = set()
    loan_by_exp_id = {}
    for l in loans:
        nar = l.Narration or ''
        for exp in exp_list:
            if (exp.ExpenseId and exp.ExpenseId in nar) or (exp.ExpenseNumber and exp.ExpenseNumber in nar):
                converted_exp_ids.add(exp.ExpenseId)
                loan_by_exp_id[exp.ExpenseId] = l

    accounts_dict = {a.AccountId: a for a in Account.objects.all()}
    desig_map = get_designation_map()

    candidates = []
    for exp in exp_list:
        is_staff_expense = False
        target_staff_id = exp.StaffId

        if target_staff_id and target_staff_id in staff_dict:
            is_staff_expense = True
        else:
            nar_lower = (exp.Narration or '').lower()
            acc = accounts_dict.get(exp.AccountId)
            acc_name_lower = (acc.Name.lower() if acc and acc.Name else '')

            if any(k in nar_lower for k in ['adv', 'advance', 'salary', 'sal', 'loan']) or \
               any(k in acc_name_lower for k in ['salary', 'salaries', 'advance', 'loan', 'staff']):
                is_staff_expense = True
                for s_name, s_id in staff_name_map.items():
                    if s_name in nar_lower and len(s_name) >= 3:
                        target_staff_id = s_id
                        break

        if not is_staff_expense:
            continue

        if staff_id and target_staff_id != staff_id:
            continue

        if search_q:
            nar_val = (exp.Narration or '').lower()
            exp_num_val = (exp.ExpenseNumber or '').lower()
            st_obj = staff_dict.get(target_staff_id)
            st_name_val = (st_obj.StaffName.lower() if st_obj else '')
            if search_q not in nar_val and search_q not in exp_num_val and search_q not in st_name_val:
                continue

        st = staff_dict.get(target_staff_id)
        acc = accounts_dict.get(exp.AccountId)
        pay_acc = accounts_dict.get(exp.PaymentAccountId)

        is_converted = exp.ExpenseId in converted_exp_ids
        linked_loan = loan_by_exp_id.get(exp.ExpenseId)

        candidates.append({
            'ExpenseId': exp.ExpenseId,
            'ExpenseNumber': exp.ExpenseNumber or '',
            'Date': exp.Date or '',
            'Amount': f"{safe_float(exp.Amount):.2f}",
            'Narration': exp.Narration or '',
            'AccountId': exp.AccountId or '',
            'AccountName': acc.Name if acc else '',
            'AccountCode': acc.Code if acc else '',
            'PaymentAccountId': exp.PaymentAccountId or '',
            'PaymentAccountName': pay_acc.Name if pay_acc else '',
            'PaymentAccountCode': pay_acc.Code if pay_acc else '',
            'StaffId': target_staff_id or '',
            'StaffName': st.StaffName if st else 'Unassigned Staff',
            'StaffCode': st.StaffCode if st else '',
            'Designation': resolve_designation_name(st.Designation, desig_map) if st else '',
            'ProfilePhoto': format_media_url(st.ProfilePhoto) if (st and hasattr(st, 'ProfilePhoto')) else '',
            'IsConverted': is_converted,
            'LinkedLoanId': linked_loan.EmployeeLoanId if linked_loan else '',
            'LinkedLoanNumber': linked_loan.LoanNumber if linked_loan else '',
            'LinkedLoanStatus': linked_loan.Status if linked_loan else '',
            'ReceiptUrl': format_media_url(exp.Receipt) if hasattr(exp, 'Receipt') else '',
            'IsBeforeLockDate': (exp.Date or '') < '2026-04-01'
        })

    return JsonResponse({
        'TotalCount': len(candidates),
        'UnreconciledCount': sum(1 for c in candidates if not c['IsConverted']),
        'ConvertedCount': sum(1 for c in candidates if c['IsConverted']),
        'Candidates': candidates
    }, safe=False)


@api_view(['POST'])
def ReconcileStaffExpense(request):
    data = JSONParser().parse(request)
    expense_id = data.get('ExpenseId')
    staff_id = data.get('StaffId')
    action = data.get('Action')  # 'convert_to_active_loan', 'convert_to_settled_loan', 'mark_as_regular_expense'
    settlement_month = data.get('SettlementMonth')
    settlement_year = data.get('SettlementYear')
    settlement_date = data.get('SettlementDate') or datetime.now().strftime('%Y-%m-%d')
    custom_narration = data.get('Narration')

    if not expense_id:
        return JsonResponse("ExpenseId is required", safe=False, status=400)

    try:
        exp = Expense.objects.get(ExpenseId=expense_id)
    except Expense.DoesNotExist:
        return JsonResponse("Expense not found", safe=False, status=404)

    if not staff_id:
        staff_id = exp.StaffId

    if not staff_id:
        return JsonResponse("StaffId must be provided to assign this advance", safe=False, status=400)

    company_id = exp.CompanyId

    from app_accounting.signals import get_or_create_default_accounts
    if company_id:
        accounts = get_or_create_default_accounts(company_id)
    adv_account = Account.objects.filter(CompanyId=company_id, Code='1300').first()

    if action == 'convert_to_active_loan':
        with transaction.atomic():
            loan_num = generate_next_loan_number(company_id)
            amt_float = safe_float(exp.Amount)
            nar_text = custom_narration or f"Advance from Expense {exp.ExpenseNumber or exp.ExpenseId}: {exp.Narration or ''}".strip()

            loan = EmployeeLoan.objects.create(
                LoanNumber=loan_num,
                StaffId=staff_id,
                CompanyId=company_id,
                LoanDate=exp.Date or datetime.now().strftime('%Y-%m-%d'),
                DisbursementAccountId=exp.PaymentAccountId or '',
                LoanAccountId=adv_account.AccountId if adv_account else '',
                PrincipalAmount=f"{amt_float:.2f}",
                OutstandingBalance=f"{amt_float:.2f}",
                TotalAmountPayable=f"{amt_float:.2f}",
                TotalRepaid='0.00',
                Status='Active',
                RepaymentType='flexible',
                InterestType='zero_interest',
                Narration=nar_text
            )

            # If current financial year (>= 2026-04-01), update expense account to 1300 Asset
            if (exp.Date or '') >= '2026-04-01' and adv_account:
                exp.AccountId = adv_account.AccountId
                exp.StaffId = staff_id
                exp.save()
                ref_num = exp.ExpenseNumber if exp.ExpenseNumber else exp.ExpenseId
                entries = JournalEntry.objects.filter(Source='expense', ReferenceNumber__in=[ref_num, exp.ExpenseId])
                for entry in entries:
                    JournalItem.objects.filter(JournalEntryId=entry.JournalEntryId, Credit='0.00').update(AccountId=adv_account.AccountId, StaffId=staff_id)
            else:
                exp.StaffId = staff_id
                exp.save()

            return JsonResponse({
                'Status': 'Success',
                'Message': f"Converted Expense {exp.ExpenseNumber or exp.ExpenseId} to Active Loan {loan.LoanNumber}",
                'EmployeeLoanId': loan.EmployeeLoanId,
                'LoanNumber': loan.LoanNumber
            }, safe=False)

    elif action == 'convert_to_settled_loan':
        with transaction.atomic():
            loan_num = generate_next_loan_number(company_id)
            repay_num = generate_next_repayment_number(company_id)
            amt_float = safe_float(exp.Amount)
            nar_text = custom_narration or f"Advance from Expense {exp.ExpenseNumber or exp.ExpenseId}: {exp.Narration or ''}".strip()

            loan = EmployeeLoan.objects.create(
                LoanNumber=loan_num,
                StaffId=staff_id,
                CompanyId=company_id,
                LoanDate=exp.Date or datetime.now().strftime('%Y-%m-%d'),
                DisbursementAccountId=exp.PaymentAccountId or '',
                LoanAccountId=adv_account.AccountId if adv_account else '',
                PrincipalAmount=f"{amt_float:.2f}",
                OutstandingBalance='0.00',
                TotalAmountPayable=f"{amt_float:.2f}",
                TotalRepaid=f"{amt_float:.2f}",
                Status='Closed',
                RepaymentType='flexible',
                InterestType='zero_interest',
                Narration=nar_text
            )

            settle_ref = f"SETTLED-{settlement_year}{int(settlement_month):02d}" if settlement_month and settlement_year else f"SETTLED-{loan_num}"
            settle_nar = f"Settled in salary deduction for {settlement_month}/{settlement_year}" if settlement_month and settlement_year else "Settled in salary deduction"

            EmployeeLoanRepayment.objects.create(
                RepaymentNumber=repay_num,
                EmployeeLoanId=loan.EmployeeLoanId,
                StaffId=staff_id,
                CompanyId=company_id,
                RepaymentDate=settlement_date,
                PaymentAccountId='',
                Amount=f"{amt_float:.2f}",
                PrincipalComponent=f"{amt_float:.2f}",
                InterestComponent='0.00',
                PaymentMode='Salary Deduction',
                ReferenceNumber=settle_ref,
                Narration=settle_nar
            )

            exp.StaffId = staff_id
            exp.save()

            return JsonResponse({
                'Status': 'Success',
                'Message': f"Converted Expense {exp.ExpenseNumber or exp.ExpenseId} as Settled Loan {loan.LoanNumber}",
                'EmployeeLoanId': loan.EmployeeLoanId,
                'LoanNumber': loan.LoanNumber
            }, safe=False)

    elif action == 'mark_as_regular_expense':
        exp.StaffId = staff_id
        exp.save()
        return JsonResponse({
            'Status': 'Success',
            'Message': f"Marked Expense {exp.ExpenseNumber or exp.ExpenseId} as regular expense"
        }, safe=False)

    return JsonResponse("Invalid action", safe=False, status=400)


@api_view(['POST'])
def BatchReconcileStaffExpenses(request):
    data = JSONParser().parse(request)
    items = data.get('Items', [])
    action = data.get('Action', 'convert_to_active_loan')

    if not items:
        return JsonResponse("No items provided", safe=False, status=400)

    success_count = 0
    results = []

    for item in items:
        exp_id = item.get('ExpenseId')
        st_id = item.get('StaffId')
        if not exp_id or not st_id:
            continue
        try:
            exp = Expense.objects.get(ExpenseId=exp_id)
        except Expense.DoesNotExist:
            continue

        company_id = exp.CompanyId
        adv_account = Account.objects.filter(CompanyId=company_id, Code='1300').first()

        with transaction.atomic():
            loan_num = generate_next_loan_number(company_id)
            amt_float = safe_float(exp.Amount)
            nar_text = f"Advance from Expense {exp.ExpenseNumber or exp.ExpenseId}: {exp.Narration or ''}".strip()

            loan = EmployeeLoan.objects.create(
                LoanNumber=loan_num,
                StaffId=st_id,
                CompanyId=company_id,
                LoanDate=exp.Date or datetime.now().strftime('%Y-%m-%d'),
                DisbursementAccountId=exp.PaymentAccountId or '',
                LoanAccountId=adv_account.AccountId if adv_account else '',
                PrincipalAmount=f"{amt_float:.2f}",
                OutstandingBalance=f"{amt_float:.2f}",
                TotalAmountPayable=f"{amt_float:.2f}",
                TotalRepaid='0.00',
                Status='Active',
                RepaymentType='flexible',
                InterestType='zero_interest',
                Narration=nar_text
            )

            if (exp.Date or '') >= '2026-04-01' and adv_account:
                exp.AccountId = adv_account.AccountId
                exp.StaffId = st_id
                exp.save()
                ref_num = exp.ExpenseNumber if exp.ExpenseNumber else exp.ExpenseId
                entries = JournalEntry.objects.filter(Source='expense', ReferenceNumber__in=[ref_num, exp.ExpenseId])
                for entry in entries:
                    JournalItem.objects.filter(JournalEntryId=entry.JournalEntryId, Credit='0.00').update(AccountId=adv_account.AccountId, StaffId=st_id)
            else:
                exp.StaffId = st_id
                exp.save()

            success_count += 1
            results.append({'ExpenseId': exp_id, 'LoanNumber': loan_num})

    return JsonResponse({
        'Status': 'Success',
        'SuccessCount': success_count,
        'Results': results
    }, safe=False)



