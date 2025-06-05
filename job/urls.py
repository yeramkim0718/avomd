from django.urls import path
from .views import JobCreateView, JobStatusView

urlpatterns = [
    path("", JobCreateView.as_view(), name="job-create"),
    path("<uuid:event_id>/", JobStatusView.as_view(), name="job-status"),
]
