import re
import base64
from django.db.models import F, Q, QuerySet
from django.db.models.aggregates import Count
from django_ratelimit.decorators import ratelimit
from django_ratelimit.core import is_ratelimited
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth import authenticate, login
from django.db import transaction, IntegrityError
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import View
from urllib.parse import urlparse, quote, unquote
from typing import Optional, List, Union, cast
from secrets import token_urlsafe

# Create your views here.
from django.templatetags.static import static
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_api_key.permissions import BaseHasAPIKey

from main.models import UserServiceConnection, Service, Code, OriginMigrationToken
from main.serializers import UserConnectionSerializer, PublicServiceSerializer, OriginMigrationTokenSerializer
=======
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_api_key.permissions import BaseHasAPIKey

from main.models import ApplicationPassword, ConfigurationApiKey, ServiceConfiguration, ServiceConfigurationStep, UserServiceConnection, Service, Code, OriginMigrationToken
from main.serializers import ServiceConfigurationStepSerializer, UserConnectionSerializer, PublicServiceSerializer, OriginMigrationTokenSerializer
>>>>>>> master


@ensure_csrf_cookie
def main_view(request, url=None):
    return render(request, "main.html", {})


def static_resolver(request, url):
    return HttpResponseRedirect(static(url))

@ratelimit(key='ip', rate='10/5m')
def ajax_login(request):
    if request.method == "POST":
        user = authenticate(username=request.POST.get("username"), password=request.POST.get("password"))
        if user:
            login(request, user)
            return HttpResponse(status=200)
        else:
            raise PermissionDenied()


def check_user_has_permission(url_or_service: Union[Service, str], user, session):
    service: Optional[Service] = url_or_service
    if not isinstance(url_or_service, Service):
        service = resolve_to_service(url_or_service)

    if user.is_authenticated and service:
        if UserServiceConnection.objects.filter(service=service, user=user).exists():
            return True

    codes: List[Code] = []
    if user.is_authenticated:
        codes = list(user.codes.filter(service=service))
    else:
        codes = list(Code.objects.filter(pk__in=session.get('codes', []), service=service))

    codes = [code for code in codes if code.is_valid()]

    if len(codes) != 0: # at least 1 valid code
        return True

    return False


def login_check(request):
    if not request.META.get("HTTP_X_ORIGINAL_URL") and request.user.is_authenticated:
        return HttpResponse(status=200)

    if request.META.get('HTTP_AUTHORIZATION'):
        # just check if we even try to authenticate
        if is_ratelimited(request, 'login_check', key="ip", increment=False, rate="10/10m"):
            # if we are ratelimited all requests will look like wrong creds, even with the right creds
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
        auth = request.META['HTTP_AUTHORIZATION'].split()
        if len(auth) == 2:
            if auth[0].lower() == "basic":
                split = base64.b64decode(auth[1]).decode("utf8").split(':')
                user = authenticate(username=split[0], password=":".join(split[1:]))
                if user is not None:
                    request.user = user
                else:
                    is_ratelimited(request, 'login_check', key="ip", increment=True, rate="10/10m")


    return HttpResponse(status=status.HTTP_200_OK) if check_user_has_permission(request.META.get("HTTP_X_ORIGINAL_URL"), request.user, request.session) else HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

def resolve_to_service(path: str) -> Optional[Service]:
    url = urlparse(path)
    services = Service.objects.filter(origin=url.netloc)
    if len(services) != 0 and services[0].sub_url == "*":
        return services[0];
    else:
        for service in services:
            if service.regex:
                if re.match(service.sub_url, url.path):
                    return service
            else:
                if url.path.startswith(service.sub_url):
                    return service


def redirect_unauthenticated(request):
    service = resolve_to_service(request.GET.get('url'))
    if not service:
        return HttpResponseRedirect('/auth')
    if service.codes.count() >= 1:
        return HttpResponseRedirect(f'/auth/go/code?next={quote(request.GET.get("url"))}')
    elif check_user_has_permission(request.GET.get("url"), request.user, request.session):
        token = CreateOriginMigrationToken.create_token(request.GET.get('url'), request.user, request.session)
        url = urlparse(request.GET.get('url', ''))
        return HttpResponseRedirect(url.scheme + "://" + url.netloc + "/_sso?token=" + token.token + "&next=" + quote(request.GET.get("url")))
    elif request.user.is_authenticated:
        return HttpResponseRedirect('/auth/go/fail')
    else:
        return HttpResponseRedirect(f'/auth?next={quote(request.GET.get("url"))}')

