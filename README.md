# Hoard

A collectibles portfolio tracker that treats your collection like an investment portfolio. Track Pokemon cards, sports cards, coins, sealed product, vintage apparel, Beanie Babies — anything with collector value. Watch your collection's value move over time like a stock chart.

Built for friend groups who collect. Multi-user, invite-only, self-hosted on Proxmox.

## What It Does

- **Portfolio charts** — Total collection value over time, just like a stock ticker
- **Item tracking** — Cards, coins, sealed boxes, shirts, anything. Each with grade, purchase price, tags, and category-specific metadata
- **Troves** — Group items however you want ("Graded Pokemon", "Sealed Boxes", "Coins") and chart each group independently
- **Price Engine** — Pluggable resolvers pull prices from multiple sources. Composite valuation uses weighted median with recency decay and source trust scores
- **Confidence indicators** — Every valuation shows how fresh and reliable it is (green/yellow/gray)
- **Gain/loss tracking** — See unrealized gains per item and across your whole collection

## Quick Start

### Development (SQLite, no Docker needed)

```bash
# Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn hoard.main:app --reload --port 8080

# Generate invite codes
python seed.py

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

The frontend dev server proxies `/api` to the backend on port 8080.

### Production (Docker Compose)

```bash
cp .env.example .env
# Edit .env with your secrets and API keys

docker compose up -d

# Generate invite codes
docker compose exec api python seed.py
```

### Running Tests

```bash
cd backend
source .venv/bin/activate
pytest -v
```

35 tests, ~8 seconds. Unit tests for composite valuation + integration tests for all API endpoints.

## Architecture

```
Frontend (React + Recharts)
    |
FastAPI Backend
    |
    +-- Database (SQLite / Postgres)
    |       Items, Appraisals, Users, Troves
    |
    +-- Price Engine
            Resolver protocol -> Composite valuation
```

### Price Engine

The price engine is protocol-based — each data source is a resolver plugin.

```
Item -> [Resolver 1, Resolver 2, ...] -> [Result, Result, ...] -> Composite Valuation
```

**Composite valuation** merges results using weighted median:
- **Recency** — prices decay over 90 days
- **Source trust** — configurable per source (e.g., TCGPlayer 0.9, manual 0.5)
- **Grade specificity** — grade-matched prices get a 1.3x weight bonus

Current resolvers:

| Resolver | Status | Covers |
|----------|--------|--------|
| Manual | Active | Everything (user-entered) |
| PriceCharting | Ready (needs API key) | Cards, sealed, games |

### Data Model

- **Item** — Any collectible. JSONB `metadata` for category-specific fields
- **Appraisal** — A price data point in time, with source, confidence, and composite valuation
- **Trove** — A user-defined grouping. Items can belong to multiple troves
- **User** — Invite-code registration, JWT auth

### Category Tiers

| Tier | Categories | Pricing |
|------|-----------|---------|
| 1 (automated) | Pokemon, Sports, MTG, Sealed | API-backed resolvers |
| 2 (semi-auto) | Coins | Cert number lookup |
| 3 (manual) | Apparel, Beanie Babies, Other | User-entered valuations |

## API

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/auth/register` | Register with invite code |
| POST | `/api/v1/auth/login` | Login, get JWT |
| GET | `/api/v1/auth/me` | Current user |
| GET | `/api/v1/items` | List items (filterable by category) |
| POST | `/api/v1/items` | Add item |
| GET | `/api/v1/items/:id` | Get item with current value |
| PATCH | `/api/v1/items/:id` | Update item |
| DELETE | `/api/v1/items/:id` | Remove item |
| GET | `/api/v1/items/:id/appraisals` | Price history |
| POST | `/api/v1/items/:id/appraisals` | Add manual appraisal |
| GET | `/api/v1/troves` | List troves |
| POST | `/api/v1/troves` | Create trove |
| POST | `/api/v1/troves/:id/items/:item_id` | Add item to trove |
| DELETE | `/api/v1/troves/:id/items/:item_id` | Remove from trove |
| GET | `/api/v1/portfolio/summary` | Portfolio value + history |
| GET | `/health` | Health check |

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `HOARD_DATABASE_URL` | `sqlite+aiosqlite:///./hoard.db` | Database URL |
| `HOARD_SECRET_KEY` | `change-me-in-production` | JWT signing key |
| `HOARD_TOKEN_EXPIRE_MINUTES` | `1440` | Token lifetime |
| `PRICECHARTING_API_KEY` | — | Enables PriceCharting resolver |
| `TCGPLAYER_API_KEY` | — | Enables TCGPlayer resolver |

### Adding a Resolver

Implement the `PriceResolver` protocol and register in `main.py`:

```python
class MyResolver:
    name = "myresolver"
    categories = ["pokemon", "sports"]

    async def resolve(self, item: Item) -> ResolverResult | None:
        return ResolverResult(price=99.99, source=self.name, confidence=0.8)

    async def health(self) -> bool:
        return True
```

## Tech Stack

- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic v2
- **Frontend**: React 19, Vite, TypeScript, Recharts
- **Database**: SQLite (dev), PostgreSQL 16 (prod)
- **Deploy**: Docker Compose on Proxmox LXC
