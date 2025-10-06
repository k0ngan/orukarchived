import streamlit as st
from utils_store import inject_base_css, ensure_cart, subtotal_cart, price_fmt, remove_from_cart
st.set_page_config(page_title="Carrito — KURO", layout="wide", initial_sidebar_state="collapsed")
inject_base_css()
st.markdown("## 🛒 Carrito")
cart = ensure_cart()
if not cart:
    st.info("Tu carrito está vacío.")
    st.page_link("pages/1_🛍️_Shop.py", label="Ir a la Tienda 🛍️")
    st.stop()
for idx,it in enumerate(cart):
    c1,c2,c3,c4,c5 = st.columns([1,3,2,1,1])
    with c1: st.image(it["image"], use_container_width=True)
    with c2: st.markdown(f"**{it['name']}**"); st.caption(f"Talla: {it.get('size','–')}")
    with c3: st.markdown(price_fmt(it["price"]))
    with c4:
        qty = st.number_input("Cant.", min_value=1, value=int(it["qty"]), step=1, key=f"qty_{idx}")
        it["qty"] = int(qty)
    with c5:
        if st.button("Eliminar", key=f"del_{idx}"):
            remove_from_cart(idx)
            st.experimental_rerun()
st.markdown("---")
sub = subtotal_cart()
shipping = 2990 if sub < 50000 else 0
total = sub + shipping
c1,c2,c3 = st.columns([2,1,1])
with c2: st.markdown("**Subtotal:** " + price_fmt(sub)); st.markdown("**Envío:** " + (price_fmt(shipping) if shipping else "Gratis"))
with c3: st.markdown("### Total: " + price_fmt(total))
if st.button("Pagar (simulado)", use_container_width=True): st.success("Checkout simulado. Aquí integrarías tu pasarela de pago.")
