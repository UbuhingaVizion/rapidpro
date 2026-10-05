from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("api/", RedirectView.as_view(pattern_name="api.v2.root", permanent=False), name="api"),
    path("api/internal/", include("temba.api.internal.urls")),
    path("api/v2/", include("temba.api.v2.urls")),
]
