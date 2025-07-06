import decimal
import uuid

import pytest
from httpx import AsyncClient

from tests.factories import products_data


@pytest.mark.usefixtures("products_inserted")
async def test_controller_query_should_filter_by_price(client, products_url):
    response = await client.get(f"{products_url}?min_price=5000&max_price=8000")
    assert response.status_code == 200
    data = response.json()
    assert all(decimal.Decimal(p["price"]) > 5000 and decimal.Decimal(p["price"]) < 8000 for p in data)

async def test_controller_create_should_return_error_on_insertion(monkeypatch, client, products_url):
    async def fake_insert_one(*args, **kwargs):
        raise Exception("erro de banco")
    from store.usecases import product as product_module
    monkeypatch.setattr(product_module.ProductUsecase, "create", lambda self, body: (_ for _ in ()).throw(Exception("erro de banco")))
    response = await client.post(products_url, json=products_data()[0])
    assert response.status_code == 500
    assert "Erro ao inserir" in response.text

async def test_controller_patch_should_return_not_found(client, products_url):
    random_id = str(uuid.uuid4())
    response = await client.patch(f"{products_url}{random_id}", json={"price": "7.000"})
    assert response.status_code == 404
    assert "Produto não encontrado" in response.text

@pytest.mark.usefixtures("product_inserted")
async def test_controller_patch_should_update_updated_at(client, products_url, product_inserted):
    response = await client.patch(f"{products_url}{product_inserted.id}", json={"price": "7.000"})
    assert response.status_code == 200
    data = response.json()
    assert "updated_at" in data
from typing import List

import pytest
from tests.factories import product_data
from fastapi import status


async def test_controller_create_should_return_success(client, products_url):
    response = await client.post(products_url, json=product_data())

    content = response.json()

    del content["created_at"]
    del content["updated_at"]
    del content["id"]

    assert response.status_code == status.HTTP_201_CREATED
    assert content == {
        "name": "Iphone 14 Pro Max",
        "quantity": 10,
        "price": "8.500",
        "status": True,
    }


async def test_controller_get_should_return_success(
    client, products_url, product_inserted
):
    response = await client.get(f"{products_url}{product_inserted.id}")

    content = response.json()

    del content["created_at"]
    del content["updated_at"]

    assert response.status_code == status.HTTP_200_OK
    assert content == {
        "id": str(product_inserted.id),
        "name": "Iphone 14 Pro Max",
        "quantity": 10,
        "price": "8.500",
        "status": True,
    }


async def test_controller_get_should_return_not_found(client, products_url):
    response = await client.get(f"{products_url}4fd7cd35-a3a0-4c1f-a78d-d24aa81e7dca")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "Product not found with filter: 4fd7cd35-a3a0-4c1f-a78d-d24aa81e7dca"
    }


@pytest.mark.usefixtures("products_inserted")
async def test_controller_query_should_return_success(client, products_url):
    response = await client.get(products_url)

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), List)
    assert len(response.json()) > 1


async def test_controller_patch_should_return_success(
    client, products_url, product_inserted
):
    response = await client.patch(
        f"{products_url}{product_inserted.id}", json={"price": "7.500"}
    )

    content = response.json()

    del content["created_at"]
    del content["updated_at"]

    assert response.status_code == status.HTTP_200_OK
    assert content == {
        "id": str(product_inserted.id),
        "name": "Iphone 14 Pro Max",
        "quantity": 10,
        "price": "7.500",
        "status": True,
    }


async def test_controller_delete_should_return_no_content(
    client, products_url, product_inserted
):
    response = await client.delete(f"{products_url}{product_inserted.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT


async def test_controller_delete_should_return_not_found(client, products_url):
    response = await client.delete(
        f"{products_url}4fd7cd35-a3a0-4c1f-a78d-d24aa81e7dca"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "Product not found with filter: 4fd7cd35-a3a0-4c1f-a78d-d24aa81e7dca"
    }
