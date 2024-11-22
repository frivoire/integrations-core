# -*- coding: utf-8 -*-

# (C) Datadog, Inc. 2024-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
import subprocess
import sys
from pathlib import Path
from typing import Any  # noqa: F401

import pytest

from datadog_checks.base import AgentCheck

PATH_TO_EMBEDDED = str(Path(__file__).resolve().parent.parent.parent / "fixtures" / "fips" / "embedded")


@pytest.fixture(scope="session", autouse=True)
def create_fipsmodule_config():
    command = [
        "openssl",
        "fipsinstall",
        "-module",
        f'{PATH_TO_EMBEDDED}/lib/ossl-modules/fips.so',
        "-out",
        f'{PATH_TO_EMBEDDED}/ssl/fipsmodule.cnf',
        "-provider_name",
        "fips",
    ]

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError:
        pytest.exit("Failed to set up FIPS mode. Exiting tests.", returncode=1)
    yield
    # subprocess.run(["rm", f'{PATH_TO_EMBEDDED}/ssl/fipsmodule.cnf'], check=True)


@pytest.fixture(scope="function")
def clean_environment():
    AgentCheck().disable_openssl_fips()
    yield


@pytest.mark.skipif(not sys.platform == "linux", reason="only testing on Linux")
def test_md5_before_fips():
    import ssl

    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.set_ciphers("MD5")
    assert True


@pytest.mark.skipif(not sys.platform == "linux", reason="only testing on Linux")
def test_md5_after_fips(clean_environment):
    import ssl

    AgentCheck().enable_openssl_fips(path_to_embedded=PATH_TO_EMBEDDED)
    with pytest.raises(ssl.SSLError, match='No cipher can be selected.'):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.set_ciphers("MD5")


@pytest.mark.skipif(not sys.platform == "linux", reason="only testing on Linux")
def test_cryptography_md5_cryptography():
    from cryptography.hazmat.primitives import hashes

    hashes.Hash(hashes.MD5())


@pytest.mark.skipif(not sys.platform == "linux", reason="only testing on Linux")
def test_cryptography_md5_fips():
    from cryptography.exceptions import InternalError
    from cryptography.hazmat.primitives import hashes

    AgentCheck().enable_cryptography_fips(path_to_embedded=PATH_TO_EMBEDDED)
    with pytest.raises(InternalError, match='Unknown OpenSSL error.'):
        hashes.Hash(hashes.MD5())
