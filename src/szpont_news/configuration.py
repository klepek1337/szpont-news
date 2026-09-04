from dataclasses import dataclass
from datetime import timedelta


@dataclass(frozen=True)
class RadarConfiguration:
    event_lookahead: timedelta = timedelta(hours=24)
    critical_event_warning_window: timedelta = timedelta(hours=4)
    event_reaction_window: timedelta = timedelta(minutes=30)
    recent_news_window: timedelta = timedelta(hours=4)
    unusual_move_multiple: float = 2.0
    typical_return_sample_size: int = 30
    okx_candle_limit: int = 32
    maximum_report_news_items: int = 5
    maximum_report_events: int = 5
