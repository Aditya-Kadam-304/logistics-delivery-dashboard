# Interview Prep — Delivery Performance & Delay Risk Dashboard

This document explains every piece of this project: what it does, why it was
built that way, and how to talk about it in an interview. Read it alongside
the actual code — this is the "why", the code is the "what".

---

## 1. The big picture — what problem does this solve?

**Business question:** Which factors (region, carrier, weather, order size)
drive late deliveries, and can we flag high-risk shipments before they ship?

Why this framing matters in an interview: a hiring manager doesn't care that
you can make a bar chart. They care whether you can turn a vague business
worry ("customers keep complaining about late deliveries") into something
measurable and actionable. This project has three components that map to
that:

1. **Diagnose** — historical analysis: where and why are deliveries late?
2. **Enrich** — add an external factor (weather) that's plausibly a cause,
   not just correlated noise.
3. **Act** — a risk score that flags future shipments before they're late,
   not just a rear-view mirror.

If asked "walk me through this project," that three-part structure
(diagnose → enrich → act) is your elevator pitch.

---

## 2. Why PostgreSQL instead of just using Excel or CSV files?

Three reasons, and each is a legitimate interview answer:

- **Scale** — 180K+ rows is workable in Excel but slow and error-prone.
  A database keeps it fast and lets you query subsets instantly.
- **Concurrency / growth** — the weather data grows every single day via
  automation. A relational database is built for data that's continuously
  appended to; a CSV that's opened and edited by hand is not.
- **Industry relevance** — real BI/Data Analyst roles almost always involve
  pulling from a database, not a folder of CSVs. Using PostgreSQL here is a
  direct simulation of what the job actually looks like.

## 3. Why a `.env` file instead of typing the password directly in the script?

This is a security best practice question that comes up often in interviews:
you never hardcode credentials (passwords, API keys) directly into code,
because:
- If you push that code to GitHub, your password/API key becomes public.
- Different environments (your laptop vs. a work server) often need
  different credentials — a `.env` file lets you swap them without touching
  code.

The `.env` file itself is excluded from Git via `.gitignore` — only
`.env.example` (with placeholder values) is committed, so anyone cloning
the repo knows what variables they need without ever seeing your real
credentials.

**Interview soundbite:** "I kept credentials out of source control using
environment variables — a basic security practice, but one a lot of
beginner projects skip."

---

## 4. Step 1 — Data cleaning (`scripts/01_clean_data.py`)

### What it does, line by line logic (not literal code, the *reasoning*):

1. **Load the raw CSV with `latin-1` encoding** — this dataset is known to
   break with standard UTF-8 encoding because of how it was originally
   exported. Recognizing and handling encoding issues is itself a real
   data-cleaning skill worth mentioning in an interview — it's the kind of
   unglamorous problem that "about 80% of real analyst work" (as one of the
   articles I found put it) actually looks like.

2. **Standardize column names** — raw datasets almost never have
   consistent, code-friendly column names (e.g., `Days for shipping (real)`
   becomes `days_for_shipping_real`). This step lowercases everything,
   replaces spaces with underscores, and strips special characters. Why it
   matters: consistent naming prevents bugs later (SQL and Python are both
   case-sensitive in different ways) and makes the whole pipeline more
   maintainable.

3. **Define "late delivery"** — this is the single most important
   judgment call in the whole project:
   ```
   is_late = 1 if days_for_shipping_real > days_for_shipment_scheduled else 0
   delay_days = max(0, days_for_shipping_real - days_for_shipment_scheduled)
   ```
   In plain English: a shipment is late if it took longer to actually ship
   than what was originally scheduled/promised. `delay_days` measures *how*
   late, clipped at zero so on-time or early shipments don't get a negative
   delay value.

   **Why this is worth explaining carefully in an interview:** every
   analytics project has a "definitions" moment like this, and hiring
   managers specifically listen for whether you understand *why* you chose
   a definition, not just that you picked one. Be ready to say: "I could
   have used the dataset's built-in `late_delivery_risk` flag instead, but
   I chose to calculate it myself from the two day-count columns so I could
   also measure *how late* — degree of lateness, not just a yes/no."

4. **Column selection** — trimming the dataset down to only the columns
   actually needed for analysis. This isn't just tidiness — in a real job,
   loading unnecessary columns into a production database wastes storage
   and slows every query down.

### Interview Q&A for this step:
- *"Why not just use the pandas `.dropna()` to handle missing data?"* →
  Because blindly dropping rows can silently bias your analysis (e.g., if
  a whole region has more missing values, dropping them under-represents
  that region). Explain you'd inspect null patterns before deciding how to
  handle them (this is a good thing to actually go do once you have the
  real dataset in front of you, and note your approach in the README).

