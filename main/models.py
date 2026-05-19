from django.db import models


class News(models.Model):
    """Новости ассоциации"""
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Содержание')
    published_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-published_at']

    def __str__(self):
        return self.title


class SupportMeasure(models.Model):
    """Меры поддержки"""
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    document = models.FileField(
        upload_to='support_documents/',
        blank=True,
        null=True,
        verbose_name='Документ (PDF)'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Мера поддержки'
        verbose_name_plural = 'Меры поддержки'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Project(models.Model):
    """Проекты ассоциации"""
    title = models.CharField(max_length=200, verbose_name='Название проекта')
    description = models.TextField(verbose_name='Описание')
    start_date = models.DateField(verbose_name='Дата начала')
    end_date = models.DateField(
        verbose_name='Дата окончания',
        blank=True,
        null=True
    )
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ['-start_date']

    def __str__(self):
        return self.title

class Event(models.Model):
    """Модель мероприятий"""
    
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('published', 'Опубликовано'),
        ('completed', 'Завершено'),
        ('cancelled', 'Отменено'),
    ]
    
    title = models.CharField(
        max_length=200,
        verbose_name='Название мероприятия'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    short_description = models.TextField(
        max_length=500,
        verbose_name='Краткое описание',
        help_text='Отображается в карточке мероприятия'
    )
    
    # Дата и время
    start_date = models.DateTimeField(
        verbose_name='Дата и время начала'
    )
    end_date = models.DateTimeField(
        verbose_name='Дата и время окончания'
    )
    registration_deadline = models.DateTimeField(
        verbose_name='Крайний срок регистрации',
        null=True,
        blank=True
    )
    
    # Место проведения
    location = models.CharField(
        max_length=255,
        verbose_name='Место проведения'
    )
    address = models.CharField(
        max_length=500,
        verbose_name='Адрес',
        blank=True
    )
    
    # Вместимость
    max_participants = models.PositiveIntegerField(
        default=0,
        verbose_name='Максимум участников',
        help_text='0 - без ограничений'
    )
    current_participants = models.PositiveIntegerField(
        default=0,
        verbose_name='Текущее количество участников'
    )
    
    # Статус
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Статус'
    )
    
    # Изображение
    image = models.ImageField(
        upload_to='events/',
        blank=True,
        null=True,
        verbose_name='Изображение мероприятия'
    )
    
    # Ссылки
    youtube_link = models.URLField(
        blank=True,
        verbose_name='Ссылка на YouTube трансляцию'
    )
    
    # Дополнительно
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    
    class Meta:
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'
        ordering = ['start_date']
    
    def __str__(self):
        return f"{self.title} - {self.start_date.strftime('%d.%m.%Y %H:%M')}"
    
    def is_registration_open(self):
        """Проверяет, открыта ли регистрация"""
        from django.utils import timezone
        if self.status != 'published':
            return False
        if self.registration_deadline and self.registration_deadline < timezone.now():
            return False
        if self.max_participants > 0 and self.current_participants >= self.max_participants:
            return False
        return True
    
    def places_left(self):
        """Возвращает количество свободных мест"""
        if self.max_participants == 0:
            return None  # Без ограничений
        return self.max_participants - self.current_participants


class EventRegistration(models.Model):
    """Регистрация участников на мероприятия"""
    
    STATUS_CHOICES = [
        ('registered', 'Зарегистрирован'),
        ('confirmed', 'Подтвержден'),
        ('cancelled', 'Отменен'),
        ('attended', 'Посетил'),
    ]
    
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='registrations',
        verbose_name='Мероприятие'
    )
    member = models.ForeignKey(
        'members.Member',
        on_delete=models.CASCADE,
        related_name='event_registrations',
        verbose_name='Участник'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='registered',
        verbose_name='Статус'
    )
    
    registered_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата регистрации'
    )
    
    comment = models.TextField(
        blank=True,
        verbose_name='Комментарий'
    )
    
    class Meta:
        verbose_name = 'Регистрация на мероприятие'
        verbose_name_plural = 'Регистрации на мероприятия'
        unique_together = ['event', 'member']  # Одна регистрация на мероприятие
    
    def __str__(self):
        return f"{self.member.company_name} - {self.event.title}"
