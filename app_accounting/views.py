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
    items = JournalItem.objects.filter(AccountId=AccountId).order_by('-SortId')
    
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
        
    return JsonResponse(enriched_items, safe=False)


@api_view(['GET'])
def CashBookByCompanyId(request, CompanyId=""):
    # Fetch all Accounts for this Company that are marked as Cash or Bank
    cash_bank_accounts = Account.objects.filter(CompanyId=CompanyId, IsCashOrBank=True)
    account_ids = [acc.AccountId for acc in cash_bank_accounts]
    
    # Fetch all JournalItems for these Accounts
    items = JournalItem.objects.filter(AccountId__in=account_ids).order_by('-SortId')
    
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
        
    return JsonResponse(enriched_items, safe=False)


@api_view(['POST'])
def SyncLedger(request):
    try:
        from app_sale.models import Invoice, PaymentReceived
        from app_accounting.signals import create_invoice_journal_entry, create_payment_journal_entry
        
        invoices = Invoice.objects.all()
        for invoice in invoices:
            create_invoice_journal_entry(sender=Invoice, instance=invoice, created=True)
            
        payments = PaymentReceived.objects.all()
        for payment in payments:
            create_payment_journal_entry(sender=PaymentReceived, instance=payment, created=True)
            
        return JsonResponse({"message": "Successfully synchronized ledger and cash book using existing records"}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
