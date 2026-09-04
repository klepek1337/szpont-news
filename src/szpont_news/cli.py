import argparse
from datetime import UTC, datetime
from pathlib import Path

from szpont_news.event_file import load_scheduled_events
from szpont_news.feed_file import load_feed_definitions
from szpont_news.okx import OkxMarketClient
from szpont_news.report import format_radar_report
from szpont_news.risk import build_radar_assessment
from szpont_news.rss import fetch_feed_news
from szpont_news.telegram import send_telegram_message

DEFAULT_EVENT_FILE = Path("config/events.json")
DEFAULT_FEED_FILE = Path("config/feeds.json")
DEFAULT_INSTRUMENT_ID = "BTC-USDT-SWAP"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="szpont-news")
    subparsers = parser.add_subparsers(dest="command", required=True)
    report = subparsers.add_parser("report", help="Build the current event-risk report")
    report.add_argument("--instrument", default=DEFAULT_INSTRUMENT_ID)
    report.add_argument("--events", type=Path, default=DEFAULT_EVENT_FILE)
    report.add_argument("--feeds", type=Path, default=DEFAULT_FEED_FILE)
    report.add_argument("--telegram", action="store_true")
    return parser


def main() -> None:
    arguments = build_parser().parse_args()
    if arguments.command == "report":
        _run_report(arguments)


def _run_report(arguments: argparse.Namespace) -> None:
    now = datetime.now(UTC)
    events = load_scheduled_events(arguments.events)
    news = fetch_feed_news(load_feed_definitions(arguments.feeds))
    market_price = OkxMarketClient().get_market_price(arguments.instrument)
    assessment = build_radar_assessment(
        now=now,
        events=events,
        news=news,
        market_price=market_price,
    )
    report = format_radar_report(assessment)
    print(report)
    if arguments.telegram:
        send_telegram_message(report)
