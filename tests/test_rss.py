from szpont_news.models import FeedDefinition, InformationBias, SourceConfidence
from szpont_news.rss import _classify_headline_bias, _fetch_one_feed


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None

    def read(self) -> bytes:
        return b"""<rss><channel><item>
        <title>Regulator approved bitcoin product</title>
        <link>https://example.com/story</link>
        <pubDate>Fri, 04 Sep 2026 12:30:00 GMT</pubDate>
        </item></channel></rss>"""


def test_parses_rss_item(monkeypatch) -> None:
    monkeypatch.setattr("szpont_news.rss.urlopen", lambda *args, **kwargs: FakeResponse())
    feed = FeedDefinition("Example", "https://example.com/rss", SourceConfidence.REPORTED)

    items = _fetch_one_feed(feed)

    assert items[0].title == "Regulator approved bitcoin product"
    assert items[0].bias == InformationBias.BULLISH
    assert items[0].published_at.isoformat() == "2026-09-04T12:30:00+00:00"


def test_marks_conflicting_headline_terms_as_mixed() -> None:
    bias = _classify_headline_bias("Approval follows exchange hack")

    assert bias == InformationBias.MIXED
