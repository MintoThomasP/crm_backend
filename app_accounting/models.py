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
    StaffId = models.CharField(blank=True, null=True, max_length=50)
    VendorId = models.CharField(blank=True, null=True, max_length=50)

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
    StaffId = models.CharField(blank=True, null=True, max_length=50)
    VendorId = models.CharField(blank=True, null=True, max_length=50)
    Receipt = models.FileField(upload_to='receipts/', null=True, blank=True)

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
    VendorId = models.CharField(blank=True, null=True, max_length=50)
    ExpenseJournalEntryId = models.CharField(blank=True, null=True, max_length=50)  # Step 1 JE
    ReimbursementJournalEntryId = models.CharField(blank=True, null=True, max_length=50)  # Step 2 JE

    def __str__(self):
        return f"Claim {self.ClaimNumber} - {self.Amount} - {self.Date}"


class EmployeeLoan(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    EmployeeLoanId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    LoanNumber = models.CharField(blank=True, null=True, max_length=50)
    StaffId = models.CharField(blank=True, null=True, max_length=50)
    CompanyId = models.CharField(blank=True, null=True, max_length=50)
    LoanDate = models.CharField(blank=True, null=True, max_length=50)
    DisbursementAccountId = models.CharField(blank=True, null=True, max_length=50)  # Cash/Bank Paid From
    LoanAccountId = models.CharField(blank=True, null=True, max_length=50)  # Asset Account (1300)
    PrincipalAmount = models.CharField(blank=True, null=True, max_length=15, default="0.00")
    RepaymentType = models.CharField(blank=True, null=True, max_length=20, default="flexible")  # flexible, installment
    InterestType = models.CharField(blank=True, null=True, max_length=20, default="zero_interest")  # zero_interest, interest_bearing
    InterestRate = models.CharField(blank=True, null=True, max_length=10, default="0.00")  # % per annum
    TotalInterest = models.CharField(blank=True, null=True, max_length=15, default="0.00")
    TotalAmountPayable = models.CharField(blank=True, null=True, max_length=15, default="0.00")
    InstallmentCount = models.CharField(blank=True, null=True, max_length=10, default="1")
    InstallmentAmount = models.CharField(blank=True, null=True, max_length=15, default="0.00")
    TotalRepaid = models.CharField(blank=True, null=True, max_length=15, default="0.00")
    OutstandingBalance = models.CharField(blank=True, null=True, max_length=15, default="0.00")
    Status = models.CharField(blank=True, null=True, max_length=20, default="Active")  # Active, Closed, Cancelled
    Narration = models.TextField(blank=True, null=True)
    Receipt = models.FileField(upload_to='loan_receipts/', null=True, blank=True)
    DisbursementJournalEntryId = models.CharField(blank=True, null=True, max_length=50)

    def __str__(self):
        return f"Loan {self.LoanNumber} - {self.PrincipalAmount} ({self.Status})"


class EmployeeLoanRepayment(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    RepaymentId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    RepaymentNumber = models.CharField(blank=True, null=True, max_length=50)
    EmployeeLoanId = models.CharField(blank=True, null=True, max_length=50)
    StaffId = models.CharField(blank=True, null=True, max_length=50)
    CompanyId = models.CharField(blank=True, null=True, max_length=50)
    RepaymentDate = models.CharField(blank=True, null=True, max_length=50)
    PaymentAccountId = models.CharField(blank=True, null=True, max_length=50)  # Cash/Bank Paid Into
    Amount = models.CharField(blank=True, null=True, max_length=15, default="0.00")
    PrincipalComponent = models.CharField(blank=True, null=True, max_length=15, default="0.00")
    InterestComponent = models.CharField(blank=True, null=True, max_length=15, default="0.00")
    PaymentMode = models.CharField(blank=True, null=True, max_length=50, default="Bank Transfer")  # Cash, Bank Transfer, Cheque, Salary Deduction
    ReferenceNumber = models.CharField(blank=True, null=True, max_length=100)
    Narration = models.TextField(blank=True, null=True)
    Receipt = models.FileField(upload_to='loan_repayments/', null=True, blank=True)
    JournalEntryId = models.CharField(blank=True, null=True, max_length=50)

    def __str__(self):
        return f"Repayment {self.RepaymentNumber} - {self.Amount} - {self.RepaymentDate}"


