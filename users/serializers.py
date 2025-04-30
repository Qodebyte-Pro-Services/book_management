from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from datetime import timedelta
from .models import EmailVerification, PasswordReset
from core.utils import generate_otp, send_verification_email, send_password_reset_email

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'full_name', 'password', 'confirm_password', 'role')
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def validate(self, data):
        # Check if passwords match
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords don't match"})
        
        # Validate password complexity
        password = data['password']
        validate_password(password)
        
        # Check for at least one uppercase, one lowercase, one digit, and one special character
        if not any(c.isupper() for c in password):
            raise serializers.ValidationError({"password": "Password must contain at least one uppercase letter"})
        if not any(c.islower() for c in password):
            raise serializers.ValidationError({"password": "Password must contain at least one lowercase letter"})
        if not any(c.isdigit() for c in password):
            raise serializers.ValidationError({"password": "Password must contain at least one number"})
        if not any(c in "!@#$%^&*()-_=+[]{}|;:'\",.<>/?`~" for c in password):
            raise serializers.ValidationError({"password": "Password must contain at least one special character"})
        
        return data
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            password=validated_data['password'],
            role=validated_data.get('role', User.ROLE_ADMIN),  # Make sure role is passed
            is_verified=False
        )
        
        return user
    
class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    
    def validate(self, data):
        try:
            user = User.objects.get(email=data['email'])
            verification = EmailVerification.objects.filter(
                user=user,
                otp=data['otp'],
                is_used=False
            ).latest('created_at')
            
            if not verification.is_valid():
                raise serializers.ValidationError("Verification code has expired")
            
            self.context['user'] = user
            self.context['verification'] = verification
            
            return data
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist")
        except EmailVerification.DoesNotExist:
            raise serializers.ValidationError("Invalid verification code")

class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
            if user.is_verified:
                raise serializers.ValidationError("This email is already verified")
            self.context['user'] = user
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this email address")

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'full_name', 'role', 'is_verified')
        read_only_fields = ('id', 'email', 'is_verified')

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
            self.context['user'] = user
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this email address")

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(min_length=8, write_only=True)
    
    def validate(self, data):
        # Check if passwords match
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords don't match"})
        
        # Validate password complexity
        password = data['new_password']
        validate_password(password)
        
        # Check for at least one uppercase, one lowercase, one digit, and one special character
        if not any(c.isupper() for c in password):
            raise serializers.ValidationError({"new_password": "Password must contain at least one uppercase letter"})
        if not any(c.islower() for c in password):
            raise serializers.ValidationError({"new_password": "Password must contain at least one lowercase letter"})
        if not any(c.isdigit() for c in password):
            raise serializers.ValidationError({"new_password": "Password must contain at least one number"})
        if not any(c in "!@#$%^&*()-_=+[]{}|;:'\",.<>/?`~" for c in password):
            raise serializers.ValidationError({"new_password": "Password must contain at least one special character"})
        
        try:
            user = User.objects.get(email=data['email'])
            reset = PasswordReset.objects.filter(
                user=user,
                otp=data['otp'],
                is_used=False
            ).latest('created_at')
            
            if not reset.is_valid():
                raise serializers.ValidationError("Password reset otp has expired")
            
            self.context['user'] = user
            self.context['reset'] = reset
            
            return data
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this email address")
        except PasswordReset.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired password reset token")
