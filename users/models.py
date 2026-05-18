from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Менеджер для кастомной модели User с email вместо username"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Кастомная модель пользователя. Вход по email вместо username.
    """
    username = None  # Убираем поле username
    email = models.EmailField(unique=True, verbose_name='Email')
    
    # Поле для будущей интеграции с Госуслугами (ЕСИА)
    esia_id = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name='ID в системе ЕСИА',
        help_text='Будет заполнено после привязки к Госуслугам'
    )
    
    USERNAME_FIELD = 'email'  # Вход по email
    REQUIRED_FIELDS = []      # Для createsuperuser не нужны другие поля
    
    objects = UserManager()   # Подключаем кастомный менеджер

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email
