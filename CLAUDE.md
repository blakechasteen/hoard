# Hoard — Collectibles Portfolio Tracker

## Metaphor
Hoard is the collection. A **Stash** is a user's portfolio. A **Trove** is a grouping
within a stash. An **Appraisal** is a valuation snapshot. The **Price Engine** runs
**Resolvers** that produce appraisals.

## Stack
- **Backend**: FastAPI + SQLAlchemy + Postgres
- **Frontend**: React + Vite + TypeScript
- **Deploy**: Docker Compose on Proxmox LXC

## Commands
```bash
# Backend
cd backend && pip install -r requirements.txt
uvicorn hoard.main:app --reload --port 8080

# Frontend
cd frontend && npm install && npm run dev

# Docker
docker compose up -d
```

## Design Decisions
- JSONB `metadata` column for category-specific fields (no rigid schema per category)
- Catalog-linked items via `catalog_ref` (e.g., "tcgplayer:12345")
- Tiered categories: Tier 1 (cards, automated), Tier 2 (coins, semi-auto), Tier 3 (other, manual)
- Confidence shown on every valuation (color-coded freshness)
- Try/except ALTER pattern for migrations (SOP-8)
- Price resolvers are protocol-based plugins, configured per deployment
- Auth: invite codes + JWT, no password reset flows
