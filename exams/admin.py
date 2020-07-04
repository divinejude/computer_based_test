from django.contrib import admin
from .models import *


class OptionInline(admin.TabularInline):
    model = Option
    extra = 4


class QuestionAdmin(admin.ModelAdmin):
    list_display = ['Q', 'id']
    fieldsets = [
        ('Question', {'fields': ['Q'], 'classes': ['collapse']})
    ]
    inlines = [OptionInline]
    list_filter = ['id']
    search_fields = ['Q']


admin.site.register(Question, QuestionAdmin)
admin.site.register(Profile)