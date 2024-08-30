#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import timedelta
import hashlib
import os
from pathlib import Path
import warnings
import shutil

try:
    import requests_cache
except ModuleNotFoundError:
    requests_cache = None

import platformdirs

try:
    import py7zr
except ModuleNotFoundError:
    py7zr = None

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
ARCHIVE_NAME = "requests-cache.7z"
CACHE_NAME = os.path.join(CACHE_DIR, BASE_NAME)

BUCKET = "projet-pynsee"
PATH_WITHIN_BUCKET = "artifacts"
ENDPOINT_URL = "https://minio.lab.sspcloud.fr"
ARTIFACT = f"{BUCKET}/{PATH_WITHIN_BUCKET}/{ARCHIVE_NAME}"

hashed_cache = ""

KWARGS_S3 = {}
for ci_key, key in {
    "S3_SECRET": "secret",
    "S3_KEY": "key",
}.items():
    try:
        KWARGS_S3[key] = os.environ[ci_key]
    except KeyError:
        continue

try:
    FS = s3fs.S3FileSystem(
        client_kwargs={"endpoint_url": ENDPOINT_URL}, **KWARGS_S3
    )
except AttributeError:
    pass

# CREDENTIALS_PATH = os.path.join(str(Path.home()), "pynsee_credentials.csv")
# credentials_content = ""


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

    # # Capture initial credentials at session start (if there)
    # global credentials_content
    # try:
    #     with open(CREDENTIALS_PATH, "rb") as f:
    #         credentials_content = f.read()
    # except FileNotFoundError:
    #     pass

    # Clear pynsee appdata if there (only on local machine)
    local_appdata_folder = platformdirs.user_cache_dir()
    insee_folder = os.path.join(local_appdata_folder, "pynsee", "pynsee")
    shutil.rmtree(insee_folder, ignore_errors=True)

    if not s3fs and not no_cache:
        warnings.warn(
            "s3fs not present, cannot restore artifacts from SSP Cloud "
            "for current test"
        )
    if not py7zr and not no_cache:
        warnings.warn(
            "py7zr not present, cannot restore artifacts from SSP Cloud "
            "for current test"
        )
    if not requests_cache and not no_cache:
        warnings.warn(
            "requests-cache not present, http caching will be deactivated "
            "during tests"
        )

    # Clean cache if needed, on local machine and on S3
    if clean_cache:
        # Clean on local machine
        try:
            os.unlink(CACHE_NAME)
        except FileNotFoundError:
            pass

        # Clean S3 file system
        try:
            FS.rm(ARTIFACT)
        except (NameError, FileNotFoundError):
            pass

    if no_cache:
        return

    if s3fs and py7zr and requests_cache:
        try:
            print("trying to restore artifact from SSP Cloud...")
            archive_path = os.path.join(CACHE_DIR, ARCHIVE_NAME)
            FS.download(ARTIFACT, archive_path)
            with py7zr.SevenZipFile(archive_path, "r") as archive:
                archive.extractall(path=CACHE_DIR)
            global hashed_cache
            hashed_cache = hash_file(CACHE_NAME)
        except FileNotFoundError:
            # No cache found on S3
            warnings.warn("No artifact found")
            pass

    if requests_cache:
        requests_cache.install_cache(
            cache_name=CACHE_NAME, expire_after=timedelta(days=30)
        )


def pytest_sessionfinish(session, exitstatus):
    "Store cached artifact on SSP Cloud's S3 File System"

    # global credentials_content
    # if credentials_content:
    #     # Restore credentials
    #     with open(CREDENTIALS_PATH, "wb") as f:
    #         f.write(credentials_content)

    no_cache = session.config.getoption("--no-cache")
    if no_cache:
        return

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
        if not s3fs:
            warnings.warn(
                "s3fs not present, cannot save artifacts to SSP Cloud "
                "from current test"
            )
        if not py7zr:
            warnings.warn(
                "py7zr not present, cannot save artifacts to SSP Cloud "
                "from current test"
            )

        if s3fs and py7zr:
            print("Trying to save current artifact:")

            print("Compressing cache...")
            archive_path = os.path.join(CACHE_DIR, ARCHIVE_NAME)
            with py7zr.SevenZipFile(archive_path, "w") as archive:
                archive.writeall(CACHE_NAME, BASE_NAME)

            print("Uploading artifact...")
            FS.put(archive_path, ARTIFACT)
            os.unlink(archive_path)
            os.unlink(CACHE_NAME)
