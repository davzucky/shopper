import os
from typing import Dict

import pytest
import python_terraform as terraform

full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "terraform")


@pytest.fixture(scope="session", autouse=True)
def setup_terraform(version, terraform_bin_path):
    tf = terraform.Terraform(
        working_dir=full_path, terraform_bin_path=terraform_bin_path
    )

    tiingo_tickers_csv = "static/tiingo_tickers.csv"
    tf.init()
    ret_code, out, err = tf.apply(
        skip_plan=True,
        var={"module_version": version, "tiingo_tickers_path": tiingo_tickers_csv},
    )

    if ret_code != 0:
        print(err)
        ret_code, out, err = tf.destroy(
            var={"module_version": version, "tiingo_tickers_path": tiingo_tickers_csv}
        )
        raise Exception("Error applying terraform. Error \n {}".format(err))

    yield

    ret_code, out, err = tf.destroy(
        var={"module_version": version, "tiingo_tickers_path": tiingo_tickers_csv}
    )

    if ret_code != 0:
        print(err)
        raise Exception("Error detroying terraform. Error \n {}".format(err))


@pytest.fixture()
def terraform_output(setup_terraform, terraform_bin_path) -> Dict[str, Dict[str, str]]:
    tf = terraform.Terraform(
        working_dir=full_path, terraform_bin_path=terraform_bin_path
    )
    outputs = tf.output()
    if outputs is not None:
        return outputs

    raise Exception("Cannot retrieve the outputs")
