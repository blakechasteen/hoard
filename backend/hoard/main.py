"""Hoard — Collectibles Portfolio Tracker API."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from hoard.config import load_config
from hoard.database import engine
from hoard.models import Base
from hoard.price_engine.engine import PriceEngine
from hoard.price_engine.resolvers.manual import ManualResolver
from hoard.routers import appraisals, auth, items, portfolio, troves

logger = logging.getLogger(__name__)
config = load_config()


# Price engine singleton
price_engine = PriceEngine(config.price_engine)


def _register_resolvers():
    """Register enabled price resolvers."""
    price_engine.register(ManualResolver())

    pc_config = config.price_engine.resolvers.get("pricecharting")
    if pc_config and pc_config.enabled:
        from hoard.price_engine.resolvers.pricecharting import PriceChartingResolver
        price_engine.register(PriceChartingResolver(api_key=pc_config.api_key))


async def _init_db():
    """Create tables and run idempotent migrations."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # Migrations (SOP-8: try/except ALTER pattern)
        migrations = [
            "ALTER TABLE items ADD COLUMN search_override VARCHAR(256)",
            "ALTER TABLE items ADD COLUMN pinned_value FLOAT",
            "ALTER TABLE appraisals ADD COLUMN composite_price FLOAT",
            "ALTER TABLE appraisals ADD COLUMN composite_confidence FLOAT",
        ]
        for sql in migrations:
            try:
                await conn.execute(text(sql))
            except Exception:
                pass  # Column already exists


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(level=logging.INFO)
    logger.info("Hoard starting up")
    await _init_db()
    _register_resolvers()
    logger.info(f"Price engine: {len(price_engine.resolvers)} resolvers active")
    yield
    await engine.dispose()
    logger.info("Hoard shut down")


app = FastAPI(
    title="Hoard",
    description="Collectibles portfolio tracker",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(items.router, prefix="/api/v1")
app.include_router(appraisals.router, prefix="/api/v1")
app.include_router(troves.router, prefix="/api/v1")
app.include_router(portfolio.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "resolvers": len(price_engine.resolvers)}
