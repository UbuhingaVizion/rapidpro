"""Sync wrappers around the async python-telegram-bot client.

The web app only manages Telegram bots (claiming, webhook registration); inbound updates are delivered to Courier, so
we don't need PTB's dispatcher/application. Django is sync, so expose the handful of async bot calls as sync functions.
"""

import telegram
from asgiref.sync import async_to_sync


async def _get_me(token: str) -> telegram.User:
    async with telegram.Bot(token) as bot:
        return await bot.get_me()


async def _set_webhook(token: str, url: str) -> bool:
    async with telegram.Bot(token) as bot:
        return await bot.set_webhook(url=url)


async def _delete_webhook(token: str) -> bool:
    async with telegram.Bot(token) as bot:
        return await bot.delete_webhook()


get_me = async_to_sync(_get_me)
set_webhook = async_to_sync(_set_webhook)
delete_webhook = async_to_sync(_delete_webhook)
