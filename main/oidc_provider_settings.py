from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from .views import check_user_has_permission
from typing import Optional
from .models import Service
from oidc_provider.lib.claims import ScopeClaims
from oidc_provider.views import AuthorizeView
from oidc_provider import settings as oidc_settings

def userinfo(claims, user):
    # Populate claims dict.
    claims['name'] = '{0} {1}'.format(user.first_name, user.last_name)
    claims['given_name'] = user.first_name
    claims['family_name'] = user.last_name
    claims['email'] = user.email

    return claims


class CustomScopeClaims(ScopeClaims):

    info_sso_groups = (
        _(u'Groups'),
        _(u'Membership to your groups'),
    )

    def scope_sso_groups(self):
        # self.user - Django user instance.
        # self.userinfo - Dict returned by OIDC_USERINFO function.
        # self.scopes - List of scopes requested.
        # self.client - Client requesting this claims.
        dic = {
            'groups': list(self.user.sso_groups.values_list('slug',flat = True)),
        }

        return dic


def check_permissions(request, user, client):
    service: Optional[Service] = None

    try:
        service = client.service

    except Service.DoesNotExist:
        service = None


    if not service:
        # assume client without attached service is open to all (or handles perms on its own)
        return None

    if check_user_has_permission(service, user, request.session):
        return None
    return HttpResponseRedirect("/auth/go/fail")


authorize_post_wrapped = False
def wrap_authorize_post():
    global authorize_post_wrapped
    if authorize_post_wrapped:
        return
    authorize_post_wrapped = True

    original = AuthorizeView.post

    def wrapped(self, request):
        print("wrapped")
        authorize = self.authorize_endpoint_class(request)
        authorize.validate_params()
        hook_resp = oidc_settings.get('OIDC_AFTER_USERLOGIN_HOOK', import_str=True)(
                    request=request, user=request.user,
                    client=authorize.client)
        if hook_resp:
            return hook_resp

        return original(self, request)

    AuthorizeView.post = wrapped
