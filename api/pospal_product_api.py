import json
import re


class PospalProductApi:
    """银豹后台商品增删改查接口封装。"""

    SAVE_PATH = "/Product/SaveProduct"
    LIST_PATH = "/Product/LoadProductsByPage"
    DELETE_PATH = "/Product/DeleteProduct"

    def __init__(self, client):
        self.client = client

    def save_product(self, product):
        return self.client.post(
            self.SAVE_PATH,
            data={"productJson": json.dumps(product, ensure_ascii=False, separators=(",", ":"))},
            headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
        )

    def list_products(
        self,
        user_id,
        keyword="",
        page_index=1,
        page_size=50,
        enable=1,
    ):
        return self.client.post(
            self.LIST_PATH,
            data={
                "groupBySpu": "false",
                "userId": user_id,
                "productbrand": "",
                "categorysJson": "[]",
                "enable": enable,
                "supplierUid": "",
                "productTagUidsJson": "[]",
                "keyword": keyword,
                "categoryType": "",
                "pageIndex": page_index,
                "pageSize": page_size,
                "orderColumn": "",
                "asc": "false",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
        )

    def delete_product(self, product_id, get_sync_stores=True):
        return self.client.post(
            self.DELETE_PATH,
            data={
                "productId": product_id,
                "getSyncStores": str(get_sync_stores).lower(),
            },
            headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
        )

    @staticmethod
    def assert_success(response):
        assert response.status_code == 200, (
            f"银豹商品接口 HTTP 状态异常：{response.status_code}，响应：{response.text[:500]}"
        )
        data = response.json()
        assert data.get("successed") is True, f"银豹商品接口失败：{data}"
        return data

    @staticmethod
    def product_in_html(html, *, product_uid=None, barcode=None, name=None):
        """查询接口返回 HTML 片段，使用行属性和文本做稳定的存在性校验。"""
        if product_uid is not None and f'data-uid="{product_uid}"' not in html:
            return False
        if barcode is not None and str(barcode) not in html:
            return False
        if name is not None and str(name) not in html:
            return False
        return True

    @staticmethod
    def extract_product_id(html, product_uid):
        """从列表行中提取修改/删除接口使用的内部 productId。"""
        match = re.search(
            rf'<tr[^>]*data="([^"]+)"[^>]*data-uid="{re.escape(str(product_uid))}"',
            html,
        )
        assert match, f"列表中未找到 productUid={product_uid} 对应的 productId"
        return match.group(1)
