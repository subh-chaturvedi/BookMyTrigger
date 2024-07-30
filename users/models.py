from django.contrib.auth.models import User
from django.db import models

class Trigger(models.Model):
    STATUS_CHOICES = [
        ('created', 'Created'),
        ('deleted', 'Deleted'),
        ('triggered', 'Triggered'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='created')

    def __str__(self):
        return f"{self.user.username} - {self.value} - {self.status}"

class BTCPrice(models.Model):
    price = models.DecimalField(max_digits=20, decimal_places=8)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.price} at {self.timestamp}"
