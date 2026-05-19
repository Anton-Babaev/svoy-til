# accounts/management/commands/test_email.py
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Test email configuration'

    def handle(self, *args, **options):
        self.stdout.write('Testing email configuration...')
        self.stdout.write(f'From: {settings.DEFAULT_FROM_EMAIL}')
        self.stdout.write(f'Host: {settings.EMAIL_HOST}')
        
        try:
            send_mail(
                'Test email from Django',
                'This is a test email to verify SMTP configuration.',
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAILS[0]],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS('Email sent successfully!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to send email: {e}'))
