from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from rest_framework_api_key.admin import APIKeyModelAdmin
from .models import ApplicationPassword, ConfigurationApiKey, CoreSetting, LoginLink, ServiceConfiguration, ServiceConfigurationStep, User, Service, UserServiceConnection, Code, Group


class TermInlineAdmin(admin.TabularInline):
    model = UserServiceConnection


UserAdmin.fieldsets += (['services', {'fields': []}],)
UserAdmin.fieldsets += (['groups', {'fields': ["sso_groups"]}],)
UserAdmin.fieldsets[0][1]["fields"] = [*UserAdmin.fieldsets[0][1]["fields"], "uid"]

UserAdmin.readonly_fields += ("uid",)

admin.site.register(User, UserAdmin)
admin.site.register(Service)
admin.site.register(UserServiceConnection)
admin.site.register(Code)
admin.site.register(Group)
admin.site.register(ServiceConfigurationStep)
admin.site.register(ServiceConfiguration)
admin.site.register(ApplicationPassword)
admin.site.register(CoreSetting)
admin.site.register(LoginLink)

@admin.register(ConfigurationApiKey)
class OrganizationAPIKeyModelAdmin(APIKeyModelAdmin):
    pass
