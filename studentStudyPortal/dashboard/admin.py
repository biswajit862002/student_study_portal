from django.contrib import admin
from .models import Notes, Homework, Todo

# Register your models here.

@admin.register(Notes)
class AdminNotes(admin.ModelAdmin):
    list_display = ['id', 'title', 'description']

@admin.register(Homework)
class AdminHomework(admin.ModelAdmin):
    list_display = ['id', 'user', 'subject', 'title', 'description', 'due', 'is_finished']


@admin.register(Todo)
class AdminTodo(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'is_finished']
