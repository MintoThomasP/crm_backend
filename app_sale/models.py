from django.db import models
from datetime import datetime
import uuid

# Create your models here.


class Quotation(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    QuotationId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    ClientId=models.CharField(blank=True, null=True, max_length=50)
    CompanyId = models.CharField(blank=True, null=True, max_length=50)
    QuotationNumber=models.CharField(blank=True, null=True, max_length=50)
    ReferenceNumber=models.CharField(blank=True, null=True, max_length=50)
    QuoteDate = models.CharField(blank=True, null=True, max_length=50)
    ExpiryDate = models.CharField(blank=True, null=True, max_length=50)
    SalesPerson=models.CharField(blank=True, null=True, max_length=50)
    ProjectId=models.CharField(blank=True, null=True, max_length=50)
    Subject=models.TextField(blank=True, null=True)
    CustomerNotes=models.TextField(blank=True, null=True)
    TermsNConditions=models.TextField(blank=True, null=True)
    SubTotalAmount=models.CharField(blank=True, null=True, max_length=15)
    TotalAmount=models.CharField(blank=True, null=True, max_length=15)
    QuotationFile=models.FileField(null=True,blank=True, upload_to='QuotationFile')


class QuotationItem(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    QuotationItemId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    QuotationId=models.CharField(blank=True, null=True, max_length=50)
    ItemName=models.CharField(blank=True, null=True, max_length=300)
    Quantity = models.IntegerField(default=1)
    Rate=models.CharField(blank=True, null=True, max_length=15)
    DiscountPercent=models.CharField(blank=True, null=True, max_length=15)
    Amount=models.CharField(blank=True, null=True, max_length=15)


class QuotationFile(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    QuotationFileId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    QuotationId=models.CharField(blank=True, null=True, max_length=50)
    QuoteFile=models.FileField(null=True,blank=True, upload_to='Quotefiles')




class Invoice(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    InvoiceId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    InvoiceNumber=models.CharField(blank=True, null=True, max_length=50)
    OrderNumber=models.CharField(blank=True, null=True, max_length=50)
    CompanyId = models.CharField(blank=True, null=True, max_length=50)
    ClientId=models.CharField(blank=True, null=True, max_length=50)
    InvoiceDate = models.CharField(blank=True, null=True, max_length=50)
    DueDate = models.CharField(blank=True, null=True, max_length=50)
    SalesPerson=models.CharField(blank=True, null=True, max_length=50)
    Subject=models.TextField(blank=True, null=True)
    CustomerNotes=models.TextField(blank=True, null=True)
    TermsNConditions=models.TextField(blank=True, null=True)
    BillingAddress=models.TextField(blank=True, null=True)
    SubTotalAmount=models.CharField(blank=True, null=True, max_length=15)
    TotalAmount=models.CharField(blank=True, null=True, max_length=15)
    AmountDue=models.CharField(blank=True, null=True, max_length=15, default="0.00")
    Payment=models.CharField(blank=True, null=True, max_length=15)
    InvoiceFile=models.FileField(null=True,blank=True, upload_to='Invoicefiles')
    Status=models.IntegerField(default=1)
    AddBankAccount=models.BooleanField(default=False)
    

class InvoiceItem(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    InvoiceItemId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    InvoiceId=models.CharField(blank=True, null=True, max_length=50)
    Code=models.CharField(blank=True, null=True, max_length=100)
    ItemDetails=models.TextField(blank=True, null=True)
    Quantity = models.IntegerField(default=1)
    Rate=models.CharField(blank=True, null=True, max_length=15)
    DiscountPercent=models.CharField(blank=True, null=True, max_length=15)
    Amount=models.CharField(blank=True, null=True, max_length=15)
    OrderNo=models.IntegerField(default=1)



class InvoiceDocument(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    InvoiceDocumentId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    InvoiceId=models.CharField(blank=True, null=True, max_length=50)
    Document=models.FileField(null=True,blank=True, upload_to='InvoiceDocument')




class PaymentReceived(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    PaymentReceivedId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    ClientId=models.CharField(blank=True, null=True, max_length=50)
    CompanyId = models.CharField(blank=True, null=True, max_length=50)
    AmountReceived=models.CharField(blank=True, null=True, max_length=15)
    IsFullAmount=models.BooleanField(default=False)
    BankCharges=models.CharField(blank=True, null=True, max_length=15)
    PaymentDate = models.CharField(blank=True, null=True, max_length=50)
    PaymentNumber=models.CharField(blank=True, null=True, max_length=15)
    PaymentMode=models.CharField(blank=True, null=True, max_length=50)
    DepositTo=models.CharField(blank=True, null=True, max_length=50)
    StaffId=models.CharField(blank=True, null=True, max_length=50)
    CreatedBy=models.CharField(blank=True, null=True, max_length=50)
    Receipt=models.FileField(null=True,blank=True, upload_to='Invoicefiles')
    ReferenceNumber=models.CharField(blank=True, null=True, max_length=50)


class PaymentReceivedDetail(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    PaymentReceivedDetailId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    PaymentReceivedId=models.CharField(blank=True, null=True, max_length=50)
    Description=models.TextField(blank=True, null=True)
    Amount=models.CharField(blank=True, null=True, max_length=15)
    Type=models.CharField(blank=True, null=True, max_length=100)# Invoice, from advance, To advance
    RefId=models.CharField(blank=True, null=True, max_length=50) # Clientid/InvoiceId
    Date=models.CharField(blank=True, null=True, max_length=300)
    

class PaymentDocument(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    PaymentDocumentId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    PaymentReceivedId=models.CharField(blank=True, null=True, max_length=50)
    Document=models.FileField(null=True,blank=True, upload_to='paymentDocument')


