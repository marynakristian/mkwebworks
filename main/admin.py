from django.contrib import admin
from .models import ContactMessage, Review  # Импортируем модель Review

# Регистрируем модель Review в админке
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'is_published')  # Показываем эти поля
    list_filter = ('is_published',)  # Фильтруем по полю is_published
    search_fields = ('name', 'content')  # Поиск по имени и контенту отзыва


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    search_fields = ('name', 'email')