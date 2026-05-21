from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils.crypto import get_random_string
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import Member


class MemberInline(admin.StackedInline):
    """Инлайн для редактирования Member прямо на странице User"""
    model = Member
    can_delete = False
    verbose_name_plural = 'Член ассоциации'
    readonly_fields = ['company_name', 'inn', 'ogrn', 'legal_address',
                       'actual_address', 'director_fullname', 'phone',
                       'membership_category', 'annual_revenue', 'provides_support']


class CustomUserAdmin(UserAdmin):
    """Расширенная админка для пользователей с инлайном Member"""
    inlines = [MemberInline]
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        Member.objects.get_or_create(user=obj, defaults={'email': obj.email})


try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
admin.site.register(User, CustomUserAdmin)


def send_status_change_email(member, old_status, new_status):
    """Отправка письма при смене статуса"""
    try:
        status_labels = {
            'pending': 'На модерации',
            'active': 'Активен',
            'blocked': 'Заблокирован'
        }
        
        subject = f'Изменение статуса заявки - {member.company_name}'
        
        context = {
            'member': member,
            'old_status': status_labels.get(old_status, old_status),
            'new_status': status_labels.get(new_status, new_status),
        }
        
        html_message = render_to_string('accounts/emails/status_change_email.html', context)
        plain_message = f"""
        Уважаемый(ая) {member.director_fullname}!
        
        Статус вашей заявки изменен с "{context['old_status']}" на "{context['new_status']}".
        
        С уважением,
        Администрация ассоциации "Свой Тыл"
        """
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [member.email],
            fail_silently=False,
            html_message=html_message
        )
        return True
    except Exception as e:
        print(f"Failed to send status change email: {e}")
        return False


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    """Админка для управления членами ассоциации"""
    list_display = ['company_name', 'membership_category', 'status', 'created_at', 'email']
    list_filter = ['status', 'membership_category', 'created_at']
    search_fields = ['company_name', 'inn', 'ogrn', 'email']
    readonly_fields = ['created_at', 'agreement_date']
    
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('company_name', 'status', 'email'),
            'description': 'Основные данные о члене ассоциации'
        }),
        ('Категория членства и взносы', {
            'fields': ('membership_category', 'annual_revenue', 'provides_support', 'next_payment_date'),
            'description': 'Категория влияет на размер взносов и доступные возможности'
        }),
        ('Персональные данные (зашифрованы)', {
            'fields': ('inn', 'ogrn', 'legal_address', 'actual_address', 'director_fullname', 'phone'),
            'description': 'Все данные шифруются в базе данных'
        }),
        ('Загруженные документы', {
            'fields': ('charter_document', 'ogrn_document', 'inn_document', 'additional_document')
        }),
        ('Согласие и даты', {
            'fields': ('agreement_signed', 'agreement_date', 'created_at'),
            'description': 'Юридически значимая информация'
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Переопределяем сохранение Member с отправкой уведомления"""
        old_status = None
        if change:
            original = Member.objects.get(pk=obj.pk)
            old_status = original.status
        
        if not change:
            # Создание нового члена
            existing_member = Member.objects.filter(email=obj.email).first()
            if existing_member:
                messages.error(request, f'Член с email {obj.email} уже существует!')
                return
            
            user = User.objects.filter(username=obj.email).first()
            if user:
                if hasattr(user, 'member'):
                    messages.error(request, f'У пользователя {user.username} уже есть член ассоциации!')
                    return
                obj.user = user
            else:
                password = get_random_string(12)
                user = User.objects.create_user(
                    username=obj.email,
                    email=obj.email,
                    password=password
                )
                obj.user = user
                # Отправляем пароль на email (безопасно, не в логах)
                try:
                    send_mail(
                        'Доступ в личный кабинет',
                        f'Ваш пароль для входа: {password}\nРекомендуем сменить его после первого входа.',
                        settings.DEFAULT_FROM_EMAIL,
                        [obj.email],
                        fail_silently=False,
                    )
                    messages.success(request, f'Создан пользователь {obj.email}. Пароль отправлен на email.')
                except Exception as e:
                    messages.warning(request, f'Создан пользователь {obj.email}, но не удалось отправить пароль по email.')
        
        super().save_model(request, obj, form, change)
        
        # Отправляем уведомление при смене статуса
        if change and old_status and old_status != obj.status:
            if send_status_change_email(obj, old_status, obj.status):
                messages.success(request, f'Уведомление отправлено пользователю {obj.email}')
            else:
                messages.warning(request, f'Не удалось отправить уведомление пользователю {obj.email}')
    
    def delete_model(self, request, obj):
        obj.delete()
        messages.warning(request, f'Член {obj.company_name} удален. Пользователь {obj.user.username} остался в системе.')
        