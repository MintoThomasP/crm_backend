from django.db import models
import uuid

# Create your models here.


class Client(models.Model):
    ClientId=models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    ClientName=models.CharField(max_length=300, blank=True, null=True)
   
    