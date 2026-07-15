import asyncio

import discord
from discord.ext import commands

from config import DISCORD_TOKEN, validate_config
from database.connection import (
    close_database,
    connect_database,
)
from database.schema import create_schema

EXTENSIONS = (
    "commands.boards",
)

class RankerClankerBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.members = True

        super().__init__(
            command_prefix="!",
            intents=intents,
        )

async def setup_hook(self) -> None:
    await connect_database()
    await create_schema()

    for extension in EXTENSIONS:
        await self.load_extension(extension)
        print(f"Loaded extension: {extension}")

    synced_commands = await self.tree.sync()

    print(
        f"Synced {len(synced_commands)} slash command(s)."
    )
    async def close(self) -> None:
        await close_database()
        await super().close()

    async def on_ready(self) -> None:
        if self.user is None:
            return

        print(
            f"Logged in as {self.user} "
            f"(ID: {self.user.id})"
        )


async def main() -> None:
    validate_config()

    bot = RankerClankerBot()

    async with bot:
        await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())