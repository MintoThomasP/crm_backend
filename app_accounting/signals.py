from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime
from decimal import Decimal, InvalidOperation
from django.db import transaction
from app_sale.models import Invoice, PaymentReceived
from app_accounting.models import Account, JournalEntry, JournalItem, Expense
from app_client.models import Client

def safe_decimal(val):
    if not val:
        return Decimal('0.00')
    try:
        cleaned = str(val).strip().replace(',', '')
        return Decimal(cleaned)
    except (ValueError, InvalidOperation, TypeError):
        return Decimal('0.00')

def get_or_create_default_accounts(company_id):
    # Default Accounts dictionary: Code -> (Name, Type, IsCashOrBank)
    defaults = {
        # Assets & Liabilities
        '1200': ('Accounts Receivable', 'Asset', False),
        '1010': ('Cash/Bank', 'Asset', True),
        '2200': ('Tax Payable', 'Liability', False),
        '2300': ('Due to Directors / Expense Clearing', 'Liability', False),
        '2400': ('Loans Payable', 'Liability', False),
        
        # Equity
        '3000': ('Opening Balance Equity', 'Equity', False),
        '3100': ('Owner Capital / Investment', 'Equity', False),
        
        # Revenue
        '4000': ('Revenue', 'Revenue', False),
        
        # Expenses
        '6150': ('Bank Charges', 'Expense', False),
        '6010': ('Salaries Expense', 'Expense', False),         # Salaries & Wages
        '6015': ('Staff Welfare & Benefits', 'Expense', False),  # Added
        '6020': ('Rent Expense', 'Expense', False),              # Office Rent
        '6030': ('Utilities Expense', 'Expense', False),         # Utilities
        '6035': ('Software & Subscriptions', 'Expense', False),  # Added
        '6040': ('General Expense', 'Expense', False),
        '6045': ('Marketing & Advertising', 'Expense', False),   # Added
        '6050': ('Legal & Professional Fees', 'Expense', False), # Added
        '6060': ('Miscellaneous / Sundry Expense', 'Expense', False) # Added
    }
    accounts = {}
    for code, (name, type_, is_cash_or_bank) in defaults.items():
        account, created = Account.objects.get_or_create(
            Code=code,
            CompanyId=company_id,
            defaults={
                'Name': name,
                'Type': type_,
                'IsCashOrBank': is_cash_or_bank
            }
        )
        accounts[code] = account
    return accounts


