from django.urls import include, path
from django.views.generic import RedirectView

from .views import RefreshAPITokenView

urlpatterns = [
    path("api/", RedirectView.as_view(pattern_name="api.v2", permanent=False), name="api"),
    path("api/v2/", include("temba.api.v2.urls")),
    path("api/apitoken/refresh/", RefreshAPITokenView.as_view(), name="api.apitoken_refresh"),
]
