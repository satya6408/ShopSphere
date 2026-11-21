
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from app.main import app

client = TestClient(app)


def create_mock_db():
    connection = MagicMock()
    cursor = MagicMock()

    connection.cursor.return_value = cursor
    connection.is_connected.return_value = True

    return connection, cursor


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_get_cart():
    connection, cursor = create_mock_db()

    cursor.fetchall.return_value = [
        {
            "id": 1,
            "product_id": 1,
            "product_name": "Laptop",
            "price": 55000.00,
            "quantity": 2
        }
    ]

    with patch("app.main.get_db_connection", return_value=connection):
        response = client.get("/cart")

    assert response.status_code == 200
    assert response.json()["total_items"] == 2
    assert response.json()["total_price"] == 110000.00


def test_add_to_cart():
    connection, cursor = create_mock_db()
    cursor.lastrowid = 1

    payload = {
        "product_id": 1,
        "product_name": "Laptop",
        "price": 55000,
        "quantity": 2
    }

    with patch("app.main.get_db_connection", return_value=connection):
        response = client.post("/cart", json=payload)

    assert response.status_code == 201
    assert response.json()["message"] == "Product added to cart"
    connection.commit.assert_called_once()


def test_update_cart():
    connection, cursor = create_mock_db()
    cursor.rowcount = 1

    with patch("app.main.get_db_connection", return_value=connection):
        response = client.put("/cart/1?quantity=3")

    assert response.status_code == 200
    assert response.json()["message"] == "Cart updated successfully"


def test_remove_from_cart():
    connection, cursor = create_mock_db()
    cursor.rowcount = 1

    with patch("app.main.get_db_connection", return_value=connection):
        response = client.delete("/cart/1")

    assert response.status_code == 200
    assert response.json()["message"] == "Product removed from cart"


def test_update_cart_not_found():
    connection, cursor = create_mock_db()
    cursor.rowcount = 0

    with patch("app.main.get_db_connection", return_value=connection):
        response = client.put("/cart/999?quantity=3")

    assert response.status_code == 404

