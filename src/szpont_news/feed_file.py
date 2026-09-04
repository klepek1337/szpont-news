import json
from pathlib import Path

from szpont_news.models import FeedDefinition, SourceConfidence


def load_feed_definitions(path: Path) -> tuple[FeedDefinition, ...]:
    if not path.exists():
        return ()
    records = json.loads(path.read_text(encoding="utf-8"))
    return tuple(
        FeedDefinition(
            name=str(record["name"]),
            url=str(record["url"]),
            confidence=SourceConfidence(str(record["confidence"])),
        )
        for record in records
    )
