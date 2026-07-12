from django.db import models


class Vehicle(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('on_trip', 'On Trip'),
        ('in_shop', 'In Shop'),
        ('retired', 'Retired'),
    ]
    TYPE_CHOICES = [
        ('van', 'Van'),
        ('truck', 'Truck'),
        ('bike', 'Bike'),
        ('car', 'Car'),
    ]
    registration_number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    max_load_capacity = models.FloatField(help_text="in kg")
    odometer = models.FloatField(default=0)
    acquisition_cost = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.registration_number} - {self.name}"

    def total_fuel_cost(self):
        return sum(log.cost for log in self.fuellog_set.all())

    def total_maintenance_cost(self):
        return sum(m.cost for m in self.maintenancelog_set.filter(status='resolved'))

    def total_operational_cost(self):
        return self.total_fuel_cost() + self.total_maintenance_cost()

    def total_revenue(self):
        return sum(t.revenue for t in self.trip_set.filter(status='completed') if t.revenue)

    def roi(self):
        if self.acquisition_cost and self.acquisition_cost > 0:
            return round(((self.total_revenue() - self.total_operational_cost()) / self.acquisition_cost) * 100, 2)
        return 0
