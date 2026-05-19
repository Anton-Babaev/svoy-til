from django.contrib import admin
from .models import News, SupportMeasure, Project, Event, EventRegistration
from django.utils.html import format_html

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'published_at', 'is_published']
    list_filter = ['is_published', 'published_at']
    search_fields = ['title', 'content']

@admin.register(SupportMeasure)
class SupportMeasureAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at']
    search_fields = ['title']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active', 'start_date']
    search_fields = ['title']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_date', 'end_date', 'status', 'current_participants', 'max_participants']
    list_filter = ['status', 'start_date']
    search_fields = ['title', 'description']
    filter_horizontal = []
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'short_description', 'description', 'status')
        }),
        ('Дата и время', {
            'fields': ('start_date', 'end_date', 'registration_deadline')
        }),
        ('Место проведения', {
            'fields': ('location', 'address')
        }),
        ('Участники', {
            'fields': ('max_participants', 'current_participants')
        }),
        ('Медиа', {
            'fields': ('image', 'youtube_link')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['event', 'member', 'status', 'registered_at']
    list_filter = ['status', 'event']
    search_fields = ['member__company_name', 'event__title']
    
    # Добавляем возможность менять статус
    list_editable = ['status']
    
    # Действия для массовой смены статуса
    actions = ['confirm_registrations', 'cancel_registrations']
    
    def confirm_registrations(self, request, queryset):
        queryset.update(status='confirmed')
        self.message_user(request, f'{queryset.count()} регистраций подтверждено')
    confirm_registrations.short_description = 'Подтвердить выбранные регистрации'
    
    def cancel_registrations(self, request, queryset):
        for reg in queryset:
            if reg.status == 'registered' and reg.event.current_participants > 0:
                reg.event.current_participants -= 1
                reg.event.save()
            reg.status = 'cancelled'
            reg.save()
        self.message_user(request, f'{queryset.count()} регистраций отменено')
    cancel_registrations.short_description = 'Отменить выбранные регистрации'