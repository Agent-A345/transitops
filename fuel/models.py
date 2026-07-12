from django.db import models
from vehicles.models import Vehicle


class FuelLog(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    liters = models.FloatField()
    cost = models.FloatField()
    date = models.DateField()
    odometer_at_fill = models.FloatField(default=0)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.vehicle} - {self.liters}L on {self.date}"

    def cost_per_liter(self):
        return round(self.cost / self.liters, 2) if self.liters > 0 else 0


class Expense(models.Model):
    EXPENSE_TYPES = [
        ('toll', 'Toll'),
        ('maintenance', 'Maintenance'),
        ('parking', 'Parking'),
        ('fine', 'Fine'),
        ('other', 'Other'),
    ]
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=EXPENSE_TYPES)
    amount = models.FloatField()
    date = models.DateField()
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.vehicle} - {self.type} ₹{self.amount}"
