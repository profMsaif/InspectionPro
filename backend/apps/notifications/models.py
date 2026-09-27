from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedUUIDModel


class Notification(TimeStampedUUIDModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    action_url = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.title

