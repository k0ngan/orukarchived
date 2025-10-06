import streamlit as st
from utils_store import inject_base_css, load_products, price_fmt
st.set_page_config(page_title="Shop — KURO", layout="wide", initial_sidebar_state="expanded")
inject_base_css()
st.markdown("## 🛍️ Shop")
products = load_products()
cats = ["Todos"] + sorted({p["category"] for p in products})
cat = st.sidebar.selectbox("Categoría", cats, index=0)
sizes_all = ["S","M","L","XL","Única"]
size = st.sidebar.multiselect("Talla", sizes_all, default=[])
price_range = st.sidebar.slider("Precio", 0, 50000, (0, 50000), step=1000)
def keep(p):
    if cat!="Todos" and p["category"]!=cat: return False
    if size and not any(s in p["sizes"] for s in size): return False
    if not (price_range[0] <= p["price"] <= price_range[1]): return False
    return True
filtered = [p for p in products if keep(p)]
if not filtered:
    st.info("No hay productos con esos filtros.")
else:
    cols = st.columns(4)
    for i,p in enumerate(filtered):
        with cols[i%4]:
            st.markdown("<div class='k-card'>", unsafe_allow_html=True)
            st.image(p["image"], use_container_width=True)
            st.markdown(f"**{p['name']}**")
            st.caption(p["category"])
            st.markdown(f"<span class='k-accent'>{price_fmt(p['price'])}</span>", unsafe_allow_html=True)
            if st.button("Ver detalle", key=f"shop_go_{p['id']}", use_container_width=True):
                st.session_state["selected_product"] = p["id"]
                st.switch_page("pages/2_👕_Product_Detail.py")
            st.markdown("</div>", unsafe_allow_html=True)
