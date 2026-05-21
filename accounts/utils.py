from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
import logging

logger = logging.getLogger(__name__)


def send_registration_email(user, member, request):
    """Отправка письма при регистрации"""
    try:
        current_site = get_current_site(request)
        subject = 'Регистрация в ассоциации "Свой Тыл"'
        
        context = {
            'user': user,
            'member': member,
            'domain': current_site.domain,
            'protocol': 'https' if request.is_secure() else 'http',
        }
        
        html_message = render_to_string('accounts/emails/registration_email.html', context)
        plain_message = f"""
        Уважаемый(ая) {member.director_fullname}!
        
        Ваша заявка на вступление в ассоциацию "Свой Тыл" успешно зарегистрирована.
        
        Данные заявки:
        - Организация: {member.company_name}
        - Email: {member.email}
        - Статус: На модерации
        
        Мы рассмотрим вашу заявку в ближайшее время и сообщим о решении.
        
        С уважением,
        Администрация ассоциации "Свой Тыл"
        """
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,  # Исправлено: используем настройки
            [member.email],
            fail_silently=False,
            html_message=html_message
        )
        logger.info(f"Registration email sent to {member.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send registration email: {e}")
        return False


def send_admin_notification(member, request):
    """Отправка уведомления админу о новой регистрации"""
    try:
        current_site = get_current_site(request)
        subject = f'Новая заявка на регистрацию - {member.company_name}'
        
        context = {
            'member': member,
            'domain': current_site.domain,
            'admin_url': f'{current_site.domain}/admin/members/member/',
        }
        
        html_message = render_to_string('accounts/emails/admin_notification.html', context)
        plain_message = f"""
        Новая заявка на регистрацию!
        
        Организация: {member.company_name}
        Email: {member.email}
        Телефон: {member.phone}
        
        Для модерации перейдите в админку: {context['admin_url']}
        """
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,  # Исправлено: используем настройки
            settings.ADMIN_EMAILS,
            fail_silently=False,
            html_message=html_message
        )
        logger.info(f"Admin notification sent for {member.company_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to send admin notification: {e}")
        return False
    