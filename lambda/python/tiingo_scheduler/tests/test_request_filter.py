import pytest

from ..handler import Filter, TiingoTicker


@pytest.mark.parametrize(
    "filter_string,filter_result",
    [
        ("{}", Filter()),
        ('{"exchange": "NYSE"}', Filter(exchange="NYSE")),
        ('{"asset_type": "ETF"}', Filter(asset_type="ETF")),
        (
            '{"exchange": "NYSE", "asset_type": "ETF"}',
            Filter(exchange="NYSE", asset_type="ETF"),
        ),
    ],
)
def test_can_deserialize_filter(filter_string: str, filter_result: Filter):
    filter = Filter.from_json(filter_string)
    assert filter == filter_result


@pytest.mark.parametrize(
    "filter,tiingo_ticker,result",
    [
        (Filter(), TiingoTicker("AAPL", "ETF", "USD"), True),
        (Filter(asset_type="STOCK"), TiingoTicker("AAPL", "ETF", "USD"), False),
        (Filter(asset_type="ETF"), TiingoTicker("AAPL", "ETF", "USD"), True),
        (
            Filter(asset_type="ETF", exchange="NYSE"),
            TiingoTicker("AAPL", "ETF", "USD"),
            False,
        ),
        (
            Filter(asset_type="ETF", exchange="NYSE"),
            TiingoTicker("AAPL", "ETF", "USD", exchange="NYSE"),
            True,
        ),
    ],
)
def test_can_filter(filter: Filter, tiingo_ticker: TiingoTicker, result: bool):
    assert filter.filter_out(tiingo_ticker) == result
