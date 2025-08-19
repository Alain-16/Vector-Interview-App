from django.db import models
from django.conf import settings
import uuid
#from account.models import organization


class JobRequisition(models.Model):
    """
    Represents a job requisition or opening within an organization
    """

    class Status(models.TextChoices):
        DRAFT = 'Draft','Draft'
        OPEN = 'Open','Open'
        CLOSED = 'Closed','Closed'
    
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    organization = models.ForeignKey('account.organization', on_delete=models.CASCADE, related_name='job_requisitions')
    title = models.CharField(max_length=255)
    description = models.TextField(null=True,blank=True)
    status = models.CharField(max_length=30,choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.organization.name})"

class InterviewTemplate(models.Model):
    """
    An interview template set of questions
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey('account.organization', on_delete=models.CASCADE, related_name='interview_template')
    creator = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL, null=True, blank=True,related_name='created_template')
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class InterviewQuestion(models.Model):
    """
    An individual interview question within a template
    """
    class QuestionType(models.TextChoices):
        VIDEO ='Video','Video'
        TEXT = 'Text','Text'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(InterviewTemplate, on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=20,choices=QuestionType.choices, default=QuestionType.VIDEO)
    question_text = models.TextField(null=True,blank=True)
    recruiter_url = models.URLField(max_length=512, null=True,blank=True)
    prep_time_seconds = models.PositiveIntegerField(default=60)
    response_time_seconds = models.PositiveIntegerField(default=120)
    retake_attempts = models.PositiveIntegerField(default=1)
    display_order = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order']
    
    def __str__(self):
        return f"Q{self.display_order}: {self.question_text[:50]}..."
