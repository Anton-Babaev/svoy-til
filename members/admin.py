from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.utils.crypto import get_random_string
from django.contrib import messages
from .models import Member


class MemberInline(admin.StackedInline):
    """Инлайн для редактирования Member прямо на странице User"""
    model = Member
    can_delete = False
    verbose_name_plural = 'Член ассоциации'
    # Эти поля нельзя редактировать при создании User
    readonly_fields = ['company_name', 'inn', 'ogrn', 'legal_address', 
                       'actual_address', 'director_fullname', 'phone', 
                       'membership_category', 'annual_revenue', 'provides_support']


class CustomUserAdmin(UserAdmin):
    """Расширенная админка для пользователей с инлайном Member"""
    inlines = [MemberInline]
    
    def save_model(self, request, obj, form, change):
        """Переопределяем сохранение User"""
        super().save_model(request, obj, form, change)
        # Если у пользователя еще нет Member - создаем
        Member.objects.get_or_create(user=obj, defaults={'email': obj.email})


# Отменяем старую регистрацию User и регистрируем новую
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
admin.site.register(User, CustomUserAdmin)


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    """Админка для управления членами ассоциации"""
    list_display = ['company_name', 'membership_category', 'status', 'created_at', 'email']
    list_filter = ['status', 'membership_category', 'created_at']
    search_fields = ['company_name', 'inn', 'ogrn', 'email']
    readonly_fields = ['created_at', 'agreement_date']
    
    # Поля для фильтрации по годам
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
        ('Согласие и даты', {
            'fields': ('agreement_signed', 'agreement_date', 'created_at'),
            'description': 'Юридически значимая информация'
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """
        Переопределяем сохранение Member.
        Главное изменение: НЕ создаем нового User, если Member уже существует.
        """
        if not change:  # Если создается новый объект
            # Проверяем, есть ли уже Member с таким email
            existing_member = Member.objects.filter(email=obj.email).first()
            
            if existing_member:
                # Если есть - сообщаем пользователю
                messages.error(
                    request, 
                    f'Член с email {obj.email} уже существует! Используйте существующего пользователя.'
                )
                return
            
            # Ищем пользователя по email
            user = User.objects.filter(username=obj.email).first()
            
            if user:
                # Пользователь существует - проверяем, есть ли у него Member
                if hasattr(user, 'member'):
                    messages.error(
                        request,
                        f'У пользователя {user.username} уже есть член ассоциации!'
                    )
                    return
                obj.user = user
            else:
                # Создаем нового пользователя
                password = get_random_string(12)
                user = User.objects.create_user(
                    username=obj.email,
                    email=obj.email,
                    password=password
                )
                obj.user = user
                
                # Показываем пароль админу
                messages.success(
                    request,
                    f'Создан пользователь {obj.email} с паролем: {password}'
                )
        
        # Сохраняем объект
        super().save_model(request, obj, form, change)
    
    def delete_model(self, request, obj):
        """При удалении члена не удаляем пользователя, только помечаем"""
        # Можно добавить логирование или просто удалить Member
        obj.delete()
        messages.warning(request, f'Член {obj.company_name} удален. Пользователь {obj.user.username} остался в системе.')