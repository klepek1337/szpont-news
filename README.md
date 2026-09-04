# Szpont News

Auditable macro, geopolitical, and crypto event-risk radar. It explains what
happened, what important events are approaching, and whether opening a new trade
deserves normal conditions, caution, or a temporary wait.

Szpont News does not place orders and does not claim that temporal correlation
proves why a market moved.

## Stage 1

- fetches closed 4H BTC candles from the public OKX API;
- compares the latest move with typical recent 4H volatility;
- reads a timezone-aware event calendar from JSON;
- reads configured official, geopolitical, and crypto RSS feeds;
- classifies `BIAS`, `EVENT RISK`, and `TRADING MODE` separately;
- prints an evidence-linked report and can send it to Telegram;
- installs a Windows Scheduled Task running every four hours.

The first stage deliberately uses a reviewed event file. RSS headlines are fetched
automatically, but their keyword bias is only a transparent heuristic. Automatic
official calendar ingestion will be added through separate source adapters, so a
broken third-party scraper cannot silently invent or omit a critical event.

## Install on Windows

```powershell
git clone https://github.com/klepek1337/szpont-news.git
cd szpont-news
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup.ps1
Copy-Item .\config\events.example.json .\config\events.json -Force
Copy-Item .\config\feeds.example.json .\config\feeds.json -Force
```

Set the same Telegram credentials used by Szpont:

```powershell
[Environment]::SetEnvironmentVariable("SZPONT_TELEGRAM_BOT_TOKEN", "YOUR_TOKEN", "User")
[Environment]::SetEnvironmentVariable("SZPONT_TELEGRAM_CHAT_ID", "YOUR_CHAT_ID", "User")
```

Open a new PowerShell window, then test:

```powershell
.\scripts\run-radar.ps1
```

Install the four-hour schedule:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install-radar-task.ps1
```

## Event format

Every timestamp must include a timezone. Store UTC with a `Z` suffix when possible.
Every event must link to its source and describe conditional scenarios instead of
pretending that its result is known in advance.

```json
{
  "event_id": "us-nfp-2026-09",
  "name": "US Nonfarm Payrolls",
  "starts_at": "2026-09-04T12:30:00Z",
  "importance": "critical",
  "potential_bias": "mixed",
  "source_name": "US Bureau of Labor Statistics",
  "source_url": "https://www.bls.gov/schedule/news_release/empsit.htm",
  "scenarios": [
    "Stronger employment can pressure crypto through higher rate expectations",
    "Weaker employment can support crypto unless recession risk dominates"
  ]
}
```

## Trust model

- `CONFIRMED`: official publication or multiple reliable sources;
- `REPORTED`: one reliable source;
- `UNCONFIRMED`: not independently verified;
- `INFERENCE`: interpretation rather than a confirmed causal claim.

The radar is decision support, not investment advice.

## Development

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
```
