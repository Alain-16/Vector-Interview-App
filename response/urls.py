from django.urls import path
from .views import InviteCandidateview

urlpatterns =[
    path('invite-candidate/',InviteCandidateview.as_view(), name='invite-candidate'),
]