class GetServiceInfo(APIView):
    @method_decorator(ratelimit(key='ip', rate='10/5m'))
    def get(self, request):
        if ('url' not in request.GET):
            return HttpResponse("URL missing", status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        return Response(data=PublicServiceSerializer(resolve_to_service(unquote(request.GET.get('url')))).data)


class GetServiceConfigurationInfo(APIView):
    def get(self, request, name):
        service = get_object_or_404(Service, name=name)
        if not check_user_has_permission(service, request.user, request.session):
            raise Http404()
        return Response(ServiceConfigurationStepSerializer(ServiceConfigurationStep.objects.filter(service=service, hidden=False), many=True).data)


class CheckPermissionForService(APIView):
    def get(self, request):
        request.META["HTTP_X_ORIGINAL_URL"] = request.GET.get("url");
        return Response(status=200 if login_check(request).status_code == 200 else 400)


class AuthenticateCrossorigin(View):
    @method_decorator(ratelimit(key='ip', rate='30/5m'))
    def get(self, request):
        if ('next' not in request.GET):
            return HttpResponse("URL missing", status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        if ('token' not in request.GET):
            return HttpResponse("Token missing", status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        next_: str = request.GET.get('next')
        token: str = request.GET.get('token')
        next_parse = urlparse(next_)

        try:
            token_obj = OriginMigrationToken.objects.get(token=token)
        except OriginMigrationToken.DoesNotExist:
            raise Http404("Token Invalid")

        if next_parse.netloc.split(':')[0] != request.META['HTTP_HOST']:
            raise PermissionDenied("Invalid Redirect URL")

        if next_parse.netloc != token_obj.service.origin:
            raise PermissionDenied("Invalid Redirect URL at service")

        if token_obj.expires <= now():
            token_obj.delete()
            raise PermissionDenied("token expired")

        if token_obj.account:
            login(request, token_obj.account)

        else:
            if not "codes" in request.session:
                request.session["codes"] = []
            request.session["codes"] += token_obj.codes.all().values_list("pk", flat=True)
            request.session["codes"] = list(set(request.session['codes'])) #dedup
            request.session.save()

        token_obj.delete()

        return HttpResponseRedirect(next_)


# Checks if a redirect is safe or not (only called if GetServiceInfo is in ratelimit as a fallback)
class CheckRedirect(APIView):
    def get(self, request):
        if ('url' not in request.GET):
            return HttpResponse("URL missing", status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        if resolve_to_service(request.GET.get('url')):
            return Response(status=204)
        else:
            return Response(status=404)


class CreateOriginMigrationToken(APIView):
    @staticmethod
    def create_token(url, user, session):

        service = resolve_to_service(url)
        if not service:
            raise Http404()
        token = OriginMigrationToken();
        token.token = token_urlsafe(128)[:128]
        token.service = service
        token.expires = now() + timedelta(minutes=1)

        if user.is_authenticated:
            token.account = user

        token.save()

        if not user.is_authenticated:
            token.codes.add(*session.get('codes', []))

        return token

    def post(self, request):
        if not "for" in request.POST:
            return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        token = CreateOriginMigrationToken.create_token(request.POST.get('for'), request.user, request.session)

        return Response(data=OriginMigrationTokenSerializer(token).data, status=status.HTTP_201_CREATED)



class ConsumeCode(APIView):
    @method_decorator(ratelimit(key='ip', rate='10/5m'))
    def post(self, request):
        if not "code" in request.POST:
            return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        codes = Code.objects.filter(code=request.POST.get("code"))
        if not codes.exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        codes = [code for code in codes if code.is_valid()]

        if len(codes) == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)

        code = codes[0]

        if request.user.is_authenticated:
            request.user.codes.add(code);

        else:
            if 'codes' not in request.session:
                request.session['codes'] = []
            request.session['codes'].append(code.pk)
            request.session.save()

        return Response(status=status.HTTP_201_CREATED)


class UserGetOwnServices(APIView):
    def get(self, request):
        return Response(data=UserConnectionSerializer(UserServiceConnection.objects.filter(user=request.user), many=True).data)


class SetNextCredentialSource(APIView):
    def post(self, request: Request):
        request.session["next_credentials"] = request.data.get("next_credentials")
        return Response(status=status.HTTP_204_NO_CONTENT)


class GetNextCredential(APIView):
    def post(self, request: Request):
        fallback = request.data.get("fallback_source")
        source = request.session.get("next_credentials") or fallback
        credentials = UserServiceConnection.objects.get(user=request.user, service__name=source)

        return Response(data=UserConnectionSerializer(credentials).data, status=status.HTTP_200_OK)


class ConfigurationsAPI(APIView):
    def post(self, request, service_name):
        if not request.user.is_authenticated:
            raise PermissionDenied()

        service = get_object_or_404(Service, name=service_name)

        if not check_user_has_permission(service, request.user, request.session):
            raise PermissionDenied()

        configSteps: QuerySet[ServiceConfigurationStep, ServiceConfigurationStep] = service.configuration_steps

        idxes = ServiceConfiguration.objects.filter(value_for_step__service=service, user=request.user).order_by("-set_idx")

        next_idx = 0
        if idxes.exists():
            next_idx = cast(ServiceConfiguration, idxes.first()).set_idx + 1
        configs: List[ServiceConfiguration] = []

        if next_idx > (UserServiceConnection.objects.get(user=request.user, service=service).configuration_allow_max or service.allow_max_configurations):
            raise PermissionDenied("No more allowed")

        for step in configSteps.filter(hidden=False):
            if step.query_id not in request.data:
                return Response(f"{step.query_id} missing", status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            configs.append(ServiceConfiguration(value_for_step=step, value=request.data[step.query_id], set_idx=next_idx, user=request.user))
            if (step.is_password):
                password = ApplicationPassword()
                password.set_password(request.data[step.query_id])
                password.save()
                configs[-1].password = password
                configs[-1].value = ""

        for step in configSteps.filter(hidden=True):
            configs.append(ServiceConfiguration(value_for_step=step, value=step.default, set_idx=next_idx, user=request.user))

        try:
            with transaction.atomic():
                for config in configs:
                    if config.password:
                        config.password.save()
                    config.save()
        except IntegrityError:
            return HttpResponseRedirect("")

        return Response(status=status.HTTP_201_CREATED)


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


def service_config_get_set_by_values(service: Service, **match_by):
    print(match_by)
    query = Q(value_for_step__service=service)
    step_value_query = Q()

    # Loop through each pair and add it to the query
    for value_for_step, value in match_by.items():
        if type(value) == list:
            step_value_query |= Q(value_for_step__query_id=value_for_step, value__in=value)
        else:
            step_value_query |= Q(value_for_step__query_id=value_for_step, value=value)


    query &= step_value_query
    print(query)

    # query from hell
    matching_sets = (
        ServiceConfiguration.objects
        .filter(query)
        .values('set_idx', 'user')  # Group by set_idx
        .annotate(step_count=Count('id'))  # Count the matching steps
        .filter(step_count=len(match_by))  # Ensure all pairs match
        .distinct()  # Ensure distinct set_idx
    )
    print(
        ServiceConfiguration.objects
        .filter(query)
    )

    print(matching_sets)


    for set_ in matching_sets:
        qs = ServiceConfiguration.objects.filter(user=set_["user"], set_idx=set_["set_idx"], value_for_step__service=service)
        yield qs


class ConfigurationByKeys(APIView):
    permission_classes = [HasServicePermission]

    def get(self, request, service_name):
        service = get_object_or_404(Service, name=service_name)
        self.check_object_permissions(request, service)
        for key, val in request.GET.items():
            if "__" in key:
                raise SuspiciousOperation()


        res_list = list()
        for qs in service_config_get_set_by_values(service, **request.GET):


            res = dict()
            if qs.exists():
                res["_username"] = qs.first().user.username
            for field in qs:
                if field.value_for_step.is_password:
                    continue
                res[field.value_for_step.query_id] = field.value

            res_list.append(res)
        return Response(res_list)



class ConfigurationByKey(APIView):
    permission_classes = [HasServicePermission]

    def get(self, request, service_name, query_id):
        service = get_object_or_404(Service, name=service_name)
        self.check_object_permissions(request, service)

        match_by = get_object_or_404(ServiceConfiguration, value_for_step__service=service, value_for_step__query_id=query_id, value=request.GET.get("q"))
        qs = ServiceConfiguration.objects.filter(value_for_step__service=service, user=match_by.user, set_idx=match_by.set_idx)
        res = dict()
        for field in qs:
            if field.value_for_step.is_password:
                continue
            res[field.value_for_step.query_id] = field.value
        return Response(res)


class ValidatePassword(APIView):
    permission_classes = [HasServicePermission]

    def post(self, request, service_name, query_id):
        service = get_object_or_404(Service, name=service_name)
        self.check_object_permissions(request, service)

        try:
            unique_idx_match = next(service_config_get_set_by_values(service, **request.GET)).first()
        except StopIteration:
            return Response({"detail": "No Configuration matching the query found"}, status=status.HTTP_404_NOT_FOUND)
        if not unique_idx_match:
            return Response({"detail": "No Configuration matching the query found (Set empty)"}, status=status.HTTP_404_NOT_FOUND)


        pwd = ApplicationPassword.objects.get(service_config__value_for_step__service=service, service_config__value_for_step__query_id=query_id, service_config__set_idx=unique_idx_match.set_idx)

        if pwd.check_password(request.POST.get("password")):
            return Response({"status": "match"}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "no-match", "detail": "Invalid Password"}, status=status.HTTP_403_FORBIDDEN)



class ViewServiceConfiguration(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, service_name):
        service = get_object_or_404(Service, name=service_name)
        configs = ServiceConfiguration.objects.filter(value_for_step__service=service, user=request.user)

        clean_objs = []

        for idx in configs.values_list("set_idx", flat=True).distinct():
            obj = dict()
            for config in configs.filter(set_idx=idx):
                obj[config.value_for_step.query_id] = config.value
            clean_objs.append(obj)

        if len(clean_objs) == 0:
            return Response(status=status.HTTP_204_NO_CONTENT)

        vals = {
            "USERNAME": request.user.username,
            "EMAIL": request.user.email,
            "CONFIGURATIONS": clean_objs,
            **clean_objs[0]
        }

        out = cast(str, service.configuration_view_template).splitlines()

        final = ""

        def fmt_line(line):
            for key, val in vals.items():
                if type(val) == str:
                    val = val.replace("<", "&gt;")
                    val = val.replace(">", "&lt;")
                    line = line.replace(f"%%{key}%%", val)
            return f"{line}<br/>"

        current_iter_item = None
        current_iter_content = None
        for line in out:
            if line.startswith("%%ITER "):
                current_iter_item = vals[line.split(" ")[1].rstrip("%%")]
                current_iter_content = []

            elif line == "%%STOPITER%%":
                for current in current_iter_item:
                    vals.update(current)
                    for line in current_iter_content:
                        final += fmt_line(line)

                current_iter_item = None
                current_iter_content = None

            elif current_iter_item:
                current_iter_content.append(line)

            else:
                final += fmt_line(line)

        return HttpResponse(final)


class SetApplicationPassword(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, service_name):
        service = get_object_or_404(Service, name=service_name)
        connection = get_object_or_404(UserServiceConnection, user=request.user, service=service)

        if not connection.application_password:
            connection.application_password = ApplicationPassword()
        print(request.data.get("password"))
        connection.application_password.set_password(request.data.get("password"))
        connection.application_password.save()
        connection.save()

        return Response(status=status.HTTP_200_OK)


class CheckApplicationPassword(APIView):
    permission_classes = [HasServicePermission]

    def post(self, request, service_name, username):
        service = get_object_or_404(Service, name=service_name)
        connection = get_object_or_404(UserServiceConnection, user__username=username, service=service)
        if not connection.application_password:
            return Response({"detail": "No Password set"}, status=status.HTTP_401_UNAUTHORIZED)

        if connection.application_password.check_password(request.data.get("password")):
            return Response({"status": "match"}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "no-match", "detail": "Invalid Password"}, status=status.HTTP_403_FORBIDDEN)


