from django.db import models
from datetime import datetime
import uuid
# Create your models here.




class Category(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    CategoryId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    RefId=models.CharField(blank=True, null=True, max_length=50)
    Category=models.CharField(blank=True, null=True, max_length=300)
    SectionType=models.CharField(blank=True, null=True, max_length=300) # Product,Finance
    CategoryType=models.CharField(blank=True, null=True, max_length=300)# data from default table
    ActiveStatus=models.BooleanField(default=True)
