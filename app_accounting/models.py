from django.db import models
from datetime import datetime
import uuid

class Account(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    AccountId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    Code = models.CharField(blank=True, null=True, max_length=50)
    Name = models.CharField(blank=True, null=True, max_length=100)
    Type = models.CharField(blank=True, null=True, max_length=50)  # Asset, Liability, Equity, Revenue, Expense
    CompanyId = models.CharField(blank=True, null=True, max_length=50)
    IsCashOrBank = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.Code} - {self.Name}"


class JournalEntry(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    JournalEntryId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    Date = models.CharField(blank=True, null=True, max_length=50)
    ReferenceNumber = models.CharField(blank=True, null=True, max_length=50)
    Source = models.CharField(blank=True, null=True, max_length=50)  # manual, invoice, payment
    Narration = models.TextField(blank=True, null=True)
    CompanyId = models.CharField(blank=True, null=True, max_length=50)

    def __str__(self):
        return f"{self.Source} ({self.ReferenceNumber}) - {self.Date}"


class JournalItem(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    JournalItemId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    JournalEntryId = models.CharField(blank=True, null=True, max_length=50)
    AccountId = models.CharField(blank=True, null=True, max_length=50)
    Debit = models.CharField(blank=True, null=True, max_length=15, default="0.00")
    Credit = models.CharField(blank=True, null=True, max_length=15, default="0.00")
    ClientId = models.CharField(blank=True, null=True, max_length=50)

    def __str__(self):
        return f"Item {self.JournalItemId} - Entry {self.JournalEntryId} - Account {self.AccountId}"


class Expense(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    ExpenseId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    ExpenseNumber = models.CharField(blank=True, null=True, max_length=50)
    Date = models.CharField(blank=True, null=True, max_length=50)
    AccountId = models.CharField(blank=True, null=True, max_length=50)  # Expense account (Salaries, Rent, Utilities, etc.)
    PaymentAccountId = models.CharField(blank=True, null=True, max_length=50)  # Bank/Cash account paid from
    Amount = models.CharField(blank=True, null=True, max_length=15)
    Narration = models.TextField(blank=True, null=True)
    CompanyId = models.CharField(blank=True, null=True, max_length=50)

    def __str__(self):
        return f"Expense {self.ExpenseNumber} - {self.Amount} - {self.Date}"


class ExpenseClaim(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    ExpenseClaimId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    ClaimNumber = models.CharField(blank=True, null=True, max_length=50)
    Date = models.CharField(blank=True, null=True, max_length=50)
    StaffId = models.CharField(blank=True, null=True, max_length=50)  # Director/Employee (Staff model)
    AccountId = models.CharField(blank=True, null=True, max_length=50)  # Expense Account (Debit)
    Amount = models.CharField(blank=True, null=True, max_length=15)
    Description = models.TextField(blank=True, null=True)
    Receipt = models.FileField(upload_to='receipts/', null=True, blank=True)
    IsReimbursed = models.BooleanField(default=False)
    ReimbursementDate = models.CharField(blank=True, null=True, max_length=50)
    ReimbursementAccountId = models.CharField(blank=True, null=True, max_length=50)  # Cash/Bank (Credit)
    CompanyId = models.CharField(blank=True, null=True, max_length=50)
    ExpenseJournalEntryId = models.CharField(blank=True, null=True, max_length=50)  # Step 1 JE
    ReimbursementJournalEntryId = models.CharField(blank=True, null=True, max_length=50)  # Step 2 JE

    def __str__(self):
        return f"Claim {self.ClaimNumber} - {self.Amount} - {self.Date}"

