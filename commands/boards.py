import discord
from discord import app_commands
from discord.ext import commands

from services.board_service import (
    create_default_boards,
    get_enabled_boards,
)


class BoardCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="setupboards",
        description="Create the default Ranker Clanker leaderboards.",
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator=True)
    async def setupboards(
        self,
        interaction: discord.Interaction,
    ) -> None:
        if interaction.guild_id is None:
            await interaction.response.send_message(
                "This command can only be used in a server.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        created = await create_default_boards(
            interaction.guild_id
        )

        if created == 0:
            message = (
                "✅ The default leaderboards are already configured."
            )
        else:
            message = (
                f"✅ Created **{created}** leaderboards.\n\n"
                "Solo, Duo, and Trio boards were created for "
                "NA, EU, AS/OCE, and SA."
            )

        await interaction.followup.send(
            message,
            ephemeral=True,
        )

    @app_commands.command(
        name="boards",
        description="Display all enabled leaderboards.",
    )
    @app_commands.guild_only()
    async def boards(
        self,
        interaction: discord.Interaction,
    ) -> None:
        if interaction.guild_id is None:
            await interaction.response.send_message(
                "This command can only be used in a server.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        boards = await get_enabled_boards(
            interaction.guild_id
        )

        if not boards:
            await interaction.followup.send(
                (
                    "No leaderboards are configured yet. "
                    "An administrator must run `/setupboards`."
                ),
                ephemeral=True,
            )
            return

        lines = [
            (
                f"**{board['name']}** — "
                f"{board['slot_count']} slots"
            )
            for board in boards
        ]

        embed = discord.Embed(
            title="🏆 Ranker Clanker Leaderboards",
            description="\n".join(lines),
            color=discord.Color.gold(),
            timestamp=discord.utils.utcnow(),
        )

        embed.set_footer(
            text=f"{len(boards)} active leaderboards"
        )

        await interaction.followup.send(
            embed=embed,
            ephemeral=True,
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BoardCommands(bot))