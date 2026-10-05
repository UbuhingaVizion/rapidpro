from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import NotificationsEndpoint

urlpatterns = [
    # ========== endpoints A-Z ===========
    path("notifications", NotificationsEndpoint.as_view(), name="api.internal.notifications"),
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=["json"])
