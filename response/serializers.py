from rest_framework import serializers
from interview.serializers import InterviewQuestionSerializer
from account.serializers import UserSerializer
from .models import Candidate, InterviewSession, InterviewResponse, Evaluation

#from .models import Candidate, InterviewSession

class CandidateInvitationSerializer(serializers.Serializer):
    """
    Serializer for inviting Candidate model
    """
    emails = serializers.ListField(child=serializers.EmailField())
    job_requisition_id = serializers.UUIDField()

    def validate_emails(self,value):
        if not value:
            raise serializers.ValidationError("Email list cannot be empty")
        return value


class EvaluationSerializer(serializers.ModelSerializer):
    """
    Serializer for Evaluation Model
    """
    evaluator = UserSerializer(read_only=True)
    class Meta:
        model = Evaluation
        fields = ['id','evaluator','response','comments','rating']
        read_only_fields = ['response']

class ResponseSerializer(serializers.ModelSerializer):
    """
    Interview response serializer for a single response including all evaluations
    """
    evaluations = EvaluationSerializer(many=True,read_only=True)
    question = InterviewQuestionSerializer(read_only=True)

    class Meta:
        model = InterviewResponse
        fields = ['id', 'question','video_url','text_response','transcription','sentiment_analysis','created_at','evaluations']
        
class CandidateSerializer(serializers.ModelSerializer):
    """
    Serializer for candidate model
    """
    class Meta:
        model = Candidate
        fields =['id', 'name' ,'email']

class InterviewSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for interview session
    The main serializer for the "Candidate Profile View".
    Shows candidate info and all their detailed responses.
    """
    candidate = CandidateSerializer(read_only=True)
    responses = ResponseSerializer(many=True, read_only=True)
    
    class Meta:
        model = InterviewSession
        fields = ['id' ,'candidate','responses','status','created_at']
        read_only_fields = ['job_requisition']

class InterviewSessionListSerializer(serializers.ModelSerializer):
    """
    A lighter weight serializer for listing interview sessions without detailed responses
    """
    candidate = CandidateSerializer(read_only=True)
    
    class Meta:
        model = InterviewSession
        fields = ['id','candidate', 'status' ,'created_at']
