from rest_framework import serializers

from app_sale.models import Invoice, InvoiceDocument, InvoiceItem, PaymentDocument, PaymentReceived, PaymentReceivedDetail, Quotation, QuotationFile, QuotationItem


class QuotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quotation
        fields = ('SortId',
                  'QuotationId',
                  'ClientId',
                  'CompanyId',
                  'QuotationNumber',
                  'ReferenceNumber',
                  'QuoteDate',
                  'ExpiryDate',
                  'SalesPerson',
                  'ProjectId',
                  'Subject',
                  'CustomerNotes',
                  'TermsNConditions',
                  'SubTotalAmount',
                  'TotalAmount',
                  'QuotationFile')


class QuotationItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationItem
        fields = ('SortId',
                  'QuotationItemId',
                  'QuotationId',
                  'ItemName',
                  'Quantity',
                  'Rate',
                  'DiscountPercent',
                  'Amount')


class QuotationFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationFile
        fields = ('SortId',
                  'QuotationFileId',
                  'QuotationId',
                  'QuoteFile',
                  )


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ('SortId',
                  'InvoiceId',
                  'InvoiceNumber',
                  'OrderNumber',
                  'ClientId',
                  'CompanyId',
                  'InvoiceDate',
                  'DueDate',
                  'SalesPerson',
                  'Subject',
                  'CustomerNotes',
                  'TermsNConditions',
                  'BillingAddress',
                  'SubTotalAmount',
                  'TaxPercentage',
                  'TaxAmount'
                  'TotalAmount',
                  'AmountDue',
                  'InvoiceFile',
                  'Payment',
                  'Status',
                  'AddBankAccount')


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ('SortId',
                  'InvoiceItemId',
                  'InvoiceId',
                  'Code',
                  'ItemDetails',
                  'Quantity',
                  'Rate',
                  'DiscountPercent',
                  'Amount',
                  'OrderNo')


class InvoiceDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceDocument
        fields = ('SortId',
                  'InvoiceDocumentId',
                  'InvoiceId',
                  'Document',
                  )


class PaymentReceivedSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentReceived
        fields = ('SortId',
                  'PaymentReceivedId',
                  'ClientId',
                  'CompanyId',
                  'AmountReceived',
                  'IsFullAmount',
                  'BankCharges',
                  'PaymentDate',
                  'PaymentNumber',
                  'PaymentMode',
                  'DepositTo',
                  'StaffId',
                  'CreatedBy',
                  'Receipt',
                  'ReferenceNumber'

                  )


class PaymentReceivedDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentReceivedDetail
        fields = ('SortId',
                  'PaymentReceivedDetailId',
                  'PaymentReceivedId',
                  'Description',
                  'Amount',
                  'Type',
                  'RefId',
                  'Date'

                  )


class PaymentDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentDocument
        fields = ('SortId',
                  'PaymentDocumentId',
                  'PaymentReceivedId',
                  'Document',
                  )
