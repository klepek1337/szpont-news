import pytest

from szpont_news.okx import OkxMarketClient


class FakeOkxMarketClient(OkxMarketClient):
    def _get_json(self, path: str) -> dict[str, object]:
        assert "ticker" in path
        return {
            "code": "0",
            "data": [{"last": "82", "open24h": "80"}],
        }


def test_reads_ticker_without_requesting_candles() -> None:
    market_price = FakeOkxMarketClient().get_market_price("BTC-USDT-SWAP")

    assert market_price.last_price == 82
    assert market_price.twenty_four_hour_change == pytest.approx(0.025)
