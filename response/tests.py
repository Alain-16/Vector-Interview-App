from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from account.models import User, organization
from interview.models import JobRequisition,InterviewQuestion,InterviewTemplate
from .models import InterviewResponse,InterviewSession,Candidate

class ResponseAPITests(APITestCase):
    """
    Test suite for the candidate invitation and evaluation workflow.
    """

    def setUp(self):
        """
        Set up a complete scenario with two orgs, a recruiter, an evaluator, a job, and a submission.
        """
        # Organization 1 setup
        self.org1 = organization.objects.create(name="Innovate Inc.")
        self.recruiter = User.objects.create_user(
            email="recruiter@innovate.com", name="Recruiter Innovate", password="password123",
            role="Recruiter", organization=self.org1
        )
        self.evaluator = User.objects.create_user(
            email="evaluator@innovate.com", name="Evaluator Innovate", password="password123",
            role="Evaluator", organization=self.org1
        )

        # Organization 2 setup
        self.org2 = organization.objects.create(name="Global Tech")
        self.other_recruiter = User.objects.create_user(
            email="recruiter@global.com", name="Recruiter Global", password="password123",
            role="Recruiter", organization=self.org2
        )

        # Create a Job Requisition for Org 1
        self.job = JobRequisition.objects.create(organization=self.org1, title="Backend Developer")

        # Create a candidate and a complete interview session with a response
        self.candidate = Candidate.objects.create(email="candidate@test.com", name="Test Candidate")
        self.session = InterviewSession.objects.create(
            candidate=self.candidate, job_requisition=self.job,
            unique_access_token="test-token-123", status="Completed"
        )
        template = InterviewTemplate.objects.create(organization=self.org1, name="Dev Template")
        self.question = InterviewQuestion.objects.create(template=template, question_text="Q1", display_order=1)
        self.response = InterviewResponse.objects.create(
            session=self.session, question=self.question,
            video_url="http://example.com/video.mp4"
        )

        # Authenticate as the recruiter from Org 1
        self.client.force_authenticate(user=self.recruiter)

    def test_invite_candidates(self):
        """
        Ensure a recruiter can invite candidates to a job in their organization.
        """
        url = reverse('invite-candidate')
        data = {
            "emails": ["new.candidate1@test.com", "new.candidate2@test.com"],
            "job_requisition_id": str(self.job.id)
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 2)
        self.assertTrue(Candidate.objects.filter(email="new.candidate1@test.com").exists())
        self.assertEqual(InterviewSession.objects.filter(job_requisition=self.job).count(), 3) # 1 existing + 2 new

    def test_cannot_invite_to_other_org_job(self):
        """
        Ensure a recruiter cannot invite candidates to a job in another organization.
        """
        other_job = JobRequisition.objects.create(organization=self.org2, title="Other Job")
        url = reverse('invite-candidate')
        data = {
            "emails": ["another.candidate@test.com"],
            "job_requisition_id": str(other_job.id)
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_submissions_for_job(self):
        """
        Ensure a user can list all submissions for a job in their organization.
        """
        # This URL is custom from the ViewSet's 'for_job' action
        url = reverse('submissions-for-job', kwargs={'job_id': self.job.id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if response.status_code != status.HTTP_200_OK:
            print("Validation Errors:",response.data)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['candidate']['email'], self.candidate.email)

    def test_retrieve_submission_detail(self):
        """
        Ensure a user can retrieve the full details of a submission.
        """
        url = reverse('submissions-detail', kwargs={'pk': self.session.pk})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['candidate']['name'], self.candidate.name)
        self.assertEqual(len(response.data['responses']), 1)
        self.assertEqual(response.data['responses'][0]['video_url'], self.response.video_url)

    def test_create_evaluation(self):
        """
        Ensure an authenticated user (e.g., an evaluator) can submit an evaluation.
        """
        # Authenticate as the evaluator to submit feedback
        self.client.force_authenticate(user=self.evaluator)
        
        # This URL is custom from the nested router
        url = reverse('response-evaluations', kwargs={'response_pk': self.response.id})
        data = {
            "rating": 5,
            "comments": "Excellent response, very clear."
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        if response.status_code != status.HTTP_201_CREATED:
            print("Validation Errors:",response.data)
        self.assertEqual(self.response.evaluations.count(), 1)
        self.assertEqual(self.response.evaluations.first().evaluator, self.evaluator)
        self.assertEqual(self.response.evaluations.first().rating, 5)


