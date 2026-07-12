from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('fleet_manager', 'Fleet Manager'),
        ('dispatcher', 'Dispatcher'),
        ('safety_officer', 'Safety Officer'),
        ('financial_analyst', 'Financial Analyst'),
    ]
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='fleet_manager')

    def is_fleet_manager(self):
        return self.role == 'fleet_manager'

    def is_dispatcher(self):
        return self.role == 'dispatcher'

    def is_safety_officer(self):
        return self.role == 'safety_officer'

    def is_financial_analyst(self):
        return self.role == 'financial_analyst'

    def can_manage_fleet(self):
        return self.role in ['fleet_manager']

    def can_dispatch(self):
        return self.role in ['fleet_manager', 'dispatcher']

    def can_view_financials(self):
        return self.role in ['fleet_manager', 'financial_analyst']

    def can_view_safety(self):
        return self.role in ['fleet_manager', 'safety_officer']
