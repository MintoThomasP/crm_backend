from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime
from app_sale.models import Invoice, PaymentReceived
from app_accounting.models import Account, JournalEntry, JournalItem

def get_or_create_default_accounts(company_id):
    # Default Accounts dictionary: Code -> (Name, Type, IsCashOrBank)
    defaults = {
        '1200': ('Accounts Receivable', 'Asset', False),
        '4000': ('Revenue', 'Revenue', False),
        '2200': ('Tax Payable', 'Liability', False),
        '1010': ('Cash/Bank', 'Asset', True),
        '6150': ('Bank Charges', 'Expense', False),
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

    # Safely convert string values to floats
    def safe_float(val):
        try:
            return float(val) if val else 0.0
        except ValueError:
            return 0.0

    total_amount = safe_float(instance.TotalAmount)
    subtotal_amount = safe_float(instance.SubTotalAmount)
    tax_amount = safe_float(instance.TaxAmount)

    # Ensure balanced entry
    calculated_total = subtotal_amount + tax_amount
    if abs(calculated_total - total_amount) > 0.001:
        subtotal_amount = total_amount - tax_amount

    ref_num = instance.InvoiceNumber or instance.InvoiceId
    
    journal_entry, entry_created = JournalEntry.objects.get_or_create(
        ReferenceNumber=ref_num,
        Source='invoice',
        CompanyId=company_id,
        defaults={
            'Date': instance.InvoiceDate or datetime.now().strftime('%Y-%m-%d'),
            'Narration': f"Invoice {ref_num} for Client {instance.ClientId}"
        }
    )

    if not entry_created:
        JournalItem.objects.filter(JournalEntryId=journal_entry.JournalEntryId).delete()
        journal_entry.Date = instance.InvoiceDate or journal_entry.Date
        journal_entry.Narration = f"Invoice {ref_num} for Client {instance.ClientId}"
        journal_entry.save()

    # Create JournalItems:
    # 1. Debit Accounts Receivable
    JournalItem.objects.create(
        JournalEntryId=journal_entry.JournalEntryId,
        AccountId=accounts['1200'].AccountId,
        Debit=f"{total_amount:.2f}",
        Credit="0.00",
        ClientId=instance.ClientId
    )

    # 2. Credit Revenue
    JournalItem.objects.create(
        JournalEntryId=journal_entry.JournalEntryId,
        AccountId=accounts['4000'].AccountId,
        Debit="0.00",
        Credit=f"{subtotal_amount:.2f}",
        ClientId=instance.ClientId
    )

    # 3. Credit Tax (if greater than 0)
    if tax_amount > 0:
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

    # Safely convert string values to floats
    def safe_float(val):
        try:
            return float(val) if val else 0.0
        except ValueError:
            return 0.0

    amount_received = safe_float(instance.AmountReceived)
    bank_charges = safe_float(instance.BankCharges)

    ref_num = instance.ReferenceNumber or instance.PaymentNumber or instance.PaymentReceivedId
    
    journal_entry, entry_created = JournalEntry.objects.get_or_create(
        ReferenceNumber=ref_num,
        Source='payment',
        CompanyId=company_id,
        defaults={
            'Date': instance.PaymentDate or datetime.now().strftime('%Y-%m-%d'),
            'Narration': f"Payment Received {ref_num} from Client {instance.ClientId}"
        }
    )

    if not entry_created:
        JournalItem.objects.filter(JournalEntryId=journal_entry.JournalEntryId).delete()
        journal_entry.Date = instance.PaymentDate or journal_entry.Date
        journal_entry.Narration = f"Payment Received {ref_num} from Client {instance.ClientId}"
        journal_entry.save()

    # Create JournalItems:
    # 1. Debit Cash/Bank
    JournalItem.objects.create(
        JournalEntryId=journal_entry.JournalEntryId,
        AccountId=accounts['1010'].AccountId,
        Debit=f"{amount_received:.2f}",
        Credit="0.00",
        ClientId=instance.ClientId
    )

    # 2. Debit Bank Charges (if any)
    if bank_charges > 0:
        JournalItem.objects.create(
            JournalEntryId=journal_entry.JournalEntryId,
            AccountId=accounts['6150'].AccountId,
            Debit=f"{bank_charges:.2f}",
            Credit="0.00",
            ClientId=instance.ClientId
        )

    # 3. Credit Accounts Receivable (receivable credit = cash received + bank charges)
    total_credit = amount_received + bank_charges
    JournalItem.objects.create(
        JournalEntryId=journal_entry.JournalEntryId,
        AccountId=accounts['1200'].AccountId,
        Debit="0.00",
        Credit=f"{total_credit:.2f}",
        ClientId=instance.ClientId
    )
