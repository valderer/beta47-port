import os
from pathlib import Path

import pytest

from common.env_util import load_env_file
from common.request_client import RequestClient
from common.yaml_util import load_yaml


PROJECT_ROOT = Path(__file__).parent
load_env_file(PROJECT_ROOT / ".env")


@pytest.fixture(scope="session")
def site_client():
    config = load_yaml(PROJECT_ROOT / "config" / "config.yaml")
    return RequestClient(
        base_url=os.environ.get("BASE_URL", config.get("base_url", "")),
        timeout=int(os.environ.get("TEST_TIMEOUT", config.get("timeout", 15))),
    )
