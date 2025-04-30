
from django.contrib.auth import get_user_model
from rest_framework import permissions
from schools.models import School

User = get_user_model()

class IsSchoolAdmin(permissions.BasePermission):
    """
    Permission to only allow school admins to access objects in their school.
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if the object is a School
        if hasattr(obj, 'admin'):
            # For School objects
            return obj.admin == request.user
        
        # For objects that belong to a school (like Class, Student, etc.)
        if hasattr(obj, 'school'):
            # Check if user is the admin of the school this object belongs to
            return obj.school.admin == request.user
        
        # For other objects, deny permission
        return False