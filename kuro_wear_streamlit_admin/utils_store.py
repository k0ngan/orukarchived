import json, os
from pathlib import Path
import streamlit as st
from PIL import Image
DATA_DIR = Path(__file__).resolve().parent / "data"
IMAGES_DIR = DATA_DIR / "images"
CATALOG_FILE = DATA_DIR / "products.json"
def load_products():
    if not CATALOG_FILE.exists():
        return []
    return json.loads(CATALOG_FILE.read_text(encoding="utf-8"))
def save_products(products):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CATALOG_FILE.write_text(json.dumps(products, ensure_ascii=False, indent=2), encoding="utf-8")
def find_product(pid, products=None):
    products = products or load_products()
    return next((p for p in products if str(p.get("id"))==str(pid)), None)
def price_fmt(x):
    try:
        return f"${float(x):,.0f}".replace(",", ".")
    except:
        return str(x)
def ensure_cart():
    if "cart" not in st.session_state:
        st.session_state["cart"] = []
    return st.session_state["cart"]
def add_to_cart(item):
    cart = ensure_cart()
    for it in cart:
        if it["id"]==item["id"] and it.get("size")==item.get("size"):
            it["qty"] += item["qty"]
            return
    cart.append(item)
def remove_from_cart(index):
    cart = ensure_cart()
    if 0 <= index < len(cart):
        cart.pop(index)
def subtotal_cart():
    cart = ensure_cart()
    return sum((it["price"]*it["qty"]) for it in cart)
def inject_base_css():
    st.markdown("""<style>header[data-testid='stHeader']{visibility:hidden}.stDeployButton{display:none}[data-testid='stStatusWidget']{display:none}.block-container{padding-top:.8rem;padding-bottom:1rem;max-width:1200px}.k-card{background:#0F1014;border:1px solid #262833;border-radius:16px;padding:14px;transition:transform .1s ease,box-shadow .12s ease}.k-card:hover{transform:translateY(-2px);box-shadow:0 10px 22px rgba(0,0,0,.35)}.k-accent{color:#8B5CF6}.k-hero{background:linear-gradient(135deg,rgba(139,92,246,.18) 0%,rgba(0,0,0,.35) 100%);border:1px solid #262833;border-radius:18px;padding:18px 18px}.k-button{border:1px solid #262833;border-radius:12px;padding:8px 12px;background:#151622;color:#E5E7EB}.k-button:hover{background:#1A1B2A}.muted{color:#94a3b8;font-size:12px}</style>""", unsafe_allow_html=True)
def safe_filename(name, suffix):
    import re, uuid
    base = re.sub(r"[^a-zA-Z0-9_-]+","-",name).strip("-").lower() or "img"
    return f"{base}-{uuid.uuid4().hex[:8]}{suffix}"
def save_image_file(uploaded_file, out_w=None, out_h=None, crop="center", fmt="JPEG", quality=90):
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    img = Image.open(uploaded_file).convert("RGB")
    w,h = img.size
    if crop=="center" and out_w and out_h:
        target_ratio = out_w/out_h
        src_ratio = w/h
        if src_ratio>target_ratio:
            new_w=int(h*target_ratio); left=(w-new_w)//2; box=(left,0,left+new_w,h)
        else:
            new_h=int(w/target_ratio); top=(h-new_h)//2; box=(0,top,w,top+new_h)
        img = img.crop(box)
    if out_w and out_h:
        img = img.resize((out_w,out_h))
    suffix = ".jpg" if fmt.upper()=="JPEG" else ".png"
    fname = safe_filename(uploaded_file.name, suffix)
    out_path = IMAGES_DIR / fname
    img.save(out_path, fmt, quality=quality, optimize=True)
    return str(out_path)
