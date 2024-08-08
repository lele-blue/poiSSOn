import re
from django_ratelimit.decorators import ratelimit
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth import authenticate, login
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render
from django.views import View
from urllib.parse import urlparse, quote, unquote
from typing import Optional, List
from secrets import token_urlsafe

# Create your views here.
from django.templatetags.static import static
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from main.models import UserServiceConnection, Service, Code, OriginMigrationToken
from main.serializers import UserConnectionSerializer, PublicServiceSerializer, OriginMigrationTokenSerializer


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


def login_check(request):
    if not request.META.get("HTTP_X_ORIGINAL_URL") and request.user.is_authenticated:
        return HttpResponse(status=200)

    service = resolve_to_service(request.META.get("HTTP_X_ORIGINAL_URL"))

    if request.user.is_authenticated and service:
        if UserServiceConnection.objects.filter(service=service, user=request.user).exists():
            return HttpResponse(status=200)

    codes: List[Code] = []
    if request.user.is_authenticated:
        codes = list(request.user.codes.filter(service=service))
    else:
        codes = list(Code.objects.filter(pk__in=request.session.get('codes', []), service=service))

    codes = [code for code in codes if code.is_valid()]

    if len(codes) != 0: # at least 1 valid code
        return HttpResponse(status=200)

    return HttpResponse(None, status=status.HTTP_401_UNAUTHORIZED)

def resolve_to_service(path: str) -> Optional[Service]:
    url = urlparse(path)
    print(url.netloc, path)
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
    def post(self, request):
        if not "for" in request.POST:
            return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        service = resolve_to_service(request.POST.get('for'))
        if not service:
            return Http404()
        token = OriginMigrationToken();
        token.token = token_urlsafe(128)[:128]
        token.service = service
        token.expires = now() + timedelta(minutes=1)

        if request.user.is_authenticated:
            token.account = request.user

        token.save()

        if not request.user.is_authenticated:
            token.codes.add(request.session.get('codes', []))

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
