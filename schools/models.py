from django.db import models
from django.conf import settings



class School(models.Model):
    SCHOOL_TYPE_CHOICES = [
        ('nursery school', 'Nursery school'),
        ('primary school', 'Primary school'),
        ('secondary school', 'Secondary school'),
        ('nursery, primary school', 'Nursery, primary school'),
        ('nursery, primary, secondary school', 'Nursery, primary, secondary school'),

    ]
    
    school_name = models.CharField(max_length=255, unique=True)
    address = models.TextField()
    description = models.TextField()
    school_type = models.CharField(max_length=100, choices=SCHOOL_TYPE_CHOICES, default = 'nursery school')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # The admin user who created this school
    admin = models.OneToOneField (settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='school')
    
    def __str__(self):
        return self.school_name

