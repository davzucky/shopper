import boto3


def get_lambda_configuration(lambda_function_name: str, region: str):
    client = boto3.client("lambda", region_name=region)
    return client.get_function_configuration(FunctionName=lambda_function_name)


def lambda_function_check_setup(
    lambda_function_name: str, region: str, lamba_timeout: int
):
    lambda_configuration = get_lambda_configuration(lambda_function_name, region)
    assert lambda_configuration["Runtime"] == "python3.7"
    assert lambda_configuration["Timeout"] == lamba_timeout


def lambda_function_setup_contain_env_var(
    lambda_function_name: str, region: str, env_var: str
):
    lambda_configuration = get_lambda_configuration(lambda_function_name, region)
    assert env_var in lambda_configuration["Environment"]["Variables"]


def lambda_function_check_env_var_value(
    lambda_function_name: str, region: str, env_var: str, value: str
):
    lambda_configuration = get_lambda_configuration(lambda_function_name, region)
    assert value == lambda_configuration["Environment"]["Variables"][env_var]
