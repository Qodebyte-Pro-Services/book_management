from django.core.management.base import BaseCommand
from schools.models import School, Domain
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Create public tenant with simplified approach'

    def handle(self, *args, **options):
        # Check if public tenant exists
        if School.objects.filter(schema_name='public').exists():
            self.stdout.write(self.style.SUCCESS('Public tenant already exists'))
            return
            
        # Create admin user directly with the model
        email = 'admin@gmail.com'
        if not User.objects.filter(email=email).exists():
            admin = User(
                email=email,
                username='admin',
                is_staff=True,
                is_superuser=True,
                is_verified=True,
                is_active=True,
                date_joined=timezone.now()
            )
            admin.set_password('admin')
            admin.save()
        else:
            admin = User.objects.get(email=email)
            
        # Create public tenant
        public_tenant = School(
            schema_name='public',
            name='Public',
            address='Public Address',
            description='Public Tenant',
            school_type='both',
            admin=admin
        )
        public_tenant.save()
        
        # Create domain
        domain = Domain(
            domain='localhost',
            tenant=public_tenant,
            is_primary=True
        )
        domain.save()
        
        self.stdout.write(self.style.SUCCESS('Public tenant created successfully'))
