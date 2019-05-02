from dataclasses import dataclass
from typing import Iterable, Dict, Any

from dataclasses_json import DataClassJsonMixin


@dataclass
class LoadDataMessage(DataClassJsonMixin):
    ticker: str
    file_path: str


def get_message(record: Dict[str, Any]) -> LoadDataMessage:
    return LoadDataMessage.from_json(record["body"])


def get_messages_from_records(event: Dict[str, Any]) -> Iterable[LoadDataMessage]:
    if len(event) == 0:
        return

    for record in event["Records"]:
        yield get_message(record)
