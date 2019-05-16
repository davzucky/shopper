import os
import subprocess

import pytest
import toml


def pytest_collection_modifyitems(items):
    for item in items:
        terraform_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "terraform"
        )
        if str(item.fspath).startswith(terraform_path):
            item.add_marker(pytest.mark.terraform_unittest)


def get_git_commit_hash() -> str:
    return (
        subprocess.check_output(["git", "describe", "--always"])
        .decode("utf-8")
        .strip("\n")
    )


@pytest.fixture(scope="session")
def version() -> str:
    full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.toml")
    config = toml.load(full_path)
    base_version = config["version"]
    return "{}.{}".format(base_version, get_git_commit_hash())


@pytest.fixture(scope="session")
def terraform_bin_path() -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "./bin/terraform")
