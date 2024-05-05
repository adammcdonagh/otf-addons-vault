"""Hashicorp Vault lookup plugin.

Uses hvac library to pull secrets from Hashicorp Vault.
This uses the VAULT_TOKEN environment variable, or variable to authenticate with Vault.
Required VAULT_ADDR to be specified in the environment or variables.json file
"""

import json
import os

import hvac
import opentaskpy.otflogging
import requests
from opentaskpy.exceptions import LookupPluginError

logger = opentaskpy.otflogging.init_logging(__name__)

plugin_name = "vault"


def run(**kwargs):  # type: ignore[no-untyped-def]
    """Pull a variable from Hashicorp Vault.

    Args:
        **kwargs: Expect a kwarg named key, and attribute. This should be the key within
         Vault to the variable to obtain. The value should be a string. If attribute is
        is not defined, it will default to 'value'.

    Raises:
        LookupPluginError: Returned if the kwarg 'key' is not provided
        FileNotFoundError: Returned if the secret does not exist

    Returns:
        _type_: The value read from Vault
    """
    # Expect a kwarg named key
    expected_kwargs = ["key"]
    for kwarg in expected_kwargs:
        if kwarg not in kwargs:
            raise LookupPluginError(
                f"Missing kwarg: '{kwarg}' while trying to run lookup plugin"
                f" '{plugin_name}'"
            )

    globals_ = kwargs.get("globals", None)

    vault_token = (
        globals_["VAULT_TOKEN"]
        if globals_ and "VAULT_TOKEN" in globals_
        else os.environ.get("VAULT_TOKEN")
    )
    vault_addr = (
        globals_["VAULT_ADDR"]
        if globals_ and "VAULT_ADDR" in globals_
        else os.environ.get("VAULT_ADDR")
    )

    vault_api_version = (
        globals_["VAULT_API_VER"]
        if globals_ and "VAULT_API_VER" in globals_
        else os.environ.get("VAULT_API_VER", "v1")
    )

    result = None
    try:
        client = hvac.Client(
            url=vault_addr,
            token=vault_token,
        )

        # Result will be some JSON, so parse it and if an attribute name is provided
        # return that value, else return the value attribute (if it exists, otherwise
        # raise an error)
        value_attribute = kwargs.get("attribute", "value")

        if vault_api_version == "v1":
            result = client.secrets.kv.v1.read_secret(
                path=kwargs["key"],
            )
            result = result["data"]
        else:
            result = client.secrets.kv.v2.read_secret_version(
                path=kwargs["key"],
            )
            result = result["data"]["data"]

        if value_attribute in result:
            result = result[value_attribute]
        else:
            raise FileNotFoundError(f"Secret not found: {kwargs['key']}")

        logger.log(12, f"Read '{result}' from secret {kwargs['key']}")

    except requests.exceptions.ConnectionError as e:
        logger.error(f"Error connecting to Hashicorp Vault: {e}")
        raise LookupPluginError("Error connecting to Hashicorp Vault")
    except hvac.exceptions.InvalidPath as e:
        logger.error(f"Secret not found: {kwargs['key']}: {e}")
        raise FileNotFoundError(f"Secret not found: {kwargs['key']}")
    except hvac.exceptions.VaultError as e:
        logger.error(f"Error connecting to Hashicorp Vault: {e}")
        raise LookupPluginError("Error connecting to Hashicorp Vault")
    except FileNotFoundError as e:
        logger.error(f"Secret not found: {kwargs['key']}: {e}")
        raise FileNotFoundError(f"Secret not found: {kwargs['key']}")

    except Exception as e:
        logger.error(f"Error reading secret {kwargs['key']}: {e}")
        raise LookupPluginError("Error connecting to Hashicorp Vault")

    # Escape any escape characters so they can be stored in JSON as a string
    if result:
        result = json.dumps(result)
        # Remove the leading and trailing quotes
        result = result[1:-1]

    return result
