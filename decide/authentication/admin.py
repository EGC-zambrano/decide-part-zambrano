from django.contrib import admin
from .models import EmailCheck


class EmailAdmin(admin.ModelAdmin):
    list_display = ("user", "emailChecked")


admin.site.register(EmailCheck, EmailAdmin)
