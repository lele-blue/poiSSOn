from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
import urllib.parse as urlparse
import django_otp

from main.core_settings import get_core_setting
from main.models import User

def reverse_proxy(get_response):
    def process_request(request):
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            request.META['REMOTE_ADDR'] = request.META.get('HTTP_X_FORWARDED_FOR').split(",")[0].strip() if not settings.DEBUG else '127.0.0.1'
        return get_response(request)
    return process_request

def admin_needs_twofa(get_response):
    def process_request(request):
        path = request.get_full_path()
        print(path, type(path))
        print(str(path), type(str(path)))
        thislocation = urlparse.quote_plus(path)
        if request.path.startswith(reverse('admin:index')):
            if not request.user.is_authenticated:
                return HttpResponseRedirect(f"/auth?next={thislocation}")
            if not request.user.is_verified() and django_otp.user_has_device(request.user):
                return HttpResponseRedirect(f"/auth/go/login_state_mod/otp?next={thislocation}")
        return get_response(request)
    return process_request

def oobe(get_response):
    oobe_finished = False
    def process_request(request):
        if oobe_finished \
            or (\
                (request.user.is_authenticated and request.user.is_admin) or User.objects.all().count() == 0\
            )\
        :
            return get_response(request)
        return HttpResponseRedirect("/auth/go/manager/oobe")

    if get_core_setting("poisson.core.oobe.state", None) != "poisson.oobe.first_start":
        raise MiddlewareNotUsed()

    return process_request
