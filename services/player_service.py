import asyncpg

from database.connection import fetchrow


VALID_REGIONS = {
    "NA",
    "EU",
    "AS/OCE",
    "SA",
}


async def get_player(
    guild_id: int,
    discord_user_id: int,
) -> asyncpg.Record | None:
    return await fetchrow(
        """
        SELECT
            id,
            guild_id,
            discord_user_id,
            region,
            elo,
            wins,
            losses,
            active,
            created_at,
            updated_at
        FROM players
        WHERE guild_id = $1
          AND discord_user_id = $2;
        """,
        guild_id,
        discord_user_id,
    )


async def register_player(
    guild_id: int,
    discord_user_id: int,
    region: str,
) -> tuple[asyncpg.Record, bool]:
    normalized_region = region.strip().upper()

    if normalized_region not in VALID_REGIONS:
        raise ValueError(
            "Region must be NA, EU, AS/OCE, or SA."
        )

    existing_player = await get_player(
        guild_id,
        discord_user_id,
    )

    if existing_player is not None:
        return existing_player, False

    player = await fetchrow(
        """
        INSERT INTO players (
            guild_id,
            discord_user_id,
            region
        )
        VALUES ($1, $2, $3)
        RETURNING
            id,
            guild_id,
            discord_user_id,
            region,
            elo,
            wins,
            losses,
            active,
            created_at,
            updated_at;
        """,
        guild_id,
        discord_user_id,
        normalized_region,
    )

    if player is None:
        raise RuntimeError(
            "The player record could not be created."
        )

    return player, True