import os

import pytest


def pytest_collection_modifyitems(items):
    for item in items:
        terraform_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "terraform"
        )
        if str(item.fspath).startswith(terraform_path):
            item.add_marker(pytest.mark.terraform_unittest)
