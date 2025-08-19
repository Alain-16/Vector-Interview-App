import secrets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .serializers import CandidateInvitationSerializer
from .models import Candidate, InterviewSession
from interview.models import JobRequisition

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