@receiver(post_save, sender=Invoice)
def create_invoice_journal_entry(sender, instance, created, **kwargs):
    company_id = instance.CompanyId
    if not company_id:
        return

    accounts = get_or_create_default_accounts(company_id)

    total_amount = safe_decimal(instance.TotalAmount)
    subtotal_amount = safe_decimal(instance.SubTotalAmount)
    tax_amount = safe_decimal(instance.TaxAmount)

    # 1. DEBIT: Account 1200 - Accounts Receivable
    #    Amount: Invoice.TotalAmount
    # 2. CREDIT: Account 4000 - Revenue
    #    Amount: Invoice.SubTotalAmount
    # 3. CREDIT: Account 2200 - Tax Payable (Only if TaxAmount > 0)
    #    Amount: Invoice.TaxAmount

    credits_sum = subtotal_amount
    if tax_amount > Decimal('0.00'):
        credits_sum += tax_amount

    # Ensure that the net total of Debits strictly equals Credits before saving the transaction splits
    if total_amount != credits_sum:
        raise ValueError(
            f"Balanced splits validation failed for Invoice {instance.InvoiceId}: "
            f"Total DEBITs ({total_amount}) != Total CREDITs ({credits_sum})"
        )

    client_name = instance.ClientId
    if instance.ClientId:
        try:
            client = Client.objects.get(ClientId=instance.ClientId)
            client_name = client.CustomerDisplayName
        except Client.DoesNotExist:
            pass

    # Use InvoiceNumber as human-readable ReferenceNumber (fallback to InvoiceId if blank)
    ref_num = instance.InvoiceNumber if instance.InvoiceNumber else instance.InvoiceId
    inv_num_part = f" #{instance.InvoiceNumber}" if instance.InvoiceNumber else ""
    narration = f"Invoice{inv_num_part} for Client {client_name}"

    with transaction.atomic():
        lookup_refs = [instance.InvoiceId]
        if instance.InvoiceNumber:
            lookup_refs.append(instance.InvoiceNumber)

        journal_entry = JournalEntry.objects.filter(
            Source='invoice',
            CompanyId=company_id
        ).filter(
            Q(ReferenceNumber__in=lookup_refs)
        ).first()

        if not journal_entry:
            journal_entry = JournalEntry.objects.create(
                ReferenceNumber=ref_num,
                Source='invoice',
                CompanyId=company_id,
                Date=instance.InvoiceDate or datetime.now().strftime('%Y-%m-%d'),
                Narration=narration
            )
        else:
            JournalItem.objects.filter(JournalEntryId=journal_entry.JournalEntryId).delete()
            journal_entry.ReferenceNumber = ref_num
            journal_entry.Date = instance.InvoiceDate or journal_entry.Date
            journal_entry.Narration = narration
            journal_entry.save()

        # Create JournalItems splits:
        # DEBIT: 1200 - Accounts Receivable
        JournalItem.objects.create(
            JournalEntryId=journal_entry.JournalEntryId,
            AccountId=accounts['1200'].AccountId,
            Debit=f"{total_amount:.2f}",
            Credit="0.00",
            ClientId=instance.ClientId
        )

        # CREDIT: 4000 - Revenue
        JournalItem.objects.create(
            JournalEntryId=journal_entry.JournalEntryId,
            AccountId=accounts['4000'].AccountId,
            Debit="0.00",
            Credit=f"{subtotal_amount:.2f}",
            ClientId=instance.ClientId
        )

        # CREDIT: 2200 - Tax Payable (Only if TaxAmount > 0)
        if tax_amount > Decimal('0.00'):
            JournalItem.objects.create(
                JournalEntryId=journal_entry.JournalEntryId,
                AccountId=accounts['2200'].AccountId,
                Debit="0.00",
                Credit=f"{tax_amount:.2f}",
                ClientId=instance.ClientId
            )


@receiver(post_save, sender=PaymentReceived)
def create_payment_journal_entry(sender, instance, created, **kwargs):
    company_id = instance.CompanyId
    if not company_id:
        return

    accounts = get_or_create_default_accounts(company_id)

    amount_received = safe_decimal(instance.AmountReceived)
    bank_charges = safe_decimal(instance.BankCharges)

    # 1. DEBIT: Account 1010 - Cash/Bank
    #    Amount: PaymentReceived.AmountReceived - PaymentReceived.BankCharges (Net deposit cash)
    # 2. DEBIT: Account 6150 - Bank Charges (Only if BankCharges > 0)
    #    Amount: PaymentReceived.BankCharges
    # 3. CREDIT: Account 1200 - Accounts Receivable
    #    Amount: PaymentReceived.AmountReceived (Gross amount clearing customer's open balance)

    net_amount = amount_received - bank_charges

    debits_sum = net_amount
    if bank_charges > Decimal('0.00'):
        debits_sum += bank_charges

    credits_sum = amount_received

    # Ensure that the net total of Debits strictly equals Credits before saving the transaction splits
    if debits_sum != credits_sum:
        raise ValueError(
            f"Balanced splits validation failed for PaymentReceived {instance.PaymentReceivedId}: "
            f"Total DEBITs ({debits_sum}) != Total CREDITs ({credits_sum})"
        )

    client_name = instance.ClientId
    if instance.ClientId:
        try:
            client = Client.objects.get(ClientId=instance.ClientId)
            client_name = client.CustomerDisplayName
        except Client.DoesNotExist:
            pass

    # Use PaymentNumber as human-readable ReferenceNumber (fallback to ReferenceNumber or PaymentReceivedId if blank)
    ref_num = instance.PaymentNumber if instance.PaymentNumber else (instance.ReferenceNumber or instance.PaymentReceivedId)
    pay_num_part = f" #{instance.PaymentNumber}" if instance.PaymentNumber else ""
    narration = f"Payment Received{pay_num_part} from Client {client_name}"

    with transaction.atomic():
        lookup_refs = [instance.PaymentReceivedId]
        if instance.PaymentNumber:
            lookup_refs.append(instance.PaymentNumber)
        if instance.ReferenceNumber:
            lookup_refs.append(instance.ReferenceNumber)

        journal_entry = JournalEntry.objects.filter(
            Source='payment',
            CompanyId=company_id
        ).filter(
            Q(ReferenceNumber__in=lookup_refs)
        ).first()

        if not journal_entry:
            journal_entry = JournalEntry.objects.create(
                ReferenceNumber=ref_num,
                Source='payment',
                CompanyId=company_id,
                Date=instance.PaymentDate or datetime.now().strftime('%Y-%m-%d'),
                Narration=narration
            )
        else:
            JournalItem.objects.filter(JournalEntryId=journal_entry.JournalEntryId).delete()
            journal_entry.ReferenceNumber = ref_num
            journal_entry.Date = instance.PaymentDate or journal_entry.Date
            journal_entry.Narration = narration
            journal_entry.save()

        # Create JournalItems splits:
        # DEBIT: 1010 - Cash/Bank
        JournalItem.objects.create(
            JournalEntryId=journal_entry.JournalEntryId,
            AccountId=accounts['1010'].AccountId,
            Debit=f"{net_amount:.2f}",
            Credit="0.00",
            ClientId=instance.ClientId
        )

        # DEBIT: 6150 - Bank Charges (Only if BankCharges > 0)
        if bank_charges > Decimal('0.00'):
            JournalItem.objects.create(
                JournalEntryId=journal_entry.JournalEntryId,
                AccountId=accounts['6150'].AccountId,
                Debit=f"{bank_charges:.2f}",
                Credit="0.00",
                ClientId=instance.ClientId
            )

        # CREDIT: 1200 - Accounts Receivable
        JournalItem.objects.create(
            JournalEntryId=journal_entry.JournalEntryId,
            AccountId=accounts['1200'].AccountId,
            Debit="0.00",
            Credit=f"{amount_received:.2f}",
            ClientId=instance.ClientId
        )


