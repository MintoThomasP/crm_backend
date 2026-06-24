import uuid
from datetime import datetime
from django.core.management.base import BaseCommand
from app_accounting.models import Account, JournalEntry, JournalItem
from app_accounting.signals import get_or_create_default_accounts

class Command(BaseCommand):
    help = 'Sets the opening balance for the bank account (Code 1010) using Opening Balance Equity (Code 3000)'

    def add_arguments(self, parser):
        parser.add_argument('--company', type=str, required=True, help='Company ID')
        parser.add_argument('--amount', type=str, required=True, help='Opening Balance Amount (e.g. 10000.00)')
        parser.add_argument('--date', type=str, default=None, help='Date of opening balance (YYYY-MM-DD)')

    def handle(self, *args, **options):
        company_id = options['company']
        amount_str = options['amount']
        date_str = options['date'] or datetime.now().strftime('%Y-%m-%d')

        try:
            amount = float(amount_str)
        except ValueError:
            self.stdout.write(self.style.ERROR('Invalid amount format.'))
            return

        # Ensure default accounts are created
        accounts = get_or_create_default_accounts(company_id)
        bank_account = accounts.get('1010')
        equity_account = accounts.get('3000')

        if not bank_account or not equity_account:
            self.stdout.write(self.style.ERROR('Default bank or equity account not found/created.'))
            return

        # Get or create manual JournalEntry for opening balance
        ref_num = 'OPENING-BALANCE'
        journal_entry, created = JournalEntry.objects.get_or_create(
            ReferenceNumber=ref_num,
            Source='manual',
            CompanyId=company_id,
            defaults={
                'Date': date_str,
                'Narration': 'Opening Balance for Cash/Bank'
            }
        )

        if not created:
            # Clear old items to avoid duplicates
            JournalItem.objects.filter(JournalEntryId=journal_entry.JournalEntryId).delete()
            journal_entry.Date = date_str
            journal_entry.save()

        # Create JournalItems
        # 1. Debit Cash/Bank
        JournalItem.objects.create(
            JournalEntryId=journal_entry.JournalEntryId,
            AccountId=bank_account.AccountId,
            Debit=f"{amount:.2f}",
            Credit="0.00"
        )

        # 2. Credit Opening Balance Equity
        JournalItem.objects.create(
            JournalEntryId=journal_entry.JournalEntryId,
            AccountId=equity_account.AccountId,
            Debit="0.00",
            Credit=f"{amount:.2f}"
        )

        self.stdout.write(self.style.SUCCESS(
            f"Successfully recorded opening balance of {amount:.2f} for Company {company_id}.\n"
            f"Debit: {bank_account.Code} - {bank_account.Name} | {amount:.2f}\n"
            f"Credit: {equity_account.Code} - {equity_account.Name} | {amount:.2f}"
        ))