---

## 5. Step 2 — The weather pipeline (`scripts/02_weather_pull.py`)

### What it does:
- Defines a fixed dictionary of hub cities and their lat/long coordinates.
- Calls the OpenWeatherMap API once per city, extracting temperature,
  condition (e.g., "Rain", "Clear"), wind speed, and humidity.
- Appends the results to a growing CSV log (`weather_log.csv`), with a
  UTC timestamp for when the data was pulled.

### Why an API instead of another static dataset?
This is the differentiator question, and you should have a sharp answer:
static Kaggle datasets are downloaded once and never change — they don't
demonstrate that you can build something that keeps working over time. An
API pull, especially one that's automated (see the next section), shows you
can build a live data pipeline — closer to what a company's actual BI stack
looks like (dashboards refreshing from live data sources, not one-off
exports).

### Why append instead of overwrite?
Because the whole point is to build up a time series. If the script
overwrote the file every day, you'd only ever have "today's weather" — you'd
never be able to analyze whether rain on a given day correlated with delays
on that day. Appending, with a timestamp column, is what turns this into
usable historical data.

### Why timestamps in UTC?
Standardizing on UTC avoids bugs from timezone confusion — especially
relevant here since your hub cities span multiple timezones. **This is a
good detail to mention in an interview** — it shows attention to a subtle
but common real-world data bug.

---

## 6. Step 3 — Automation (`.github/workflows/weather_pull.yml`)

### What it does:
A GitHub Actions "workflow" file — essentially a recipe that GitHub runs on
a schedule (every day at 06:00 UTC) in a temporary virtual machine. It:
1. Checks out your repository code.
2. Installs Python and your project's dependencies.
3. Runs `02_weather_pull.py`, using your OpenWeatherMap key stored securely
   as a GitHub "secret" (never exposed in the code or logs).
4. Commits the updated `weather_log.csv` back into your repository.

### Why this matters more than it might seem:
This is genuinely the hardest-to-fake part of a junior portfolio, because
it requires you to understand:
- **Scheduling** (`cron` syntax) — the `"0 6 * * *"` line means "at minute 0
  of hour 6, every day."
- **Secrets management** — never hardcoding a key even in a private repo.
- **CI/CD concepts** — GitHub Actions is the same technology (conceptually)
  used for deploying real production software. Being able to say "I've used
  GitHub Actions" in an interview, even for something small, signals you
  understand automation beyond just writing a script and running it
  manually.

**Interview soundbite:** "I automated the data collection with GitHub
Actions rather than running the script manually — it's the same CI/CD
pattern used in production data pipelines, just scaled down."

---

## 7. Step 4 — Loading into PostgreSQL (`scripts/03_load_to_postgres.py`)

