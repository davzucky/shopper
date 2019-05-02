from typing import Dict, Any, List

import pytest

from ..message import get_messages_from_records, Message


def test_return_empty_list_when_no_event():
    messages = [msg for msg in get_messages_from_records({})]
    assert len(messages) == 0


@pytest.mark.parametrize(
    "input_dic,output_list",
    [
        (
            {
                "Records": [
                    {
                        "body": '{"ticker": "ticker.test", "file_path": '
                                '"/temp/ticker.test.csv"} '
                    }
                ]
            },
            [Message("ticker.test", "/temp/ticker.test.csv")],
        ),
        (
            {
                "Records": [
                    {
                        "body": '{"ticker": "ticker1.test", "file_path": '
                                '"/temp/ticker1.test.csv"} '
                    },
                    {
                        "body": '{"ticker": "ticker2.test", "file_path": '
                                '"/temp/ticker2.test.csv"} '
                    },
                ]
            },
            [
                Message("ticker1.test", "/temp/ticker1.test.csv"),
                Message("ticker2.test", "/temp/ticker2.test.csv"),
            ],
        ),
    ],
)
def test_input_return_output_data(
    input_dic: Dict[str, Any], output_list: List[Message]
):
    messages = [msg for msg in get_messages_from_records(input_dic)]
    assert len(messages) == len(output_list)
    assert messages == output_list
