
import os
import mysql.connector
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="ShopSphere Cart Service")


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        database=os.getenv("MYSQL_DATABASE", "shopsphere"),
        user=os.getenv("MYSQL_USER", "shopsphere_user"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        connection_timeout=5
    )


class CartItem(BaseModel):
    product_id: int
    product_name: str
    price: float
    quantity: int


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/cart")
def get_cart():
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, product_id, product_name, price, quantity
            FROM cart_items
        """)

        items = cursor.fetchall()

        total_items = sum(item["quantity"] for item in items)
        total_price = sum(
            float(item["price"]) * item["quantity"]
            for item in items
        )

        for item in items:
            item["price"] = float(item["price"])

        return {
            "items": items,
            "total_items": total_items,
            "total_price": round(total_price, 2)
        }

    except mysql.connector.Error as error:
        raise HTTPException(status_code=503, detail=str(error))

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


@app.post("/cart", status_code=201)
def add_to_cart(item: CartItem):
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO cart_items
            (product_id, product_name, price, quantity)
            VALUES (%s, %s, %s, %s)
        """, (
            item.product_id,
            item.product_name,
            item.price,
            item.quantity
        ))

        connection.commit()

        return {
            "message": "Product added to cart",
            "cart_item_id": cursor.lastrowid
        }

    except mysql.connector.Error as error:
        raise HTTPException(status_code=503, detail=str(error))

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


@app.put("/cart/{product_id}")
def update_cart(product_id: int, quantity: int):
    if quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero"
        )

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE cart_items
            SET quantity = %s
            WHERE product_id = %s
        """, (quantity, product_id))

        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Product not found in cart"
            )

        return {"message": "Cart updated successfully"}

    except mysql.connector.Error as error:
        raise HTTPException(status_code=503, detail=str(error))

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM cart_items
            WHERE product_id = %s
        """, (product_id,))

        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Product not found in cart"
            )

        return {"message": "Product removed from cart"}

    except mysql.connector.Error as error:
        raise HTTPException(status_code=503, detail=str(error))

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

