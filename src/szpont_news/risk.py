from datetime import datetime

from szpont_news.configuration import RadarConfiguration
from szpont_news.models import (
    EventImportance,
    EventRisk,
    InformationBias,
    MarketPrice,
    NewsItem,
    RadarAssessment,
    ScheduledEvent,
    TradingMode,
)


def build_radar_assessment(
    *,
    now: datetime,
    events: tuple[ScheduledEvent, ...],
    news: tuple[NewsItem, ...],
    market_price: MarketPrice,
    configuration: RadarConfiguration | None = None,
) -> RadarAssessment:
    selected_configuration = configuration or RadarConfiguration()
    upcoming_events = _select_upcoming_events(
        events, now, selected_configuration.event_lookahead
    )
    recent_events = _select_recent_events(
        events, now, selected_configuration.event_reaction_window
    )
    recent_news = tuple(
        item
        for item in news
        if now - selected_configuration.recent_news_window
        <= item.published_at
        <= now
    )
    event_risk = _classify_event_risk(
        upcoming_events, now, selected_configuration
    )
    trading_mode = _classify_trading_mode(
        event_risk=event_risk,
        has_recent_high_impact_event=_has_high_impact_event(recent_events),
    )
    information_bias = _combine_information_bias(upcoming_events, recent_news)
    reasons = _build_reasons(
        upcoming_events=upcoming_events,
        recent_events=recent_events,
    )
    return RadarAssessment(
        generated_at=now,
        information_bias=information_bias,
        event_risk=event_risk,
        trading_mode=trading_mode,
        upcoming_events=upcoming_events,
        recent_news=recent_news,
        market_price=market_price,
        reasons=reasons,
    )


def _select_upcoming_events(events, now, lookahead):
    return tuple(sorted(
        (event for event in events if now <= event.starts_at <= now + lookahead),
        key=lambda event: event.starts_at,
    ))


def _select_recent_events(events, now, reaction_window):
    return tuple(
        event for event in events if now - reaction_window <= event.starts_at < now
    )


def _classify_event_risk(upcoming_events, now, configuration):
    if not upcoming_events:
        return EventRisk.LOW
    highest_importance = max(
        upcoming_events,
        key=lambda event: _importance_rank(event.importance),
    ).importance
    critical_is_close = any(
        event.importance == EventImportance.CRITICAL
        and event.starts_at - now <= configuration.critical_event_warning_window
        for event in upcoming_events
    )
    if critical_is_close:
        return EventRisk.CRITICAL
    if highest_importance in (EventImportance.CRITICAL, EventImportance.HIGH):
        return EventRisk.HIGH
    return EventRisk.MEDIUM


def _classify_trading_mode(*, event_risk, has_recent_high_impact_event):
    if has_recent_high_impact_event:
        return TradingMode.WAIT_FOR_REACTION
    if event_risk == EventRisk.CRITICAL:
        return TradingMode.WAIT_FOR_EVENT
    if event_risk in (EventRisk.HIGH, EventRisk.MEDIUM):
        return TradingMode.CAUTION
    return TradingMode.NORMAL


def _combine_information_bias(events, news):
    directional_biases = {
        bias
        for bias in (
            *(event.potential_bias for event in events),
            *(item.bias for item in news),
        )
        if bias not in (InformationBias.UNKNOWN, InformationBias.MIXED)
    }
    contains_mixed = any(
        event.potential_bias == InformationBias.MIXED for event in events
    ) or any(
        item.bias == InformationBias.MIXED for item in news
    )
    if contains_mixed or len(directional_biases) > 1:
        return InformationBias.MIXED
    if directional_biases:
        return directional_biases.pop()
    return InformationBias.UNKNOWN


def _has_high_impact_event(events):
    return any(
        event.importance in (EventImportance.HIGH, EventImportance.CRITICAL)
        for event in events
    )


def _build_reasons(*, upcoming_events, recent_events):
    reasons = []
    if upcoming_events:
        next_event = upcoming_events[0]
        reasons.append(f"next event: {next_event.name}")
    if recent_events:
        reasons.append(f"recent event: {recent_events[-1].name}")
    if not reasons:
        reasons.append("no elevated information risk detected")
    return tuple(reasons)


def _importance_rank(importance):
    return {
        EventImportance.MEDIUM: 1,
        EventImportance.HIGH: 2,
        EventImportance.CRITICAL: 3,
    }[importance]
