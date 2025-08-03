# notifications/models.py

from django.db import models
from django.conf import settings

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('Booking Request', 'Booking Request'),
        ('New Booking Request', 'New Booking Request'),
        ('Booking Confirmation', 'Booking Confirmation'),
        ('Booking Rejection', 'Booking Rejection'),
        ('Cancellation Request', 'Cancellation Request'),
        ('Booking Cancellation', 'Booking Cancellation'),
        ('Booking Approved', 'Booking Approved'),
        ('Cancellation Approved', 'Cancellation Approved'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.notification_type} for {self.user.username} at {self.created_at}"

    class Meta:
        ordering = ['-created_at']  # Newest notifications first
