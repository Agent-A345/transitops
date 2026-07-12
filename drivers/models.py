from django.db import models
from datetime import date


class Driver(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('on_trip', 'On Trip'),
        ('off_duty', 'Off Duty'),
        ('suspended', 'Suspended'),
    ]
    LICENSE_CATEGORIES = [
        ('LMV', 'Light Motor Vehicle'),
        ('HMV', 'Heavy Motor Vehicle'),
        ('HPMV', 'Heavy Passenger Motor Vehicle'),
        ('MGV', 'Medium Goods Vehicle'),
    ]
    name = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50, unique=True)
    license_category = models.CharField(max_length=20, choices=LICENSE_CATEGORIES)
    license_expiry = models.DateField()
    contact = models.CharField(max_length=15)
    safety_score = models.FloatField(default=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def is_license_valid(self):
        return self.license_expiry >= date.today()

    def days_until_expiry(self):
        return (self.license_expiry - date.today()).days

    def license_status(self):
        days = self.days_until_expiry()
        if days < 0:
            return 'expired'
        elif days <= 30:
            return 'expiring_soon'
        return 'valid'
