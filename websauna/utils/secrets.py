"""INI-file basd secrets reading."""
import os
import io

import configparser
from urllib.parse import urlparse

import pkg_resources



_resource_manager = pkg_resources.ResourceManager()


class MissingSecretsEnvironmentVariable(Exception):
    """Thrown when we try to interpolate an environment variable that does not exist."""


def resolve(uri):
    """Resolve secrets location."""

    # Do we look like a relative file (no URL scheme)
    if not "://" in uri:
        uri = "file://" + os.path.abspath(os.path.join(os.getcwd(), uri))

    parts = urlparse(uri)

    assert parts.scheme in ("resource", "file"), "Only resource: supported ATM, got {} in {}".format(include_file, fpname)

    if parts.scheme == "resource":
        package = parts.netloc
        path = parts.path

        assert _resource_manager.resource_exists(pkg_resources.Requirement.parse(package), path), "Could not find {}".format(uri)

        config_source = _resource_manager.resource_stream(pkg_resources.Requirement.parse(package), path)
    else:
        config_source = io.open(parts.path, "rb")

    return config_source



def read_ini_secrets(secrets_file) -> dict:
    """Read plaintext .INI file to pick up secrets.

    Dummy secrets handler which does not have encryption. Reads INI file. Creates dictionary keys in format [ini section name].[ini key name] = value.

    Example INI contents::

        [authentication]
        secret = CHANGEME

        [authomatic]
        # This is a secret seed used in various OAuth related keys
        secret = CHANGEME

    The following ``secrets_file`` formats are supported

    * A path relative to the current working directory, e.g. ``test-secrets.ini``

    * Absolute path using ``file://`` URL: ``file:///etc/myproject/mysecrets.ini``

    * A path relative to deployed Python package. E.g. ``resource://websauna/test-settings.ini``

    :return: ``ConfigParser`` instance.

    """
    secrets = {}

    fp = resolve(secrets_file)
    text = fp.read().decode("utf-8")

    secrets_config = configparser.ConfigParser()
    secrets_config.read_string(text, source=secrets_file)

    for section in secrets_config.sections():
        for key, value in secrets_config.items(section):

            if value.startswith("$"):
                environment_variable = value[1:]
                value = os.getenv(environment_variable, None)
                if not value:
                    raise MissingSecretsEnvironmentVariable("Secrets key {} needs environment variable {} in file {} section {}".format(key, environment_variable, secrets_file, section))

            secrets["{}.{}".format(section, key)] = value

    return secrets

