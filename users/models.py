from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import timedelta

class UserManager(BaseUserManager):
    def create_user(self, email, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        
        email = self.normalize_email(email)
        
        # Set is_staff to True if role is admin
        role = extra_fields.get('role')
        if role == 'admin':
            extra_fields['is_staff'] = True 
        
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)
        
        return self.create_user(email, full_name, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    full_name = models.CharField(_('username'), max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    
    # User role choices
    ROLE_ADMIN = 'admin'
    ROLE_TEACHER = 'teacher'
    ROLE_STUDENT = 'student'
    ROLE_STAFF = 'staff'
    
    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_TEACHER, 'Teacher'),
        (ROLE_STUDENT, 'Student'),
        (ROLE_STAFF, 'Staff'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_ADMIN)
    
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']
   
    def __str__(self):
        return self.email
    
from django.db.models.signals import pre_save
from django.dispatch import receiver

@receiver(pre_save, sender=User)
def ensure_staff_status(sender, instance, **kwargs):
    """Ensure that admin users always have is_staff=True"""
    if instance.role == User.ROLE_ADMIN and not instance.is_staff:
        instance.is_staff = True

class EmailVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verifications')
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    
    def __str__(self):
        return f"Password reset for {self.user.email}"
    
    def is_valid(self):
        return not self.is_used and self.expires_at > timezone.now()
    
    def can_resend(self):
        """Check if enough time has passed to resend the code (1 minute)"""
        if not self.last_resent_at:
            return True
        
        one_minute_ago = timezone.now() - timedelta(minutes=1)
        return self.last_resent_at < one_minute_ago
   
class PasswordReset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_resets')
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Password reset for {self.user.email}"
    
    def is_valid(self):
        return not self.is_used and self.expires_at > timezone.now()
