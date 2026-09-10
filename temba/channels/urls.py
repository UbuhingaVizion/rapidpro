from django.urls import include, path
from django.urls import re_path

from temba.utils.views import CourierURLHandler

from .models import Channel
from .views import ChannelCRUDL, ChannelEventCRUDL, ChannelLogCRUDL

# we iterate all our channel types, finding all the URLs they want to wire in
courier_urls = []
type_urls = []

for ch_type in Channel.get_types():
    channel_urls = ch_type.get_urls()
    for u in channel_urls:
        u.name = "channels.types.%s.%s" % (ch_type.slug, u.name)

    if channel_urls:
        type_urls.append(re_path("^%s/" % ch_type.slug, include(channel_urls)))

    # register a Courier placeholder URL which will error if ever accessed directly
    courier_urls.append(
        re_path(ch_type.courier_url, CourierURLHandler.as_view(), name="courier.%s" % ch_type.code.lower())
    )


urlpatterns = [
    path("", include(ChannelEventCRUDL().as_urlpatterns())),
    path("channels/", include(ChannelCRUDL().as_urlpatterns() + ChannelLogCRUDL().as_urlpatterns())),
    path("c/", include(courier_urls)),
    path("channels/types/", include(type_urls)),
]
