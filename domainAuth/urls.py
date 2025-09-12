"""domainAuth URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from main.views import CheckApplicationPassword, CodeView, ConfigurationByKeys, ConfigurationsAPI, GetServiceConfigurationInfo, LogOut, LoginLinkView, ServiceView, SetApplicationPassword, UserViewSet, ValidatePassword, ViewServiceConfiguration, main_view, main_view_dev_inlay_helper, static_resolver, AjaxLogin, login_check, UserGetOwnServices, GetNextCredential, \
    SetNextCredentialSource, GetServiceInfo, redirect_unauthenticated, ConsumeCode, CheckRedirect, CreateOriginMigrationToken, AuthenticateCrossorigin, CheckPermissionForService, ConfigurationByKey, TwoFactorStatus, TwoFactorVerification, TwoFactorManagement, TotpQrGenerator, ManagerCoreSetting
from main.oobe import CreateAdminAndFinishOOBE
from main.oidc_provider_settings import wrap_authorize_post

from oidc_provider.views import AuthorizeView
from rest_framework.routers import SimpleRouter

# Add permission check to post
wrap_authorize_post()

router = SimpleRouter(trailing_slash=False)
router.register(f'{settings.BASEPATH_REL}/api/manager/users', UserViewSet, basename='user')
router.register(f'{settings.BASEPATH_REL}/api/manager/login_links', LoginLinkView, basename='login_link')
router.register(f'{settings.BASEPATH_REL}/api/manager/services', ServiceView, basename='service')


urlpatterns = [
    path(f'{settings.BASEPATH_REL}/go/admin/', admin.site.urls),
    path(f'{settings.BASEPATH_REL}/go/admin', RedirectView.as_view(url="/auth/go/admin/")),
    path(f'{settings.BASEPATH_REL}/go/static/resolve/<path:url>', static_resolver),
    path(f'{settings.BASEPATH_REL}/go/unauthenticated', redirect_unauthenticated, name="redirect_unauth"),
    path(f'{settings.BASEPATH_REL}/api/logon', AjaxLogin.as_view()),
    path(f'{settings.BASEPATH_REL}/api/logoff', LogOut.as_view()),
    path(f'{settings.BASEPATH_REL}/api/service/<str:name>/configuration', GetServiceConfigurationInfo.as_view()),
    path(f'{settings.BASEPATH_REL}/api/services/query', GetServiceInfo.as_view()),
    path(f'{settings.BASEPATH_REL}/api/services/redirect_check', CheckRedirect.as_view()),
    path(f'{settings.BASEPATH_REL}/api/crossorigin/create_migration_token', CreateOriginMigrationToken.as_view()),
    path(f'{settings.BASEPATH_REL}/crossorigin', AuthenticateCrossorigin.as_view()),
    path(f'{settings.BASEPATH_REL}/api/consume_code', ConsumeCode.as_view()),
    path(f'{settings.BASEPATH_REL}/api/ping', login_check),
    path(f'{settings.BASEPATH_REL}/api/alt_ping', login_check),
    path(f'{settings.BASEPATH_REL}/api/configuration/<str:service_name>', ConfigurationsAPI.as_view()),
    path(f'{settings.BASEPATH_REL}/api/next_credentials/store', SetNextCredentialSource.as_view()),
    path(f'{settings.BASEPATH_REL}/api/next_credentials/retrieve', GetNextCredential.as_view()),
    path(f'{settings.BASEPATH_REL}/api/services', UserGetOwnServices.as_view()),
    path(f'{settings.BASEPATH_REL}/api/services/check', CheckPermissionForService.as_view()),
    path(f'{settings.BASEPATH_REL}/api/2fa/status', TwoFactorStatus.as_view()),
    path(f'{settings.BASEPATH_REL}/api/2fa/verification', TwoFactorVerification.as_view()),
    path(f'{settings.BASEPATH_REL}/api/2fa/manage', TwoFactorManagement.as_view()),
    path(f'{settings.BASEPATH_REL}/api/2fa/totp/qrcode', TotpQrGenerator.as_view()),

    path(f'{settings.BASEPATH_REL}/api/configuration/management/<str:service_name>/by_key/<str:query_id>', ConfigurationByKey.as_view()),
    path(f'{settings.BASEPATH_REL}/api/configuration/management/<str:service_name>/by_keys', ConfigurationByKeys.as_view()),
    path(f'{settings.BASEPATH_REL}/api/configuration/management/<str:service_name>/check_password/<str:query_id>', ValidatePassword.as_view()),
    path(f'{settings.BASEPATH_REL}/api/application_password/management/<str:service_name>/check_password/<str:username>', CheckApplicationPassword.as_view()),
    path(f'{settings.BASEPATH_REL}/api/configuration/view/<str:service_name>', ViewServiceConfiguration.as_view()),
    path(f'{settings.BASEPATH_REL}/api/application_password/<str:service_name>', SetApplicationPassword.as_view()),
    path(f'{settings.BASEPATH_REL}/api/oobe/create_admin_and_finish_oobe', CreateAdminAndFinishOOBE.as_view()),

    path(f'{settings.BASEPATH_REL}/api/manager/core_setting/<str:setting>', ManagerCoreSetting.as_view()),

    *router.urls,

    path(f'{settings.BASEPATH_REL}/openid/', include('oidc_provider.urls', namespace='oidc_provider')),
    path(f'{settings.BASEPATH_REL}/go/code', CodeView.as_view()),
    path(f'{settings.BASEPATH_REL}/<path:url>', main_view),
    path(f'{settings.BASEPATH_REL}', main_view),
]

if settings.DEBUG:
    urlpatterns.insert(0, path(f"{settings.BASEPATH_REL}/debug/dev_inlay", main_view_dev_inlay_helper))
