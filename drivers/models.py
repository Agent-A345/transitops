from django.db import models

class Driver(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('on_trip', 'On Trip'),
        ('off_duty', 'Off Duty'),
        ('suspended', 'Suspended'),
    ]
    name = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50, unique=True)
    license_category = models.CharField(max_length=20)
    license_expiry = models.DateField()
    contact = models.CharField(max_length=15)
    safety_score = models.FloatField(default=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        return self.name

    def is_license_valid(self):
        from datetime import date
        return self.license_expiry >= date.today()