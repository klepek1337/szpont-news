import json
from pathlib import Path

import pytest

from szpont_news.event_file import load_scheduled_events


def test_loads_timezone_aware_event(tmp_path: Path) -> None:
    path = tmp_path / "events.json"
    path.write_text(json.dumps([{
        "event_id": "cpi",
        "name": "US CPI",
        "starts_at": "2026-09-11T12:30:00Z",
        "importance": "critical",
        "potential_bias": "mixed",
        "source_name": "BLS",
        "source_url": "https://www.bls.gov/",
        "scenarios": []
    }]), encoding="utf-8")

    events = load_scheduled_events(path)

    assert events[0].name == "US CPI"
    assert events[0].starts_at.utcoffset().total_seconds() == 0


def test_rejects_event_without_timezone(tmp_path: Path) -> None:
    path = tmp_path / "events.json"
    path.write_text(json.dumps([{
        "event_id": "cpi",
        "name": "US CPI",
        "starts_at": "2026-09-11T12:30:00",
        "importance": "critical",
        "potential_bias": "mixed",
        "source_name": "BLS",
        "source_url": "https://www.bls.gov/",
        "scenarios": []
    }]), encoding="utf-8")

    with pytest.raises(ValueError, match="timezone"):
        load_scheduled_events(path)
