from django.utils.translation import gettext_lazy as _

from temba.contacts.models import URN

from ...models import ChannelType
from .views import ClaimView


class TikTokType(ChannelType):
    """
    A TikTok Business Messaging channel. Each channel is a TikTok developer app authorized by one business
    account, so the webhook URL carries the channel uuid and deliveries do not have to be routed by open_id.
    """

    code = "TT"
    name = "TikTok"
    category = ChannelType.Category.SOCIAL_MEDIA

    courier_url = r"^tt/(?P<uuid>[a-z0-9\-]+)/receive"

    # TikTok contacts are identified by an app-scoped open_id, carried as an external URN. Adding a new
    # scheme would mean changes in goflow and mailroom, which this channel does not need.
    schemes = [URN.EXTERNAL_SCHEME]

    claim_blurb = _(
        "Add a %(link)s business account to send and receive direct messages. "
        "The account must have Advanced Access or be a Verified Business Account, and the developer app "
        "must have passed TikTok's data security and privacy review."
    ) % {"link": '<a target="_blank" href="https://www.tiktok.com/business">TikTok</a>'}

    claim_view = ClaimView
