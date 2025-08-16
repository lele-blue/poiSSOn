from django.contrib.auth import login
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView, Response
from main.core_settings import get_core_setting, set_core_setting_universally
from main.session_tree import login_master_session


# returns true IF a) no user exists in the DB AND b) oobe was never completed, since the user is logged in after creating the first user
def is_in_oobe_mode():
    from main.models import User
    match get_core_setting("poisson.core.oobe.state", None):
        case "poisson.oobe.first_start":
            return User.objects.all().count() == 0
        case _:
            return False


class OOBEAdminUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=32)
    password = serializers.CharField(max_length=64)


class CreateAdminAndFinishOOBE(APIView):
    def post(self, request):
        from main.models import User
        with transaction.atomic():
            if is_in_oobe_mode():
                set_core_setting_universally("poisson.core.oobe.state", "poisson.oobe.finished")
                data = OOBEAdminUserSerializer(data=request.data)
                data.is_valid(raise_exception=True)
                admin = User()
                admin.is_superuser = True
                admin.is_staff = True
                admin.username = data.data.get("username")
                admin.set_password(data.data.get("password"))
                admin.save()
                login_master_session(request, admin)
                return Response({"status": "created"}, status=201)
            else:
                raise PermissionDenied()

