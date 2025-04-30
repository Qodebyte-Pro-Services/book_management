from django.db import models
from django.conf import settings
from schools.models import School
from students.models import Class

class Teacher(models.Model):
    # Relationship fields
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teacher_profile')
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='teachers')
    
    # Basic Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    profile_image = models.ImageField(upload_to='teachers/profiles/', null=True, blank=True)
    
    # Contact Information
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    
    # Emergency Contact Information
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_relationship = models.CharField(max_length=50)
    emergency_contact_phone = models.CharField(max_length=20)
    
    # Qualification Information
    highest_certificate = models.CharField(max_length=100)
    school_name = models.CharField(max_length=200)
    graduation_year = models.IntegerField()
    
    # Work Experience Information
    previous_workplace = models.CharField(max_length=200, blank=True, null=True)
    job_title = models.CharField(max_length=100, blank=True, null=True)
    job_duration = models.CharField(max_length=50, blank=True, null=True)  # e.g., "2 years"
    job_reference_contact = models.CharField(max_length=100, blank=True, null=True)
    
    # School-specific Information
    employee_id = models.CharField(max_length=50, unique=False)
    joining_date = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    
    # Access Control
    ACCESS_LEVEL_CHOICES = [
        ('full', 'Full Access'),
        ('limited', 'Limited Access'),
        ('class_only', 'Class Only Access')
    ]
    access_level = models.CharField(max_length=10, choices=ACCESS_LEVEL_CHOICES, default='limited')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['school', 'employee_id']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.employee_id}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class TeacherClassAssignment(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='class_assignments')
    assigned_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='assigned_teachers')
    is_primary = models.BooleanField(default=False)  # Whether this teacher is the primary teacher for this class
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['teacher', 'assigned_class']
        
        
    def __str__(self):
        return f"{self.teacher.full_name} - {self.assigned_class.class_name}"

class TeacherAttendance(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    is_present = models.BooleanField(default=True)
    remarks = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ['teacher', 'date']
    
    def __str__(self):
        status = "Present" if self.is_present else "Absent"
        return f"{self.teacher.full_name} - {self.date} - {status}"
