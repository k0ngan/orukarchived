import streamlit as st
from utils_store import inject_base_css, load_products, find_product, add_to_cart, price_fmt
st.set_page_config(page_title="Producto — KURO", layout="wide", initial_sidebar_state="collapsed")
inject_base_css()
pid = st.session_state.get("selected_product")
products = load_products()
if pid is None:
    st.warning("No hay producto seleccionado. Volver a la tienda.")
    st.page_link("pages/1_🛍️_Shop.py", label="🛍️ Ir a Shop")
    st.stop()
p = find_product(pid, products)
if not p:
    st.error("Producto no encontrado.")
    st.stop()
left, right = st.columns([2,1])
with left:
    st.image(p["image"], use_container_width=True)
    with st.expander("Detalles de envío y devolución"):
        st.markdown("- Envío nacional 48–72h.\n- Cambios y devoluciones en 10 días.\n- Soporte por DM/Email.")
with right:
    st.markdown(f"### {p['name']}")
    st.caption(p["category"])
    st.markdown(f"<span class='k-accent' style='font-size:22px;'>{price_fmt(p['price'])}</span>", unsafe_allow_html=True)
    st.write(p["desc"])
    size = st.selectbox("Talla", p["sizes"])
    qty = st.number_input("Cantidad", min_value=1, value=1, step=1)
    if st.button("Añadir al Carrito", use_container_width=True):
        add_to_cart({"id":p["id"],"name":p["name"],"price":p["price"],"size":size,"qty":int(qty),"image":p["image"]})
        st.success("Añadido al carrito.")
        st.page_link("pages/3_🛒_Cart.py", label="Ir al Carrito 🛒")