@receiver(post_save, sender=Expense)
def create_expense_journal_entry(sender, instance, created, **kwargs):
    company_id = instance.CompanyId
    if not company_id:
        return

    # Safely convert string values to floats
    def safe_float(val):
        try:
            return float(val) if val else 0.0
        except ValueError:
            return 0.0

    amount = safe_float(instance.Amount)
    ref_num = instance.ExpenseNumber if instance.ExpenseNumber else instance.ExpenseId

    with transaction.atomic():
        lookup_refs = [instance.ExpenseId]
        if instance.ExpenseNumber:
            lookup_refs.append(instance.ExpenseNumber)

        journal_entry = JournalEntry.objects.filter(
            Source='expense',
            CompanyId=company_id
        ).filter(
            Q(ReferenceNumber__in=lookup_refs)
        ).first()

        if not journal_entry:
            journal_entry = JournalEntry.objects.create(
                ReferenceNumber=ref_num,
                Source='expense',
                CompanyId=company_id,
                Date=instance.Date or datetime.now().strftime('%Y-%m-%d'),
                Narration=instance.Narration or f"Expense {ref_num}"
            )
        else:
            JournalItem.objects.filter(JournalEntryId=journal_entry.JournalEntryId).delete()
            journal_entry.ReferenceNumber = ref_num
            journal_entry.Date = instance.Date or journal_entry.Date
            journal_entry.Narration = instance.Narration or f"Expense {ref_num}"
            journal_entry.save()

        sort_time = journal_entry.SortId if journal_entry.SortId else datetime.now()

        # Create JournalItems:
        # 1. Debit chosen Expense account (instance.AccountId)
        if instance.AccountId:
            JournalItem.objects.create(
                JournalEntryId=journal_entry.JournalEntryId,
                AccountId=instance.AccountId,
                Debit=f"{amount:.2f}",
                Credit="0.00",
                StaffId=instance.StaffId,
                VendorId=instance.VendorId,
                SortId=sort_time
            )

        # 2. Credit chosen Bank/Cash payment account (instance.PaymentAccountId)
        if instance.PaymentAccountId:
            JournalItem.objects.create(
                JournalEntryId=journal_entry.JournalEntryId,
                AccountId=instance.PaymentAccountId,
                Debit="0.00",
                Credit=f"{amount:.2f}",
                StaffId=instance.StaffId,
                VendorId=instance.VendorId,
                SortId=sort_time
            )
