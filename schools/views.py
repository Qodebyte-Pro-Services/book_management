from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import School
from .serializers import SchoolSerializer
from .permissions import IsSchoolAdmin
from core.utils import send_school_creation_email
from rest_framework.exceptions import NotFound
from core.permissions import IsAdminOnly


class CreateSchoolView(generics.CreateAPIView):
    serializer_class = SchoolSerializer
    permission_classes = [IsAuthenticated, IsAdminOnly]
    
    def perform_create(self, serializer):
        # Get the admin user from the request
        admin_user = self.request.user
        
        # Create the school with the admin user
        serializer.save(admin=admin_user)
    
    def post(self, request, *args, **kwargs):
        # Check if user is verified
        if not request.user.is_verified:
            return Response(
                {"error": "Your email must be verified before creating a school"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if user already has a school
        if hasattr(request.user, 'school'):
            return Response(
                {"error": "You already have a school registered"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.serializer_class(data=request.data)  # Remove context={'request': request}
        if serializer.is_valid():
            self.perform_create(serializer)  # Call perform_create to save the school
            school = serializer.instance  # Access the created school object
            
            # Send email notification
            try:
                send_school_creation_email(
                    email=request.user.email,
                    school_name=school.school_name,
                    school_type=school.school_type,
                    full_name=request.user.full_name
                )
            except Exception as e:
                # Log the error but don't fail the request
                print(f"Failed to send school creation email: {str(e)}")
            
            return Response({
                "message": "School created successfully",
                "school": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SchoolDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = SchoolSerializer
    permission_classes = [IsAuthenticated, IsSchoolAdmin]
    
    def get_object(self):
        if hasattr(self.request.user, 'school'):
            return self.request.user.school
        else:
            raise NotFound("You don't have a school associated with your account.")
        
        
        