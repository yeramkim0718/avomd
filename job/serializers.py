from rest_framework import serializers
from .models import Job


class JobCreateSerializer(serializers.Serializer):
    text = serializers.CharField()


class JobCreateResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ["event_id"]


class JobStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ["event_id", "status", "result"]