### What it does:
Uses `pandas.to_sql()` (via SQLAlchemy) to push the cleaned CSV data into
PostgreSQL tables. The shipments table is fully *replaced* each time you
re-run the cleaning step (since it's a static historical dataset), while
the weather table is *appended* to, matching the growing nature of that
data.

### Why SQLAlchemy instead of writing raw `INSERT` statements?
SQLAlchemy handles a lot of tedious, error-prone work for you — matching
pandas data types to PostgreSQL column types, batching inserts efficiently,
and managing the connection safely. Writing raw INSERT statements for
180K rows by hand would be slow and fragile.

---

## 8. Step 5 — SQL analysis (`sql/analysis_queries.sql`)

Walk through each query's *purpose*, not just its syntax — this is what
interviewers actually probe:

| Query | Business purpose |
|---|---|
| #1 Overall on-time rate | The headline KPI — "how are we doing overall?" |
| #2 By region | "Where is the problem concentrated?" |
| #3 By shipping mode | "Is this a carrier/service-level problem?" |
| #4 By category | "Are certain product types harder to ship on time?" |
| #5 Monthly trend | "Is this getting better or worse over time?" |
| #6 Risk score | "Which specific combinations should we act on first?" |
| #7 Weather correlation | "Is weather actually a contributing cause?" |

### The risk score formula, explained:
```sql
risk_score = (late_pct * 0.7) + (avg_delay_days * 10 * 0.3)
```
This is a **weighted composite metric** — a very common real-world BI
pattern. It combines two different signals (how *often* something is late,
and how *badly* late it tends to be) into one sortable number, weighted
70/30 toward frequency. 

**Be ready to defend this weighting in an interview** — a good answer is:
"I weighted frequency higher than severity because a shipment that's late
50% of the time but only by half a day is a more systemic operational
problem than one that's rarely late but occasionally very delayed. That's a
judgment call, and a different business might reasonably weight it the
other way — for instance, a company shipping perishable goods might weight
severity much higher."

This is exactly the kind of "I made a judgment call and can defend it"
answer that separates a real analyst from someone who just ran a tutorial.

### Why `HAVING COUNT(*) > 30` in the risk score query?
This filters out combinations with very few shipments, which would
otherwise produce misleadingly extreme risk scores (e.g., 1 shipment that
happened to be late = "100% late rate" but tells you nothing statistically
meaningful). This is a basic but important data-quality safeguard —
mentioning it shows statistical awareness.

---

## 9. Step 6 — The Power BI dashboard

Refer to `POWERBI_BUILD_NOTES.md` for the layout. In the interview, explain
the *design philosophy*, not just the visuals:

- **KPI cards up top** — decision-makers scan top-down; the most important
  numbers go first.
- **Risk table, not just a heatmap** — a heatmap shows *where* the problem
  is, but a ranked table of specific combinations tells someone exactly
  *what to do next*. This is the difference between a report and a
  decision-support tool.
- **Weather panel built last** — a practical, honest detail: you sequenced
  the build around a real constraint (needing time for the automated data
  to accumulate), rather than pretending everything was built in one pass.

---

## 10. Anticipated interview questions (and how to answer them)

**"Why logistics as your domain?"**
Germany's logistics sector (DHL, Kuehne+Nagel, DB Schenker) is huge, and
most portfolios default to e-commerce or finance — this differentiates you
while still being immediately relevant to local employers.

**"What was the hardest part of this project?"**
A strong honest answer: defining "late delivery" precisely, and building
the weighted risk score — both required making a judgment call with no
single right answer, and being able to justify the choice.

**"What would you do differently with more time?"**
Good answers: validate the risk-score weighting against real stakeholder
input rather than picking weights yourself; add a simple forecasting model
to predict risk for *future* shipments rather than just scoring historical
ones; expand the weather correlation with more granular, hourly data.

**"How is this different from a Kaggle notebook?"**
It has a live, automated data pipeline (GitHub Actions), a real database
(not a CSV loaded in-memory), and it ends in a decision-support artifact
(the risk table) rather than just an analysis.

---

## A second investigation — the July 2016 "improvement" that wasn't

The monthly trend chart showed a dip in late deliveries in July 2016 — at
first glance, a nice story ("performance improved that month"). Rather than
report it as a win, it was investigated by breaking the same time window
down by region and by shipping mode, comparing July against the surrounding
June/August baseline.

The region breakdown revealed the real explanation: **every region except
four US regions had zero shipments recorded in July 2016**, compared to
normal volume in the baseline months. International data was simply missing
for that month — the apparent improvement was an artifact of the dataset
skewing toward only US shipments (which happened to have somewhat better
performance), not a genuine operational change.

**How to tell this story in an interview:**

> "My trend chart showed a dip in late deliveries in one particular month,
> which looked like a positive result at first. Before reporting it as an
> improvement, I broke that month down by region and shipping mode compared
> to the months around it, and found that almost every non-US region had
> zero recorded shipments that month — it was a data gap, not a real
> performance change. I flagged it as a data quality limitation rather than
> a finding, since presenting it as an improvement would have been
> misleading."

This is genuinely one of the best things to lead with when asked about your
analytical process — it shows the habit of verifying a surprising result
before trusting it, which is exactly what real analyst work requires and
what junior candidates often skip.

## Real finding from this project — and how to talk about it

Once real data was loaded, the numbers surfaced something genuinely
interesting: First Class shipments showed a 100% late rate. Rather than
report that at face value, it was investigated further — a query against
the raw scheduled vs. actual shipping days showed all 27,814 First Class
orders are scheduled for 1 day but consistently take 2 days, with zero
variance. That's not inconsistent fulfillment — it's a scheduling promise
that was never achievable in the first place.

**This is one of the best things to talk about in an interview**, because
it demonstrates something more valuable than "I ran a query" — it shows
you don't take a surprising number at face value, you dig into *why* it's
surprising before drawing a conclusion. A good way to tell this story:

> "One of my metrics showed First Class shipments were late 100% of the
> time, which seemed too extreme to be a real operational pattern. I dug
> into the underlying scheduled-vs-actual shipping days and found every
> single First Class order was promised a 1-day delivery window but
> consistently took 2 days — completely uniform, no exceptions. That told
> me the problem wasn't fulfillment performance, it was an unrealistic SLA
> baked into how that tier was set up. So my recommendation split into two
> tracks: renegotiate the First Class SLA, and separately focus operational
> attention on the shipping-mode/region combinations that showed genuine,
> variable delay — like Second Class to Central Asia."

Full findings are documented in the README's Key Findings section — keep
that updated as you explore further in Power BI.
