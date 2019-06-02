from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class TiingoTicker():
    ticker: str
    exchange: str
    asset_type: str
    price_currency: str
    start_date: str
    end_date: str

def handler(event: Dict[str, Any], context):
    pass