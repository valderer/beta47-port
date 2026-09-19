import copy

import allure
import pytest

from api.pospal_product_api import PospalProductApi


@allure.feature("银豹商品管理")
@allure.story("商品增删改查全流程")
@pytest.mark.product
@pytest.mark.smoke
@pytest.mark.regression
def test_product_crud_flow(
    pospal_product_api,
    pospal_user_id,
    pospal_product_data,
):
    product = pospal_product_data
    created_product_id = None

    with allure.step("新增商品"):
        create_response = pospal_product_api.save_product(product)
        create_data = PospalProductApi.assert_success(create_response)
        created_product_id = create_data.get("productUid")
        assert created_product_id, f"新增成功但未返回 productUid：{create_data}"
        product["id"] = str(created_product_id)

    try:
        with allure.step("查询新增商品"):
            query_response = pospal_product_api.list_products(
                user_id=pospal_user_id,
                keyword=product["barcode"],
            )
            query_data = PospalProductApi.assert_success(query_response)
            assert PospalProductApi.product_in_html(
                query_data.get("contentView", ""),
                product_uid=created_product_id,
                barcode=product["barcode"],
                name=product["name"],
            ), "商品新增后未在列表中查询到"
            product["id"] = PospalProductApi.extract_product_id(
                query_data.get("contentView", ""), created_product_id
            )

        with allure.step("修改商品"):
            updated_product = copy.deepcopy(product)
            updated_product["name"] = f"{product['name']}_已修改"
            updated_product["sellPrice"] = "119"
            update_response = pospal_product_api.save_product(updated_product)
            PospalProductApi.assert_success(update_response)

        with allure.step("查询修改后的商品"):
            query_response = pospal_product_api.list_products(
                user_id=pospal_user_id,
                keyword=product["barcode"],
            )
            query_data = PospalProductApi.assert_success(query_response)
            assert PospalProductApi.product_in_html(
                query_data.get("contentView", ""),
                product_uid=created_product_id,
                barcode=product["barcode"],
                name=updated_product["name"],
            ), "商品修改后查询结果不符合预期"

        with allure.step("删除商品"):
            delete_response = pospal_product_api.delete_product(product["id"])
            PospalProductApi.assert_success(delete_response)

        with allure.step("删除后查询商品"):
            query_response = pospal_product_api.list_products(
                user_id=pospal_user_id,
                keyword=product["barcode"],
            )
            query_data = PospalProductApi.assert_success(query_response)
            assert not PospalProductApi.product_in_html(
                query_data.get("contentView", ""),
                product_uid=created_product_id,
            ), "商品删除后仍能查询到"
            created_product_id = None
    finally:
        if created_product_id:
            # 主流程任一步失败时，尽力清理已经创建的测试商品。
            cleanup_response = pospal_product_api.delete_product(product.get("id", created_product_id))
            assert cleanup_response.status_code == 200, (
                f"测试商品清理失败：product_id={created_product_id}，"
                f"HTTP {cleanup_response.status_code}"
            )
