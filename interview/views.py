from rest_framework import viewsets,permissions
from .serializers import InterviewTemplateSerializer, JobRequisitionSerializer
from .models import InterviewTemplate, JobRequisition

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Assumes that the model has an 'organization' field.
    """
    def has_object_permission(self,request,obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.organization == request.user.organization

class InterviewTemplateView(viewsets.ModelViewSet):
    """
    API endpoint for managing interview templates.
    """
    queryset = InterviewTemplate.objects.prefetch_related('questions').all()
    serializer_class = InterviewTemplateSerializer
    permission_classes =[permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return self.queryset.filter(organization=self.request.user.organization)
    
    def perform_create(self, serializer):
        return serializer.save(organization=self.request.user.organization, creator=self.request.user)
    
class JobRequisitionView(viewsets.ModelViewSet):
    """
    API endpoint for managing job requisitions.
    """
    queryset = JobRequisition.objects.all()
    serializer_class = JobRequisitionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return self.queryset.filter(organization=self.request.user.organization)
    
    def perform_create(self,serializer):
        return serializer.save(organization=self.request.user.organization)