from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class InformationBias(StrEnum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class EventImportance(StrEnum):
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EventRisk(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TradingMode(StrEnum):
    NORMAL = "normal"
    CAUTION = "caution"
    WAIT_FOR_EVENT = "wait_for_event"
    WAIT_FOR_REACTION = "wait_for_reaction"


class SourceConfidence(StrEnum):
    CONFIRMED = "confirmed"
    REPORTED = "reported"
    UNCONFIRMED = "unconfirmed"
    INFERENCE = "inference"


@dataclass(frozen=True)
class FeedDefinition:
    name: str
    url: str
    confidence: SourceConfidence


@dataclass(frozen=True)
class ScheduledEvent:
    event_id: str
    name: str
    starts_at: datetime
    importance: EventImportance
    potential_bias: InformationBias
    source_name: str
    source_url: str
    scenarios: tuple[str, ...]


@dataclass(frozen=True)
class NewsItem:
    title: str
    published_at: datetime
    source_name: str
    source_url: str
    confidence: SourceConfidence
    bias: InformationBias


@dataclass(frozen=True)
class MarketMove:
    instrument_id: str
    last_price: float
    four_hour_return: float
    typical_absolute_four_hour_return: float

    @property
    def unusual_move_ratio(self) -> float:
        if self.typical_absolute_four_hour_return == 0:
            return 0.0
        return abs(self.four_hour_return) / self.typical_absolute_four_hour_return


@dataclass(frozen=True)
class RadarAssessment:
    generated_at: datetime
    information_bias: InformationBias
    event_risk: EventRisk
    trading_mode: TradingMode
    upcoming_events: tuple[ScheduledEvent, ...]
    recent_news: tuple[NewsItem, ...]
    market_move: MarketMove
    reasons: tuple[str, ...]
