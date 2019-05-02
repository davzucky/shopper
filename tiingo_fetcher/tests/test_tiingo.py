import tempfile

from ..handler import get_tiingo_market_data, transform_to_output, save_to_csv_file


def test_transform_input_dict_to_new_format():
    input_dic = {
        "date": "2019-04-08",
        "close": "200.1",
        "high": "200.23",
        "low": "196.34",
        "open": "196.42",
        "volume": "25881697",
        "adjClose": "200.1",
        "adjHigh": "200.23",
        "adjLow": "196.34",
        "adjOpen": "196.42",
        "adjVolume": "25881697",
        "divCash": "0.0",
        "splitFactor": "1.0",
    }
    output_dic = transform_to_output(input_dic)
    expected_result = {
        "date": "2019-04-08",
        "close": "200.1",
        "high": "200.23",
        "low": "196.34",
        "open": "196.42",
        "volume": "25881697",
    }
    assert expected_result == output_dic


def test_write_dict_to_memory_string_csv():
    input_dict = [
        {
            "date": "2019-04-08",
            "close": "200.1",
            "high": "200.23",
            "low": "196.34",
            "open": "196.42",
            "volume": "25881697",
        }
    ]
    temp_file = tempfile.NamedTemporaryFile().name
    csv_path = save_to_csv_file(input_dict, temp_file)
    with open(temp_file, "r") as csv:
        output_str = csv.read()
    expected_str = (
        "date,close,high,low,open,volume\n2019-04-08,200.1,200.23,"
        "196.34,196.42,25881697\n"
    )
    print(csv_path)
    assert output_str == expected_str


def test_call_tiingo():
    prices = get_tiingo_market_data(
        "AAPL", frequency="daily", start_date="2019-4-8", end_date="2019-4-12"
    )
    assert len([p for p in prices]) == 5
