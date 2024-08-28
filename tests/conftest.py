#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import timedelta
import hashlib
import os
import warnings

try:
    import requests_cache
except ModuleNotFoundError:
    requests_cache = None

import platformdirs

try:
    import s3fs
except ModuleNotFoundError:
    s3fs = None


def pytest_addoption(parser):
    "Add 2 flags for pytest : --clean-cache and --no-cache"
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

hashed_cache = ""

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


def hash_file(file_path):
    """
    https://gist.github.com/mjohnsullivan/9322154
    Get the MD5 hash value of a file
    :param file_path: path to the file for hash validation
    """
    m = hashlib.md5()
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(1000 * 1000)  # 1MB
            if not chunk:
                break
            m.update(chunk)
    return m.hexdigest()


def pytest_sessionstart(session):
    """
    Add cache to reduce test duration over multiple python version and restore
    artifact from SSP Cloud
    """

    clean_cache = session.config.getoption("--clean-cache")
    no_cache = session.config.getoption("--no-cache")

    if not s3fs and not no_cache:
        warnings.warn(
            "s3fs not present, cannot restore artifacts from SSP Cloud "
            "for current test"
        )
    if not requests_cache and not no_cache:
        warnings.warn(
            "requests-cache not present, http caching will be deactivated "
            "during tests"
        )

    try:
        fs = s3fs.S3FileSystem(
            client_kwargs={"endpoint_url": ENDPOINT_URL}, **KWARGS_S3
        )
        artifact = f"{BUCKET}/{PATH_WITHIN_BUCKET}/{BASE_NAME}"
    except AttributeError:
        pass

    # Clean cache if needed, on local machine and on S3
    if clean_cache:
        # Clean on local machine
        os.unlink(CACHE_NAME)

        # Clean S3 file system
        try:
            fs.rm(artifact)
        except NameError:
            pass

    if no_cache:
        return

    if s3fs and requests_cache:
        try:
            fs.download(artifact, CACHE_NAME)
            global hashed_cache
            hashed_cache = hash_file(CACHE_NAME)
        except FileNotFoundError:
            # No cache found on S3
            pass

    if requests_cache:
        requests_cache.install_cache(
            cache_name=CACHE_NAME, expire_after=timedelta(days=30)
        )


def pytest_sessionfinish(session, exitstatus):
    "Store cached artifact on SSP Cloud's S3 File System"

    upload = False
    try:
        if hashed_cache != hash_file(CACHE_NAME):
            # Upload SQLite only if the current cache has been updated
            upload = True
    except FileNotFoundError:
        # No local cache: either by design using flag (which cleaned local
        # machine on session start) or due to a missing dependency preventing
        # the cache to be created
        pass

    if upload:
        if s3fs:
            fs = s3fs.S3FileSystem(
                client_kwargs={"endpoint_url": ENDPOINT_URL}, **KWARGS_S3
            )
            fs.put(CACHE_NAME, f"{BUCKET}/{PATH_WITHIN_BUCKET}/{BASE_NAME}")

        else:
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
