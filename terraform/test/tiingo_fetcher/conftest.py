import os
from typing import Dict

import pytest
from python_terraform import Terraform

full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "terraform")


@pytest.fixture(scope="module", autouse=True)
def setup_terraform(version, environment, aws_region, terraform_bin_path):
    print(f"deploy test to region {aws_region}")
    tf = Terraform(working_dir=full_path, terraform_bin_path=terraform_bin_path)
    var_tf = {
        "module_version": version,
        "tiingo_api_key": os.environ.get("TIINGO_API_KEY"),
        "aws_region": aws_region,
        "environment": environment,
    }

    tf.init()
    ret_code, out, err = tf.apply(skip_plan=True, var=var_tf)

    if ret_code != 0:
        print(err)
        ret_code, out, err = tf.destroy(var=var_tf)
        raise Exception("Error applying terraform. Error \n {}".format(err))

    yield

    ret_code, out, err = tf.destroy(var=var_tf)

    if ret_code != 0:
        print(err)
        raise Exception("Error detroying terraform. Error \n {}".format(err))


@pytest.fixture()
def terraform_output(setup_terraform, terraform_bin_path) -> Dict[str, Dict[str, str]]:
    tf = Terraform(working_dir=full_path, terraform_bin_path=terraform_bin_path)
    outputs = tf.output()
    if outputs is not None:
        return outputs

    raise Exception("Cannot retrieve the outputs")
