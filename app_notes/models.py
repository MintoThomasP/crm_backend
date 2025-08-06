from django.db import models
from datetime import datetime
import uuid
from django.utils import timezone
import pytz
# Create your models here.


class MeetingNotes(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    MeetingNoteId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    StartTime = models.CharField(blank=True, null=True, max_length=100)
    EndTime = models.CharField(blank=True, null=True, max_length=100)
    TeamParticipants = models.JSONField(
        default=list, blank=True, null=True)
    MeetingType = models.CharField(blank=True, null=True, max_length=50)
    CreatedBy = models.CharField(blank=True, null=True, max_length=50)
    CreatedDate = models.DateTimeField(default=timezone.now)
    Title = models.CharField(blank=True, null=True, max_length=300)
    Description = models.TextField(blank=True, null=True)
    ClientId = models.CharField(blank=True, null=True, max_length=50)
    CompanyId = models.CharField(blank=True, null=True, max_length=50)
    AssignedBy = models.CharField(blank=True, null=True, max_length=50)
    ScheduledOn = models.DateTimeField(
        blank=True, null=True, default=timezone.now)
    Status = models.IntegerField(default=2)  # 1=Scheduled, 2= Completed

    def save(self, *args, **kwargs):
        if not self.CreatedDate:
            # Convert current time to IST
            ist = pytz.timezone('Asia/Kolkata')
            self.CreatedDate = datetime.now(ist)
        super(MeetingNotes, self).save(*args, **kwargs)


class MeetingNoteDocument(models.Model):
    MeetingNoteDocumentId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    MeetingNoteId = models.CharField(blank=True, null=True, max_length=50)
    Document = models.FileField(
        null=True, blank=True, upload_to='Meetingdocuments')
