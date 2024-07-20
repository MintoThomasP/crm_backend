from django.db import models
import uuid
from datetime import datetime
# Create your models here.
class SiteSettings(models.Model):
    SiteSettingsId=models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    CompanyId=models.CharField(blank=True, null=True, max_length=50) 
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
    Logo=models.FileField(upload_to='logo/',null=True,blank=True,max_length=300)
    PrimaryColor=models.CharField(max_length=50, blank=True, null=True)
    SecondaryColor=models.CharField(max_length=50, blank=True, null=True)
    FavIcon=models.FileField(upload_to='FavIcon/',null=True,blank=True,max_length=300)




class Notification(models.Model):
    NotificationId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    Title=models.CharField(blank=True, null=True, max_length=300)
    Message=models.TextField(blank=True, null=True)
    FromUser=models.CharField(blank=True, null=True, max_length=50)
    ToUser=models.CharField(blank=True, null=True, max_length=300)
    CreatedDate=models.DateTimeField(editable=False, default=datetime.now)



