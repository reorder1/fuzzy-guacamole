import os

from django.core.management.base import BaseCommand

from accounts.models import User


class Command(BaseCommand):
    help = 'Seed the default admin user from environment variables.'

    def handle(self, *args, **options):
        email = os.environ.get('ADMIN_EMAIL')
        password = os.environ.get('ADMIN_PASSWORD')
        if not email or not password:
            self.stdout.write(self.style.WARNING('ADMIN_EMAIL or ADMIN_PASSWORD not set; skipping.'))
            return
        user, created = User.objects.get_or_create(username=email, defaults={'email': email})
        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.role = User.ROLE_ADMIN
        user.set_password(password)
        user.save()
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created admin user {email}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Updated admin user {email}'))
