from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.

class User(AbstractUser):
    services = models.ManyToManyField("Service", through="UserServiceConnection")
    codes = models.ManyToManyField('Code')


class Service(models.Model):
    name = models.CharField(max_length=128)
    icon = models.CharField(max_length=32)
    sub_url = models.CharField(max_length=128)
    regex = models.BooleanField(default=False)
    origin = models.CharField(max_length=64)

    def __str__(self):
        return self.name


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
