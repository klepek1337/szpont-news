from datetime import UTC, datetime, timedelta

from szpont_news.models import (
    EventImportance,
    EventRisk,
    InformationBias,
    MarketPrice,
    ScheduledEvent,
    TradingMode,
)
from szpont_news.risk import build_radar_assessment

NOW = datetime(2026, 9, 4, 12, tzinfo=UTC)


def _market_price() -> MarketPrice:
    return MarketPrice("BTC-USDT-SWAP", 82_000, 0.01)


def _critical_event(starts_at: datetime) -> ScheduledEvent:
    return ScheduledEvent(
        event_id="nfp",
        name="US Nonfarm Payrolls",
        starts_at=starts_at,
        importance=EventImportance.CRITICAL,
        potential_bias=InformationBias.MIXED,
        source_name="BLS",
        source_url="https://www.bls.gov/",
        scenarios=("hot data can pressure risk assets",),
    )


def test_waits_for_critical_event_inside_warning_window() -> None:
    assessment = build_radar_assessment(
        now=NOW,
        events=(_critical_event(NOW + timedelta(minutes=30)),),
        news=(),
        market_price=_market_price(),
    )

    assert assessment.event_risk == EventRisk.CRITICAL
    assert assessment.trading_mode == TradingMode.WAIT_FOR_EVENT
    assert assessment.information_bias == InformationBias.MIXED


def test_waits_for_reaction_after_recent_critical_event() -> None:
    assessment = build_radar_assessment(
        now=NOW,
        events=(_critical_event(NOW - timedelta(minutes=10)),),
        news=(),
        market_price=_market_price(),
    )

    assert assessment.trading_mode == TradingMode.WAIT_FOR_REACTION


def test_normal_mode_without_information_risk() -> None:
    assessment = build_radar_assessment(
        now=NOW,
        events=(),
        news=(),
        market_price=_market_price(),
    )

    assert assessment.event_risk == EventRisk.LOW
    assert assessment.trading_mode == TradingMode.NORMAL
