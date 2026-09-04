from datetime import UTC

from szpont_news.configuration import RadarConfiguration
from szpont_news.models import RadarAssessment


def format_radar_report(
    assessment: RadarAssessment,
    configuration: RadarConfiguration | None = None,
) -> str:
    selected_configuration = configuration or RadarConfiguration()
    market_price = assessment.market_price
    lines = [
        "SZPONT NEWS RADAR",
        f"Generated: {assessment.generated_at.astimezone(UTC).isoformat()}",
        f"Instrument: {market_price.instrument_id}",
        "",
        f"Bias: {assessment.information_bias.value.upper()}",
        f"Event risk: {assessment.event_risk.value.upper()}",
        f"Trading mode: {assessment.trading_mode.value.upper()}",
        "",
        "MARKET CONTEXT — DISPLAY ONLY",
        f"Price: {market_price.last_price:,.2f}",
        f"24H change: {_format_optional_percentage(market_price.twenty_four_hour_change)}",
        "",
        "UPCOMING EVENTS",
    ]
    events = assessment.upcoming_events[
        : selected_configuration.maximum_report_events
    ]
    if events:
        for event in events:
            remaining = event.starts_at - assessment.generated_at
            lines.append(
                f"• {event.name} in {_format_duration(remaining)} "
                f"[{event.importance.value.upper()}]"
            )
            lines.extend(f"  - {scenario}" for scenario in event.scenarios)
            lines.append(f"  Source: {event.source_url}")
    else:
        lines.append("• No configured event in the next 24 hours")
    lines.extend(("", "RECENT INFORMATION"))
    news = assessment.recent_news[: selected_configuration.maximum_report_news_items]
    if news:
        for item in news:
            lines.append(
                f"• [{item.confidence.value.upper()}] {item.title} "
                f"({item.bias.value.upper()})"
            )
            lines.append(f"  {item.source_url}")
    else:
        lines.append("• No recent configured information")
    lines.extend(("", "WHY", *(f"• {reason}" for reason in assessment.reasons)))
    return "\n".join(lines)


def _format_duration(duration) -> str:
    total_minutes = max(0, int(duration.total_seconds() // 60))
    hours, minutes = divmod(total_minutes, 60)
    if hours:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def _format_optional_percentage(value: float | None) -> str:
    return f"{value:+.2%}" if value is not None else "not available"
