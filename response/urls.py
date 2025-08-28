from django.urls import path
from .views import InviteCandidateview,SubmissionView,EvaluationView
from rest_framework_nested import routers
from django.urls import include

router = routers.DefaultRouter()
router.register(r'submissions',SubmissionView,basename='submissions')

#response_router = routers.NestedSimpleRouter(router , r'submissions',lookup='submission')
#response_router.register(r'responses/(?P<response_pk>[^/.]+)/evaluations',EvaluationView , basename='response-evaluations')


urlpatterns =[
    path('invite-candidate/',InviteCandidateview.as_view(), name='invite-candidate'),
    path('',include(router.urls)),
    path('responses/<uuid:response_pk>/evaluations/',EvaluationView.as_view({'post':'create'}), name='response-evaluations'),
]