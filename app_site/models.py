from django.db import models

# Create your models here.
class SiteSettings(models.Model):
    SiteSettingsId=models.AutoField(primary_key=True, editable=False)       
    Address=models.TextField(null=True,blank=True)
    Email1=models.CharField(blank=True, null=True, max_length=150) 
    Email2=models.CharField(blank=True, null=True, max_length=150) 
    Phone1=models.CharField(blank=True, null=True, max_length=20)
    Phone2=models.CharField(blank=True, null=True, max_length=20)
    WhatsappNumber=models.CharField(blank=True, null=True, max_length=15)
    GoogleMapLink=models.TextField(null=True,blank=True)  
    InvoicePrefix=models.CharField(blank=True, null=True, max_length=300)
    QuotationPrefix=models.CharField(blank=True, null=True, max_length=300) 
    MobilePrefix=models.CharField(blank=True, null=True, max_length=10)          
    TaxPercentage = models.CharField(max_length=4, blank=True, null=True) 
    TaxType  = models.CharField(max_length=300, blank=True, null=True)            
    CurrencyType = models.CharField(max_length=300, blank=True, null=True)
    InvoiceTemplate=models.CharField(max_length=300, blank=True, null=True)
    MobilePattern=models.CharField(blank=True, null=True, max_length=300)   
    WhatsAppPattern = models.CharField(max_length=300, blank=True, null=True)