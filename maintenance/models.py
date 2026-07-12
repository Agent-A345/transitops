from django.db import models
from vehicles.models import Vehicle

class MaintenanceLog(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    issue = models.TextField()
    cost = models.FloatField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.vehicle} - {self.status}"