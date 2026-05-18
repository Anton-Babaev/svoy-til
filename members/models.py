from django.db import models
from users.models import User


class Member(models.Model):
    """Модель члена ассоциации (заглушка)"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    STATUS_CHOICES = (
        ('pending', 'Ожидает проверки'),
        ('active', 'Активен'),
        ('exited', 'Вышел'),
        ('excluded', 'Исключен'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Член ассоциации'
        verbose_name_plural = 'Члены ассоциации'
    
    def __str__(self):
        return f"{self.user.email} - {self.get_status_display()}"