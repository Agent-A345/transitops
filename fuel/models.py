from django.db import models
from vehicles.models import Vehicle

class FuelLog(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    liters = models.FloatField()
    cost = models.FloatField()
    date = models.DateField()

    def __str__(self):
        return f"{self.vehicle} - {self.liters}L"

class Expense(models.Model):
    EXPENSE_TYPES = [
        ('toll', 'Toll'),
        ('maintenance', 'Maintenance'),
        ('other', 'Other'),
    ]
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=EXPENSE_TYPES)
    amount = models.FloatField()
    date = models.DateField()
    note = models.TextField(blank=True)