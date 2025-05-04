from rest_framework import generics, status, filters, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Class, Student, StudentAttendance
from .serializers import ( ClassSerializer, StudentSerializer, StudentAttendanceSerializer, 
StudentCreateSerializer, ClassCreateSerializer )
from schools.permissions import IsSchoolAdmin
from core.permissions import ( IsTeacherOrAdmin, IsTeacherWithFullAccess, 
IsTeacherWithLimitedAccess, IsTeacherWithClassOnlyAccess )
from rest_framework.exceptions import ValidationError
from rest_framework.exceptions import NotFound
from django.db import IntegrityError  

class ClassListCreateView(generics.ListCreateAPIView):
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    permission_classes = [IsAuthenticated, IsSchoolAdmin]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ClassCreateSerializer
        return ClassSerializer
    
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
                return Class.objects.none()
        
        # Filter classes by the current school
        return Class.objects.filter(school=school)
    
    def perform_create(self, serializer):
        try:
            # Try to get school from request
            if hasattr(self.request, 'school') and self.request.school:
                school = self.request.school
            else:
                # Fallback: try to get school from user
                from schools.models import School
                school = School.objects.filter(admin=self.request.user).first()
                
                if not school:
                    raise ValidationError("No school found for this user. Please create a school first.")
            
            serializer.save(school=school)
        except IntegrityError as e:
            if "unique constraint" in str(e).lower() and "class_name" in str(e).lower():
                raise serializers.ValidationError({"class_name": "A class with this name already exists in this school."})
            else:
                # Re-raise the exception if it's not a unique constraint violation
                raise


class ClassDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ClassSerializer
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
                return Class.objects.none()
        
        # Filter classes by the current school
        return Class.objects.filter(school=school)
    
    def get_object(self):
        queryset = self.get_queryset()
        try:
            obj = queryset.get(custom_id=self.kwargs['pk'])  # Use custom_id for lookup
        except Class.DoesNotExist:
            raise NotFound("Class not found")
        return obj


class StudentListCreateView(generics.ListCreateAPIView):
    serializer_class = StudentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'gender', 'class_assigned']
    search_fields = ['first_name', 'last_name', 'registration_number', 'parent_name']
    ordering_fields = ['first_name', 'last_name', 'admission_date']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return StudentCreateSerializer
        return StudentSerializer
    
    def get_permissions(self):
        if self.request.method == 'POST':
            # Only admins can create students
            return [IsAuthenticated(), IsSchoolAdmin()]
        else:
            # For GET requests, check role-based permissions
            if self.request.user.role == 'admin':
                return [IsAuthenticated(), IsSchoolAdmin()]
            elif self.request.user.role == 'teacher':
                # Teachers with at least limited access can view students
                return [IsAuthenticated(), IsTeacherWithLimitedAccess()]
            return [IsAuthenticated()]
    
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
                return Student.objects.none()
        
        # Base filtering by school
        queryset = Student.objects.filter(school=school)
        
        # Additional filtering based on role and access level
        if self.request.user.role == 'teacher':
            teacher = self.request.user.teacher_profile
            if teacher.access_level == 'class_only':
                # Teacher can only see students in their assigned classes
                teacher_classes = Class.objects.filter(teacher=teacher)
                return queryset.filter(class_assigned__in=teacher_classes)
        
        # Admin and teachers with full/limited access see all students in the school
        return queryset
    
    def perform_create(self, serializer):
        # Try to get school from request
        if hasattr(self.request, 'school') and self.request.school:
            school = self.request.school
        else:
            # Fallback: try to get school from user
            from schools.models import School
            school = School.objects.filter(admin=self.request.user).first()
            
            if not school:
                raise serializers.ValidationError("No school found for this user. Please create a school first.")
        
        serializer.save(school=school)

class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StudentSerializer
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            # Only admins can update or delete students
            return [IsAuthenticated(), IsSchoolAdmin()]
        else:
            # For GET requests, check role-based permissions
            if self.request.user.role == 'admin':
                return [IsAuthenticated(), IsSchoolAdmin()]
            elif self.request.user.role == 'teacher':
                # Teachers with at least limited access can view student details
                return [IsAuthenticated(), IsTeacherWithLimitedAccess()]
            return [IsAuthenticated()]
    
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
                return Student.objects.none()
        
        # Base filtering by school
        queryset = Student.objects.filter(school=school)
        
        # Additional filtering based on role and access level
        if self.request.user.role == 'teacher':
            teacher = self.request.user.teacher_profile
            if teacher.access_level == 'class_only':
                # Teacher can only see students in their assigned classes
                teacher_classes = Class.objects.filter(teacher=teacher)
                return queryset.filter(class_assigned__in=teacher_classes)
        
        # Admin and teachers with full/limited access see all students in the school
        return queryset

class StudentAttendanceListCreateView(generics.ListCreateAPIView):
    serializer_class = StudentAttendanceSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['date', 'is_present', 'student', 'student__class_assigned']
    ordering_fields = ['date']
    
    def get_permissions(self):
        if self.request.method == 'POST':
            # Only admins and teachers with full access can create attendance records
            if self.request.user.role == 'admin':
                return [IsAuthenticated(), IsSchoolAdmin()]
            else:
                return [IsAuthenticated(), IsTeacherWithFullAccess()]
        else:
            # For GET requests, check role-based permissions
            if self.request.user.role == 'admin':
                return [IsAuthenticated(), IsSchoolAdmin()]
            elif self.request.user.role == 'teacher':
                # All teachers can view attendance
                return [IsAuthenticated(), IsTeacherOrAdmin()]
            return [IsAuthenticated()]
    
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
                return StudentAttendance.objects.none()
        
        # Base filtering by school (through student)
        queryset = StudentAttendance.objects.filter(student__school=school)
        
        # Additional filtering based on role and access level
        if self.request.user.role == 'teacher':
            teacher = self.request.user.teacher_profile
            if teacher.access_level == 'class_only':
                # Teacher can only see attendance for students in their assigned classes
                teacher_classes = Class.objects.filter(teacher=teacher)
                return queryset.filter(student__class_assigned__in=teacher_classes)
        
        # Admin and teachers with full/limited access see all attendance records in the school
        return queryset
    
    def perform_create(self, serializer):
        serializer.save()

class StudentAttendanceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StudentAttendanceSerializer
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            # Only admins and teachers with full access can update or delete attendance records
            if self.request.user.role == 'admin':
                return [IsAuthenticated(), IsSchoolAdmin()]
            else:
                return [IsAuthenticated(), IsTeacherWithFullAccess()]
        else:
            # For GET requests, check role-based permissions
            if self.request.user.role == 'admin':
                return [IsAuthenticated(), IsSchoolAdmin()]
            elif self.request.user.role == 'teacher':
                # All teachers can view attendance details
                return [IsAuthenticated(), IsTeacherOrAdmin()]
            return [IsAuthenticated()]
    
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
                return StudentAttendance.objects.none()
        
        # Base filtering by school
        queryset = StudentAttendance.objects.filter(student__school=school)
        
        # Additional filtering based on role and access level
        if self.request.user.role == 'teacher':
            teacher = self.request.user.teacher_profile
            if teacher.access_level == 'class_only':
                # Teacher can only see attendance for students in their assigned classes
                teacher_classes = Class.objects.filter(teacher=teacher)
                return queryset.filter(student__class_assigned__in=teacher_classes)
        
        # Admin and teachers with full/limited access see all attendance records in the school
        return queryset