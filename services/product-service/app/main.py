
import os
import mysql.connector

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI(
    title="ShopSphere Product Service",
    description="Product management microservice",
    version="1.0.0"
)


# MySQL database connection
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        database=os.getenv("MYSQL_DATABASE", "shopsphere"),
        user=os.getenv("MYSQL_USER", "shopsphere_user"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        connection_timeout=5
    )


# Product request model
class Product(BaseModel):
    name: str
    price: float
    quantity: int


# Health API
@app.get("/health")
def health():
    return {
        "status": "UP",
        "service": "product-service"
    }


# Get all products
@app.get("/products")
def get_products():
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT id, name, price, quantity FROM products ORDER BY id"
        )

        products = cursor.fetchall()

        for product in products:
            product["price"] = float(product["price"])

        return products

    except mysql.connector.Error:
        raise HTTPException(
            status_code=503,
            detail="Unable to connect to product database"
        )

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


# Get product by ID
@app.get("/products/{product_id}")
def get_product(product_id: int):
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT id, name, price, quantity FROM products WHERE id = %s",
            (product_id,)
        )

        product = cursor.fetchone()

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        product["price"] = float(product["price"])

        return product

    except mysql.connector.Error:
        raise HTTPException(
            status_code=503,
            detail="Unable to connect to product database"
        )

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


# Add new product
@app.post("/products", status_code=201)
def add_product(product: Product):
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
            INSERT INTO products (name, price, quantity)
            VALUES (%s, %s, %s)
        """

        values = (
            product.name,
            product.price,
            product.quantity
        )

        cursor.execute(query, values)
        connection.commit()

        return {
            "id": cursor.lastrowid,
            **product.model_dump()
        }

    except mysql.connector.Error:
        if connection and connection.is_connected():
            connection.rollback()

        raise HTTPException(
            status_code=503,
            detail="Unable to save product to database"
        )

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

