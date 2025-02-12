import os
import re
import shutil

import requests

import pynsee.constants
from pynsee.utils.requests_session import PynseeAPISession


config_file = pynsee.constants.CONFIG_FILE
config_backup = f"{config_file}.back"


def patch_configfile_os_keys(func):
    """
    patch the session with a no-retry policy to speed-up tests intended to get
    http failures
    """

    def wrapper(*args, **kwargs):
        import pynsee.utils._get_credentials

        patched_values = {
            "CONFIG_FILE": "./dummy_config.json",
            "SIRENE_KEY": "DUMMY_SIRENE_KEY",
            "HTTP_PROXY_KEY": "DUMMY_HTTP_PROXY_KEY",
            "HTTPS_PROXY_KEY": "DUMMY_HTTPS_PROXY_KEY",
        }
        init_attrs = {k: getattr(pynsee.constants, k) for k in patched_values}

        for module in [
            pynsee.constants,
            pynsee.utils._get_credentials,
            pynsee.utils.init_connection,
            pynsee.utils.requests_session,
        ]:
            for key, patched in patched_values.items():
                try:
                    getattr(module, key)
                except AttributeError:
                    continue
                setattr(module, key, patched)

        try:
            func(*args, **kwargs)
        except Exception:
            raise
        finally:

            for module in [
                pynsee.constants,
                pynsee.utils._get_credentials,
                pynsee.utils.init_connection,
                pynsee.utils.requests_session,
            ]:
                for key, init in init_attrs.items():
                    try:
                        getattr(module, key)
                    except AttributeError:
                        continue
                    setattr(module, key, init)

            try:
                os.remove(patched_values["CONFIG_FILE"])
            except FileNotFoundError:
                pass

    return wrapper


def patch_retries(func):
    """
    patch the session with a no-retry policy to speed-up tests intended to get
    http failures
    """

    def wrapper(*args, **kwargs):
        init = PynseeAPISession._mount_adapters
        PynseeAPISession._mount_adapters = lambda x: None
        try:
            func(*args, **kwargs)
        except Exception:
            raise
        finally:
            PynseeAPISession._mount_adapters = init

    return wrapper


def patch_test_connections(func):
    """
    patch the session to simulate a valid connection for each API
    """

    def wrapper(*args, **kwargs):
        init = PynseeAPISession._test_connections
        PynseeAPISession._test_connections = lambda x: {}
        try:
            func(*args, **kwargs)
        except Exception:
            raise
        finally:
            PynseeAPISession._test_connections = init

    return wrapper


def patch_test_connections_and_failure_for_sirene(func):
    """
    patch the session to simulate a valid connection for each API except SIRENE
    """

    def wrapper(*args, **kwargs):
        init = PynseeAPISession._request_api_insee

        def _request_api_insee(url, *args, **kwargs):
            if re.match(".*api-sirene.*", url):
                dummy_response = object()
                dummy_response.status_code = 400
                raise requests.exceptions.RequestException(
                    response=dummy_response
                )
            else:

                return

        PynseeAPISession._request_api_insee = _request_api_insee
        try:
            func(*args, **kwargs)
        except Exception:
            raise
        finally:
            PynseeAPISession._request_api_insee = init

    return wrapper


def clean_os_patch(func):
    """
    clean/restore the os variables
    """

    def wrapper(*args, **kwargs):
        keys = (
            "sirene_key",
            "https_proxy",
            "http_proxy",
            "dummy_sirene_key",
            "dummy_https_proxy_key",
            "dummy_http_proxy_key",
        )

        keys = list(keys) + [x.upper() for x in keys]
        init = {k: os.environ[k] for k in keys if k in os.environ}
        for k in init:
            del os.environ[k]
        try:
            func(*args, **kwargs)
        except Exception:
            raise
        finally:
            for k in keys:
                try:
                    del os.environ[k]
                except KeyError:
                    pass
            os.environ.update(init)

    return wrapper


def save_restore_config(func):
    """
    save/restore config.json
    """

    def wrapper(*args, **kwargs):
        # save config
        try:
            shutil.copy(config_file, config_backup)
        except FileNotFoundError:
            pass

        func(*args, **kwargs)

        # restore config
        try:
            shutil.move(config_backup, config_file)
        except FileNotFoundError:
            pass
