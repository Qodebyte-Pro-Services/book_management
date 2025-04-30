from rest_framework import serializers
from .models import School

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ('id', 'school_name', 'address', 'description', 'school_type', 'created_at')
        read_only_fields = ('id', 'created_at')
    
    def create(self, validated_data):
        # Get the user from the context
        user = self.context['request'].user
        
        # Create the school with the user as admin
        school = School.objects.create(
            admin=user,
            **validated_data
        )
        
        return school
