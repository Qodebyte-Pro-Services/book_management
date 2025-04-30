from django.contrib import admin
from .models import School

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('school_name', 'school_type', 'admin', 'created_at')
    search_fields = ('school_name', 'admin__email')
    list_filter = ('school_type',)
