from django.db import models
from vehicles.models import Vehicle
from drivers.models import Driver


class Trip(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('dispatched', 'Dispatched'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT)
    driver = models.ForeignKey(Driver, on_delete=models.PROTECT)
    cargo_weight = models.FloatField(help_text="in kg")
    planned_distance = models.FloatField(help_text="in km")
    revenue = models.FloatField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    dispatched_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    final_odometer = models.FloatField(null=True, blank=True)
    fuel_consumed = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.source} → {self.destination} ({self.status})"

    def fuel_efficiency(self):
        if self.fuel_consumed and self.fuel_consumed > 0 and self.planned_distance:
            return round(self.planned_distance / self.fuel_consumed, 2)
        return None
