from django.contrib import admin
from .models import Teacher, TeacherAttendance, TeacherClassAssignment

class TeacherClassAssignmentInline(admin.TabularInline):
    model = TeacherClassAssignment
    extra = 1

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'first_name', 'last_name', 'school', 'highest_certificate', 'joining_date', 'is_active')
    list_filter = ('is_active', 'school', 'gender', 'access_level')
    search_fields = ('first_name', 'last_name', 'employee_id', 'highest_certificate')
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'school')
        }),
        ('Basic Information', {
            'fields': ('employee_id', 'first_name', 'last_name', 'date_of_birth', 'gender', 'profile_image')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'address', 'state', 'city')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_relationship', 'emergency_contact_phone')
        }),
        ('Qualification', {
            'fields': ('highest_certificate', 'school_name', 'graduation_year')
        }),
        ('Work Experience', {
            'fields': ('previous_workplace', 'job_title', 'job_duration', 'job_reference_contact')
        }),
        ('School Details', {
            'fields': ('joining_date', 'salary', 'is_active', 'access_level')
        }),
    )
    inlines = [TeacherClassAssignmentInline]

@admin.register(TeacherAttendance)
class TeacherAttendanceAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'date', 'is_present')
    list_filter = ('is_present', 'date')
    search_fields = ('teacher__first_name', 'teacher__last_name', 'teacher__employee_id')

@admin.register(TeacherClassAssignment)
class TeacherClassAssignmentAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'assigned_class', 'is_primary')
    list_filter = ('is_primary', 'assigned_class__school')
    search_fields = ('teacher__first_name', 'teacher__last_name', 'assigned_class__name')
