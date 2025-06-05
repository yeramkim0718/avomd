from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from job.models import Job
import time
import pytest
from celery.result import EagerResult


class JobsApiTests(APITestCase):
    def test_create_job_api_speed(self):
        url = reverse("job-create")
        data = {"text": "속도 테스트"}
        start = time.time()
        response = self.client.post(url, data, format="json")
        elapsed = (time.time() - start) * 1000  # ms 단위
        print(f"API 응답 시간: {elapsed:.2f}ms")
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertLess(
            elapsed, 200, f"API 응답이 200ms를 초과했습니다: {elapsed:.2f}ms"
        )

    def test_create_job(self):
        url = reverse("job-create")
        data = {"text": "create job"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn("event_id", response.data)
        event_id = response.data["event_id"]
        self.assertTrue(Job.objects.filter(event_id=event_id).exists())

    def test_create_job_invalid_input(self):
        url = reverse("job-create")
        data = {}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_job_status_pending(self):
        job = Job.objects.create(input_text="test input")
        event_id = str(job.event_id)
        url = reverse("job-status", kwargs={"event_id": event_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("status", response.data)
        self.assertEqual(response.data["status"], "queued")

    def test_get_job_status_success(self):
        job = Job.objects.create(
            input_text="test input",
            status="SUCCESS",
            result={"summary": "요약", "checklist": ["a", "b"]},
        )
        event_id = str(job.event_id)
        url = reverse("job-status", kwargs={"event_id": event_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "SUCCESS")
        self.assertIn("result", response.data)
        self.assertIn("summary", response.data["result"])
        self.assertIn("checklist", response.data["result"])

    def test_get_job_status_not_found(self):
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        url = reverse("job-status", kwargs={"event_id": fake_uuid})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_process_job_task(self):
        from job.tasks import process_job

        job = Job.objects.create(input_text="celery 직접 호출 테스트")
        process_job(str(job.event_id))  # delay() 대신 직접 호출
        job.refresh_from_db()
        self.assertEqual(job.status, "SUCCESS")
        self.assertIn("summary", job.result)
        self.assertIn("checklist", job.result)
