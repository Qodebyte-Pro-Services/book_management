from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from .models import Teacher, TeacherClassAssignment, TeacherAttendance
from .serializers import (
    TeacherSerializer, 
    TeacherCreateSerializer, 
    TeacherUpdateSerializer,
    TeacherProfileUpdateSerializer,
    TeacherAttendanceSerializer,
    TeacherClassAssignmentSerializer
)
from schools.permissions import IsSchoolAdmin
from core.permissions import IsTeacherOrAdmin, IsTeacherWithFullAccess
from core.utils import send_teacher_credentials_email
import secrets
import string
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import NotFound


# In teachers/views.py
class TeacherListCreateView(generics.ListCreateAPIView):
    """
    List all teachers or create a new teacher
    """
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'gender', 'access_level']
    search_fields = ['first_name', 'last_name', 'employee_id', 'highest_certificate']
    ordering_fields = ['first_name', 'last_name', 'joining_date', 'salary']
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        # Try to get school from request
        if hasattr(self.request, 'school') and self.request.school:
            school = self.request.school
        else:
            # Fallback: try to get school from user
            from schools.models import School
            school = School.objects.filter(admin=self.request.user).first()
            
            if not school:
                # Return empty queryset if no school found
                return Teacher.objects.none()
        
        # Filter teachers by the current school
        return Teacher.objects.filter(school=school)
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TeacherCreateSerializer
        return TeacherSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsTeacherOrAdmin()]
    
    def perform_create(self, serializer):
        # Try to get school from request
        if hasattr(self.request, 'school') and self.request.school:
            school = self.request.school
        else:
            # Fallback: try to get school from user
            from schools.models import School
            school = School.objects.filter(admin=self.request.user).first()
            
            if not school:
                raise ValidationError("No school found for this user. Please create a school first.")
        
        # Pass the school to the serializer context
        serializer.context['school'] = school
        teacher = serializer.save()  # Save the teacher object
        
        # Use the TeacherSerializer to format the response
        response_serializer = TeacherSerializer(teacher, context=self.get_serializer_context())
        
        # Get the serialized data
        teacher_data = response_serializer.data
        
        # Create the response data
        response_data = {
            'custom_id': teacher_data['custom_id'],  # Add teacher custom_id
            **teacher_data,
        }
        
        # Remove redundant custom_id and user
        response_data.pop('custom_id')
        del response_data['user']
        
        return Response(response_data, status=status.HTTP_201_CREATED)


class TeacherDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a teacher instance
    """
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated, IsSchoolAdmin]
    lookup_field = 'custom_id'  # Use custom_id for lookups
    
    def get_queryset(self):
        # Try to get school from request
        if hasattr(self.request, 'school') and self.request.school:
            school = self.request.school
        else:
            # Fallback: try to get school from user
            from schools.models import School
            school = School.objects.filter(admin=self.request.user).first()
            
            if not school:
                # Return empty queryset if no school found
                return Teacher.objects.none()
        
        # Filter teachers by the current school
        return Teacher.objects.filter(school=school)
    
    def get_object(self):
        queryset = self.get_queryset()
        custom_id = self.kwargs['pk']
       # print(f"Attempting to retrieve teacher with custom_id: {custom_id}")
        try:
            obj = queryset.get(custom_id=custom_id)
            print(f"Found teacher: {obj}")
        except Teacher.DoesNotExist:
           # print("Teacher not found")
            raise NotFound("Teacher not found")
        return obj
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = instance.user  # Get the associated user
        
        # Delete the teacher instance
        self.perform_destroy(instance)
        
        # Delete the associated user
        user.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def perform_destroy(self, instance):
        instance.delete()

# class TeacherProfileView(generics.RetrieveUpdateAPIView):
#     """
#     Get or update the current teacher's profile
#     """
#     serializer_class = TeacherProfileUpdateSerializer
#     permission_classes = [IsAuthenticated]
#     parser_classes = [MultiPartParser, FormParser]
    
#     def get_object(self):
#         try:
#             return self.request.user.teacher_profile
#         except Teacher.DoesNotExist:
#             return Response(
#                 {"detail": "Teacher profile not found."},
#                 status=status.HTTP_404_NOT_FOUND
#             )
    
#     def get_serializer_class(self):
#         if self.request.method == 'GET':
#             return TeacherSerializer
#         return TeacherProfileUpdateSerializer

class TeacherProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update the current teacher's profile
    """
    serializer_class = TeacherProfileUpdateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_object(self):
        try:
            # Try to get the teacher profile directly
            teacher = Teacher.objects.get(user=self.request.user)
            return teacher
        except Teacher.DoesNotExist:
            # Raise NotFound exception instead of returning a Response
            raise NotFound("Teacher profile not found.")
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TeacherSerializer
        return TeacherProfileUpdateSerializer
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TeacherSerializer
        return TeacherProfileUpdateSerializer

class TeacherClassListView(generics.ListAPIView):
    """
    List classes assigned to a teacher
    """
    serializer_class = TeacherClassAssignmentSerializer
    permission_classes = [IsAuthenticated, IsTeacherOrAdmin]
    lookup_field = 'custom_id'
    
    def get_queryset(self):
        teacher_id = self.kwargs.get('teacher_id')
        
        # Try to get school from request
        if hasattr(self.request, 'school') and self.request.school:
            school = self.request.school
        else:
            # Fallback: try to get school from user
            from schools.models import School
            school = School.objects.filter(admin=self.request.user).first()
            
            if not school:
                # Return empty queryset if no school found
                return TeacherClassAssignment.objects.none()
        
        return TeacherClassAssignment.objects.filter(
            teacher__custom_id=teacher_id,
            teacher__school=school
        )



class TeacherAttendanceListCreateView(generics.ListCreateAPIView):
    """
    List all teacher attendance records or create a new one
    """
    serializer_class = TeacherAttendanceSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['date', 'is_present', 'teacher']
    ordering_fields = ['date']
    
    def get_queryset(self):
        # Try to get school from request
        if hasattr(self.request, 'school') and self.request.school:
            school = self.request.school
        else:
            # Fallback: try to get school from user
            from schools.models import School
            school = School.objects.filter(admin=self.request.user).first()
            
            if not school:
                # Return empty queryset if no school found
                return TeacherAttendance.objects.none()
        
        # Filter attendance by teachers in the current school
        return TeacherAttendance.objects.filter(teacher__school=school)
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsTeacherOrAdmin()]

class TeacherAttendanceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a teacher attendance record
    """
    serializer_class = TeacherAttendanceSerializer
    
    def get_queryset(self):
        # Try to get school from request
        if hasattr(self.request, 'school') and self.request.school:
            school = self.request.school
        else:
            # Fallback: try to get school from user
            from schools.models import School
            school = School.objects.filter(admin=self.request.user).first()
            
            if not school:
                # Return empty queryset if no school found
                return TeacherAttendance.objects.none()
        
        # Filter attendance by teachers in the current school
        return TeacherAttendance.objects.filter(teacher__school=school)
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsTeacherOrAdmin()]

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSchoolAdmin])
def resend_teacher_credentials(request, pk):
    """
    Resend login credentials to a teacher
    """
    # Try to get school from request
    if hasattr(request, 'school') and request.school:
        school = request.school
    else:
        # Fallback: try to get school from user
        from schools.models import School
        school = School.objects.filter(admin=request.user).first()
        
        if not school:
            return Response(
                {"detail": "No school found for this user. Please create a school first."},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    try:
        teacher = Teacher.objects.get(custom_id=pk, school=school)
    except Teacher.DoesNotExist:
        return Response(
            {"detail": "Teacher not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    
    user = teacher.user
    
    # Generate a new password
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice("!@#$%^&*")
    ]
    password.extend(secrets.choice(alphabet) for _ in range(8))
    secrets.SystemRandom().shuffle(password)
    new_password = ''.join(password)
    
    # Update the user's password
    user.set_password(new_password)
    user.save()
    
    # Send the new credentials
    try:
        send_teacher_credentials_email(
            email=user.email,
            password=new_password,
            full_name=teacher.full_name,
            school_name=teacher.school.school_name
        )
        return Response({
            "message": f"New credentials sent to {user.email}",
            "email": user.email
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "error": "Failed to send credentials email",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSchoolAdmin | IsTeacherWithFullAccess])
def teacher_dashboard(request):
    """
    Get dashboard statistics for teachers
    """
    # Try to get school from request
    if hasattr(request, 'school') and request.school:
        school = request.school
    else:
        # Fallback: try to get school from user
        from schools.models import School
        school = School.objects.filter(admin=request.user).first()
        
        if not school:
            return Response(
                {"detail": "No school found for this user. Please create a school first."},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Get basic statistics
    total_teachers = Teacher.objects.filter(school=school).count()
    active_teachers = Teacher.objects.filter(school=school, is_active=True).count()
    
    # Get attendance statistics
    attendance_data = TeacherAttendance.objects.filter(teacher__school=school)
    total_attendance = attendance_data.count()
    present_count = attendance_data.filter(is_present=True).count()
    
    # Calculate attendance percentage
    attendance_percentage = 0
    if total_attendance > 0:
        attendance_percentage = (present_count / total_attendance) * 100
    
    return Response({
        'total_teachers': total_teachers,
        'active_teachers': active_teachers,
        'total_attendance': total_attendance,
        'present_count': present_count,
        'attendance_percentage': attendance_percentage
    })