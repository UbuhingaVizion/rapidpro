from django.urls import include, path, re_path

from .models import IntegrationType
from .views import (
    ConfirmAccessView,
    LoginView,
    OrgCRUDL,
    OrgImportCRUDL,
    TwoFactorBackupView,
    TwoFactorVerifyView,
    UserCRUDL,
    check_login,
)

urlpatterns = OrgCRUDL().as_urlpatterns()
urlpatterns += OrgImportCRUDL().as_urlpatterns()
urlpatterns += UserCRUDL().as_urlpatterns()

# we iterate all our integration types, finding all the URLs they want to wire in
integration_type_urls = []

for integration in IntegrationType.get_all():
    integration_urls = integration.get_urls()
    for u in integration_urls:
        u.name = f"integrations.{integration.slug}.{u.name}"

    if integration_urls:
        integration_type_urls.append(re_path(f"^{integration.slug}/", include(integration_urls)))

urlpatterns += [
    path("login/", check_login, name="users.user_check_login"),
    path("users/login/", LoginView.as_view(), name="users.login"),
    path("users/two-factor/verify/", TwoFactorVerifyView.as_view(), name="users.two_factor_verify"),
    path("users/two-factor/backup/", TwoFactorBackupView.as_view(), name="users.two_factor_backup"),
    path("users/confirm-access/", ConfirmAccessView.as_view(), name="users.confirm_access"),
    path("integrations/", include(integration_type_urls)),
]
