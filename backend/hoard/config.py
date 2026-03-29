"""Hoard configuration — env vars with sensible defaults."""

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class DatabaseConfig:
    url: str = os.environ.get(
        "HOARD_DATABASE_URL",
        "sqlite+aiosqlite:///./hoard.db",
    )


@dataclass(frozen=True)
class AuthConfig:
    secret_key: str = os.environ.get("HOARD_SECRET_KEY", "change-me-in-production")
    algorithm: str = "HS256"
    token_expire_minutes: int = int(os.environ.get("HOARD_TOKEN_EXPIRE_MINUTES", "1440"))


@dataclass(frozen=True)
class ResolverConfig:
    enabled: bool = True
    api_key: str = ""
    refresh_cadence: str = "daily"


@dataclass(frozen=True)
class PriceEngineConfig:
    resolvers: dict[str, ResolverConfig] = field(default_factory=dict)
    source_trust: dict[str, float] = field(default_factory=lambda: {
        "tcgplayer": 0.9,
        "pricecharting": 0.85,
        "ebay_sold": 0.7,
        "manual": 0.5,
    })
    decay_days: int = 90
    high_value_threshold: float = 100.0


@dataclass(frozen=True)
class HoardConfig:
    db: DatabaseConfig = field(default_factory=DatabaseConfig)
    auth: AuthConfig = field(default_factory=AuthConfig)
    price_engine: PriceEngineConfig = field(default_factory=PriceEngineConfig)


def load_config() -> HoardConfig:
    """Load config from environment. YAML overlay planned for v0.2."""
    resolvers = {}

    pc_key = os.environ.get("PRICECHARTING_API_KEY", "")
    resolvers["pricecharting"] = ResolverConfig(
        enabled=bool(pc_key),
        api_key=pc_key,
    )

    tcg_key = os.environ.get("TCGPLAYER_API_KEY", "")
    resolvers["tcgplayer"] = ResolverConfig(
        enabled=bool(tcg_key),
        api_key=tcg_key,
    )

    resolvers["manual"] = ResolverConfig(enabled=True)

    return HoardConfig(
        price_engine=PriceEngineConfig(resolvers=resolvers),
    )
