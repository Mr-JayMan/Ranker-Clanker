from database.connection import execute


async def create_schema() -> None:
    print("Creating database tables...")

    await execute(
        """
        CREATE TABLE IF NOT EXISTS server_settings (
            guild_id BIGINT PRIMARY KEY,
            challenge_channel_id BIGINT,
            review_channel_id BIGINT,
            log_channel_id BIGINT,
            announcement_channel_id BIGINT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """
    )

    await execute(
        """
        CREATE TABLE IF NOT EXISTS boards (
            id BIGSERIAL PRIMARY KEY,
            guild_id BIGINT NOT NULL,
            name TEXT NOT NULL,
            mode TEXT NOT NULL,
            region TEXT NOT NULL,
            team_size INTEGER NOT NULL,
            slot_count INTEGER NOT NULL DEFAULT 10,
            acceptance_days INTEGER NOT NULL DEFAULT 7,
            completion_days INTEGER NOT NULL DEFAULT 7,
            rematch_cooldown_days INTEGER NOT NULL DEFAULT 5,
            enabled BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

            UNIQUE(guild_id, mode, region),

            CHECK (team_size >= 1),
            CHECK (slot_count >= 1)
        );
        """
    )

    await execute(
        """
        CREATE TABLE IF NOT EXISTS players (
            id BIGSERIAL PRIMARY KEY,
            guild_id BIGINT NOT NULL,
            discord_user_id BIGINT NOT NULL,
            region TEXT,
            elo INTEGER NOT NULL DEFAULT 1500,
            wins INTEGER NOT NULL DEFAULT 0,
            losses INTEGER NOT NULL DEFAULT 0,
            active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

            UNIQUE(guild_id, discord_user_id)
        );
        """
    )

    await execute(
        """
        CREATE TABLE IF NOT EXISTS teams (
            id BIGSERIAL PRIMARY KEY,
            guild_id BIGINT NOT NULL,
            name TEXT NOT NULL,
            team_size INTEGER NOT NULL,
            region TEXT NOT NULL,
            captain_player_id BIGINT NOT NULL
                REFERENCES players(id)
                ON DELETE RESTRICT,
            status TEXT NOT NULL DEFAULT 'pending',
            replacement_deadline TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

            CHECK (team_size IN (2, 3))
        );
        """
    )

    await execute(
        """
        CREATE TABLE IF NOT EXISTS team_members (
            id BIGSERIAL PRIMARY KEY,
            team_id BIGINT NOT NULL
                REFERENCES teams(id)
                ON DELETE CASCADE,
            player_id BIGINT NOT NULL
                REFERENCES players(id)
                ON DELETE CASCADE,
            join_order INTEGER NOT NULL,
            confirmation_status TEXT NOT NULL DEFAULT 'pending',
            joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

            UNIQUE(team_id, player_id),
            UNIQUE(team_id, join_order)
        );
        """
    )

    await execute(
        """
        CREATE TABLE IF NOT EXISTS leaderboard_entries (
            id BIGSERIAL PRIMARY KEY,
            board_id BIGINT NOT NULL
                REFERENCES boards(id)
                ON DELETE CASCADE,
            position INTEGER NOT NULL,
            player_id BIGINT
                REFERENCES players(id)
                ON DELETE CASCADE,
            team_id BIGINT
                REFERENCES teams(id)
                ON DELETE CASCADE,
            wins_while_holding INTEGER NOT NULL DEFAULT 0,
            position_started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

            UNIQUE(board_id, position),

            CHECK (position >= 1),
            CHECK (
                (player_id IS NOT NULL AND team_id IS NULL)
                OR
                (player_id IS NULL AND team_id IS NOT NULL)
            )
        );
        """
    )

    await execute(
        """
        CREATE INDEX IF NOT EXISTS boards_guild_enabled_idx
        ON boards(guild_id, enabled);
        """
    )

    await execute(
        """
        CREATE INDEX IF NOT EXISTS players_guild_user_idx
        ON players(guild_id, discord_user_id);
        """
    )

    await execute(
        """
        CREATE INDEX IF NOT EXISTS teams_guild_status_idx
        ON teams(guild_id, status);
        """
    )

    await execute(
        """
        CREATE INDEX IF NOT EXISTS leaderboard_board_position_idx
        ON leaderboard_entries(board_id, position);
        """
    )

    await execute(
        """
        ALTER TABLE boards
        ADD COLUMN IF NOT EXISTS display_channel_id BIGINT;
        """
    )

    await execute(
        """
        ALTER TABLE boards
        ADD COLUMN IF NOT EXISTS display_message_id BIGINT;
        """
    )


    print("Database tables ready.")