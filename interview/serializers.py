from rest_framework import serializers
from .models import InterviewQuestion,JobRequisition,InterviewTemplate

class InterviewQuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for InterviewQuestion model
    """

    class Meta:
        model = InterviewQuestion
        fields =['id','question_type','question_text','recruiter_url','prep_time_seconds','response_time_seconds','retake_attempts','display_order']

class InterviewTemplateSerializer(serializers.ModelSerializer):
    """
    Serializer for InterviewTemplate model
    """

    questions = InterviewQuestionSerializer(many=True)

    class Meta:
        model = InterviewTemplate
        fields = ['id','name','organization','questions','created_at']
        read_only_fields =['creator','organization']
    
    def create(self, validated_data):
        user = self.context['request'].user
        questions_data = validated_data.pop('questions')
        template = InterviewTemplate.objects.create(
            **validated_data)
        for question_data in questions_data:
            InterviewQuestion.objects.create(template=template, **question_data)
        return template

class JobRequisitionSerializer(serializers.ModelSerializer):
    """
    serializer for JobRequisition model
    """
    class Meta:
        model = JobRequisition
        fields = ['id','title','organization','description','status']
        read_only_fields = ['organization']