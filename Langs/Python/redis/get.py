import asyncio
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass

import redis.asyncio as redis
from redis.asyncio.retry import Retry
from redis.backoff import ExponentialBackoff
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import RedisError, TimeoutError as RedisTimeoutError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RedisSettings:
    url: str = "redis://localhost:6379/0"
    max_connections: int = 50
    socket_timeout: float = 1.5          # مهلة قراءة/كتابة العملية الواحدة (ثوانٍ)
    socket_connect_timeout: float = 1.0  # مهلة فتح اتصال TCP جديد
    health_check_interval: int = 30      # فحص صحة الاتصالات الخاملة كل 30 ثانية
    retry_attempts: int = 3
    retry_base_delay: float = 0.05
    retry_max_delay: float = 0.5


def create_redis_client(settings: RedisSettings) -> redis.Redis:
    """يبني عميل Redis غير متزامن بإعدادات مناسبة للإنتاج."""
    retry_policy = Retry(
        backoff=ExponentialBackoff(
            cap=settings.retry_max_delay,
            base=settings.retry_base_delay,
        ),
        retries=settings.retry_attempts,
    )

    pool = redis.ConnectionPool.from_url(
        settings.url,
        max_connections=settings.max_connections,
        socket_timeout=settings.socket_timeout,
        socket_connect_timeout=settings.socket_connect_timeout,
        health_check_interval=settings.health_check_interval,
        retry=retry_policy,
        retry_on_error=[RedisConnectionError, RedisTimeoutError],
        decode_responses=True,  # يُرجع str بدلًا من bytes عند القراءة
    )

    return redis.Redis(connection_pool=pool)


@asynccontextmanager
async def redis_lifespan(settings: RedisSettings):
    """يدير دورة حياة العميل: تحقق من الاتصال عند البدء وإغلاق الـ pool نظيفًا."""
    client = create_redis_client(settings)
    try:
        await client.ping()
        logger.info("Connected to Redis successfully.")
        yield client
    finally:
        await client.aclose()
        logger.info("Redis connection pool closed.")


async def set_value(
    client: redis.Redis,
    key: str,
    value: str,
    *,
    ex_seconds: int | None = None,
    nx: bool = False,
) -> bool:
    """
    ينفذ أمر SET بشكل آمن.
    يُرجع True إذا تم التخزين، وFalse إذا رُفض بسبب شرط مثل NX.
    """
    try:
        result = await client.set(
            name=key,
            value=value,
            ex=ex_seconds,
            nx=nx,
        )
        return bool(result)
    except (RedisTimeoutError, RedisConnectionError) as exc:
        logger.warning("Redis transient failure on SET key=%s: %s", key, exc)
        raise
    except RedisError as exc:
        logger.error("Redis error on SET key=%s: %s", key, exc)
        raise


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = RedisSettings(
        url="redis://localhost:6379/0",
        max_connections=50,
    )

    async with redis_lifespan(settings) as client:
        stored = await set_value(
            client,
            key="service:status",
            value="healthy",
            ex_seconds=120,
        )
        logger.info("SET result: %s", stored)


if __name__ == "__main__":
    asyncio.run(main())
