from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    JobCreateSerializer,
    JobStatusSerializer,
    JobCreateResponseSerializer,
    JobSerializer,
)
from .models import Job
from .tasks import process_job
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from django.shortcuts import get_object_or_404


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


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    lookup_field = 'event_id'

    def create(self, request, *args, **kwargs):
        """POST /jobs 엔드포인트"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        job = serializer.save()
        
        # Celery 태스크 실행
        process_job.delay(str(job.event_id))
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        """GET /jobs/{event_id} 엔드포인트"""
        job = get_object_or_404(Job, event_id=kwargs['event_id'])
        serializer = self.get_serializer(job)
        return Response(serializer.data)
