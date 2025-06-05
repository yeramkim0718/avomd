from django.db import models
import uuid


class Job(models.Model):
    event_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    input_text = models.TextField()
    status = models.CharField(max_length=20, default="queued")
    result = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
