from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    JobCreateSerializer,
    JobStatusSerializer,
    JobCreateResponseSerializer,
)
from .models import Job
from .tasks import process_job
from drf_spectacular.utils import extend_schema


class JobCreateView(APIView):
    @extend_schema(
        summary="Create a new job",
        description="Create a new job with the given input text",
        request=JobCreateSerializer,
        responses={202: JobCreateResponseSerializer},
    )
    def post(self, request):
        serializer = JobCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        input_text = serializer.validated_data["text"]

        job = Job.objects.create(input_text=input_text)
        process_job.delay(str(job.event_id))
        serializer = JobCreateResponseSerializer(job)

        return Response(
            {"event_id": str(job.event_id)}, status=status.HTTP_202_ACCEPTED
        )


class JobStatusView(APIView):
    @extend_schema(
        summary="Get the status of a job",
        description="Get the status of a job with the given event_id",
        responses={200: JobStatusSerializer},
    )
    def get(self, request, event_id):
        try:
            job = Job.objects.get(event_id=event_id)
        except Job.DoesNotExist:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = JobStatusSerializer(job)
        return Response(serializer.data)
