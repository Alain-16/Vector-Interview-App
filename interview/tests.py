from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from account.models import User, organization
from .models import JobRequisition, InterviewTemplate, InterviewQuestion

class InterviewAPITests(APITestCase):
    """
    Test suite for the JobRequisition and InterviewTemplate API endpoints.
    """

    def setUp(self):
        """
        Set up initial data for the tests, including two separate organizations and users.
        """
        # Create Organization 1 and User 1
        self.org1 = organization.objects.create(name="Test Corp")
        self.user1 = User.objects.create_user(
            email="recruiter1@testcorp.com",
            name="Recruiter One",
            password="password123",
            role="Recruiter",
            organization=self.org1
        )

        # Create Organization 2 and User 2
        self.org2 = organization.objects.create(name="Another Corp")
        self.user2 = User.objects.create_user(
            email="recruiter2@anothercorp.com",
            name="Recruiter Two",
            password="password123",
            role="Recruiter",
            organization=self.org2
        )

        # Authenticate as User 1
        self.client.force_authenticate(user=self.user1)

        # Data payloads
        self.job_data = {
            "title": "Senior Python Developer",
            "description": "A job for a senior developer.",
            "status": "Open"
        }
        self.template_data = {
            "name": "Standard Python Dev Template",
            "questions": [
                {
                    "question_type": "Video",
                    "question_text": "Tell us about a challenging project.",
                    "prep_time_seconds": 30,
                    "response_time_seconds": 180,
                    "retake_attempts": 1,
                    "display_order": 1
                },
                {
                    "question_type": "Text",
                    "question_text": "What are your salary expectations?",
                    "prep_time_seconds": 15,
                    "response_time_seconds": 60,
                    "retake_attempts": 0,
                    "display_order": 2
                }
            ]
        }

    # --- Job Requisition Tests ---

    def test_create_job_requisition(self):
        """
        Ensure an authenticated user can create a job requisition for their organization.
        """
        url = reverse('job-requisition-list')
        response = self.client.post(url, self.job_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(JobRequisition.objects.count(), 1)
        self.assertEqual(JobRequisition.objects.get().organization, self.org1)

    def test_list_job_requisitions_for_own_org(self):
        """
        Ensure a user can only list job requisitions from their own organization.
        """
        # Create a job for the user's org
        JobRequisition.objects.create(organization=self.org1, title="Job 1")
        # Create a job for the other org
        JobRequisition.objects.create(organization=self.org2, title="Job 2")

        url = reverse('job-requisition-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Job 1")

    def test_cannot_access_other_org_job(self):
        """
        Ensure a user cannot retrieve a job requisition from another organization.
        """
        job_for_org2 = JobRequisition.objects.create(organization=self.org2, title="Job 2")
        url = reverse('job-requisition-detail', kwargs={'pk': job_for_org2.pk})
        response = self.client.get(url, format='json')
        # We expect a 404 because the queryset in the view filters by the user's org
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # --- Interview Template Tests ---

    def test_create_interview_template_with_questions(self):
        """
        Ensure a user can create an interview template with nested questions.
        """
        url = reverse('interview-template-list')
        response = self.client.post(url, self.template_data, format='json')
        if response.status_code != status.HTTP_201_CREATED:
            print("Validation Errors:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(InterviewTemplate.objects.count(), 1)
        self.assertEqual(InterviewQuestion.objects.count(), 2)
        template = InterviewTemplate.objects.get()
        self.assertEqual(template.organization, self.user1.organization)
        self.assertEqual(template.creator, self.user1)

    def test_list_interview_templates_for_own_org(self):
        """
        Ensure a user can only list templates from their own organization.
        """
        InterviewTemplate.objects.create(organization=self.org1, creator=self.user1, name="Template 1")
        InterviewTemplate.objects.create(organization=self.org2, creator=self.user2, name="Template 2")

        url = reverse('interview-template-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Template 1")

    def test_unauthenticated_access_is_denied(self):
        """
        Ensure unauthenticated users cannot access any interview endpoints.
        """
        self.client.force_authenticate(user=None) # Log out the user
        url = reverse('job-requisition-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        url = reverse('interview-template-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

