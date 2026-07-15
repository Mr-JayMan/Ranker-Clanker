import discord
from discord import app_commands
from discord.ext import commands

from services.board_display_service import (
    publish_region_boards,
)


VALID_REGIONS = {
    "NA",
    "EU",
    "AS/OCE",
    "SA",
}


class BoardDisplayCommands(commands.Cog):
    def __init__(
        self,
        bot: commands.Bot,
    ) -> None:
        self.bot = bot

    @app_commands.command(
        name="setregionchannel",
        description=(
            "Publish a region's Solo, Duo, "
            "and Trio leaderboards in a channel."
        ),
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(
        administrator=True
    )
    async def setregionchannel(
        self,
        interaction: discord.Interaction,
        region: str,
        channel: discord.TextChannel,
    ) -> None:
        if interaction.guild_id is None:
            await interaction.response.send_message(
                "This command can only be used in a server.",
                ephemeral=True,
            )
            return

        normalized_region = (
            region.strip().upper()
        )

        if normalized_region not in VALID_REGIONS:
            await interaction.response.send_message(
                (
                    "Invalid region. Use one of:\n"
                    "`NA`, `EU`, `AS/OCE`, or `SA`"
                ),
                ephemeral=True,
            )
            return

        await interaction.response.defer(
            ephemeral=True
        )

        published = await publish_region_boards(
            self.bot,
            interaction.guild_id,
            normalized_region,
            channel,
        )

        if published == 0:
            await interaction.followup.send(
                (
                    "No boards were found for that region. "
                    "Run `/setupboards` first."
                ),
                ephemeral=True,
            )
            return

        await interaction.followup.send(
            (
                f"✅ Published **{published}** "
                f"{normalized_region} leaderboards in "
                f"{channel.mention}."
            ),
            ephemeral=True,
        )

    @app_commands.command(
        name="refreshregionboards",
        description=(
            "Refresh a region's displayed leaderboards."
        ),
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(
        administrator=True
    )
    async def refreshregionboards(
        self,
        interaction: discord.Interaction,
        region: str,
        channel: discord.TextChannel,
    ) -> None:
        if interaction.guild_id is None:
            await interaction.response.send_message(
                "This command can only be used in a server.",
                ephemeral=True,
            )
            return

        normalized_region = (
            region.strip().upper()
        )

        if normalized_region not in VALID_REGIONS:
            await interaction.response.send_message(
                (
                    "Invalid region. Use `NA`, `EU`, "
                    "`AS/OCE`, or `SA`."
                ),
                ephemeral=True,
            )
            return

        await interaction.response.defer(
            ephemeral=True
        )

        published = await publish_region_boards(
            self.bot,
            interaction.guild_id,
            normalized_region,
            channel,
        )

        await interaction.followup.send(
            (
                f"✅ Refreshed **{published}** boards "
                f"in {channel.mention}."
            ),
            ephemeral=True,
        )


async def setup(
    bot: commands.Bot,
) -> None:
    await bot.add_cog(
        BoardDisplayCommands(bot)
    )