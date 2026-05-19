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
