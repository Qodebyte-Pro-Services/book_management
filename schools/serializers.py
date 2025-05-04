from rest_framework import serializers
from .models import School
from django.contrib.auth import get_user_model

User = get_user_model()

class SchoolSerializer(serializers.ModelSerializer):
    # admin = serializers.PrimaryKeyRelatedField(read_only=True)  # Remove this line

    class Meta:
        model = School
        fields = ('custom_id', 'school_name', 'address', 'description', 'school_type', 'created_at', 'updated_at')  # Remove 'admin' from here
        read_only_fields = ('custom_id', 'created_at', 'updated_at')

    def create(self, validated_data):
        # Get the user from the context
        #user = self.context['request'].user

        # Create the school with the user as admin
        school = School.objects.create(
            #admin=user,
            **validated_data
        )

        return school
