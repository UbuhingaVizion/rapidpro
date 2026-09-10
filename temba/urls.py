from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.urls import re_path
from django.views.generic import RedirectView
from django.views.i18n import JavaScriptCatalog

from temba.channels.views import register, sync

# javascript translation packages
js_info_dict = {"packages": ()}  # this is empty due to the fact that all translation are in one folder

urlpatterns = [
    path("", include("temba.airtime.urls")),
    path("", include("temba.api.urls")),
    path("", include("temba.apks.urls")),
    path("", include("temba.archives.urls")),
    path("", include("temba.campaigns.urls")),
    path("", include("temba.channels.urls")),
    path("", include("temba.classifiers.urls")),
    path("", include("temba.contacts.urls")),
    path("", include("temba.dashboard.urls")),
    path("", include("temba.flows.urls")),
    path("", include("temba.globals.urls")),
    path("", include("temba.ivr.urls")),
    path("", include("temba.locations.urls")),
    path("", include("temba.msgs.urls")),
    path("", include("temba.notifications.urls")),
    path("", include("temba.policies.urls")),
    path("", include("temba.public.urls")),
    path("", include("temba.request_logs.urls")),
    path("", include("temba.schedules.urls")),
    path("", include("temba.tickets.urls")),
    path("", include("temba.triggers.urls")),
    path("", include("temba.orgs.urls")),
    re_path(r"^relayers/relayer/sync/(\d+)/$", sync, {}, "sync"),
    path("relayers/relayer/register/", register, {}, "register"),
    re_path(r"users/user/forget/", RedirectView.as_view(pattern_name="orgs.user_forget", permanent=True)),
    path("users/", include("smartmin.users.urls")),
    path("imports/", include("smartmin.csv_imports.urls")),
    path("assets/", include("temba.assets.urls")),
    path("jsi18n/", JavaScriptCatalog.as_view(), js_info_dict, name="django.views.i18n.javascript_catalog"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# import any additional urls
for app in settings.APP_URLS:  # pragma: needs cover
    urlpatterns.append(path("", include(app)))


def handler500(request):
    """
    500 error handler which includes ``request`` in the context.

    Templates: `500.html`
    Context: None
    """
    from sentry_sdk import last_event_id

    from django.http import HttpResponseServerError
    from django.template import loader

    t = loader.get_template("500.html")
    return HttpResponseServerError(t.render({"request": request, "sentry_id": last_event_id()}))  # pragma: needs cover
