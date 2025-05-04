import random
import string
import secrets
from django.core.mail import send_mail
from django.conf import settings
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import uuid
import re

def generate_custom_id(prefix, length=7):
    """Generates a custom ID in the format PREFIX + UUID"""
    # Generate a UUID
    unique_id = str(uuid.uuid4()).upper()
    # Extract alphanumeric characters
    alphanumeric_id = re.sub(r'[^A-Z0-9]', '', unique_id)
    # Truncate or pad to the desired length
    if len(alphanumeric_id) > length:
        alphanumeric_id = alphanumeric_id[:length]
    else:
        alphanumeric_id = alphanumeric_id.ljust(length, '0')
    return f"{prefix}{alphanumeric_id[:5]}-{alphanumeric_id[5:]}"


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
       # print(f"Exception when calling TransactionalEmailsApi->send_transac_email: {e}")
        raise e



def send_verification_email(email, otp):
    """Send verification email with OTP using Brevo."""
    subject = 'Verify Your Email - School Management System'

    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: auto; padding: 20px; border: 1px solid #eee; border-radius: 8px;">
                <h2 style="color: #2c3e50;">Email Verification</h2>
                <p>Dear User,</p>
                <p>Thank you for registering with the <strong>School Management System</strong>.</p>
                <p>Please use the verification code below to complete your registration:</p>
                <p style="font-size: 20px; font-weight: bold; background-color: #f4f4f4; padding: 10px; display: inline-block; border-radius: 4px;">
                    {otp}
                </p>
                <p>This code will expire in <strong>1 hour</strong>.</p>
                <p>If you did not request this email, you can safely ignore it.</p>
                <p>Best regards,<br>School Management,<br>Qodebyte Team</p>
            </div>
        </body>
    </html>
    """

    text_content = f"""\
    Dear User,

    Thank you for registering with the School Management System.

    Your verification code is: {otp}

    This code will expire in 1 hour.

    If you did not request this verification, please ignore this email.

    Best regards,
    School Management
    Qodebyte Team
    """

    try:
        return send_email_with_brevo(email, subject, html_content, text_content)
    except Exception as e:
       #print(f"Failed to send verification email: {str(e)}")
        raise e

def send_password_reset_email(email, otp):
    """Send password reset email with token using Brevo."""
    subject = 'Password Reset Request - School Management System'

    html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: auto; padding: 20px; border: 1px solid #eee; border-radius: 8px;">
                    <h2 style="color: #2c3e50;">Password Reset Request</h2>
                    <p>Dear User,</p>
                    <p>We received a request to reset your password for your <strong>School Management System</strong> account.</p>
                    <p>Please use the following token to reset your password:</p>
                    <p style="font-size: 20px; font-weight: bold; background-color: #f4f4f4; padding: 10px; display: inline-block; border-radius: 4px;">
                        {otp}
                    </p>
                    <p>This token is valid for <strong>1 hour</strong>.</p>
                    <p>If you did not request this password reset, please ignore this email or contact support.</p>
                    <p>Best regards,<br>School Management,<br>Qodebyte Team</p>
                </div>
            </body>
        </html>
        """

    text_content = f"""\
        Dear User,

        We received a request to reset your password for your School Management System account.

        Your password reset token is: {otp}

        This token will expire in 1 hour.

        If you did not request this, please ignore this message or contact support.

       Best regards,
       School Management
       Qodebyte Team
        """

    try:
        return send_email_with_brevo(email, subject, html_content, text_content)
    except Exception as e:
       # print(f"Failed to send password reset email: {str(e)}")
        raise e

def send_school_creation_email(email, school_name, school_type, full_name):
    """Send email notification when a school is created using Brevo."""
    subject = 'School Registration Confirmation - School Management System'

    login_url = "https://your-domain.com/login"  # Replace with your actual login URL

    html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: auto; padding: 20px; border: 1px solid #eee; border-radius: 8px;">
                    <h2 style="color: #2c3e50;">School Registration Confirmation</h2>
                    <p>Dear {full_name},</p>
                    <p>Congratulations! Your school has been successfully registered with the <strong>School Management System</strong>.</p>
                    <p><strong>School Details:</strong></p>
                    <ul style="list-style-type: none; padding-left: 0;">
                        <li><strong>School Name:</strong> {school_name}</li>
                        <li><strong>School Type:</strong> {school_type.title()}</li>
                    </ul>
                    <p>You can now log in to your account and start managing your school’s operations efficiently.</p>
                    <p>
                        <a href="{login_url}" style="display: inline-block; padding: 10px 20px; background-color: #2c3e50; color: #fff; text-decoration: none; border-radius: 4px;">
                            Log In Now
                        </a>
                    </p>
                    <p>If the button above doesn't work, copy and paste this URL into your browser: <br>
                        <a href="{login_url}">{login_url}</a>
                    </p>
                    <p>We’re excited to have you on board!</p>
                    <p>Best regards,<br>School Management,<br>Qodebyte Team</p>
                </div>
            </body>
        </html>
        """

    text_content = f"""\
        School Registration Confirmation

        Dear {full_name},

        Congratulations! Your school has been successfully registered with the School Management System.

        School Details:
        - School Name: {school_name}
        - School Type: {school_type.title()}

        You can now log in and start managing your school.

        Login here: {login_url}

        Best regards,
        School Management
        Qodebyte Team
        """
    try:
        return send_email_with_brevo(email, subject, html_content, text_content)
    except Exception as e:
        #print(f"Failed to send school creation email: {str(e)}")
        raise e

def send_teacher_credentials_email(email, password, full_name, school_name):
    """Send login credentials to a newly created teacher using Brevo."""
    subject = 'Your Teacher Account Credentials - School Management System'

    login_url = "https://your-domain.com/login"  # Replace with your actual login URL

    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: auto; padding: 20px; border: 1px solid #eee; border-radius: 8px;">
                <h2 style="color: #2c3e50;">Welcome to the School Management System</h2>
                <p>Dear {full_name},</p>
                <p>Your teacher account has been successfully created for <strong>{school_name}</strong>.</p>
                <p><strong>Your login credentials:</strong></p>
                <ul style="list-style-type: none; padding-left: 0;">
                    <li><strong>Email:</strong> {email}</li>
                    <li><strong>Password:</strong> {password}</li>
                </ul>
                <p>To access your account, please click the button below:</p>
                <p>
                    <a href="{login_url}" style="display: inline-block; padding: 10px 20px; background-color: #2c3e50; color: #fff; text-decoration: none; border-radius: 4px;">
                        Log In to Your Account
                    </a>
                </p>
                <p>If the button above doesn’t work, copy and paste this URL into your browser:<br>
                    <a href="{login_url}">{login_url}</a>
                </p>
                <p>We recommend changing your password after your first login.</p>
                <p>Best regards,<br>School Management,<br>Qodebyte Team</p>
            </div>
        </body>
    </html>
    """

    text_content = f"""\
    Welcome to the School Management System

    Dear {full_name},

    Your teacher account has been created for {school_name}.

    Login Credentials:
    - Email: {email}
    - Password: {password}

    You can log in here: {login_url}

    We recommend changing your password after your first login.

    Best regards,
    School Management
    Qodebyte Team
    """

    
    try:
        return send_email_with_brevo(email, subject, html_content, text_content)
    except Exception as e:
        #print(f"Failed to send teacher credentials email: {str(e)}")
        raise e