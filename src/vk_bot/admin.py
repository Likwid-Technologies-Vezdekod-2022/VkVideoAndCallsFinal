from django.contrib import admin
from . import models


@admin.register(models.VkUser)
class VkUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat_id', 'name',)
    search_fields = ('id', 'chat_id', 'name',)
    ordering = ['-update_date']


@admin.register(models.Operator)
class OperatorAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'number', 'url')
    ordering = ['-update_date']
