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