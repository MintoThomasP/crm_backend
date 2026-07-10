from django.test import TestCase
from app_client.models import Client
from app_accounting.models import Account, JournalItem, JournalEntry
from app_sale.views import check_credit_limit
import uuid

class CreditLimitTestCase(TestCase):
    def setUp(self):
        # Create a Client
        self.client_id = str(uuid.uuid4())
        self.client = Client.objects.create(
            ClientId=self.client_id,
            CustomerDisplayName="Test Customer",
            CreditLimit="500.00",
            CreditLimitEnforced=True
        )

        # Create Accounts Receivable Account
        self.ar_account = Account.objects.create(
            AccountId=str(uuid.uuid4()),
            Code="1200",
            Name="Accounts Receivable",
            CompanyId="test-company",
            IsCashOrBank=False
        )

    def test_credit_limit_not_enforced(self):
        # Disable enforcement
        self.client.CreditLimitEnforced = False
        self.client.save()

        # Under or over, it should allow
        allowed, msg = check_credit_limit(self.client_id, "1000.00")
        self.assertTrue(allowed)
        self.assertEqual(msg, "")

    def test_credit_limit_within_limit(self):
        # Enforced, under limit ($400 < $500)
        allowed, msg = check_credit_limit(self.client_id, "400.00")
        self.assertTrue(allowed)
        self.assertEqual(msg, "")

    def test_credit_limit_exceeded(self):
        # Enforced, over limit ($600 > $500)
        allowed, msg = check_credit_limit(self.client_id, "600.00")
        self.assertFalse(allowed)
        self.assertIn("exceeded", msg)

    def test_credit_limit_with_existing_balance(self):
        # Create an existing outstanding ledger debit of $300
        entry = JournalEntry.objects.create(
            JournalEntryId=str(uuid.uuid4()),
            ReferenceNumber="INV-1",
            Source="invoice",
            CompanyId="test-company"
        )
        JournalItem.objects.create(
            JournalItemId=str(uuid.uuid4()),
            JournalEntryId=entry.JournalEntryId,
            AccountId=self.ar_account.AccountId,
            Debit="300.00",
            Credit="0.00",
            ClientId=self.client_id
        )

        # Existing balance $300 + new invoice $150 = $450 (< $500). Should be allowed.
        allowed, msg = check_credit_limit(self.client_id, "150.00")
        self.assertTrue(allowed)

        # Existing balance $300 + new invoice $250 = $550 (> $500). Should be blocked.
        allowed, msg = check_credit_limit(self.client_id, "250.00")
        self.assertFalse(allowed)
