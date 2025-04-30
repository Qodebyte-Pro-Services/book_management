import sib_api_v3_sdk
from django.conf import settings

def configure_brevo_api():
    """Configure Brevo API with API key from settings."""
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.BREVO_API_KEY
    return configuration

def get_brevo_api_instance():
    """Get an instance of the Brevo API."""
    configuration = configure_brevo_api()
    return sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
