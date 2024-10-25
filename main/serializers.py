import django_otp
from rest_framework import serializers

from main.models import ServiceConfiguration, ServiceConfigurationStep, UserServiceConnection, Service, OriginMigrationToken


class ServiceSerializer(serializers.ModelSerializer):
    configurable = serializers.SerializerMethodField()
    max_configurations = serializers.SerializerMethodField()
    has_configurations = serializers.SerializerMethodField()
    require_2fa = serializers.SerializerMethodField()

    def get_require_2fa(self, obj: Service):
        return obj.require_2fa_if_configured and not self.context["user"].is_verified() and django_otp.user_has_device(self.context["user"])

    def get_configurable(self, obj: Service):
        return obj.configuration_steps.exists()

    def get_max_configurations(self, service: Service):
        if not "user" in self.context:
            return service.allow_max_configurations
        try:
            conn = UserServiceConnection.objects.get(user=self.context["user"], service = service)
            return conn.configuration_allow_max or service.allow_max_configurations
        except UserServiceConnection.DoesNotExist:
            return service.allow_max_configurations

    def get_has_configurations(self, service: Service):
        if not "user" in self.context:
            return None
        return ServiceConfiguration.objects.filter(value_for_step__service=service, user=self.context["user"]).values_list("set_idx", flat=True).distinct().count()


    class Meta:
        model = Service
        fields = ["name", "icon", "sub_url", "origin", "max_configurations", "has_configurations", "configurable", "can_have_application_password", "configuration_view_template", "require_2fa"]


class ServiceConfigurationStepSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["query_id", "title", "description", "check_regex", "default", "is_password"]
        model = ServiceConfigurationStep


class PublicServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ["name", "icon"]


class OriginMigrationTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = OriginMigrationToken
        fields = ["token"]


class UserConnectionSerializer(serializers.ModelSerializer):
    service = serializers.SerializerMethodField(read_only=True)

    def get_service(self, obj):
        return ServiceSerializer(obj.service, context={"user": self.context.get("request_user") or obj.user}).data

    class Meta:
        model = UserServiceConnection
        fields = ["service", "username", "passwordPlain"]
