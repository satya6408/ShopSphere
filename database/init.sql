
CREATE DATABASE IF NOT EXISTS shopsphere;

USE shopsphere;

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    quantity INT NOT NULL
);

CREATE TABLE IF NOT EXISTS cart_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    quantity INT NOT NULL
);

INSERT INTO products (name, price, quantity)
SELECT 'Laptop', 55000, 10
WHERE NOT EXISTS (
    SELECT 1 FROM products WHERE name = 'Laptop'
);

INSERT INTO products (name, price, quantity)
SELECT 'Mobile', 25000, 20
WHERE NOT EXISTS (
    SELECT 1 FROM products WHERE name = 'Mobile'
);
