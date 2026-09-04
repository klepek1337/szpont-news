from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from szpont_news.models import FeedDefinition, InformationBias, NewsItem

RSS_TIMEOUT_SECONDS = 15
HTTP_USER_AGENT = "szpont-news/0.1 (+https://github.com/klepek1337/szpont-news)"
BULLISH_HEADLINE_TERMS = (
    "approval",
    "approved",
    "ceasefire",
    "rate cut",
    "inflows",
    "stimulus",
)
BEARISH_HEADLINE_TERMS = (
    "attack",
    "exploit",
    "hack",
    "outflows",
    "rate hike",
    "sanctions",
    "shutdown",
)


def fetch_feed_news(feeds: tuple[FeedDefinition, ...]) -> tuple[NewsItem, ...]:
    items = []
    for feed in feeds:
        items.extend(_fetch_one_feed(feed))
    return tuple(sorted(items, key=lambda item: item.published_at, reverse=True))


def _fetch_one_feed(feed: FeedDefinition) -> list[NewsItem]:
    request = Request(feed.url, headers={"User-Agent": HTTP_USER_AGENT})
    with urlopen(request, timeout=RSS_TIMEOUT_SECONDS) as response:
        document = ElementTree.fromstring(response.read())
    return [
        NewsItem(
            title=title,
            published_at=published_at,
            source_name=feed.name,
            source_url=link,
            confidence=feed.confidence,
            bias=_classify_headline_bias(title),
        )
        for element in _entry_elements(document)
        if (title := _entry_title(element))
        and (link := _entry_link(element))
        and (published_at := _entry_timestamp(element)) is not None
    ]


def _entry_elements(document: ElementTree.Element) -> list[ElementTree.Element]:
    rss_items = document.findall("./channel/item")
    if rss_items:
        return rss_items
    return document.findall("{*}entry")


def _entry_title(element: ElementTree.Element) -> str:
    node = _find_first_element(element, "title", "{*}title")
    return (node.text or "").strip() if node is not None else ""


def _entry_link(element: ElementTree.Element) -> str:
    node = _find_first_element(element, "link", "{*}link")
    if node is None:
        return ""
    return (node.text or node.attrib.get("href", "")).strip()


def _find_first_element(
    parent: ElementTree.Element, *names: str
) -> ElementTree.Element | None:
    for name in names:
        node = parent.find(name)
        if node is not None:
            return node
    return None


def _entry_timestamp(element: ElementTree.Element) -> datetime | None:
    for name in ("pubDate", "{*}published", "{*}updated"):
        node = element.find(name)
        if node is not None and node.text:
            return _parse_feed_timestamp(node.text.strip())
    return None


def _parse_feed_timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        parsed = parsedate_to_datetime(value)
    if parsed.tzinfo is None:
        raise ValueError("feed timestamp must include a timezone")
    return parsed.astimezone(UTC)


def _classify_headline_bias(title: str) -> InformationBias:
    normalized_title = title.casefold()
    bullish = any(term in normalized_title for term in BULLISH_HEADLINE_TERMS)
    bearish = any(term in normalized_title for term in BEARISH_HEADLINE_TERMS)
    if bullish and bearish:
        return InformationBias.MIXED
    if bullish:
        return InformationBias.BULLISH
    if bearish:
        return InformationBias.BEARISH
    return InformationBias.UNKNOWN
