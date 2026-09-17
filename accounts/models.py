from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = 'CUSTOMER', 'Customer'
        PROVIDER = 'PROVIDER', 'Service Provider'
        ADMIN = 'ADMIN', 'Administrator'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    phone = models.CharField(max_length=15, blank=True, null=True)

    @property
    def is_customer_user(self):
        return self.role == self.Role.CUSTOMER

    @property
    def is_provider_user(self):
        return self.role == self.Role.PROVIDER

    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN or self.is_superuser


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"Customer Profile: {self.user.username}"


class ProviderProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='provider_profile')
    service_category = models.ForeignKey('services.ServiceCategory', on_delete=models.SET_NULL, null=True, blank=True, related_name='providers')
    experience_years = models.PositiveIntegerField(default=1)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    bio = models.TextField(blank=True, null=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        category_name = self.service_category.name if self.service_category else "Unassigned"
        return f"Provider Profile: {self.user.username} ({category_name})"
