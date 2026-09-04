import pytest

from szpont_news.configuration import RadarConfiguration
from szpont_news.okx import OkxMarketClient


class FakeOkxMarketClient(OkxMarketClient):
    def _get_json(self, path: str) -> dict[str, object]:
        assert "bar=4H" in path
        return {
            "code": "0",
            "data": [
                _candle("103", confirmed="0"),
                _candle("102"),
                _candle("100"),
                _candle("99"),
                _candle("98"),
            ],
        }


def _candle(close: str, confirmed: str = "1") -> list[str]:
    return ["0", close, close, close, close, "0", "0", "0", confirmed]


def test_ignores_open_candle_and_measures_latest_closed_move() -> None:
    configuration = RadarConfiguration(typical_return_sample_size=2)

    move = FakeOkxMarketClient().get_four_hour_market_move(
        "BTC-USDT-SWAP", configuration
    )

    assert move.last_price == 102
    assert move.four_hour_return == pytest.approx(0.02)
    assert move.typical_absolute_four_hour_return > 0
