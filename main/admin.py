from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Service, UserServiceConnection, Code


class TermInlineAdmin(admin.TabularInline):
    model = UserServiceConnection


UserAdmin.fieldsets += (['services', {'fields': []}],)

admin.site.register(User, UserAdmin)
admin.site.register(Service)
admin.site.register(UserServiceConnection)
admin.site.register(Code)
