import datetime

from bloomberg.bloomberg import (
    get_bloomberg_ticker_market_data,
    BloombergFundMarketData,
    BloombergMarketDataError,
)


UNKNOWN_SAMPLE_DATA = {"securityType": "UNKNOWN"}
FUND_SAMPLE_DATA = {
    "id": "JPMPCAA:HK",
    "fundType": "Open-End Fund",
    "fundObjective": "Conservative Allocation",
    "fundAssetClassFocus": "Mixed Allocation",
    "fundGeographicFocus": "North American Region",
    "totalReturn1Year": -2.594618,
    "totalReturnYtd": 4.767293,
    "name": "JPMorgan Provident Capital Fund",
    "price": 240.64,
    "issuedCurrency": "HKD",
    "priceChange1Day": 0.14,
    "percentChange1Day": 0.05821206,
    "priceMinDecimals": 2,
    "nyTradeStartTime": "01:00:00.000",
    "nyTradeEndTime": "23:59:00.000",
    "timeZoneOffset": -4,
    "lastUpdateEpoch": "1552453170",
    "lowPrice52Week": 229.09,
    "highPrice52Week": 247.27,
}


def set_request_mock_unknown_ticker(requests_mock, ticker: str):
    requests_mock.register_uri(
        "GET",
        "https://www.bloomberg.com/markets/api/security/basic/{}".format(ticker),
        json=UNKNOWN_SAMPLE_DATA,
        status_code=304,
    )


def set_request_mock_valid_data(requests_mock, ticker: str):
    fund_data = FUND_SAMPLE_DATA.copy()
    fund_data["id"] = ticker
    requests_mock.register_uri(
        "GET",
        "https://www.bloomberg.com/markets/api/security/basic/{}".format(ticker),
        json=fund_data,
        status_code=200,
    )


def test_when_ticker_valid_ticker_return_fund_object(requests_mock):
    ticker = "JPMPCAA:HK"
    set_request_mock_valid_data(requests_mock, ticker)

    return_value = get_bloomberg_ticker_market_data(ticker)
    assert type(return_value) == BloombergFundMarketData
    assert return_value.status_code == 200
    assert return_value.price == 240.64
    assert return_value.open == 240.64
    assert return_value.high == 240.64
    assert return_value.low == 240.64
    assert return_value.close == 240.64
    assert return_value.date == datetime.date(2019, 3, 13)


def test_when_ticker_not_valid_return_unknow(requests_mock):
    ticker = "UNKNOW"
    set_request_mock_unknown_ticker(requests_mock, ticker)

    return_value = get_bloomberg_ticker_market_data(ticker)

    assert type(return_value) == BloombergMarketDataError
    assert return_value.status_code == 304

    assert return_value.error == '{"securityType": "UNKNOWN"}'
