import discord

from database.connection import execute, fetch, fetchrow


async def get_board_entries(
    board_id: int,
) -> list:
    return await fetch(
        """
        SELECT
            entries.position,
            entries.wins_while_holding,
            players.discord_user_id,
            teams.name AS team_name
        FROM leaderboard_entries AS entries
        LEFT JOIN players
            ON players.id = entries.player_id
        LEFT JOIN teams
            ON teams.id = entries.team_id
        WHERE entries.board_id = $1
        ORDER BY entries.position ASC;
        """,
        board_id,
    )


async def build_board_embed(
    board,
) -> discord.Embed:
    entries = await get_board_entries(
        board["id"]
    )

    entries_by_position = {
        entry["position"]: entry
        for entry in entries
    }

    embed = discord.Embed(
        title=f"🏆 {board['name']} Leaderboard",
        description=(
            "Current competitive standings\n"
            "━━━━━━━━━━━━━━━━━━━━"
        ),
        color=discord.Color.gold(),
        timestamp=discord.utils.utcnow(),
    )

    medal_icons = {
        1: "🥇",
        2: "🥈",
        3: "🥉",
    }

    for position in range(
        1,
        board["slot_count"] + 1,
    ):
        entry = entries_by_position.get(
            position
        )

        if entry is None:
            display_name = "*Empty Slot*"
            wins = 0

        elif entry["discord_user_id"] is not None:
            display_name = (
                f"<@{entry['discord_user_id']}>"
            )
            wins = entry["wins_while_holding"]

        else:
            display_name = (
                f"**{entry['team_name']}**"
            )
            wins = entry["wins_while_holding"]

        medal = medal_icons.get(
            position
        )

        if medal:
            field_name = (
                f"Position #{position}\n"
                f"{medal} {display_name}"
            )
        else:
            field_name = (
                f"Position #{position}\n"
                f"{display_name}"
            )

        embed.add_field(
            name=field_name,
            value=(
                f"⚔️ **Wins:** `{wins}`"
            ),
            inline=False,
        )

    embed.set_footer(
        text=(
            f"{board['slot_count']} positions "
            "• Ranker Clanker"
        )
    )

    return embed

async def publish_board(
    bot: discord.Client,
    board,
    channel: discord.TextChannel,
) -> None:
    embed = await build_board_embed(board)

    existing_message = None
    message_id = board[
        "display_message_id"
    ]

    if message_id is not None:
        try:
            existing_message = (
                await channel.fetch_message(
                    message_id
                )
            )
        except (
            discord.NotFound,
            discord.Forbidden,
            discord.HTTPException,
        ):
            existing_message = None

    if existing_message is not None:
        await existing_message.edit(
            embed=embed,
            content=None,
        )
        return

    new_message = await channel.send(
        embed=embed
    )

    await execute(
        """
        UPDATE boards
        SET
            display_channel_id = $1,
            display_message_id = $2,
            updated_at = NOW()
        WHERE id = $3;
        """,
        channel.id,
        new_message.id,
        board["id"],
    )


async def publish_region_boards(
    bot: discord.Client,
    guild_id: int,
    region: str,
    channel: discord.TextChannel,
) -> int:
    boards = await fetch(
        """
        SELECT
            id,
            name,
            mode,
            region,
            slot_count,
            display_channel_id,
            display_message_id
        FROM boards
        WHERE guild_id = $1
          AND region = $2
          AND enabled = TRUE
        ORDER BY
            CASE mode
                WHEN 'solo' THEN 1
                WHEN 'duo' THEN 2
                WHEN 'trio' THEN 3
                ELSE 4
            END;
        """,
        guild_id,
        region,
    )

    for board in boards:
        await publish_board(
            bot,
            board,
            channel,
        )

    return len(boards)