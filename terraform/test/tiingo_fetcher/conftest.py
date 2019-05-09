import os
from typing import Dict

import pytest
import python_terraform as terraform


full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "terraform")
tf = terraform.Terraform(working_dir=full_path)


@pytest.fixture(scope="session", autouse=True)
def setup_terraform():
    tf.init()
    ret_code, out, err = tf.apply(
        skip_plan=True,
        var={
            "module_version": "0.1.81f4b54",
            "tiingo_api_key": os.environ.get("TIINGO_API_KEY"),
        },
    )

    if ret_code != 0:
        print(err)
        raise Exception("Error applying terraform. Error \n {}".format(err))
    # yield
    # tf.destroy(skip_plan=True, var={'module_version': '0.1.81f4b54',
    #                               'tiingo_api_key': '51a96da20f20137299ac9511b8adb5f1fcfbca94'})


@pytest.fixture()
def terraform_output(setup_terraform) -> Dict[str, Dict[str, str]]:
    outputs = tf.output()
    if outputs is not None:
        return outputs

    raise Exception("Cannot retrieve the outputs")
