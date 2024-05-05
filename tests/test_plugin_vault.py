# pylint: skip-file
# ruff: noqa
# mypy: ignore-errors
import json
import logging

import pytest
from opentaskpy.config.loader import ConfigLoader
from pytest_shell import fs

from opentaskpy.plugins.lookup.hashicorp.vault import run
from tests.fixtures.vault import *  # noqa: F403

PLUGIN_NAME = "vault"

# Get the default logger and set it to DEBUG
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def test_vault_plugin_missing_name():
    with pytest.raises(Exception) as ex:
        run()

    assert (
        ex.value.args[0]
        == f"Missing kwarg: 'key' while trying to run lookup plugin '{PLUGIN_NAME}'"
    )


def test_vault_connection_error():
    # Run the test with an invalid vault address
    os.environ["VAULT_ADDR"] = "http://NONEXISTENT:8200"

    with pytest.raises(Exception) as ex:
        run(key="my_test_param")

    assert ex.value.args[0] == "Error connecting to Hashicorp Vault"


def test_vault_plugin_param_name_not_found(vault_service):

    with pytest.raises(FileNotFoundError) as ex:
        run(key="does_not_exist")

    assert ex.value.args[0] == f"Secret not found: does_not_exist"


def test_vault_plugin(vault_service_v1):
    os.environ["VAULT_API_VER"] = "v1"
    expected = "test1234"
    # Populate the vault with a test value
    vault_service_v1.secrets.kv.v1.create_or_update_secret(
        path="some-secret",
        secret=dict(value=expected),
    )

    result = run(key="some-secret")

    assert result == expected

    expected = "mySecretPassword"
    # Insert a new secret, but use a different attribute name
    vault_service_v1.secrets.kv.v1.create_or_update_secret(
        path="some-secret-password",
        secret=dict(password=expected),
    )

    result = run(key="some-secret-password", attribute="password")

    assert result == expected


def test_vault_plugin_v1(vault_service_v1):

    os.environ["VAULT_API_VER"] = "v1"
    expected = "test1234"
    # Populate the vault with a test value
    vault_service_v1.secrets.kv.v1.create_or_update_secret(
        path="some-secret",
        secret=dict(value=expected),
    )

    result = run(key="some-secret")

    assert result == expected

    expected = "mySecretPassword1"
    # Insert a new secret, but use a different attribute name
    vault_service_v1.secrets.kv.v1.create_or_update_secret(
        path="some-secret-password1",
        secret=dict(password=expected),
    )

    result = run(key="some-secret-password1", attribute="password")

    del os.environ["VAULT_API_VER"]
    assert result == expected


def test_vault_lookup_attribute_missing(vault_service_v2):
    os.environ["VAULT_API_VER"] = "v2"
    expected = "test1234"
    # Populate the vault with a test value
    vault_service_v2.secrets.kv.v2.create_or_update_secret(
        path="some-secret",
        secret=dict(value=expected),
    )

    with pytest.raises(FileNotFoundError) as ex:
        run(key="some-secret", attribute="does_not_exist")


def test_config_loader_using_vault_plugin(vault_service_v1, tmpdir):
    os.environ["VAULT_API_VER"] = "v1"
    json_obj = {
        "testLookup": "{{ lookup('hashicorp.vault', key='my_test_secret') }}",
    }

    fs.create_files(
        [
            {
                f"{tmpdir}/variables.json.j2": {
                    "content": json.dumps(json_obj),
                }
            },
        ]
    )
    # Test with a multi line string to make sure that it doesn't break the parser
    expected = """config_loader_test_1234\\nanother_line"""

    vault_service_v1.secrets.kv.v1.create_or_update_secret(
        path="my_test_secret",
        secret=dict(value=expected),
    )

    # Test that the global variables are loaded correctly
    config_loader = ConfigLoader(tmpdir)
    config_loader._load_global_variables()
    config_loader._resolve_templated_variables()

    assert config_loader.get_global_variables()["testLookup"] == expected


def test_config_loader_using_vault_plugin_custom_attribute(vault_service_v1, tmpdir):
    os.environ["VAULT_API_VER"] = "v1"
    json_obj = {
        "testLookup": "{{ lookup('hashicorp.vault', key='my_test_secret', attribute='password' ) }}",
    }

    fs.create_files(
        [
            {
                f"{tmpdir}/variables.json.j2": {
                    "content": json.dumps(json_obj),
                }
            },
        ]
    )
    # Test with a multi line string to make sure that it doesn't break the parser
    expected = """some_random_password"""

    vault_service_v1.secrets.kv.v1.create_or_update_secret(
        path="my_test_secret",
        secret=dict(password=expected),
    )

    # Test that the global variables are loaded correctly
    config_loader = ConfigLoader(tmpdir)
    config_loader._load_global_variables()
    config_loader._resolve_templated_variables()

    assert config_loader.get_global_variables()["testLookup"] == expected
