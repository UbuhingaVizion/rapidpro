from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from smartmin.views import SmartFormView

from ...models import Channel
from ...views import ClaimViewMixin


class ClaimView(ClaimViewMixin, SmartFormView):
    class Form(ClaimViewMixin.Form):
        client_key = forms.CharField(
            label=_("Client key"),
            help_text=_("The developer app's client key from TikTok for Business."),
        )
        client_secret = forms.CharField(
            label=_("Client secret"),
            widget=forms.PasswordInput,
            help_text=_("The app secret. Also used to verify webhook signatures."),
        )
        business_id = forms.CharField(
            label=_("Business ID"),
            help_text=_("The business account's open_id from the token exchange."),
        )
        access_token = forms.CharField(
            label=_("Access token"),
            widget=forms.PasswordInput,
            help_text=_("The short-lived token TikTok returned for this account."),
        )
        refresh_token = forms.CharField(
            label=_("Refresh token"),
            widget=forms.PasswordInput,
            required=False,
            help_text=_("Used when the access token is refreshed."),
        )
        webhook_secret = forms.CharField(
            label=_("Webhook secret"),
            widget=forms.PasswordInput,
            required=False,
            help_text=_("Only needed when the signing secret is kept separate from the app secret."),
        )

        def clean_business_id(self):
            business_id = self.cleaned_data["business_id"].strip()

            existing = Channel.objects.filter(
                org=self.request.org, is_active=True, channel_type=self.channel_type.code, address=business_id
            )
            if existing.exists():
                raise ValidationError(_("A TikTok channel for this business account is already connected."))

            return business_id

    form_class = Form

    def form_valid(self, form):
        data = form.cleaned_data

        config = {
            Channel.CONFIG_AUTH_TOKEN: data["access_token"],
            "client_key": data["client_key"],
            "client_secret": data["client_secret"],
            "business_id": data["business_id"],
            "refresh_token": data.get("refresh_token", ""),
            "webhook_secret": data.get("webhook_secret") or data["client_secret"],
        }

        self.object = Channel.create(
            self.request.org,
            self.request.user,
            None,
            self.channel_type,
            name=f"TikTok: {data['business_id']}",
            address=data["business_id"],
            config=config,
        )

        return super().form_valid(form)
