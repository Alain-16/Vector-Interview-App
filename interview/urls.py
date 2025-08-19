from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import InterviewTemplateView, JobRequisitionView

router = DefaultRouter()
router.register(r'templates', InterviewTemplateView, basename='interview-template')
router.register(r'jobs', JobRequisitionView, basename='job-requisition')

urlpatterns =[
    path('',include(router.urls)),
]