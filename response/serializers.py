from rest_framework import serializers
#from .models import Candidate, InterviewSession

class CandidateInvitationSerializer(serializers.ModelSerializer):
    """
    Serializer for inviting Candidate model
    """
    emails = serializers.ListField(child=serializers.EmailField())
    job_requisition_id = serializers.UUIDField()

    def validate_emails(self,value):
        if not value:
            raise serializers.ValidationError("Email list cannot be empty")
        return value