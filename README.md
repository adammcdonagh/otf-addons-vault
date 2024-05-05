[![PyPi](https://img.shields.io/pypi/v/otf-addons-vault.svg)](https://pypi.org/project/otf-addons-vault/)
![unittest status](https://github.com/adammcdonagh/otf-addons-vault/actions/workflows/test.yml/badge.svg)
[![Coverage](https://img.shields.io/codecov/c/github/adammcdonagh/otf-addons-vault.svg)](https://codecov.io/gh/adammcdonagh/otf-addons-vault)
[![License](https://img.shields.io/github/license/adammcdonagh/otf-addons-vault.svg)](https://github.com/adammcdonagh/otf-addons-vault/blob/master/LICENSE)
[![Issues](https://img.shields.io/github/issues/adammcdonagh/otf-addons-vault.svg)](https://github.com/adammcdonagh/otf-addons-vault/issues)
[![Stars](https://img.shields.io/github/stars/adammcdonagh/otf-addons-vault.svg)](https://github.com/adammcdonagh/otf-addons-vault/stargazers)

This repository contains a variable lookup plugins for [Open Task Framework (OTF)](https://github.com/adammcdonagh/open-task-framework) to pull dynamic variables from HashiCorp Vault.

Open Task Framework (OTF) is a Python based framework to make it easy to run predefined file transfers and scripts/commands on remote machines.

# Vault Variables

This package uses `hvac` to communicate with Vault.

Credentials can be set via config using specific named variables alongside the protocol definition, or by using environment variables e.g;

```json
"protocol": {
    "name": "local",
    "VAULT_ADDR": "https://vault.example.com:8200",
    "VAULT_TOKEN": "some_token"
}
```

If these variables are set in the environment, then these will be used if not set elsewhere.

# Vault KV Secrets Engine Version

The default version is v1. This can be overridden by setting the environment variable `VAULT_API_VER` to `v2` (or specifying the variable manually)

# Variable Lookup

Variables can be looked up using the `vault` plugin. This is done using standard Jinja2 syntax e.g;

```json
{
  "name": "my_task",
  "variables": {
    "my_variable": "{{ vault('secret/data/my_secret', key='my_key') }}"
  }
}
```

If not supplied using the `attribute` argument, the default key is `value`. If the key does not exist, the plugin will return an error.

```json
{
  "name": "my_task",
  "variables": {
    "my_variable": "{{ vault('secret/data/my_secret', key='some_key', attribute='password') }}"
  }
}
```
