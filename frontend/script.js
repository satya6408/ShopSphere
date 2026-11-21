
const API = {
    products: "/api/products",
    cart: "/api/cart"
};

// Load products from Product Service
async function loadProducts() {
    const container = document.getElementById("product-list");

    try {
        const response = await fetch(API.products);

        if (!response.ok) {
            throw new Error("Unable to load products");
        }

        const products = await response.json();

        container.innerHTML = "";

        products.forEach(product => {
            const card = document.createElement("div");
            card.className = "product-card";

            card.innerHTML = `
                <h3>${product.name}</h3>
                <p>Price: ₹${product.price}</p>
                <p>Available: ${product.quantity}</p>
                <button>Add to Cart</button>
            `;

            card.querySelector("button").addEventListener("click", () => {
                addToCart(product);
            });

            container.appendChild(card);
        });

    } catch (error) {
        container.textContent = error.message;
    }
}

// Add product to Cart Service
async function addToCart(product) {
    try {
        const response = await fetch(API.cart, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                product_id: product.id,
                product_name: product.name,
                price: product.price,
                quantity: 1
            })
        });

        if (!response.ok) {
            throw new Error("Unable to add product to cart");
        }

        await loadCart();
        alert("Product added to cart!");

    } catch (error) {
        alert(error.message);
    }
}

// Load cart from Cart Service
async function loadCart() {
    const container = document.getElementById("cart-items");
    const totalElement = document.getElementById("cart-total");

    try {
        const response = await fetch(API.cart);

        if (!response.ok) {
            throw new Error("Unable to load cart");
        }

        const cart = await response.json();

        container.innerHTML = "";

        if (cart.items.length === 0) {
            container.textContent = "Your cart is empty.";
        }

        cart.items.forEach(item => {
            const div = document.createElement("div");
            div.className = "cart-item";

            div.innerHTML = `
                <span>
                    ${item.product_name} -
                    ₹${item.price} × ${item.quantity}
                </span>
                <button>Remove</button>
            `;

            div.querySelector("button").addEventListener("click", () => {
                removeFromCart(item.product_id);
            });

            container.appendChild(div);
        });

        totalElement.textContent = `Total: ₹${cart.total_price}`;

    } catch (error) {
        container.textContent = error.message;
    }
}

// Remove product from cart
async function removeFromCart(productId) {
    try {
        const response = await fetch(`${API.cart}/${productId}`, {
            method: "DELETE"
        });

        if (!response.ok) {
            throw new Error("Unable to remove product");
        }

        await loadCart();

    } catch (error) {
        alert(error.message);
    }
}

// Initialize application
loadProducts();
loadCart();

