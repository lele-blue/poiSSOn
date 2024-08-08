from rest_framework import serializers

from main.models import UserServiceConnection, Service, OriginMigrationToken


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ["name", "icon", "sub_url", "origin"]

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
        return ServiceSerializer(obj.service).data

    class Meta:
        model = UserServiceConnection
        fields = ["service", "username", "passwordPlain"]
