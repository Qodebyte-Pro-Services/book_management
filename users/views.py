from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import (
    UserRegistrationSerializer,
    VerifyEmailSerializer,
    ResendVerificationSerializer,
    UserLoginSerializer,
    UserSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer
)
from .models import User, EmailVerification, PasswordReset
from core.utils import generate_otp, send_verification_email, send_password_reset_email
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import login
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication 
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.views import APIView
from django.contrib.auth import logout




class RegisterUserView(generics.GenericAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                # Generate OTP
                otp = generate_otp()
                
                # Try sending email first
                send_verification_email(serializer.validated_data['email'], otp)
                
                # If email is sent successfully, save the user
                user = serializer.save()
                
                # Create verification record
                expires_at = timezone.now() + timedelta(hours=1)
                EmailVerification.objects.create(user=user, otp=otp, expires_at=expires_at)
                
                return Response({
                    "message": "User registered successfully. Please check your email for verification code.",
                    "user": {
                        "email": serializer.validated_data['email'],
                        "full_name": serializer.validated_data['full_name']
                    }
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    "error": "Failed to send verification email. Please try again.",
                    "details": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    
class VerifyEmailView(generics.GenericAPIView):
    serializer_class = VerifyEmailSerializer
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.context['user']
            verification = serializer.context['verification']
            
            # Mark user as verified
            user.is_verified = True
            user.save()
            
            # Mark verification as used
            verification.is_used = True
            verification.save()
            
            # Log in the user
            login(request, user)
            
          # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                "message": "Email verified successfully. You are now logged in.",
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                "user": {
                    "custom_id": user.custom_id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role, 
                    "has_school": hasattr(user, 'school')
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationView(generics.GenericAPIView):
    serializer_class = ResendVerificationSerializer
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.context['user']
            
            try:
                # Generate new OTP
                otp = generate_otp()
                
                # Try sending email first
                send_verification_email(user.email, otp)
                
                # Create new verification record
                expires_at = timezone.now() + timedelta(minutes=30)
                EmailVerification.objects.create(user=user, otp=otp, expires_at=expires_at)
                
                return Response({
                    "message": "Verification email resent successfully. Please check your email for the new verification code.",
                    "email": user.email
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    "error": "Failed to send verification email. Please try again.",
                    "details": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            user = authenticate(request, username=email, password=password)
            
            if user is None:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            
            if not user.is_verified:
                return Response({'error': 'Email not verified'}, status=status.HTTP_401_UNAUTHORIZED)
            
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.custom_id,
                    'email': user.email,
                    'full_name': user.full_name,
                    'role': user.role,
                    'has_school': hasattr(user, 'school')
                }
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # For Token Authentication
        if hasattr(request.user, 'auth_token'):
            request.user.auth_token.delete()
        
        # For JWT Authentication with refresh token
        if 'refresh' in request.data:
            try:
                from rest_framework_simplejwt.tokens import RefreshToken
                refresh_token = request.data["refresh"]
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception as e:
                return Response(
                    {"error": f"Could not log out: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # For Session Authentication
        logout(request)
        
        # Force the client to delete the token by returning specific instructions
        response = Response(
            {"detail": "Successfully logged out. Please remove all tokens from client storage."},
            status=status.HTTP_200_OK
        )
        
        # Clear any cookies that might be used for authentication
        response.delete_cookie('auth_token')
        response.delete_cookie('jwt_access')
        response.delete_cookie('jwt_refresh')
        
        return response

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    

class ForgotPasswordView(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.context['user']
            
            try:
                # Generate OTP
                otp = generate_otp() 
                
                # Try sending email first
                send_password_reset_email(user.email, otp) 
                
                # Create password reset record
                expires_at = timezone.now() + timedelta(minutes=30)
                PasswordReset.objects.create(
                    user=user, 
                    otp=otp, 
                    expires_at=expires_at
                )  # Store OTP instead of token
                
                return Response({
                    "message": "Password reset email sent successfully. Please check your email for the reset code.",
                    "email": user.email
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    "error": "Failed to send password reset email. Please try again.",
                    "details": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.context['user']
            reset = serializer.context['reset']
            
            # Update user password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Mark reset code as used
            reset.is_used = True
            reset.save()
            
            return Response({
                "message": "Password reset successfully. You can now login with your new password.",
                "email": user.email
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
