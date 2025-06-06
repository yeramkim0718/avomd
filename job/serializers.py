from rest_framework import serializers
from .models import Job


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['event_id', 'input_text', 'status', 'result', 'created_at', 'updated_at']
        read_only_fields = ['event_id', 'status', 'result', 'created_at', 'updated_at']


class JobCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['input_text']


class JobStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['event_id', 'status', 'result']
        read_only_fields = ['event_id', 'status', 'result']


class JobCreateResponseSerializer(serializers.Serializer):
    event_id = serializers.UUIDField()
