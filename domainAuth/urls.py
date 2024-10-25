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
from django.contrib import admin
from django.urls import path, include

from main.views import CheckApplicationPassword, ConfigurationByKeys, ConfigurationsAPI, GetServiceConfigurationInfo, SetApplicationPassword, ValidatePassword, ViewServiceConfiguration, main_view, static_resolver, ajax_login, login_check, UserGetOwnServices, GetNextCredential, \
    SetNextCredentialSource, GetServiceInfo, redirect_unauthenticated, ConsumeCode, CheckRedirect, CreateOriginMigrationToken, AuthenticateCrossorigin, CheckPermissionForService, ConfigurationByKey, TwoFactorStatus, TwoFactorVerification, TwoFactorManagement, TotpQrGenerator
from main.oidc_provider_settings import wrap_authorize_post

from oidc_provider.views import AuthorizeView

# Add permission check to post
wrap_authorize_post()


urlpatterns = [
    path('auth/go/admin', admin.site.urls),
    path('auth/go/static/resolve/<path:url>', static_resolver),
    path('auth/go/unauthenticated', redirect_unauthenticated, name="redirect_unauth"),
    path('auth/api/logon', ajax_login),
    path('auth/api/service/<str:name>/configuration', GetServiceConfigurationInfo.as_view()),
    path('auth/api/services/query', GetServiceInfo.as_view()),
    path('auth/api/services/redirect_check', CheckRedirect.as_view()),
    path('auth/api/crossorigin/create_migration_token', CreateOriginMigrationToken.as_view()),
    path('auth/crossorigin', AuthenticateCrossorigin.as_view()),
    path('auth/api/consume_code', ConsumeCode.as_view()),
    path('auth/api/ping', login_check),
    path('auth/api/alt_ping', login_check),
    path('auth/api/configuration/<str:service_name>', ConfigurationsAPI.as_view()),
    path('auth/api/next_credentials/store', SetNextCredentialSource.as_view()),
    path('auth/api/next_credentials/retrieve', GetNextCredential.as_view()),
    path('auth/api/services', UserGetOwnServices.as_view()),
    path('auth/api/services/check', CheckPermissionForService.as_view()),
    path('auth/api/2fa/status', TwoFactorStatus.as_view()),
    path('auth/api/2fa/verification', TwoFactorVerification.as_view()),
    path('auth/api/2fa/manage', TwoFactorManagement.as_view()),

    path('auth/api/2fa/totp/qrcode', TotpQrGenerator.as_view()),

    path('auth/api/configuration/management/<str:service_name>/by_key/<str:query_id>', ConfigurationByKey.as_view()),
    path('auth/api/configuration/management/<str:service_name>/by_keys', ConfigurationByKeys.as_view()),
    path('auth/api/configuration/management/<str:service_name>/check_password/<str:query_id>', ValidatePassword.as_view()),
    path('auth/api/application_password/management/<str:service_name>/check_password/<str:username>', CheckApplicationPassword.as_view()),
    path('auth/api/configuration/view/<str:service_name>', ViewServiceConfiguration.as_view()),
    path('auth/api/application_password/<str:service_name>', SetApplicationPassword.as_view()),

    path('auth/openid/', include('oidc_provider.urls', namespace='oidc_provider')),
    path('auth/<path:url>', main_view),
    path('auth', main_view),
]
