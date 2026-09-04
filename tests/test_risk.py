from datetime import UTC, datetime, timedelta

from szpont_news.models import (
    EventImportance,
    EventRisk,
    InformationBias,
    MarketMove,
    ScheduledEvent,
    TradingMode,
)
from szpont_news.risk import build_radar_assessment

NOW = datetime(2026, 9, 4, 12, tzinfo=UTC)


def _market_move(current_return: float = 0.01) -> MarketMove:
    return MarketMove("BTC-USDT-SWAP", 82_000, current_return, 0.01)


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
        market_move=_market_move(),
    )

    assert assessment.event_risk == EventRisk.CRITICAL
    assert assessment.trading_mode == TradingMode.WAIT_FOR_EVENT
    assert assessment.information_bias == InformationBias.MIXED


def test_waits_for_reaction_after_event_and_unusual_move() -> None:
    assessment = build_radar_assessment(
        now=NOW,
        events=(_critical_event(NOW - timedelta(minutes=10)),),
        news=(),
        market_move=_market_move(current_return=-0.03),
    )

    assert assessment.trading_mode == TradingMode.WAIT_FOR_REACTION


def test_normal_mode_without_event_or_unusual_move() -> None:
    assessment = build_radar_assessment(
        now=NOW,
        events=(),
        news=(),
        market_move=_market_move(),
    )

    assert assessment.event_risk == EventRisk.LOW
    assert assessment.trading_mode == TradingMode.NORMAL
