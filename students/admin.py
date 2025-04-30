from django.contrib import admin
from .models import Class, Student, StudentAttendance

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('class_name', 'school', 'created_at')
    list_filter = ('school',)
    search_fields = ('school_name', 'description')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('registration_number', 'first_name', 'last_name', 'class_assigned', 'school', 'admission_date', 'is_active')
    list_filter = ('is_active', 'school', 'class_assigned', 'gender')
    search_fields = ('first_name', 'last_name', 'registration_number', 'parent_name', 'parent_email')

@admin.register(StudentAttendance)
class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'is_present')
    list_filter = ('is_present', 'date', 'student__class_assigned')
    search_fields = ('student__first_name', 'student__last_name', 'student__registration_number')
