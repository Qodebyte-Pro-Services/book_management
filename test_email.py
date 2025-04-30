import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

# Now you can import Django stuff
from django.core.mail import send_mail

def test_django_email():
    recipient = input("Enter test email recipient: ")
    
    print(f"Sending test email to {recipient}...")
    try:
        result = send_mail(
            subject='Test Email from Django',
            message='This is a test email sent from Django.',
            from_email=None,  # Will use DEFAULT_FROM_EMAIL from settings
            recipient_list=[recipient],
            fail_silently=False,
        )
        print(f"Email sent successfully! Result: {result}")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        # If it's an SMTPException, print more details
        if hasattr(e, 'smtp_code'):
            print(f"SMTP code: {e.smtp_code}")
            print(f"SMTP error: {e.smtp_error}")

if __name__ == "__main__":
    test_django_email()