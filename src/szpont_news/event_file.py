import json
from datetime import UTC, datetime
from pathlib import Path

from szpont_news.models import EventImportance, InformationBias, ScheduledEvent


def load_scheduled_events(path: Path) -> tuple[ScheduledEvent, ...]:
    if not path.exists():
        return ()
    records = json.loads(path.read_text(encoding="utf-8"))
    return tuple(_event_from_record(record) for record in records)


def _event_from_record(record: dict[str, object]) -> ScheduledEvent:
    return ScheduledEvent(
        event_id=str(record["event_id"]),
        name=str(record["name"]),
        starts_at=_parse_utc_timestamp(str(record["starts_at"])),
        importance=EventImportance(str(record["importance"])),
        potential_bias=InformationBias(str(record["potential_bias"])),
        source_name=str(record["source_name"]),
        source_url=str(record["source_url"]),
        scenarios=tuple(str(value) for value in record.get("scenarios", [])),
    )


def _parse_utc_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("event timestamp must include a timezone")
    return parsed.astimezone(UTC)
