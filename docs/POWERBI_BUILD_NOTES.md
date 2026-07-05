# Power BI Build Notes — Delivery Risk Dashboard

Layout reference and build checklist based on the agreed wireframe (hybrid:
ops-manager decision focus + portfolio breadth).

## Layout order (top to bottom)

### 1. Header / filter bar
- Slicers: Region, Shipping mode, Date range
- These should filter every visual below them

### 2. KPI cards (top row, 4 across)
| Card | Metric | Source query |
|---|---|---|
| On-time rate | % | `analysis_queries.sql` #1 |
| Avg delay | days | `analysis_queries.sql` #1 |
| Shipments (30d) | count | rolling filter on `shipments` |
| High-risk shipments | count above risk threshold | `analysis_queries.sql` #6 |

Style note: make the "High-risk shipments" card visually distinct (red background) — this is the card an ops manager glances at first.

### 3. Region heatmap + top risk combinations (side by side)
- Left: filled map or matrix visual, colored by on-time %, from query #2
- Right: table of top 4-5 region + shipping_mode combos by risk_score, from query #6
  - This table is the "so what" of the dashboard — it should read like a to-do list, not just data

### 4. Monthly trend + weather correlation (side by side)
- Left: line chart, on-time % by month, from query #5
- Right: bar chart, delay rate by weather condition, from query #7
  - **Build this panel last** — needs a couple of weeks of weather_log history to be meaningful. Placeholder or "collecting data" note is fine until then.

### 5. Carrier scorecard (bottom, full width)
- Built in Excel first (pivot table: shipping_mode x volume/on-time %/avg delay)
- Bring into Power BI either as a linked image or re-keyed as a table visual

## Build order recommendation
1. KPI cards + region heatmap + top risk table (core decision-making visuals)
2. Monthly trend
3. Excel carrier scorecard
4. Weather correlation (once data has accumulated)

## Before you call it done
- [ ] Every visual responds correctly to the filter bar
- [ ] Risk score definition is documented (link back to README's Key Findings)
- [ ] Colors are consistent: red/amber/green mapped to risk level throughout, not randomly assigned per visual
- [ ] Add a one-line takeaway as a text box under the top risk table — e.g. "LatAm + Standard Class shipments carry the highest risk — consider upgrading shipping mode for this lane"
