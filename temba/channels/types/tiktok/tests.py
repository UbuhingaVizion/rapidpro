from django.urls import reverse

from temba.tests import TembaTest

from ...models import Channel


class TikTokTypeTest(TembaTest):
    def test_claim(self):
        url = reverse("channels.types.tiktok.claim")

        self.login(self.admin)

        # the type is available on the claim list
        response = self.client.get(reverse("channels.channel_claim"))
        self.assertContains(response, url)

        response = self.client.get(url)
        self.assertContains(response, "Connect TikTok")

        # required fields are validated
        response = self.client.post(url, {})
        self.assertEqual(200, response.status_code)
        form = response.context["form"]
        for field in ["client_key", "client_secret", "business_id", "access_token"]:
            self.assertIn(field, form.errors)

        data = {
            "client_key": "app123",
            "client_secret": "secret123",
            "business_id": "business123",
            "access_token": "token123",
            "refresh_token": "refresh123",
        }

        response = self.client.post(url, data)
        self.assertEqual(302, response.status_code)

        channel = Channel.objects.get(channel_type="TT")
        self.assertEqual("business123", channel.address)
        self.assertEqual("TikTok: business123", channel.name)
        self.assertIsNone(channel.country)
        self.assertEqual(["ext"], list(channel.schemes))
        self.assertEqual("token123", channel.config[Channel.CONFIG_AUTH_TOKEN])
        self.assertEqual("app123", channel.config["client_key"])
        self.assertEqual("secret123", channel.config["client_secret"])
        self.assertEqual("business123", channel.config["business_id"])
        self.assertEqual("refresh123", channel.config["refresh_token"])

        # the webhook secret falls back to the app secret
        self.assertEqual("secret123", channel.config["webhook_secret"])

        # the same business account can't be connected twice
        response = self.client.post(url, data)
        self.assertEqual(200, response.status_code)
        self.assertIn(
            "A TikTok channel for this business account is already connected.",
            response.context["form"].errors["business_id"],
        )

    def test_channel_type(self):
        channel_type = Channel.get_type_from_code("TT")
        self.assertEqual("TikTok", channel_type.name)
        self.assertEqual(["ext"], channel_type.schemes)
