#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import timedelta
import os
import warnings

try:
    import requests_cache
except ModuleNotFoundError:
    pass
import platformdirs

try:
    import s3fs
except ModuleNotFoundError:
    pass


def pytest_addoption(parser):
    parser.addoption(
        "--clean-cache",
        action="store_true",
        help="remove previous tests' cache",
    )

    parser.addoption(
        "--no-cache",
        action="store_true",
        help="disable cache during tests",
    )


APPNAME = "pynsee-test-http-cache"
CACHE_DIR = platformdirs.user_cache_dir(APPNAME, ensure_exists=True)
BASE_NAME = "requests-cache.sqlite"
CACHE_NAME = os.path.join(CACHE_DIR, BASE_NAME)

BUCKET = "projet-pynsee"
PATH_WITHIN_BUCKET = "artifacts"
ENDPOINT_URL = "https://minio.lab.sspcloud.fr"

KWARGS_S3 = {}
for ci_key, key in {
    "S3_SECRET": "secret",
    "S3_KEY": "key",
}.items():
    try:
        KWARGS_S3[key] = os.environ[ci_key]
    except KeyError as e:
        continue


def pytest_sessionstart(session):
    """
    Add cache to reduce test duration over multiple python version and restore
    artifact from SSP Cloud
    """

    clean_cache = session.config.getoption("--clean-cache")
    if clean_cache:
        # Clean on local machine
        os.unlink(CACHE_NAME)

    no_cache = session.config.getoption("--no-cache")
    if no_cache:
        return

    if not clean_cache:
        try:
            fs = s3fs.S3FileSystem(
                client_kwargs={"endpoint_url": ENDPOINT_URL}, **KWARGS_S3
            )
            artifact = f"{BUCKET}/{PATH_WITHIN_BUCKET}/{BASE_NAME}"
            fs.download(artifact, CACHE_NAME)
        except NameError:
            warnings.warn(
                "s3fs not present, cannot restore artifacts from SSP Cloud "
                "for current test"
            )

    try:
        requests_cache.install_cache(
            cache_name=CACHE_NAME, expire_after=timedelta(days=30)
        )
    except NameError:
        warnings.warn(
            "requests-cache not present, http caching will be deactivated "
            "during tests"
        )


def pytest_sessionfinish(session, exitstatus):
    "Store cached artifact on SSP Cloud's S3 File System"

    try:
        fs = s3fs.S3FileSystem(
            client_kwargs={"endpoint_url": ENDPOINT_URL}, **KWARGS_S3
        )
        fs.put(CACHE_NAME, f"{BUCKET}/{PATH_WITHIN_BUCKET}/{BASE_NAME}")

    except NameError:
        warnings.warn(
            "s3fs not present, cannot save artifacts to SSP Cloud "
            "from current test"
        )


# if __name__ == "__main__":

#     fs = s3fs.S3FileSystem(
#         client_kwargs={"endpoint_url": ENDPOINT_URL}, **KWARGS_S3
#     )
#     path = f"{BUCKET}/{PATH_WITHIN_BUCKET}/**/*"
#     print(fs.glob(path))
