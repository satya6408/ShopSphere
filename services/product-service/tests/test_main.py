
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from decimal import Decimal

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
    assert response.json()["status"] == "UP"


def test_get_products():
    connection, cursor = create_mock_db()

    cursor.fetchall.return_value = [
        {
            "id": 1,
            "name": "Laptop",
            "price": Decimal("55000.00"),
            "quantity": 10
        },
        {
            "id": 2,
            "name": "Mobile",
            "price": Decimal("25000.00"),
            "quantity": 20
        }
    ]

    with patch("app.main.get_db_connection", return_value=connection):
        response = client.get("/products")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "Laptop"


def test_get_product():
    connection, cursor = create_mock_db()

    cursor.fetchone.return_value = {
        "id": 1,
        "name": "Laptop",
        "price": Decimal("55000.00"),
        "quantity": 10
    }

    with patch("app.main.get_db_connection", return_value=connection):
        response = client.get("/products/1")

    assert response.status_code == 200
    assert response.json()["name"] == "Laptop"


def test_product_not_found():
    connection, cursor = create_mock_db()

    cursor.fetchone.return_value = None

    with patch("app.main.get_db_connection", return_value=connection):
        response = client.get("/products/999")

    assert response.status_code == 404

