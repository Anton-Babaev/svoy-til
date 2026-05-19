from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from fernet_fields import EncryptedCharField


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

    # Категория членства
    membership_category = models.CharField(
        max_length=30,
        choices=MEMBERSHIP_CATEGORIES,
        default='associate_partner',
        verbose_name='Категория членства'
    )

    # Для юридических лиц — годовой оборот (для расчёта взносов)
    annual_revenue = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Годовой оборот (руб.)',
        help_text='Для расчёта членского взноса'
    )

    # Флаг: оказывает ли поддержку ветеранам (для категории "Партнёр-поддержка")
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

    # Согласие на обработку ПДн
    agreement_signed = models.BooleanField(
        default=False,
        verbose_name='Согласие на обработку ПДн'
    )
    agreement_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата согласия'
    )

    # Для автоматизации платежей (пока заглушка)
    next_payment_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Дата следующего платежа'
    )

    # Документы
    charter_document = models.FileField(
        upload_to='documents/',
        blank=True,
        null=True,
        verbose_name='Устав организации (PDF)',
        help_text='Загрузите устав организации в формате PDF'
    )
    ogrn_document = models.FileField(
        upload_to='documents/',
        blank=True,
        null=True,
        verbose_name='Свидетельство ОГРН (PDF)',
        help_text='Свидетельство о государственной регистрации'
    )
    inn_document = models.FileField(
        upload_to='documents/',
        blank=True,
        null=True,
        verbose_name='Свидетельство ИНН (PDF)',
        help_text='Свидетельство о постановке на учет в налоговом органе'
    )
    additional_document = models.FileField(
        upload_to='documents/',
        blank=True,
        null=True,
        verbose_name='Дополнительный документ (PDF)',
        help_text='Любые дополнительные документы'
    )

    class Meta:
        verbose_name = 'Член ассоциации'
        verbose_name_plural = 'Члены ассоциации'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.company_name} ({self.get_status_display()})"


# Сигналы временно отключены (работаем через админку)
# @receiver(post_save, sender=User)
# def create_user_member(sender, instance, created, **kwargs):
#     """Автоматически создаёт профиль члена при создании пользователя"""
#     if created:
#         Member.objects.create(user=instance, email=instance.username)


# @receiver(post_save, sender=User)
# def save_user_member(sender, instance, **kwargs):
#     """Автоматически сохраняет профиль члена при сохранении пользователя"""
#     try:
#         instance.member.save()
#     except Member.DoesNotExist:
#         Member.objects.create(user=instance, email=instance.username)
