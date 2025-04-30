# User Manual for ShopEasy

## Project Overview

ShopEasy is a basic e-commerce web application that allows users to browse products, add them to a cart, view the cart, and simulate a checkout process. It is built using Streamlit for the frontend and Python for the backend. Product data is stored in a `products.json` file, and cart information is managed using Streamlit's session state.

## Features

1.  **Product Catalog:** Displays a list of products with images, descriptions, and prices. Product data is loaded from the `products.json` file.
2.  **Cart Functionality:** Allows users to add products to a cart, view the cart, update quantities, and remove items. The cart data is stored in the Streamlit session state.
3.  **Checkout Simulation:** Implements a mock checkout process that displays a summary of the order and simulates placing the order.
4.  **Search Functionality:** Allows users to search for products by name or description.

## Data Storage

*   `products.json`: Stores product information, including `id`, `name`, `description`, `price`, and `image_url`.
*   Streamlit session state: Stores the user's cart information.

## How to Run

1.  **Install Dependencies:**

    ```bash
    pip install streamlit
    ```

2.  **Run the Application:**

    ```bash
    streamlit run ShopEasy/app.py
    ```

    This command will start the Streamlit application, and you can access it in your web browser.

## Code Snippets

### Loading Products

```python
import streamlit as st
import json

@st.cache_data
def load_products():
    with open("ShopEasy/products.json", "r") as f:
        products = json.load(f)
    return products

products = load_products()
```

### Adding to Cart

```python
def add_to_cart(product_id):
    if product_id in st.session_state['cart']:
        st.session_state['cart'][product_id] += 1
    else:
        st.session_state['cart'][product_id] = 1
    st.success(f"{products[product_id-1]['name']} added to cart!")
```

## Limitations

*   This application does not include real payment processing.
*   It lacks advanced security features.
*   The product data is stored in a static JSON file and is not dynamically updated.
