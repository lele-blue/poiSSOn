from typing import Optional
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
import django_otp
from django_otp.models import Device
from django_otp.plugins.otp_totp.models import TOTPDevice
from rest_framework import serializers
from django.contrib.auth.password_validation import password_changed, validate_password
from rest_framework.exceptions import PermissionDenied

from main.core_settings import CORE_SETTINGS, get_core_setting
from main.models import CoreSetting, LoginLink, ServiceConfiguration, ServiceConfigurationStep, User, UserServiceConnection, Service, OriginMigrationToken
from main.permissions import check_user_has_manage_permission
from otp_webauthn.models import WebauthnDevice


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


class AdminServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ["name", "icon", "sub_url", "origin", "can_have_application_password", "require_2fa_if_configured", "uid"]


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


class UserPermissionStateSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()

    def get_permissions(self, obj: User):
        perms = []
        if obj.is_superuser:
            perms.append("poisson.manage")
            perms.append("poisson.admin")
            perms.append("poisson.core.webauthn")
            perms.append("poisson.core/poisson.core.webauthn.resident_key_requirement")
            perms.append("poisson.core/poisson.core.webauthn.hint")
            perms.append("poisson.core/poisson.core.webauthn.user_verification_requirement")
            perms.append("poisson.core/poisson.core.webauthn.authenticator_attachment")
            perms.append("poisson.manage.user.reset_password")
            perms.append("poisson.theme.manage")

        if get_core_setting("poisson.self_service.password", obj):
            perms.append("poisson.self_service.password_change")
        return perms

    @classmethod
    def get_oobe(cls):
        user = User()
        user.is_superuser = True
        user.username = "first time Setup"
        user.pk = 1337
        user.uid = "user_oobe"
        oobe = cls(user)
        print(oobe.data)
        return oobe

    class Meta:
        model = User
        fields = ["username", "permissions", "uid"]


class SmallUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    def __init__(self, instance: Optional[User] = None, *args, **kwargs):
        # prevent admin field change if not explicitly allowed
        if "data" in kwargs and instance and instance.is_superuser != kwargs.get("data", {}).get("is_superuser") and not kwargs.get("context", {}).get("can_set_superuser"):
            raise PermissionDenied()
        if "data" in kwargs and not instance:
            if kwargs.get("data", {}).get("is_superuser"):
                raise PermissionDenied()
        super().__init__(instance, *args, **kwargs)

    def get_full_name(self, obj: User):
        return obj.get_full_name()

    class Meta:
        model = User
        fields = ["username", "email", "full_name", "uid", "is_superuser"]


class FullUserSerializer(SmallUserSerializer):
    class Meta(SmallUserSerializer.Meta):
        fields = [*SmallUserSerializer.Meta.fields, "first_name", "last_name", "is_superuser"]


class CoreSettingValue(serializers.ModelSerializer):
    class Meta:
        model = CoreSetting
        fields = ["key", "value"]
        read_only_fields = ["key"]

    def validate(self, data):
        setting = CORE_SETTINGS[self.context.get("key")]
        match setting["type"]:
            case "choice":
                if data.get("value") not in setting["values"]:
                    raise serializers.ValidationError("value must be one of " + ",".join(CORE_SETTINGS[self.context.get("key")]["values"]))
            case "string":
                if len(data.get("value", "")) > setting["max_length"]:
                    raise serializers.ValidationError(f"{data.get('key')} can not be longer than {setting['max_length']} Characters.")
            case "integer":
                val = data.get("value", "")
                if not val.isnumeric():
                    raise serializers.ValidationError("Can only set integers")
                val = int(val)
                if setting.get("min") and val < setting.get("min"):
                    raise serializers.ValidationError("Value < min")
                if setting.get("max") and val > setting.get("max"):
                    raise serializers.ValidationError("Value > max")
            case "boolean":
                if data.get("value") not in ["true", "false"]:
                    raise serializers.ValidationError("Can only set to true or false")

        return data


class OTPDeviceSerializer(serializers.ModelSerializer):
    icon  = serializers.SerializerMethodField()
    type  = serializers.SerializerMethodField()

    def get_icon(self, obj):
        if isinstance(obj, WebauthnDevice):
            return obj.icon
        return None

    def get_type(self, obj):
        return obj.model_label()

    class Meta:
        # This is not true, this serializer is for all `Device`s, but since Device is abstract this is a workaround abusing ducktyping
        model = TOTPDevice
        fields = ["persistent_id", "name", "icon", "type"]


class SmallLoginLinkSerializer(serializers.ModelSerializer):

    link = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()

    def get_username(self, obj):
        return obj.user.username

    def get_link(self, obj):
        return settings.SITE_URL + settings.BASEPATH + "/go/code?token=" + obj.token

    class Meta:
        model = LoginLink
        fields = ["purpose", "service", "link", "username"]
        read_only_fields = ["creator", "created"]

class LoginLinkSerializer(SmallLoginLinkSerializer):
    created = serializers.DateTimeField(
        default=serializers.CreateOnlyDefault(timezone.now),
        read_only = True
    )

    user = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="uid", style={'base_template': 'input.html'})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self, data):
        # important check!
        # fixme, permission check in the serializer is bad
        if self.context["user"].uid != data["user"] and not check_user_has_manage_permission(self.context["user"], "poisson.user.manage"):
            raise serializers.ValidationError("Missing poisson.user.manage.password_reset permission")

        if not data.get("created"):
            data["created"] = timezone.now()

        if not data.get("creator"):
            data["creator"] = self.context["user"]

        return data

    class Meta(SmallLoginLinkSerializer.Meta):
        fields = ["purpose", "service", "user", "valid_until", "created", "link", "username"]
        read_only_fields = ["creator"]


# This class only handles password change redemptions, since session or service logins are handled on the fly in the code view
class PasswordChangeSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=32)

    def validate_password(self, password):
        validate_password(password, self.instance)
        return password


    def update(self, instance: User, validated_data):
        print(validated_data)
        instance.set_password(validated_data.get("password"))
        password_changed(validated_data.get("password"), instance)
        instance.save()
        return instance

# This class only handles password change redemptions, since session or service logins are handled on the fly in the code view
class RedeemLoginLinkDto(PasswordChangeSerializer):
    def __init__(self, instance: LoginLink, *args, **kwargs):
        super().__init__(instance.user, *args, **kwargs)

class SetUserServiceConnectionsDto(serializers.Serializer):
    services = serializers.SlugRelatedField(queryset=Service.objects.all(), many=True, slug_field="uid", style={'base_template': 'input.html'})
