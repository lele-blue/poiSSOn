from django_ratelimit.core import is_ratelimited
from rest_framework.permissions import BasePermission
from rest_framework_api_key.permissions import BaseHasAPIKey

from main.models import ConfigurationApiKey, Service
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
