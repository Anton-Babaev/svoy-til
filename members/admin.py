from django.contrib import admin
from .models import Member


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'joined_at')
    list_filter = ('status',)
    search_fields = ('user__email',)
