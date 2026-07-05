# Setting Up the Automated Weather Pull

The `.github/workflows/weather_pull.yml` workflow runs `scripts/02_weather_pull.py`
automatically every day at 06:00 UTC and commits the updated data back to the repo.

## One-time setup

1. Push this repo to GitHub.
2. Go to **Settings → Secrets and variables → Actions → New repository secret**.
3. Add a secret named `OPENWEATHER_API_KEY` with your API key from
   https://openweathermap.org/api (free tier is enough for this project).
4. Go to the **Actions** tab, select "Daily Weather Pull", and click
   **Run workflow** to trigger it manually and confirm it works.
5. After that, it runs automatically every day — no further action needed.

## Why this matters for your portfolio

This is the piece that separates this project from a one-off Kaggle notebook.
Anyone reviewing your GitHub can go to the Actions tab and see the pipeline
actually running on a schedule, with commit history showing the dataset
growing over time. Point this out explicitly in interviews — it's evidence
of a real automated workflow, not just a single script you ran once.

## Troubleshooting

- If the workflow fails with a 401 error, double check the secret name matches
  `OPENWEATHER_API_KEY` exactly (case-sensitive).
- GitHub Actions on a free personal account has generous free minutes for
  public repos — this workflow uses well under a minute per run, so cost is
  not a concern.
