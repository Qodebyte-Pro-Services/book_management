from rest_framework import permissions

class IsTeacherOrAdmin(permissions.BasePermission):
    """
    Permission to only allow teachers or admins to access the view.
    """
    
    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False
        
        # Allow if user is admin or teacher
        return request.user.role in ['admin', 'teacher']

class IsAdminOnly(permissions.BasePermission):
    """
    Permission to only allow admins to access the view.
    """
    
    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False
        
        # Allow if user is admin
        return request.user.role == 'admin'

class IsTeacherWithFullAccess(permissions.BasePermission):
    """
    Permission to only allow teachers with full access.
    """
    
    def has_permission(self, request, view):
        # Check if user is authenticated and is a teacher with full access
        if not request.user.is_authenticated or request.user.role != 'teacher':
            return False
        
        # Check if teacher has full access
        return hasattr(request.user, 'teacher_profile') and request.user.teacher_profile.access_level == 'full'

class IsTeacherWithLimitedAccess(permissions.BasePermission):
    """
    Permission to only allow teachers with at least limited access.
    """
    
    def has_permission(self, request, view):
        # Check if user is authenticated and is a teacher
        if not request.user.is_authenticated or request.user.role != 'teacher':
            return False
        
        # Check if teacher has at least limited access
        return hasattr(request.user, 'teacher_profile') and request.user.teacher_profile.access_level in ['limited', 'full']

class IsTeacherWithClassOnlyAccess(permissions.BasePermission):
    """
    Permission to only allow teachers with class-only access.
    """
    
    def has_permission(self, request, view):
        # Check if user is authenticated and is a teacher
        if not request.user.is_authenticated or request.user.role != 'teacher':
            return False
        
        # All teachers can access their own classes
        return hasattr(request.user, 'teacher_profile')

class IsOwnProfileOrAdmin(permissions.BasePermission):
    """
    Permission to only allow users to edit their own profile or admins to edit any profile.
    """
    
    def has_object_permission(self, request, view, obj):
        # Admin can edit any profile
        if request.user.role == 'admin':
            return True
        
        # Teachers can only edit their own profile
        if hasattr(request.user, 'teacher_profile'):
            return obj.id == request.user.teacher_profile.id
        
        return False
