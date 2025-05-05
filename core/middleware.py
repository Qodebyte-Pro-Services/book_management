from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden



class TenantMiddleware(MiddlewareMixin):
    """
    Middleware to handle multi-tenancy using the filtering approach.
    This middleware sets the current school based on the user's association.
    """
    
    def process_request(self, request):
        # Skip for authentication-related paths
        path = request.path_info
        if path.startswith('/api/users/register') or path.startswith('/api/users/verify') or \
           path.startswith('/api/users/login') or path.startswith('/admin'):
            return None
        
        # Skip for unauthenticated users
        if not request.user.is_authenticated:
            return None
        
        # Add debug print
       # print(f"TenantMiddleware: Processing request for user {request.user.email}, role: {request.user.role}")
        
        # Check if user is an admin and is trying to create a school
        if request.user.role == 'admin' and request.path_info == '/api/schools/create/':
           # print("TenantMiddleware: Allowing admin to create school")
            return None  # Allow access to create school
        
        # Try to get the school
        try:
            # Check if user is an admin with a school
            from schools.models import School
            school = School.objects.filter(admin=request.user).first()
            
            if school:
                #print(f"TenantMiddleware: Found school {school.school_name} for admin user")
                request.school = school
            else:
                # Check if user is a teacher
                if hasattr(request.user, 'teacher_profile'):
                    school = request.user.teacher_profile.school
                    #print(f"TenantMiddleware: Found school {school.school_name} for teacher user")
                    request.school = school
                # Check if user is a student
                elif hasattr(request.user, 'student_profile'):
                    school = request.user.student_profile.school
                    #print(f"TenantMiddleware: Found school {school.school_name} for student user")
                    request.school = school
                # For superusers without a school, allow access
                elif request.user.is_superuser:
                   # print("TenantMiddleware: Superuser without school, allowing access")
                    request.school = None
                else:
                    # For regular users without a school, deny access
                   # print("TenantMiddleware: Regular user without school, denying access")
                    return HttpResponseForbidden("You don't have access to any school")
        except Exception as e:
            #print(f"TenantMiddleware: Error setting school: {str(e)}")
            # For debugging only - in production you might want to return an error
            request.school = None
        
        return None

