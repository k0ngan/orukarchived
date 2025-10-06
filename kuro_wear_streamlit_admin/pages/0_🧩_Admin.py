import os, json
import streamlit as st
from utils_store import inject_base_css, load_products, save_products, price_fmt, save_image_file
st.set_page_config(page_title="Admin — KURO", layout="wide", initial_sidebar_state="collapsed")
inject_base_css()
st.markdown("## 🧩 Admin")
ADMIN_PIN = os.environ.get("ADMIN_PIN", "kuroadmin")
if not st.session_state.get("pin_ok"):
    with st.form("pin_form"):
        pin = st.text_input("PIN de administrador", type="password")
        if st.form_submit_button("Entrar"):
            if pin == ADMIN_PIN:
                st.session_state["pin_ok"] = True
                st.rerun()
            else:
                st.error("PIN incorrecto.")
    st.stop()
st.success("Acceso admin concedido.")
products = load_products()
st.markdown("### Sincronización con GitHub")

# Carga secretos
gh_cfg = st.secrets.get("github", {})
TOKEN  = gh_cfg.get("token") or os.environ.get("GITHUB_TOKEN")
REPO   = gh_cfg.get("repo")  or os.environ.get("GITHUB_REPO")
BRANCH = gh_cfg.get("branch", "main")
BASE   = gh_cfg.get("base_path", "")

if not TOKEN or not REPO:
    st.warning("Configura github.token y github.repo en Secrets para habilitar la sincronización.")
else:
    gh = GitHubSync(TOKEN, REPO, BRANCH, BASE)

    col1, col2, col3 = st.columns([1,1,2])
    with col1:
        if st.button("⬆️ Subir products.json", use_container_width=True):
            try:
                gh.sync_products_json("data/products.json", "data/products.json")
                st.success("products.json sincronizado.")
            except Exception as e:
                st.error(f"Error: {e}")

    with col2:
        if st.button("⬆️ Subir imágenes", use_container_width=True):
            try:
                n = gh.sync_folder_images("data/images", "data/images")
                st.success(f"Imágenes sincronizadas: {len(n)} archivo(s).")
            except Exception as e:
                st.error(f"Error: {e}")

    with col3:
        if st.button("⬆️ Subir todo (JSON + imágenes)", use_container_width=True):
            try:
                gh.sync_products_json("data/products.json", "data/products.json")
                n = gh.sync_folder_images("data/images", "data/images")
                st.success(f"Todo sincronizado. Imágenes: {len(n)}")
            except Exception as e:
                st.error(f"Error: {e}")
st.markdown("### Crear producto")
with st.form("new_product"):
    c1,c2 = st.columns(2)
    with c1:
        nid = st.text_input("ID", placeholder="KW-NEW-011")
        name = st.text_input("Nombre")
        category = st.text_input("Categoría", value="Camisetas")
        price = st.number_input("Precio", min_value=0, step=500)
        sizes = st.text_input("Tallas (coma)", value="S,M,L,XL")
    with c2:
        desc = st.text_area("Descripción", height=100)
        file = st.file_uploader("Imagen (JPG/PNG)", type=["jpg","jpeg","png","webp"])
        aspect = st.selectbox("Proporción", ["Original","1:1","4:5","16:9"])
        width = st.number_input("Ancho final (px)", min_value=0, value=800, step=10)
        quality = st.slider("Calidad JPG", 60, 100, 90)
    if st.form_submit_button("Crear"):
        if not nid or not name or not category or price<=0:
            st.error("Completa ID, Nombre, Categoría y Precio.")
        else:
            img_path = ""
            if file is not None:
                ow = width if width>0 else None
                if aspect=="1:1":
                    img_path = save_image_file(file, out_w=ow or 800, out_h=ow or 800, crop="center", fmt="JPEG", quality=quality)
                elif aspect=="4:5":
                    img_path = save_image_file(file, out_w=800, out_h=1000, crop="center", fmt="JPEG", quality=quality)
                elif aspect=="16:9":
                    img_path = save_image_file(file, out_w=1280, out_h=720, crop="center", fmt="JPEG", quality=quality)
                else:
                    img_path = save_image_file(file, out_w=ow or None, out_h=None, crop="center", fmt="JPEG", quality=quality)
            products.append({"id":nid.strip(),"name":name.strip(),"price":int(price),"category":category.strip(),"sizes":[s.strip() for s in sizes.split(",") if s.strip()],"image":img_path or "","desc":desc.strip()})
            save_products(products)
            st.success("Producto creado.")
st.markdown("---")
st.markdown("### Editar productos")
if not products:
    st.info("No hay productos.")
else:
    for idx,p in enumerate(products):
        with st.expander(f"{p.get('name','')} ({p.get('id','')})"):
            c1,c2 = st.columns([3,2])
            with c1:
                name = st.text_input("Nombre", value=p.get("name",""), key=f"name_{idx}")
                category = st.text_input("Categoría", value=p.get("category",""), key=f"cat_{idx}")
                price = st.number_input("Precio", min_value=0, value=int(p.get("price",0)), step=500, key=f"price_{idx}")
                sizes = st.text_input("Tallas (coma)", value=",".join(p.get("sizes",[])), key=f"sizes_{idx}")
                desc = st.text_area("Descripción", value=p.get("desc",""), height=100, key=f"desc_{idx}")
                if st.button("Guardar cambios", key=f"save_{idx}"):
                    p["name"]=name.strip(); p["category"]=category.strip(); p["price"]=int(price); p["sizes"]=[s.strip() for s in sizes.split(",") if s.strip()]; p["desc"]=desc.strip(); save_products(products); st.success("Cambios guardados.")
            with c2:
                if p.get("image"): st.image(p["image"], use_container_width=True, caption="Imagen actual")
                upload = st.file_uploader("Reemplazar imagen", type=["jpg","jpeg","png","webp"], key=f"file_{idx}")
                aspect = st.selectbox("Proporción", ["Original","1:1","4:5","16:9"], key=f"asp_{idx}")
                width = st.number_input("Ancho final (px)", min_value=0, value=800, step=10, key=f"w_{idx}")
                quality = st.slider("Calidad JPG", 60, 100, 90, key=f"q_{idx}")
                if st.button("Actualizar imagen", key=f"imgup_{idx}"):
                    if upload is None:
                        st.error("Sube una imagen.")
                    else:
                        ow = width if width>0 else None
                        if aspect=="1:1": path = save_image_file(upload, out_w=ow or 800, out_h=ow or 800, crop="center", fmt="JPEG", quality=quality)
                        elif aspect=="4:5": path = save_image_file(upload, out_w=800, out_h=1000, crop="center", fmt="JPEG", quality=quality)
                        elif aspect=="16:9": path = save_image_file(upload, out_w=1280, out_h=720, crop="center", fmt="JPEG", quality=quality)
                        else: path = save_image_file(upload, out_w=ow or None, out_h=None, crop="center", fmt="JPEG", quality=quality)
                        p["image"] = path; save_products(products); st.success("Imagen actualizada.")
            if st.button("Eliminar producto", key=f"del_{idx}"):
                products.pop(idx); save_products(products); st.warning("Producto eliminado."); st.rerun()
st.markdown("### Exportar catálogo")
data = json.dumps(products, ensure_ascii=False, indent=2)
st.download_button("⬇️ Descargar products.json", data=data, file_name="products.json", mime="application/json", use_container_width=True)
