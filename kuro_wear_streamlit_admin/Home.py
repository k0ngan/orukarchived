import streamlit as st
from utils_store import inject_base_css, load_products, price_fmt
st.set_page_config(page_title="ORUK", layout="wide", initial_sidebar_state="collapsed")
inject_base_css()
st.markdown("""<div class=\"k-hero\"><h1 style=\"margin:0; font-size:42px; letter-spacing:-0.02em;\">KURO <span class=\"k-accent\">WEAR</span></h1><p style=\"margin-top:6px; color:#cbd5e1;\">Streetwear oscuro, minimalista y técnico.</p></div>""", unsafe_allow_html=True)
c1,c2,c3,c4 = st.columns([1,1,1,1])
with c1: st.page_link("Home.py", label="🏠 Home", use_container_width=True)
with c2: st.page_link("pages/1_🛍️_Shop.py", label="🛍️ Shop", use_container_width=True)
with c3: st.page_link("pages/3_🛒_Cart.py", label="🛒 Cart", use_container_width=True)
with c4: st.page_link("pages/0_🧩_Admin.py", label="🧩 Admin", use_container_width=True)
st.markdown("---")

prods = load_products()[:4]
cols = st.columns(4)
for i,p in enumerate(prods):
    with cols[i%4]:
        st.markdown("<div class='k-card'>", unsafe_allow_html=True)
        st.image(p["image"], use_container_width=True)
        st.markdown(f"**{p['name']}**")
        st.caption(p["category"])
        st.markdown(f"<span class='k-accent'>{price_fmt(p['price'])}</span>", unsafe_allow_html=True)
        if st.button("Ver producto", key=f"home_go_{p['id']}", use_container_width=True):
            st.session_state["selected_product"] = p["id"]
            st.switch_page("pages/2_👕_Product_Detail.py")
        st.markdown("</div>", unsafe_allow_html=True)
