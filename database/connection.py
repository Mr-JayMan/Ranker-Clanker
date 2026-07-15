from typing import Any

import asyncpg
from asyncpg import Pool

from config import DATABASE_URL


_pool: Pool | None = None


async def connect_database() -> Pool:
    global _pool

    if _pool is not None:
        return _pool

    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is missing.")

    print("Connecting to PostgreSQL...")

    _pool = await asyncpg.create_pool(
        dsn=DATABASE_URL,
        min_size=1,
        max_size=5,
        command_timeout=30,
    )

    print("PostgreSQL connected.")

    return _pool


async def close_database() -> None:
    global _pool

    if _pool is None:
        return

    print("Closing PostgreSQL connection...")

    await _pool.close()
    _pool = None


async def get_pool() -> Pool:
    if _pool is None:
        return await connect_database()

    return _pool


async def execute(
    query: str,
    *arguments: Any,
) -> str:
    pool = await get_pool()

    async with pool.acquire() as connection:
        return await connection.execute(
            query,
            *arguments,
        )


async def fetch(
    query: str,
    *arguments: Any,
) -> list[asyncpg.Record]:
    pool = await get_pool()

    async with pool.acquire() as connection:
        records = await connection.fetch(
            query,
            *arguments,
        )

    return list(records)


async def fetchrow(
    query: str,
    *arguments: Any,
) -> asyncpg.Record | None:
    pool = await get_pool()

    async with pool.acquire() as connection:
        return await connection.fetchrow(
            query,
            *arguments,
        )


async def fetchval(
    query: str,
    *arguments: Any,
) -> Any:
    pool = await get_pool()

    async with pool.acquire() as connection:
        return await connection.fetchval(
            query,
            *arguments,
        )