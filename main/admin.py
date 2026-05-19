from django.contrib import admin
from .models import News, SupportMeasure, Project


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
