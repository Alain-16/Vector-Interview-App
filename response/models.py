from django.db import models
from django.conf import settings
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q, CheckConstraint

class Candidate(models.Model):
    """
    Represents an interview candidate
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField()
    name = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class InterviewSession(models.Model):
    """
    A single candidate's interview session for a specific job requisition
    """

    class Status(models.TextChoices):
        INVITED = 'Invited','Invited'
        STARTED = 'Started','Started'
        COMPLETED = 'Completed','Completed'
        REVIEWED = 'Reviewed','Reviewed'

    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='interview_sessions')
    job_requisition = models.ForeignKey('interview.JobRequisition', on_delete=models.CASCADE, related_name='interview_sessions')
    unique_access_token = models.CharField(max_length=64, unique=True,db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.INVITED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Session for{self.candidate.email} on {self.job_requisition.title}"

class InterviewResponse(models.Model):
    """
    A candidate's response to a single interview question
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='responsesSession')
    question = models.ForeignKey('interview.InterviewQuestion', on_delete=models.CASCADE, related_name='responses')
    video_url = models.URLField(max_length=512, blank=True,null=True)
    text_response = models.TextField(blank=True,null=True)

    #AI analysis fields
    transcription = models.TextField(blank=True,null=True)
    sentiment_analysis = models.JSONField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints =[
            CheckConstraint(
                check=(
                    Q(video_url__isnull=False, text_response__isnull=True) |
                    Q(video_url__isnull=True, text_response__isnull=False)
                ),
                name='either_video_or_text_response_required'
            )
        ]

    def __str__(self):
        return f"Response by {self.session.candidate.email} to QID {self.question.id}"

class Evaluation(models.Model):

    """
    An evaluator's feedback on a candidate's response
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    response = models.ForeignKey(InterviewResponse, on_delete=models.CASCADE, related_name='evaluations')
    evaluator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,related_name='evaluations')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comments = models.TextField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('response', 'evaluator')
    
    def __str__(self):
        return f"Evaluation by {self.evaluator.email} for {self.response.id}"
    
        
