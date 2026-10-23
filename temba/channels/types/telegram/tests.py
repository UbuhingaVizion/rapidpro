from unittest.mock import patch

import telegram
from django.urls import reverse

from temba.tests import TembaTest

from ...models import Channel
from .type import TelegramType


class TelegramTypeTest(TembaTest):
    def setUp(self):
        super().setUp()

        self.channel = self.create_channel(
            "TG",
            "Telegram",
            "12345",
            config={"auth_token": "123456789:BAEKbsOKAL23CXufXG4ksNV7Dq7e_1qi3j8"},
        )

    @patch("temba.channels.types.telegram.type.set_webhook")
    @patch("temba.channels.types.telegram.views.get_me")
    def test_claim(self, mock_get_me, mock_set_webhook):
        url = reverse("channels.types.telegram.claim")

        self.login(self.admin)

        # check that claim page URL appears on claim list page
        response = self.client.get(reverse("channels.channel_claim"))
        self.assertContains(response, url)

        # can fetch the claim page
        response = self.client.get(url)
        self.assertContains(response, "Connect Telegram")

        # claim with an invalid token
        mock_get_me.side_effect = telegram.error.TelegramError("Boom")
        response = self.client.post(url, {"auth_token": "invalid"})
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            "Your authentication token is invalid, please check and try again",
            response.context["form"].errors["auth_token"][0],
        )

        user = telegram.User(id=123, first_name="Rapid", is_bot=True, last_name="Bot", username="rapidbot")

        mock_get_me.side_effect = None
        mock_get_me.return_value = user
        mock_set_webhook.return_value = True

        response = self.client.post(url, {"auth_token": "184875172:BAEKbsOKAL23CXufXG4ksNV7Dq7e_1qi3j8"})
        channel = Channel.objects.get(address="rapidbot")
        self.assertEqual(channel.channel_type, "TG")
        self.assertEqual(
            channel.config,
            {
                "auth_token": "184875172:BAEKbsOKAL23CXufXG4ksNV7Dq7e_1qi3j8",
                "callback_domain": channel.callback_domain,
            },
        )

        self.assertRedirect(response, reverse("channels.channel_read", args=[channel.uuid]))
        self.assertEqual(302, response.status_code)

        response = self.client.post(url, {"auth_token": "184875172:BAEKbsOKAL23CXufXG4ksNV7Dq7e_1qi3j8"})
        self.assertEqual(
            "A telegram channel for this bot already exists on your account.",
            response.context["form"].errors["auth_token"][0],
        )

        # make sure we our telegram channel satisfies as a send channel
        send_channel = self.org.get_send_channel()
        self.assertIsNotNone(send_channel)
        self.assertEqual(send_channel.channel_type, "TG")

    @patch("temba.channels.types.telegram.type.delete_webhook")
    def test_release(self, mock_delete_webhook):
        token = self.channel.config["auth_token"]
        self.channel.release(self.admin)

        mock_delete_webhook.assert_called_once_with(token)

    def test_get_error_ref_url(self):
        self.assertEqual("https://core.telegram.org/api/errors", TelegramType().get_error_ref_url(None, "420"))
