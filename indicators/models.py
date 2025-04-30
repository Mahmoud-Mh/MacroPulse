from django.db import models
from django.utils import timezone


class Indicator(models.Model):
    """
    Model to store macroeconomic indicators like interest rates, inflation, PMI, etc.
    """
    name = models.CharField(max_length=100, help_text="Name of the indicator (e.g. 'Interest Rate')")
    country = models.CharField(max_length=100, help_text="Country or region the indicator belongs to")
    value = models.DecimalField(
        max_digits=12, 
        decimal_places=4,
        help_text="Current value of the indicator"
    )
    previous_value = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Previous value of the indicator"
    )
    unit = models.CharField(
        max_length=50,
        help_text="Unit of measurement (e.g. '%', 'USD', 'Points')"
    )
    frequency = models.CharField(
        max_length=50,
        help_text="Update frequency (e.g. 'Daily', 'Monthly', 'Quarterly')"
    )
    last_update = models.DateTimeField(
        default=timezone.now,
        help_text="Last time the indicator was updated"
    )
    source = models.CharField(
        max_length=100,
        default="Trading Economics",
        help_text="Source of the indicator data"
    )
    category = models.CharField(
        max_length=100,
        help_text="Category of the indicator (e.g. 'Monetary', 'Economic Growth', 'Trade')"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of what the indicator measures"
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['country', 'name']),
            models.Index(fields=['category']),
            models.Index(fields=['last_update']),
        ]
        unique_together = ['country', 'name']
        ordering = ['-last_update']
    
    def __str__(self):
        return f"{self.country} - {self.name}: {self.value} {self.unit}"
    
    def save(self, *args, **kwargs):
        if self.pk:  # If updating existing record
            old_record = Indicator.objects.get(pk=self.pk)
            self.previous_value = old_record.value
        super().save(*args, **kwargs)

class Task(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]
    
    SCHEDULE_CHOICES = [
        ('manual', 'Manual'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    schedule = models.CharField(max_length=10, choices=SCHEDULE_CHOICES, default='manual')
    created_at = models.DateTimeField(auto_now_add=True)
    last_run = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.status})"
