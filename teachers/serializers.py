from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Teacher, TeacherClassAssignment, TeacherAttendance
from students.models import Class
from users.serializers import UserSerializer
from core.utils import send_teacher_credentials_email
import secrets
import string
from django.db import transaction

User = get_user_model()



class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ('id', 'name')

class TeacherClassAssignmentSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='class_assigned.class_name', read_only=True)
    
    class Meta:
        model = TeacherClassAssignment
        fields = ('id', 'assigned_class', 'class_name', 'is_primary')
        read_only_fields = ('id',)

class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    assigned_classes = TeacherClassAssignmentSerializer(source='class_assignments', many=True, read_only=True)
    profile_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Teacher
        fields = (
            'id', 'user', 'employee_id', 'first_name', 'last_name', 'date_of_birth', 'gender',
            'profile_image', 'profile_image_url', 'phone_number', 'address', 'state', 'city',
            'emergency_contact_name', 'emergency_contact_relationship', 'emergency_contact_phone',
            'highest_certificate', 'school_name', 'graduation_year',
            'previous_workplace', 'job_title', 'job_duration', 'job_reference_contact',
            'joining_date', 'salary', 'is_active', 'access_level', 'assigned_classes',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'user', 'school', 'created_at', 'updated_at')
    
    def get_profile_image_url(self, obj):
        if obj.profile_image:
            return obj.profile_image.url
        return None


class TeacherCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})
    assigned_classes = serializers.PrimaryKeyRelatedField(
        queryset=Class.objects.all(),
        many=True,
        required=False,
        write_only=True
    )
    profile_image = serializers.ImageField(required=False)
    send_credentials = serializers.BooleanField(default=True, write_only=True)
    
    class Meta:
        model = Teacher
        fields = (
            'email', 'password', 'employee_id', 'first_name', 'last_name', 'date_of_birth', 'gender',
            'profile_image', 'phone_number', 'address', 'state', 'city',
            'emergency_contact_name', 'emergency_contact_relationship', 'emergency_contact_phone',
            'highest_certificate', 'school_name', 'graduation_year',
            'previous_workplace', 'job_title', 'job_duration', 'job_reference_contact',
            'joining_date', 'salary', 'is_active', 'access_level', 'assigned_classes',
            'send_credentials'
        )
    
    def validate_email(self, value):
        # Check if email already exists
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def generate_secure_password(self, length=12):
        """Generate a secure random password."""
        alphabet = string.ascii_letters + string.digits
        # Ensure at least one of each: uppercase, lowercase, digit.
        password = [
            secrets.choice(string.ascii_uppercase),
            secrets.choice(string.ascii_lowercase),
            secrets.choice(string.digits)
        ]
        # Fill the rest with random characters
        password.extend(secrets.choice(alphabet) for _ in range(length - 4))
        # Shuffle to avoid predictable pattern
        secrets.SystemRandom().shuffle(password)
        return ''.join(password)
    
    @transaction.atomic  # Add this decorator to make the entire creation atomic
    def create(self, validated_data):
        request = self.context.get('request')
        
        # Get school from context (set by perform_create) or try to find it
        school = self.context.get('school')
        if not school and request:
            # Try to get school from request
            if hasattr(request, 'school') and request.school:
                school = request.school
            else:
                # Fallback: try to get school from user
                from schools.models import School
                school = School.objects.filter(admin=request.user).first()
        
        if not school:
            raise serializers.ValidationError("No school found for this user. Please create a school first.")
        
        # Extract user data and assigned classes
        email = validated_data.pop('email')
        password = validated_data.pop('password', None)
        assigned_classes = validated_data.pop('assigned_classes', [])
        send_credentials = validated_data.pop('send_credentials', True)
        
        # Generate password if not provided
        if not password:
            password = self.generate_secure_password()
        
        # Create full name from first and last name
        full_name = f"{validated_data['first_name']} {validated_data['last_name']}"
        
        # Create user
        user = User.objects.create_user(
            email=email,
            full_name=full_name,
            password=password,
            role=User.ROLE_TEACHER,
            is_verified=True  # Teachers created by admin are auto-verified
        )
        
        # Create teacher
        teacher = Teacher.objects.create(
            user=user,
            school=school,
            **validated_data
        )
        
        # Assign classes
        for class_obj in assigned_classes:
            TeacherClassAssignment.objects.create(
                teacher=teacher,
                assigned_class=class_obj,
                is_primary=False  # Default to not primary
            )
        
        # Send credentials email if requested
        if send_credentials:
            try:
                send_teacher_credentials_email(
                    email=email,
                    password=password,
                    full_name=full_name,
                    school_name=school.school_name
                )
            except Exception as e:
                # Log the error but don't fail the request
                print(f"Failed to send teacher credentials email: {str(e)}")
        
        return teacher

class TeacherUpdateSerializer(serializers.ModelSerializer):
    assigned_classes = serializers.PrimaryKeyRelatedField(
        queryset=Class.objects.all(),
        many=True,
        required=False,
        write_only=True
    )
    
    class Meta:
        model = Teacher
        fields = (
            'first_name', 'last_name', 'date_of_birth', 'gender',
            'profile_image', 'phone_number', 'address', 'state', 'city',
            'emergency_contact_name', 'emergency_contact_relationship', 'emergency_contact_phone',
            'highest_certificate', 'school_name', 'graduation_year',
            'previous_workplace', 'job_title', 'job_duration', 'job_reference_contact',
            'joining_date', 'salary', 'is_active', 'access_level', 'assigned_classes'
        )
    
    def update(self, instance, validated_data):
        # Handle assigned classes if provided
        assigned_classes = validated_data.pop('assigned_classes', None)
        
        if assigned_classes is not None:
            # Clear existing assignments
            instance.class_assignments.all().delete()
            
            # Create new assignments
            for class_obj in assigned_classes:
                TeacherClassAssignment.objects.create(
                    teacher=instance,
                    assigned_class=class_obj,
                    is_primary=False  # Default to not primary
                )
        
        # Update other fields
        return super().update(instance, validated_data)

class TeacherProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for teachers to update their own profile with limited fields
    """
    class Meta:
        model = Teacher
        fields = (
            'phone_number', 'address', 'state', 'city',
            'emergency_contact_name', 'emergency_contact_relationship', 'emergency_contact_phone',
            'profile_image'
        )

class TeacherAttendanceSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    
    class Meta:
        model = TeacherAttendance
        fields = '__all__'
        read_only_fields = ('teacher_name',)
