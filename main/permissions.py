from django_otp import user_has_device
from django_ratelimit.core import is_ratelimited
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework_api_key.permissions import BaseHasAPIKey

from main.core_settings import get_core_setting
from main.models import ConfigurationApiKey, Service, User
from main.session_tree import is_master_session


class HasServicePermission(BaseHasAPIKey):
    model = ConfigurationApiKey

    def has_permission(self, request, view):
        if is_ratelimited(request, "config_management", key="ip", increment=False, rate="10/10m"):
            return False
        if super().has_permission(request, view):
            return True
        is_ratelimited(request, "config_management", key="ip", increment=True, rate="10/10m")
        return False

    def has_object_permission(self, request, view, obj: Service):
        super().has_object_permission(request, view, obj)
        key = self.get_key(request)
        if not key: return False

        setattr(request, "api_key", ConfigurationApiKey.objects.get_from_key(self.get_key(request)))


        return request.api_key.service == obj



class IsMasterSession(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and is_master_session(request)


def check_user_has_manage_permission(user: User, permission: str):
    if user.is_superuser:
        return True

    return False


class HasCoreSettingPermission(BasePermission):
    def has_permission(self, request, view):
        return check_user_has_manage_permission(request.user, view.manage_permission)

    def has_object_permission(self, request, view, obj: str):
        return check_user_has_manage_permission(request.user, f"poisson.core/{obj}")


class HasUserServiceManagePermission(BasePermission):
    def has_permission(self, request, view):
        return check_user_has_manage_permission(request.user, "poisson.user.services.manage")

class HasUserManagePermission(BasePermission):
    def has_permission(self, request, view):
        return check_user_has_manage_permission(request.user, "poisson.user.manage")

class IsSelf(BasePermission):
    def has_permission(self, request, view):
        if hasattr(view, "kwargs"):
            return request.user.uid == view.kwargs.get("uid")
        return request.user.uid == request.kwargs.get("uid")


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class IsPasswordSelfServiceEnabled(BasePermission):
    def has_permission(self, request, view):
        return get_core_setting("poisson.self_service.password", request.user)

class Verify2FactorFirst(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED

    def __init__(self):
        self.detail = {"action": "upgrade"}


class Is2FactorAuthenticated(BasePermission):
    def has_permission(self, request, view):
        if user_has_device(request.user, True) and (not request.user.is_verified()):
            raise Verify2FactorFirst()
        return True

