
from rest_framework import serializers
from .models import Class, Student, StudentAttendance
from schools.models import School  # Import the School model

class ClassCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ('class_name', 'description')  # Only include fields needed for creation

class ClassSerializer(serializers.ModelSerializer):
    student_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Class
        fields = ('id', 'custom_id', 'class_name', 'description', 'student_count', 'created_at')
        read_only_fields = ('id', 'custom_id', 'created_at', 'student_count')
    
    def get_student_count(self, obj):
        return obj.students.count()

class StudentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ('registration_number', 'first_name', 'last_name', 'date_of_birth', 'gender', 'address', 'parent_name', 'parent_phone', 'parent_email', 'admission_date', 'is_active', 'class_assigned')  # Only include fields needed for creation

class StudentSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='class_assigned.name', read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = ('id', 'custom_id', 'registration_number', 'first_name', 'last_name', 'date_of_birth', 'gender', 'address', 'parent_name', 'parent_phone', 'parent_email', 'admission_date', 'is_active', 'class_assigned', 'class_name', 'school', 'created_at', 'updated_at')
        read_only_fields = ('id', 'custom_id', 'school', 'created_at', 'updated_at', 'class_name', 'full_name')
        
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

class StudentAttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    class_name = serializers.CharField(source='student.class_assigned.name', read_only=True)
    
    class Meta:
        model = StudentAttendance
        fields = '__all__'
        read_only_fields = ('student_name', 'class_name')
    
    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}"













# from rest_framework import serializers
# from .models import Class, Student, StudentAttendance
# from schools.models import School  # Import the School model

# class ClassSerializer(serializers.ModelSerializer):
#     student_count = serializers.SerializerMethodField()
    
#     class Meta:
#         model = Class
#         fields = ('id', 'custom_id', 'class_name', 'description', 'student_count', 'created_at')
#         read_only_fields = ('id', 'custom_id', 'created_at', 'student_count')
    
#     def get_student_count(self, obj):
#         return obj.students.count()
    
#     def create(self, validated_data):
#         request = self.context.get('request')
        
#         # Try to get school from request
#         if hasattr(request, 'school') and request.school:
#             school = request.school
#         else:
#             # Fallback: try to get school from user
#             school = School.objects.filter(admin=request.user).first()
            
#             if not school:
#                 raise serializers.ValidationError(
#                     "No school found for this user. Please create a school first."
#                 )
        
#         # Create class with the current school
#         class_obj = Class.objects.create(
#             school=school,
#             **validated_data
#         )
        
#         return class_obj

# class StudentSerializer(serializers.ModelSerializer):
#     class_name = serializers.CharField(source='class_assigned.name', read_only=True)
#     full_name = serializers.SerializerMethodField()
    
#     class Meta:
#         model = Student
#         fields = ('id', 'custom_id', 'registration_number', 'first_name', 'last_name', 'date_of_birth', 'gender', 'address', 'parent_name', 'parent_phone', 'parent_email', 'admission_date', 'is_active', 'class_assigned', 'class_name', 'school', 'created_at', 'updated_at')
#         read_only_fields = ('id', 'custom_id', 'school', 'created_at', 'updated_at', 'class_name', 'full_name')
        
#     def get_full_name(self, obj):
#         return f"{obj.first_name} {obj.last_name}"
    
#     def create(self, validated_data):
#         request = self.context.get('request')
        
#         # Try to get school from request
#         if hasattr(request, 'school') and request.school:
#             school = request.school
#         else:
#             # Fallback: try to get school from user
#             school = School.objects.filter(admin=request.user).first()
            
#             if not school:
#                 raise serializers.ValidationError(
#                     "No school found for this user. Please create a school first."
#                 )
        
#         # Create student with the current school
#         student = Student.objects.create(
#             school=school,
#             **validated_data
#         )
        
#         return student

# class StudentAttendanceSerializer(serializers.ModelSerializer):
#     student_name = serializers.SerializerMethodField()
#     class_name = serializers.CharField(source='student.class_assigned.name', read_only=True)
    
#     class Meta:
#         model = StudentAttendance
#         fields = '__all__'
#         read_only_fields = ('student_name', 'class_name')
    
#     def get_student_name(self, obj):
#         return f"{obj.student.first_name} {obj.student.last_name}"
    
#     def create(self, validated_data):
#         # For StudentAttendance, we don't need to set the school directly
#         # since it's related to the student who already has a school
#         return super().create(validated_data)