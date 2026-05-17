"""共享 pytest fixtures。

提供：
- 配置 ``app.*`` 包路径，使用 ``backend/`` 作为顶级（与现有测试一致）
- 异步 mock DB / Redis fixture
- ``fakeredis`` 作为 Redis 实例（用于锁定流程的真实集成测试）

注：目前认证相关测试不依赖真实数据库，仅 mock SQLAlchemy 调用即可。
后续若引入真实 DB 集成测试，可在此扩展 ``aiosqlite`` 内存库 fixture。
"""

from __future__ import annotations

import asyncio
import sys
import uuid
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio


# 让 ``app.*`` 可解析（pytest 在 backend/ 目录下运行时本就可用，这里兜底以
# 防 IDE 或 CI 在仓库根运行 pytest）。
_BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))


# ─── Mock DB / Redis ─────────────────────────────────────────────────


@pytest.fixture
def mock_db() -> AsyncMock:
    """SQLAlchemy AsyncSession mock。"""
    db = AsyncMock()
    db.add = MagicMock()  # add() 在 SQLAlchemy 中是同步方法
    db.flush = AsyncMock()
    db.delete = AsyncMock()
    db.refresh = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    return db


@pytest.fixture
def mock_redis() -> AsyncMock:
    """Redis 客户端 mock（不真实存储，适合行为校验）。"""
    redis = AsyncMock()
    redis.hgetall = AsyncMock(return_value={})
    redis.hset = AsyncMock()
    redis.expire = AsyncMock()
    redis.delete = AsyncMock()
    return redis


# ─── fakeredis ───────────────────────────────────────────────────────


@pytest_asyncio.fixture
async def fake_redis():
    """基于 fakeredis 的真实异步 Redis 实例（用于锁定窗口端到端测试）。"""
    fakeredis = pytest.importorskip("fakeredis")
    client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    try:
        yield client
    finally:
        await client.aclose()


# ─── Helpers ─────────────────────────────────────────────────────────


@pytest.fixture
def fixed_user_id() -> str:
    """可复用的固定用户 ID（避免每个测试都生成 UUID）。"""
    return str(uuid.uuid4())
