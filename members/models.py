from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from fernet_fields import EncryptedCharField


def validate_file_size(value):
    """Валидация размера файла"""
    filesize = value.size
    if filesize > 5 * 1024 * 1024:  # 5 MB
        raise ValidationError(f'Размер файла не должен превышать 5 МБ. Текущий размер: {filesize / 1024 / 1024:.1f} МБ')


class Member(models.Model):
    """Модель члена ассоциации"""
    
    # Статусы участников
    STATUS_CHOICES = [
        ('pending', 'На модерации'),
        ('active', 'Активен'),
        ('blocked', 'Заблокирован'),
    ]
    
    # Категории членства
    MEMBERSHIP_CATEGORIES = [
        ('veteran', 'Ветеран (физ. лицо, пожизненно)'),
        ('partner_veteran', 'Партнёр-ветеран (юридическое лицо)'),
        ('partner_support', 'Партнёр-поддержка (юридическое лицо)'),
        ('associate_partner', 'Ассоциированный партнёр (юридическое лицо)'),
    ]
    
    # Связь с пользователем Django (один к одному)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    
    # Публичные поля (не шифруются)
    company_name = models.CharField(
        max_length=255,
        verbose_name='Название компании',
        help_text='Полное юридическое название организации'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата регистрации'
    )
    
    email = models.EmailField(
        verbose_name='Email для входа',
        unique=True
    )
    
    membership_category = models.CharField(
        max_length=30,
        choices=MEMBERSHIP_CATEGORIES,
        default='associate_partner',
        verbose_name='Категория членства'
    )
    
    annual_revenue = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Годовой оборот (руб.)',
        help_text='Для расчёта членского взноса'
    )
    
    provides_support = models.BooleanField(
        default=False,
        verbose_name='Оказывает поддержку ветеранам'
    )
    
    # Зашифрованные поля (персональные данные)
    inn = EncryptedCharField(
        max_length=12,
        verbose_name='ИНН',
        help_text='Идентификационный номер налогоплательщика (10 или 12 цифр)'
    )
    
    ogrn = EncryptedCharField(
        max_length=15,
        verbose_name='ОГРН',
        help_text='Основной государственный регистрационный номер (13 или 15 цифр)'
    )
    
    legal_address = EncryptedCharField(
        max_length=500,
        verbose_name='Юридический адрес'
    )
    
    actual_address = EncryptedCharField(
        max_length=500,
        verbose_name='Фактический адрес',
        blank=True,
        null=True,
        help_text='Если не указан, совпадает с юридическим'
    )
    
    director_fullname = EncryptedCharField(
        max_length=255,
        verbose_name='ФИО директора'
    )
    
    phone = EncryptedCharField(
        max_length=20,
        verbose_name='Телефон'
    )
    
    agreement_signed = models.BooleanField(
        default=False,
        verbose_name='Согласие на обработку ПДн'
    )
    
    agreement_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата согласия'
    )
    
    next_payment_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Дата следующего платежа'
    )
    
    # Документы с валидацией (исправлено!)
    charter_document = models.FileField(
        upload_to='documents/',
        blank=True,
        null=True,
        verbose_name='Устав организации (PDF)',
        help_text='Загрузите устав организации в формате PDF',
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'],
                message='Поддерживаются только PDF, JPG и PNG файлы'
            ),
            validate_file_size
        ]
    )
    
    ogrn_document = models.FileField(
        upload_to='documents/',
        blank=True,
        null=True,
        verbose_name='Свидетельство ОГРН (PDF)',
        help_text='Свидетельство о государственной регистрации',
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'],
                message='Поддерживаются только PDF, JPG и PNG файлы'
            ),
            validate_file_size
        ]
    )
    
    inn_document = models.FileField(
        upload_to='documents/',
        blank=True,
        null=True,
        verbose_name='Свидетельство ИНН (PDF)',
        help_text='Свидетельство о постановке на учет в налоговом органе',
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'],
                message='Поддерживаются только PDF, JPG и PNG файлы'
            ),
            validate_file_size
        ]
    )
    
    additional_document = models.FileField(
        upload_to='documents/',
        blank=True,
        null=True,
        verbose_name='Дополнительный документ (PDF)',
        help_text='Любые дополнительные документы',
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'],
                message='Поддерживаются только PDF, JPG и PNG файлы'
            ),
            validate_file_size
        ]
    )
    
    class Meta:
        verbose_name = 'Член ассоциации'
        verbose_name_plural = 'Члены ассоциации'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.company_name} ({self.get_status_display()})"
    