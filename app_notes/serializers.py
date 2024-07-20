from rest_framework import serializers

from app_notes.models import MeetingNoteDocument, MeetingNotes


class MeetingNotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingNotes
        fields = ('SortId',
                  'MeetingNoteId',
                  'StartTime',
                  'EndTime',
                  'TeamParticipants',
                  'MeetingType',
                  'CreatedBy',
                  'CreatedDate',
                  'Title',
                  'Description',
                  'ClientId',
                  'CompanyId'           
        )

class MeetingNoteDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingNoteDocument
        fields = ('MeetingNoteDocumentId',
                 'MeetingNoteId',
                  'Document' )