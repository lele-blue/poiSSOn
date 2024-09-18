from uuid import uuid4
from django.contrib.auth.models import AbstractUser
from oidc_provider.models import Client as OIDCClient
from django.db import models
from django.contrib.auth.hashers import check_password, make_password
from rest_framework_api_key.models import AbstractAPIKey


# Create your models here.

class User(AbstractUser):
    services = models.ManyToManyField("Service", through="UserServiceConnection")
    codes = models.ManyToManyField('Code')
    sso_groups = models.ManyToManyField("Group", related_name="users")


class Group(models.Model):
    slug = models.CharField(max_length=32)
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=128)
    icon = models.CharField(max_length=32)
    sub_url = models.CharField(max_length=128)
    regex = models.BooleanField(default=False)
    origin = models.CharField(max_length=64, null=True, blank=True)
    oidc_client = models.OneToOneField(OIDCClient, on_delete=models.SET_NULL, null=True, blank=True)
    allow_max_configurations = models.PositiveSmallIntegerField(null=True, blank=True, default=0)
    can_have_application_password = models.BooleanField(default=False)
    configuration_view_template = models.TextField(blank=True)

    def __str__(self):
        return self.name


class ApplicationPassword(models.Model):
    password = models.TextField()
    id = models.UUIDField(default=uuid4, primary_key=True)

    def save(self, *args, **kwargs):
        if len(self.password.split("$")) < 4:
            self.set_password(self.password)
        return super().save(*args, **kwargs)

    def set_password(self, password):
        self.password = make_password(password)

    def check_password(self, password):
        return check_password(password, self.password)

    def __str__(self):
        if self.service_config.exists():
            return f"ApplicationPassword for ServiceConfiguration {self.service_config.first().value_for_step.service.name}/{self.service_config.first().value_for_step.title}/{self.service_config.first().set_idx} - {self.service_config.first().user.username}"
        elif self.service_connection.exists():
            return f"ApplicationPassword for ServiceConnection {self.service_connection.first().service.name} - {self.service_connection.first().user.username}"

        else:
            return "Not linked - Orphaned"


class ServiceConfigurationStep(models.Model):
    index = models.PositiveSmallIntegerField();
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="configuration_steps")
    query_id = models.CharField(max_length=32)
    title = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    check_regex = models.CharField(max_length=512, blank=True)
    hidden = models.BooleanField(default=False)
    is_password = models.BooleanField()
    default = models.TextField(blank=True)

    def __str__(self):
        return f"{self.service.name} - {self.index} - {self.title}"

    class Meta:
        unique_together = ["index", "service"]
        ordering = ["service", "index"]

class ServiceConfiguration(models.Model):
    value_for_step = models.ForeignKey(ServiceConfigurationStep, on_delete=models.CASCADE)
    value = models.TextField()
    set_idx = models.PositiveSmallIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    password = models.ForeignKey(ApplicationPassword, null=True, blank=True, on_delete=models.CASCADE, related_name="service_config")

    def __str__(self):
        return f"{self.value_for_step.service.name} {self.value_for_step.title} {self.user.username}"

    class Meta:
        unique_together = ["value_for_step", "set_idx", "user"]
        ordering = ["user", "value_for_step__service", "set_idx"]


class ConfigurationApiKey(AbstractAPIKey):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)


class OriginMigrationToken(models.Model):
    token = models.CharField(max_length=128, primary_key=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    codes = models.ManyToManyField("Code")
    expires = models.DateTimeField()
    account = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)


class Code(models.Model):
    code = models.CharField(max_length=20)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='codes')

    def is_valid(self):
        return True


class UserServiceConnection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    username = models.CharField(max_length=128, blank=True)
    passwordPlain = models.CharField(max_length=128, blank=True)
    configuration_allow_max = models.PositiveSmallIntegerField(null=True, blank=True, default=None)
    application_password = models.ForeignKey(ApplicationPassword, on_delete=models.SET_NULL, null=True, blank=True, related_name="service_connection")

    def __str__(self):
        return f"{self.user.username} - {self.service.name}"

    class Meta:
        ordering = ["user"]
