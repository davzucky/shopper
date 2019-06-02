import os
from dataclass_csv import DataclassReader

from ..handler import TiingoTicker




def test_read_empty_tiingo_ticker(tmpdir):
    filename = os.path.join(tmpdir.dirname, "tiingo_tickers.csv")
    header = "ticker,exchange,assetType,priceCurrency,startDate,endDate"

    with open(filename, "w") as h:
        h.write(header)

    with open(filename) as users_csv:
        reader = DataclassReader(users_csv, User)
        for row in reader:
            print(row)

    assert 1 == 1