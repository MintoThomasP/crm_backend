from django.urls import path, re_path as url
from app_notes import views


urlpatterns = [
    path('MeetingNotesApi/', views.MeetingNotesApi),
    url(r'^MeetingNotesApiById/(?P<MeetingNoteId>[0-9a-zA-Z\-]+)$', views.MeetingNotesApiById),
    path('UploadMeetingNoteDocument/', views.UploadMeetingNoteDocument.as_view()),
    url(r'^DeleteMeetingDocument/(?P<MeetingNoteDocumentId>[0-9a-zA-Z\-]+)$', views.DeleteMeetingDocument),


    path('MeetingNotesApiByCompanyId/', views.MeetingNotesApiByCompanyId.as_view()),

]