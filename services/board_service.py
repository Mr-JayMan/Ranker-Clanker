from database.connection import execute, fetch


DEFAULT_REGIONS = ("NA", "EU", "AS/OCE", "SA")

DEFAULT_MODES = {
    "solo": 1,
    "duo": 2,
    "trio": 3,
}


async def create_default_boards(guild_id: int) -> int:
    created = 0

    for mode, team_size in DEFAULT_MODES.items():
        for region in DEFAULT_REGIONS:
            result = await execute(
                """
                INSERT INTO boards (
                    guild_id,
                    name,
                    mode,
                    region,
                    team_size,
                    slot_count
                )
                VALUES ($1, $2, $3, $4, $5, 10)
                ON CONFLICT (guild_id, mode, region)
                DO NOTHING;
                """,
                guild_id,
                f"{region} {mode.title()}",
                mode,
                region,
                team_size,
            )

            if result == "INSERT 0 1":
                created += 1

    return created


async def get_enabled_boards(
    guild_id: int,
) -> list:
    return await fetch(
        """
        SELECT
            id,
            name,
            mode,
            region,
            team_size,
            slot_count
        FROM boards
        WHERE guild_id = $1
          AND enabled = TRUE
        ORDER BY
            CASE mode
                WHEN 'solo' THEN 1
                WHEN 'duo' THEN 2
                WHEN 'trio' THEN 3
                ELSE 4
            END,
            region;
        """,
        guild_id,
    )