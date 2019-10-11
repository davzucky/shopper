import os
import subprocess

import pytest
import toml


aws_regions = [
    "eu-west-1",
    "eu-west-2",
    "eu-west-3",
    "eu-central-1",
    "eu-north-1",
    "us-east-2",
    "us-east-1",
    "us-west-1",
    "us-west-2",
]

run_id = 0


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
    full_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "../config.toml"
    )
    config = toml.load(full_path)
    base_version = config["version"]
    return "{}.{}".format(base_version, get_git_commit_hash())


@pytest.fixture(scope="session")
def environment(version) -> str:
    global run_id
    run_id += 1
    environment = version.split(".")[-1]
    return f"{environment}{run_id}"


@pytest.fixture(scope="session")
def aws_region(version) -> str:
    hash_version = hash(version)
    nb_region = len(aws_regions)

    return aws_regions[hash_version % nb_region]


@pytest.fixture(scope="session")
def terraform_bin_path() -> str:
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "../bin/terraform"
    )
