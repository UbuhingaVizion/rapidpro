from django.urls import include, path
from django.urls import re_path

from .models import Ticketer
from .views import TicketCRUDL, TicketerCRUDL

# build up all the type specific urls
service_urls = []
for ticketer_type in Ticketer.get_types():
    urls = ticketer_type.get_urls()
    for u in urls:
        u.name = "tickets.types.%s.%s" % (ticketer_type.slug, u.name)

    if urls:
        service_urls.append(re_path("^%s/" % ticketer_type.slug, include(urls)))

urlpatterns = [
    path("", include(TicketCRUDL().as_urlpatterns())),
    path("", include(TicketerCRUDL().as_urlpatterns())),
    path("tickets/types/", include(service_urls)),
]
