from rest_framework.decorators import api_view
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from app_accounting.models import Account, JournalEntry, JournalItem
from app_accounting.serializers import AccountSerializer, JournalEntrySerializer, JournalItemSerializer
from app_client.models import Client
from app_client.serializers import ClientSerializer

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
    accounts = Account.objects.filter(CompanyId=CompanyId).order_by('Code')
    serializer = AccountSerializer(accounts, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
def JournalItemByAccountId(request, AccountId=""):
    # Fetch all items for this Account
    items = JournalItem.objects.filter(AccountId=AccountId).order_by('SortId')
    
    # Enrich each JournalItem with JournalEntry information (Date, ReferenceNumber, Source, Narration)
    enriched_items = []
    for item in items:
        item_data = JournalItemSerializer(item).data
        try:
            entry = JournalEntry.objects.get(JournalEntryId=item.JournalEntryId)
            item_data['Date'] = entry.Date
            item_data['ReferenceNumber'] = entry.ReferenceNumber
            item_data['Source'] = entry.Source
            item_data['Narration'] = entry.Narration
        except JournalEntry.DoesNotExist:
            item_data['Date'] = ""
            item_data['ReferenceNumber'] = ""
            item_data['Source'] = ""
            item_data['Narration'] = ""
            
        try:
            client = Client.objects.get(ClientId=item.ClientId)
            item_data['ClientName'] = client.CustomerDisplayName
        except:
            item_data['ClientName'] = ""
            
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
            item_data['ReferenceNumber'] = entry.ReferenceNumber
            item_data['Source'] = entry.Source
            item_data['Narration'] = entry.Narration
            
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
            
        try:
            client = Client.objects.get(ClientId=item.ClientId)
            item_data['ClientName'] = client.CustomerDisplayName
        except:
            item_data['ClientName'] = ""
            
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
            serializer.save()
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
        serializer = ExpenseSerializer(expense, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data['ExpenseId'], safe=False)
        return JsonResponse("Failed to update Expense", safe=False, status=400)
    
    elif request.method == 'DELETE':
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
            
        enriched_expenses.append(data)
        
    return JsonResponse(enriched_expenses, safe=False)


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
    
    if export_format == 'excel':
        import openpyxl
        from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
        from django.http import HttpResponse
        
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
        
        ws.merge_cells("A1:G1")
        ws["A1"] = company_name
        ws["A1"].font = title_font
        ws["A1"].alignment = Alignment(horizontal="center")
        
        ws.merge_cells("A2:G2")
        ws["A2"] = f"Period: {period_str}"
        ws["A2"].font = subtitle_font
        ws["A2"].alignment = Alignment(horizontal="center")
        
        ws.append([]) # Empty row
        
        ws.append(["Opening Balance", "", "", "", "", "", f"INR {opening_balance:.2f}"])
        ws.merge_cells(f"A4:F4")
        ws["A4"].font = bold_font
        ws["G4"].font = bold_font
        ws["G4"].alignment = Alignment(horizontal="right")
        ws["A4"].fill = summary_fill
        ws["G4"].fill = summary_fill
        
        headers = ["Date", "Reference", "Contra Account", "Narration", "Receipt (Dr)", "Payment (Cr)", "Running Balance"]
        ws.append(headers)
        header_row = 5
        for col_idx, h in enumerate(headers, 1):
            cell = ws.cell(row=header_row, column=col_idx)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center" if col_idx <= 3 else "left" if col_idx == 4 else "right")
            
        current_row = 6
        for row in period_items:
            ws.append([
                row['Date'],
                row['ReferenceNumber'],
                f"{row['ContraAccountCode']} - {row['ContraAccountName']}" if row['ContraAccountCode'] else row['ContraAccountName'],
                row['Narration'],
                f"INR {row['Debit']}" if safe_float(row['Debit']) > 0 else "-",
                f"INR {row['Credit']}" if safe_float(row['Credit']) > 0 else "-",
                f"INR {row['RunningBalance']}"
            ])
            for col_idx in range(1, 8):
                cell = ws.cell(row=current_row, column=col_idx)
                cell.font = regular_font
                cell.border = thin_border
                cell.alignment = Alignment(horizontal="center" if col_idx <= 2 else "left" if col_idx in (3, 4) else "right")
            current_row += 1
            
        ws.append(["Closing Balance", "", "", "", "", "", f"INR {closing_balance:.2f}"])
        ws.merge_cells(f"A{current_row}:F{current_row}")
        ws[f"A{current_row}"].font = bold_font
        ws[f"G{current_row}"].font = bold_font
        ws[f"G{current_row}"].alignment = Alignment(horizontal="right")
        ws[f"A{current_row}"].border = double_bottom_border
        ws[f"G{current_row}"].border = double_bottom_border
        ws[f"A{current_row}"].fill = summary_fill
        ws[f"G{current_row}"].fill = summary_fill
        
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = openpyxl.utils.get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 3, 12)
            
        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = f'attachment; filename="CashBook_{CompanyId}.xlsx"'
        wb.save(response)
        return response
        
    else:
        from django.http import HttpResponse
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="CashBook_{CompanyId}.pdf"'
        
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
            spaceAfter=15
        )
        cell_style = ParagraphStyle(
            'CellText',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            leading=10
        )
        cell_bold = ParagraphStyle(
            'CellBold',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            leading=10
        )
        header_cell_style = ParagraphStyle(
            'HeaderCell',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=11,
            textColor=colors.white
        )
        
        story.append(Paragraph(company_name, title_style))
        story.append(Paragraph(f"Cash Book Statement &mdash; Period: {period_str}", subtitle_style))
        
        col_widths = [65, 65, 110, 190, 95, 95, 100]
        
        table_data = []
        table_data.append([
            Paragraph("Date", header_cell_style),
            Paragraph("Reference", header_cell_style),
            Paragraph("Contra Account", header_cell_style),
            Paragraph("Narration", header_cell_style),
            Paragraph("Receipt (Dr)", header_cell_style),
            Paragraph("Payment (Cr)", header_cell_style),
            Paragraph("Running Balance", header_cell_style)
        ])
        
        table_data.append([
            Paragraph("<b>Opening Balance</b>", cell_bold),
            "", "", "", "", "",
            Paragraph(f"<b>INR {opening_balance:.2f}</b>", cell_bold)
        ])
        
        for row in period_items:
            table_data.append([
                Paragraph(row['Date'], cell_style),
                Paragraph(row['ReferenceNumber'], cell_style),
                Paragraph(f"{row['ContraAccountCode']} - {row['ContraAccountName']}" if row['ContraAccountCode'] else row['ContraAccountName'], cell_style),
                Paragraph(row['Narration'], cell_style),
                Paragraph(f"INR {row['Debit']}" if safe_float(row['Debit']) > 0 else "-", cell_style),
                Paragraph(f"INR {row['Credit']}" if safe_float(row['Credit']) > 0 else "-", cell_style),
                Paragraph(f"INR {row['RunningBalance']}", cell_style)
            ])
            
        table_data.append([
            Paragraph("<b>Closing Balance</b>", cell_bold),
            "", "", "", "", "",
            Paragraph(f"<b>INR {closing_balance:.2f}</b>", cell_bold)
        ])
        
        t = Table(table_data, colWidths=col_widths, repeatRows=1)
        t_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e3a8a")),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
            
            ('SPAN', (0, 1), (5, 1)),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor("#f3f4f6")),
            ('ALIGN', (6, 1), (6, 1), 'RIGHT'),
            
            ('SPAN', (0, -1), (5, -1)),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#f3f4f6")),
            ('ALIGN', (6, -1), (6, -1), 'RIGHT'),
            
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ])
        t.setStyle(t_style)
        story.append(t)
        
        doc.build(story)
        return response

