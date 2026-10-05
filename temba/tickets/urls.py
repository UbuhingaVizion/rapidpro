from django.urls import include, path

from .views import TicketCRUDL, TopicCRUDL

urlpatterns = [
    path("", include(TicketCRUDL().as_urlpatterns())),
    path("", include(TopicCRUDL().as_urlpatterns())),
]
