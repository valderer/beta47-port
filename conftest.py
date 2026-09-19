import os
import copy
import time
from pathlib import Path

import pytest

from common.env_util import load_env_file
from common.request_client import RequestClient
from common.yaml_util import load_yaml
from api.pospal_auth_api import PospalAuthApi
from api.pospal_product_api import PospalProductApi


PROJECT_ROOT = Path(__file__).parent
load_env_file(PROJECT_ROOT / ".env")


@pytest.fixture(scope="session")
def site_client():
    config = load_yaml(PROJECT_ROOT / "config" / "config.yaml")
    return RequestClient(
        base_url=os.environ.get("BASE_URL", config.get("base_url", "")),
        timeout=int(os.environ.get("TEST_TIMEOUT", config.get("timeout", 15))),
    )


@pytest.fixture(scope="session")
def pospal_session(site_client):
    if "pospal.cn" not in site_client.base_url:
        pytest.skip(
            f"BASE_URL 不是银豹环境（当前为 {site_client.base_url}），"
            "请设置 BASE_URL=https://beta47.pospal.cn"
        )
    username = os.environ.get("TEST_USERNAME")
    password = os.environ.get("TEST_PASSWORD")
    if not username or not password:
        pytest.skip("未配置 TEST_USERNAME/TEST_PASSWORD，跳过银豹接口测试")

    response = PospalAuthApi(site_client).sign_in(username, password)
    PospalAuthApi.assert_success(response)
    return site_client


@pytest.fixture
def pospal_product_api(pospal_session):
    return PospalProductApi(pospal_session)


@pytest.fixture
def pospal_user_id():
    user_id = os.environ.get("TEST_USER_ID")
    if not user_id:
        pytest.skip("未配置 TEST_USER_ID，无法调用银豹商品列表接口")
    return user_id


@pytest.fixture
def pospal_product_data():
    product = copy.deepcopy(
        load_yaml(PROJECT_ROOT / "data" / "pospal_product.yaml")["create_product"]
    )
    suffix = str(int(time.time() * 1000))[-10:]
    product.update(
        id="0",
        userId=os.environ.get("TEST_USER_ID", ""),
        barcode=f"99{suffix}",
        name=f"API自动化商品{suffix}",
        pinyin=f"api{suffix[-4:]}",
    )
    return product
