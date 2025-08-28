import secrets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.decorators import action
from .serializers import CandidateInvitationSerializer, InterviewSessionSerializer, ResponseSerializer, EvaluationSerializer,InterviewSessionListSerializer
from .models import Candidate, InterviewSession,Evaluation, InterviewResponse
from interview.models import JobRequisition
from rest_framework import viewsets,permissions,status


class InviteCandidateview(APIView):
    """
     API endpoint to invite multiple candidates to a job requisition.
     Uses APIView for custom logic.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = CandidateInvitationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
        emails = serializer.validated_data['emails']
        job_requisition_id = serializer.validated_data['job_requisition_id']

        try:
            job = JobRequisition.objects.get(id=job_requisition_id, organization=request.user.organization)
        except JobRequisition.DoesNotExist:
            return Response({"Error":"Job requisition not found or you do not have permission to access it."}, status=status.HTTP_404_NOT_FOUND)
        
        candidate_sessions =[]
        for email in emails:
            candidate, _ = Candidate.objects.get_or_create(email=email)
             
            session = InterviewSession.objects.create(
                candidate=candidate,
                job_requisition=job,
                unique_access_token=secrets.token_urlsafe(32)
            )
            candidate_sessions.append({
                "email":email,
                "interview_link":f"/interview/{session.unique_access_token}"
            })
        
        return Response(candidate_sessions,status=status.HTTP_201_CREATED)


class SubmissionView(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint to invite multiple candidates to a job requisition.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self,*args,**kwargs):
        return InterviewSession.objects.filter(
            job_requisition__organization=self.request.user.organization
        ).select_related('candidate').prefetch_related('responses')
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return InterviewSessionSerializer
        return InterviewSessionListSerializer
    
    @action(detail=False, methods=['get'], url_path='job/(?P<job_id>[^/.]+)')
    def for_job(self,request,job_id=None):
       """
      Custom action to list all submissions for a specific job.
        Access via /api/submissions/job/{job_id}/ 
       """ 
       queryset = self.get_queryset().filter(job_requisition_id=job_id)
       page = self.paginate_queryset(queryset)
       serializer_class = self.get_serializer_class()

       if page is not None:
           serializer = serializer_class(page, many=True)
           return self.get_paginated_response(serializer.data)
       serializer = serializer_class(queryset,many=True)
       return Response(serializer.data)

class EvaluationView(viewsets.ModelViewSet):
    """
    ViewSet for creating evaluations for a specific response.
    """
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post']

    def perform_create(self,serializer):
        response_id =self.kwargs['response_pk']
        try:
            response = InterviewResponse.objects.get(
                id=response_id,
                session__job_requisition__organization = self.request.user.organization
            )
            serializer.save(evaluator=self.request.user,response=response)
        except InterviewResponse.DoesNotExist:
            raise serializer.ValidationError("Response not found or you do not have permission to evaluate it.")

