import streamlit as st
import json

# Load product data from JSON file
@st.cache_data
def load_products():
    with open("ShopEasy/products.json", "r") as f:
        products = json.load(f)
    return products

products = load_products()

# Initialize cart in session state
if 'cart' not in st.session_state:
    st.session_state['cart'] = {}

# Function to add item to cart
def add_to_cart(product_id):
    if product_id in st.session_state['cart']:
        st.session_state['cart'][product_id] += 1
    else:
        st.session_state['cart'][product_id] = 1
    st.success(f"{products[product_id-1]['name']} added to cart!")

# Function to remove item from cart
def remove_from_cart(product_id):
    if product_id in st.session_state['cart']:
        del st.session_state['cart'][product_id]
    st.rerun()

# Function to update quantity in cart
def update_quantity(product_id, quantity):
    if quantity > 0:
        st.session_state['cart'][product_id] = quantity
    else:
        remove_from_cart(product_id)
    st.rerun()

# Main application
st.title("ShopEasy")

# Product catalog
st.header("Product Catalog")
product_search = st.text_input("Search for products")

filtered_products = products
if product_search:
    filtered_products = [p for p in products if product_search.lower() in p['name'].lower() or product_search.lower() in p['description'].lower()]

if not filtered_products:
    st.write("No products found matching your search.")
else:
    for product in filtered_products:
        col1, col2, col3 = st.columns([1,2,1])
        with col1:
            st.image(product['image_url'], width=100)
        with col2:
            st.subheader(product['name'])
            st.write(product['description'])
            st.write(f"Price: ${product['price']}")
        with col3:
            st.button("Add to Cart", key=f"add_{product['id']}", on_click=lambda product_id=product['id']: add_to_cart(product_id))

# Shopping cart
st.header("Shopping Cart")

if st.session_state['cart']:
    cart_items = st.session_state['cart']
    total_price = 0
    for product_id, quantity in cart_items.items():
        product = next(p for p in products if p['id'] == product_id)
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col1:
            st.write(product['name'])
        with col2:
            num_quantity = st.number_input(label="Quantity", min_value=1, max_value=10, value=quantity, key=f"quantity_{product_id}", on_change=lambda product_id=product_id: update_quantity(product_id, int(st.session_state[f"quantity_{product_id}"])))
        with col3:
            st.write(f"Price: ${product['price'] * quantity}")
        with col4:
            st.button("Remove", key=f"remove_{product_id}", on_click=lambda product_id=product_id: remove_from_cart(product_id))
        total_price += product['price'] * quantity

    st.subheader(f"Total: ${total_price}")

    if st.button("Checkout"):
        st.success("Order placed successfully!")
        st.write("Thank you for your purchase!")
        st.session_state['cart'] = {}  # Clear the cart after checkout
else:
    st.write("Your cart is empty.")
