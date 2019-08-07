import os

import daiquiri

logger = daiquiri.getLogger(__name__)


def get_env_variable(env_var_name: str):
    variable = os.environ.get(env_var_name, None)
    if variable is None:
        logger.error(f"The environment variable {env_var_name} is not set.")
        raise ReferenceError(f"The environment variable {env_var_name} is not set.")

    return variable


def get_env_variable_or_default(env_var_name: str, default: str):
    return os.environ.get(env_var_name, default)
