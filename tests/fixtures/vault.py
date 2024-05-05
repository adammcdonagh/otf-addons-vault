# pylint: skip-file
# ruff: noqa
# mypy: ignore-errors
import os

import hvac
import pytest

VAULT_TOKEN = "root"
VAULT_PORT = 8200


def github_actions() -> bool:
    if os.getenv("GITHUB_ACTIONS"):
        return True
    return False


@pytest.fixture(scope="session")
def root_dir() -> str:
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "test",
    )


@pytest.fixture(scope="session")
def root_dir_tests() -> str:
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "tests",
    )


@pytest.fixture(scope="session")
def docker_compose_files(root_dir, root_dir_tests) -> list[str]:
    """Get the docker-compose.yml absolute path."""
    return [
        f"{root_dir_tests}/docker-compose.yml",
    ]


@pytest.fixture(scope="session")
def vault_service(docker_services) -> hvac.Client:

    docker_services.start("vault")
    port = docker_services.port_for("vault", VAULT_PORT)
    address = f"http://{docker_services.docker_ip}:{port}"

    # Insert a dummy secret into vault
    client = hvac.Client(
        url=address,
        token=VAULT_TOKEN,
    )
    create_response = client.secrets.kv.v2.create_or_update_secret(
        path="my-secret-password",
        secret=dict(password="Hashi123"),
    )

    assert not create_response["warnings"]

    # Export environment variables
    os.environ["VAULT_ADDR"] = address
    os.environ["VAULT_TOKEN"] = VAULT_TOKEN

    return client


@pytest.fixture(scope="session")
def vault_token(vault) -> str:
    return VAULT_TOKEN
