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


@api_view(['GET'])
def CashBookByCompanyId(request, CompanyId=""):
    # Fetch all Accounts for this Company that are marked as Cash or Bank
    cash_bank_accounts = Account.objects.filter(CompanyId=CompanyId, IsCashOrBank=True)
    account_ids = [acc.AccountId for acc in cash_bank_accounts]
    
    # Fetch all JournalItems for these Accounts
    items = JournalItem.objects.filter(AccountId__in=account_ids).order_by('SortId')
    
    # Enrich with JournalEntry info
    enriched_items = []
    for item in items:
        item_data = JournalItemSerializer(item).data
        try:
            account = Account.objects.get(AccountId=item.AccountId)
            item_data['AccountName'] = account.Name
            item_data['AccountCode'] = account.Code
        except Account.DoesNotExist:
            item_data['AccountName'] = ""
            item_data['AccountCode'] = ""
            
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

