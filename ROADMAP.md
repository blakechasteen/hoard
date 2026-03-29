# Hoard Roadmap

## v0.1 — Foundation (done)

- [x] FastAPI backend with SQLite/Postgres support
- [x] Item CRUD with JSONB metadata, tags, grades, catalog refs
- [x] Manual appraisals with confidence scoring
- [x] Composite valuation (weighted median, recency decay, source trust)
- [x] Protocol-based price engine with PriceCharting resolver
- [x] Troves (user-defined item groupings)
- [x] Portfolio summary with time-series history
- [x] Multi-user auth (invite codes + JWT)
- [x] React frontend with dark theme, portfolio chart, item grid
- [x] Docker Compose for production deployment
- [x] 35 tests passing

## v0.2 — User-Configured Price Sources

The big idea: collectors have their trusted sites, and those sites change. Instead of hardcoding resolvers, let users bring their own price sources.

### Custom scrape targets
- [ ] **Site registry** — Users add websites they trust for pricing (eBay, specific card shops, forums, auction houses)
- [ ] **Scrape config per site** — CSS selector or XPath for the price element, with a test/preview before saving
- [ ] **Per-user source trust** — Each user sets their own trust weights ("I trust CardMarket more than TCGPlayer for European prices")
- [ ] **Site health monitoring** — Track scrape success rate, auto-degrade sites that start failing

### Tunable price scoring
- [ ] **Scoring dashboard** — UI to adjust source trust weights, recency decay rate, and grade specificity bonus
- [ ] **Preview mode** — Show how changing weights affects your portfolio valuation before committing
- [ ] **Per-category overrides** — Different trust weights for coins vs cards vs apparel

### Image suggestions on item creation
- [ ] **Preferred site image pull** — When logging a new item, search the user's preferred site for the closest name match
- [ ] **One-click image select** — Show top 3-5 image results, user picks one with a single click
- [ ] **Fallback chain** — If preferred site has no image, try next site, then generic image search
- [ ] **Image cache** — Store selected images locally to avoid broken links

### Automated price refresh
- [ ] Background worker on configurable cadence (daily/weekly/monthly based on item value)
- [ ] Rate limiting and retry logic per resolver
- [ ] Refresh history visible per item

## v0.3 — Social and Insights

### Friend group features
- [ ] **Leaderboard** — Who's up the most this month/quarter/year
- [ ] **Collection overlap** — See what items multiple friends own
- [ ] **Trade suggestions** — "You have two of X, Blake wants one"
- [ ] **Activity feed** — "Sarah added a PSA 10 Charizard"

### Grading ROI calculator
- [ ] Input: raw card value, grading cost, expected grade distribution
- [ ] Output: expected value after grading, break-even probability
- [ ] "What should I grade next?" ranked by expected ROI

### Analytics
- [ ] Best/worst performers over time
- [ ] Category breakdown (pie chart of collection by category)
- [ ] Acquisition timeline (when did you buy what)
- [ ] Market trend overlay (compare your collection to category-wide trends)

## v0.4 — Smart Input

### Barcode / set number scan
- [ ] Camera input to scan card barcodes or set numbers
- [ ] Auto-populate item details from catalog

### Photo-based identification
- [ ] Upload a photo, ML identifies the card/item
- [ ] Pre-fill name, set, category from the match
- [ ] Works offline with a local model or via API

### Bulk import
- [ ] CSV import for existing spreadsheet inventories
- [ ] TCGPlayer collection export import
- [ ] PCGS/NGC cert number batch lookup

## v0.5 — Infrastructure

### Proxmox deployment
- [ ] LXC template with everything pre-configured
- [ ] Automated backups of database
- [ ] HTTPS via Caddy reverse proxy
- [ ] Optional Tailscale for remote access

### Performance
- [ ] Time-series partitioning for appraisals table
- [ ] Redis cache for frequently accessed portfolio summaries
- [ ] Lazy-load items grid with pagination

---

## Design Principles

These carry forward from the global architecture:

1. **Protocol first** — Every resolver is a protocol implementation. Swap or add sources without touching core code.
2. **Graceful degradation** — If a resolver fails, skip it. If all fail, show the last known value with a stale indicator.
3. **User configurable** — Trust weights, scrape targets, refresh cadence, image sources — all user-adjustable. The system learns what you trust.
4. **Confidence visible** — Never hide uncertainty. If a price is stale or from a single source, the user sees it.
