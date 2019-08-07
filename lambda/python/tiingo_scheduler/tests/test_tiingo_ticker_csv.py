import os

import pytest

from ..handler import get_tiingo_tickers


@pytest.mark.parametrize(
    "file_content,nb_rows",
    [
        ("", 0),
        (
            "000001,SHE,Stock,CNY,2007-08-30,2019-05-30\n000002,SHE,Stock,CNY,"
            "2000-01-04,2019-05-30",
            2,
        ),
        ("000001,SHE,Stock,CNY,2007-08-30,2019-05-30\n000003,SHE,Stock,CNY,,\n", 2),
    ],
)
def test_read_empty_tiingo_ticker(tmpdir, file_content: str, nb_rows: int):
    filename = os.path.join(tmpdir.dirname, "tiingo_tickers.csv")
    header = "ticker,exchange,assetType,priceCurrency,startDate,endDate"

    with open(filename, "w") as h:
        h.write(f"{header}\n{file_content}")

    tickers = [t for t in get_tiingo_tickers(filename)]

    assert len(tickers) == nb_rows
