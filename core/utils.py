import random
import string
import secrets
from django.core.mail import send_mail
from django.conf import settings
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException


def generate_otp(length=6):
    """Generate a random OTP of specified length."""
    return ''.join(random.choices(string.digits, k=length))

def generate_token(length=64):
    """Generate a secure random token for password reset."""
    return secrets.token_hex(length // 2)

def send_email_with_brevo(to_email, subject, html_content, text_content=None):
    """Send email using Brevo API."""
    if not text_content:
        text_content = html_content  # Fallback to HTML content if text content is not provided
    
    # Configure API key authorization
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.BREVO_API_KEY
    
    # Create an instance of the API class
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    
    # Create a SendSmtpEmail object
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": to_email}],
        html_content=html_content,
        text_content=text_content,
        sender={"name": "School Management System", "email": settings.DEFAULT_FROM_EMAIL},
        subject=subject
    )
    
    try:
        # Send the email
        api_response = api_instance.send_transac_email(send_smtp_email)
        return True
    except ApiException as e:
        print(f"Exception when calling TransactionalEmailsApi->send_transac_email: {e}")
        raise e

def send_verification_email(email, otp):
    """Send verification email with OTP using Django's email backend."""
    from django.core.mail import send_mail
    from django.conf import settings
    
    subject = 'Email Verification for School Management System'
    html_content = f"""
    <html>
        <body>
            <h1>Email Verification</h1>
            <p>Thank you for registering with the School Management System.</p>
            <p>Your verification code is: <strong>{otp}</strong></p>
            <p>This code will expire in 1 hour.</p>
            <p>If you did not request this verification, please ignore this email.</p>
        </body>
    </html>
    """
    text_content = f"Your verification code is: {otp}. This code will expire in 1 hour."
    
    try:
        print(f"Sending verification email to {email}...")
        result = send_mail(
            subject=subject,
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_content,
            fail_silently=False,
        )
        print(f"Email sent successfully! Result: {result}")
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        
        # For development, print the OTP to console
        if settings.DEBUG:
            print("\n==== DEVELOPMENT MODE: EMAIL WOULD BE SENT ====")
            print(f"To: {email}")
            print(f"Subject: {subject}")
            print(f"OTP: {otp}")
            print("==============================================\n")
            return True  # Return True in development so registration can continue
        
        # In production, re-raise the exception
        raise e

def send_password_reset_email(email, otp):
    """Send password reset email with token using Django's email backend."""
    from django.core.mail import send_mail
    from django.conf import settings
    
    subject = 'Password Reset for School Management System'
    html_content = f"""
    <html>
        <body>
            <h1>Password Reset</h1>
            <p>You have requested to reset your password for the School Management System.</p>
            <p>Your password reset token is: <strong>{otp}</strong></p>
            <p>This token will expire in 1 hour.</p>
            <p>If you did not request this password reset, please ignore this email.</p>
        </body>
    </html>
    """
    text_content = f"Your password reset token is: {otp}. This token will expire in 1 hour."
    
    try:
        print(f"Sending password reset email to {email}...")
        result = send_mail(
            subject=subject,
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_content,
            fail_silently=False,
        )
        print(f"Email sent successfully! Result: {result}")
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        
        # For development, print the token to console
        if settings.DEBUG:
            print("\n==== DEVELOPMENT MODE: EMAIL WOULD BE SENT ====")
            print(f"To: {email}")
            print(f"Subject: {subject}")
            print(f"Token: {otp}")
            print("==============================================\n")
            return True  # Return True in development so password reset can continue
        
        # In production, re-raise the exception
        raise e

def send_school_creation_email(email, school_name, school_type, full_name):
    """Send email notification when a school is created using Django's email backend."""
    from django.core.mail import send_mail
    from django.conf import settings
    
    subject = 'School Registration Confirmation'
    html_content = f"""
    <html>
        <body>
            <h1>School Registration Confirmation</h1>
            <p>Dear {full_name},</p>
            <p>Congratulations! Your school has been successfully registered with the School Management System.</p>
            <p><strong>School Details:</strong></p>
            <ul>
                <li><strong>School Name:</strong> {school_name}</li>
                <li><strong>School Type:</strong> {school_type.title()}</li>
            </ul>
            <p>You can now log in to the School Management System to manage your school.</p>
            <p>Thank you for choosing our platform!</p>
        </body>
    </html>
    """
    text_content = f"""
    School Registration Confirmation
    
    Dear {full_name},
    
    Congratulations! Your school has been successfully registered with the School Management System.
    
    School Details:
    - School Name: {school_name}
    - School Type: {school_type.title()}
    
    You can now log in to the School Management System to manage your school.
    
    Thank you for choosing our platform!
    """
    
    try:
        print(f"Sending school creation email to {email}...")
        result = send_mail(
            subject=subject,
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_content,
            fail_silently=False,
        )
        print(f"Email sent successfully! Result: {result}")
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        
        # For development, print the school details to console
        if settings.DEBUG:
            print("\n==== DEVELOPMENT MODE: EMAIL WOULD BE SENT ====")
            print(f"To: {email}")
            print(f"Subject: {subject}")
            print(f"School Details:")
            print(f"  Name: {school_name}")
            print(f"  Type: {school_type.title()}")
            print("==============================================\n")
            return True  # Return True in development so school creation can continue
        
        # In production, re-raise the exception
        raise e

def send_teacher_credentials_email(email, password, full_name, school_name):
    """Send login credentials to a newly created teacher using Django's email backend."""
    from django.core.mail import send_mail
    from django.conf import settings
    
    subject = 'Your Teacher Account Credentials'
    html_content = f"""
    <html>
        <body>
            <h1>Welcome to the School Management System</h1>
            <p>Dear {full_name},</p>
            <p>Your teacher account has been created for <strong>{school_name}</strong>.</p>
            <p><strong>Your login credentials:</strong></p>
            <ul>
                <li><strong>Email:</strong> {email}</li>
                <li><strong>Password:</strong> {password}</li>
            </ul>
            <p>Please log in to the School Management System using these credentials. For security reasons, we recommend changing your password after your first login.</p>
            <p>If you have any questions, please contact your school administrator.</p>
            <p>Thank you for joining our platform!</p>
        </body>
    </html>
    """
    text_content = f"""
    Welcome to the School Management System
    
    Dear {full_name},
    
    Your teacher account has been created for {school_name}.
    
    Your login credentials:
    - Email: {email}
    - Password: {password}
    
    Please log in to the School Management System using these credentials. For security reasons, we recommend changing your password after your first login.
    
    If you have any questions, please contact your school administrator.
    
    Thank you for joining our platform!
    """
    
    try:
        print(f"Sending teacher credentials email to {email}...")
        result = send_mail(
            subject=subject,
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_content,
            fail_silently=False,
        )
        print(f"Email sent successfully! Result: {result}")
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        
        # For development, print the credentials to console
        if settings.DEBUG:
            print("\n==== DEVELOPMENT MODE: EMAIL WOULD BE SENT ====")
            print(f"To: {email}")
            print(f"Subject: {subject}")
            print(f"Credentials:")
            print(f"  Email: {email}")
            print(f"  Password: {password}")
            print("==============================================\n")
            return True  # Return True in development so teacher creation can continue
        
        # In production, re-raise the exception
        raise e