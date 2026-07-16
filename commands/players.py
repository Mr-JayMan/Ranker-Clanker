import discord
from discord import app_commands
from discord.ext import commands

from services.player_service import (
    get_player,
    register_player,
)


REGION_CHOICES = [
    app_commands.Choice(
        name="North America",
        value="NA",
    ),
    app_commands.Choice(
        name="Europe",
        value="EU",
    ),
    app_commands.Choice(
        name="Asia / Oceania",
        value="AS/OCE",
    ),
    app_commands.Choice(
        name="South America",
        value="SA",
    ),
]


class PlayerCommands(commands.Cog):
    def __init__(
        self,
        bot: commands.Bot,
    ) -> None:
        self.bot = bot

    @app_commands.command(
        name="register",
        description=(
            "Register as a Ranker Clanker competitor."
        ),
    )
    @app_commands.guild_only()
    @app_commands.choices(region=REGION_CHOICES)
    async def register(
        self,
        interaction: discord.Interaction,
        region: app_commands.Choice[str],
    ) -> None:
        if interaction.guild_id is None:
            await interaction.response.send_message(
                "This command can only be used in a server.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(
            ephemeral=True
        )

        try:
            player, created = await register_player(
                interaction.guild_id,
                interaction.user.id,
                region.value,
            )
        except Exception as error:
            await interaction.followup.send(
                (
                    "❌ Registration failed.\n\n"
                    f"`{error}`"
                ),
                ephemeral=True,
            )
            return

        if not created:
            await interaction.followup.send(
                (
                    "You are already registered.\n\n"
                    f"**Region:** {player['region']}\n"
                    f"**Starting ELO:** {player['elo']}"
                ),
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title="⚔️ Competitor Registered",
            description=(
                "Your Ranker Clanker profile "
                "has been created."
            ),
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow(),
        )

        embed.add_field(
            name="Player",
            value=interaction.user.mention,
            inline=False,
        )

        embed.add_field(
            name="Region",
            value=player["region"],
            inline=True,
        )

        embed.add_field(
            name="Starting ELO",
            value=str(player["elo"]),
            inline=True,
        )

        embed.set_footer(
            text=(
                "Your region applies to Solo, "
                "Duo, and Trio competition."
            )
        )

        await interaction.followup.send(
            embed=embed,
            ephemeral=True,
        )

    @app_commands.command(
        name="playerinfo",
        description=(
            "View basic registration information "
            "for a competitor."
        ),
    )
    @app_commands.guild_only()
    async def playerinfo(
        self,
        interaction: discord.Interaction,
        member: discord.Member | None = None,
    ) -> None:
        if interaction.guild_id is None:
            await interaction.response.send_message(
                "This command can only be used in a server.",
                ephemeral=True,
            )
            return

        target = member or interaction.user

        await interaction.response.defer(
            ephemeral=True
        )

        player = await get_player(
            interaction.guild_id,
            target.id,
        )

        if player is None:
            await interaction.followup.send(
                (
                    f"{target.mention} is not registered yet.\n\n"
                    "They must use `/register` first."
                ),
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title="⚔️ Ranker Clanker Competitor",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow(),
        )

        embed.set_thumbnail(
            url=target.display_avatar.url
        )

        embed.add_field(
            name="Player",
            value=target.mention,
            inline=False,
        )

        embed.add_field(
            name="Region",
            value=player["region"],
            inline=True,
        )

        embed.add_field(
            name="ELO",
            value=str(player["elo"]),
            inline=True,
        )

        embed.add_field(
            name="Record",
            value=(
                f"{player['wins']} wins – "
                f"{player['losses']} losses"
            ),
            inline=False,
        )

        await interaction.followup.send(
            embed=embed,
            ephemeral=True,
        )


async def setup(
    bot: commands.Bot,
) -> None:
    await bot.add_cog(
        PlayerCommands(bot)
    )