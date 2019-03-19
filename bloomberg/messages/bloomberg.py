from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin


@dataclass
class BloombergMessage(DataClassJsonMixin):
    ticker: str
    file_path: str
