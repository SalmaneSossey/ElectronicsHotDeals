# -*- coding: utf-8 -*-
from __future__ import annotations

import os, sys, subprocess, textwrap, re
from pathlib import Path

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA

# graceful fallback if fancy menu missing
try:
    from streamlit_option_menu import option_menu
except ModuleNotFoundError:
    st.sidebar.warning(" 'streamlit-option-menu' not installed – using basic menu.")
    def option_menu(menu_title, options, icons=None, default_index=0, styles=None):
        return st.sidebar.radio(menu_title or "", options, index=default_index)

try:
    import google.generativeai as genai
except ModuleNotFoundError:
    genai = None

DATA_CSV = Path("jumia_products_clean.csv")

# ---------------------------------------------------------------------------
# Theme & page config
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Jumia Deals Explorer", page_icon="🛍️", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """<style>
    :root{--primary:#FF5A00;--secondary:#FFC5A3;--bg:#F7F7F8;--card:#FFFFFF;--text:#252734;--radius:0.8rem;--shadow:0 12px 24px rgba(0,0,0,.06);}    
    html,body,[data-testid="stApp"]{background:var(--bg);color:var(--text);font-family:"Inter",sans-serif;}
    h1,h2,h3,h4,h5,h6{color:var(--primary);} .card{background:var(--card);border-radius:var(--radius);padding:1rem 1.2rem;box-shadow:var(--shadow);}    
    .pill{display:inline-block;padding:0.1rem 0.55rem;font-size:0.7rem;border-radius:999px;background:var(--secondary);color:var(--primary);font-weight:600;margin-left:0.3rem;vertical-align:middle;}
    header{visibility:hidden;}
    </style>""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def get_col(df: pd.DataFrame, contains: tuple[str, ...]):
    for c in df.columns:
        if any(sub in c.lower() for sub in contains):
            return c
    return None


def ensure_numeric(df: pd.DataFrame, col: str | None, new: str) -> str | None:
    if col is None or col not in df:
        return None
    if pd.api.types.is_numeric_dtype(df[col]):
        return col
    cleaned = (
        df[col].astype(str)
        .str.replace(r"[^0-9.,]", "", regex=True)
        .str.replace(",", "", regex=False)
        .str.replace("\u202f", "", regex=False)
    )
    df[new] = pd.to_numeric(cleaned, errors="coerce")
    return new

@st.cache_data(show_spinner="Loading data …")
def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_CSV) if DATA_CSV.exists() else pd.DataFrame()

_df = load_data()

# ---------------------------------------------------------------------------
# Sidebar: scrape button + filters + nav
# ---------------------------------------------------------------------------
with st.sidebar:
    if st.button(" Rescrape & Clean"):
        env=os.environ.copy(); env["PYTHONIOENCODING"]="utf-8"; env["PYTHONUTF8"]="1"
        with st.spinner("Pipeline running…"):
            subprocess.run([sys.executable,"scraper_jumia_electronics.py"],check=True,env=env)
            subprocess.run([sys.executable,"clean_jumia_data.py"],check=True,env=env)
        load_data.clear(); st.rerun()

with st.sidebar:
    st.markdown("## 🛒 Jumia Explorer")
    nav = option_menu(None, ["Home", "Visualisation", "PCA", "Ask Gemini", "About"], icons=["house", "bar-chart", "graph-up", "question-circle", "info-circle"], default_index=0, styles={"container":{"padding":"0!important","background":"transparent"},"icon":{"color":"var(--primary)","font-size":"1.2rem"},"nav-link-selected":{"background-color":"var(--secondary)"}})

# build filters (shared across tabs)
if not _df.empty:
    price_col = ensure_numeric(_df, get_col(_df,("price",)), "price_numeric")
    disc_col = ensure_numeric(_df, get_col(_df,("discount",)), "discount_numeric")
    cat_col  = get_col(_df,("category",))
    with st.sidebar.expander("Filters", expanded=True):
        cats   = sorted(_df[cat_col].dropna().unique()) if cat_col else []
        sel_c  = st.multiselect("Category", cats, default=cats)
        brands = sorted(_df["brand"].dropna().unique()) if "brand" in _df else []
        sel_b  = st.multiselect("Brand", brands, default=brands)
        types  = sorted(_df["type_product"].dropna().unique()) if "type_product" in _df else []
        sel_t  = st.multiselect("Type", types, default=types)
        if price_col:
            pmin, pmax = int(_df[price_col].min()), int(_df[price_col].max())
            sel_p  = st.slider("Price (Dhs)", pmin, pmax, (pmin, pmax), step=100)
        else:
            sel_p=None
    mask = pd.Series(True, index=_df.index)
    if sel_c and cat_col: mask &= _df[cat_col].isin(sel_c)
    if sel_b: mask &= _df["brand"].isin(sel_b)
    if sel_t: mask &= _df["type_product"].isin(sel_t)
    if sel_p and price_col: mask &= _df[price_col].between(*sel_p)
    df_f = _df[mask]
else:
    df_f = _df.copy()
    price_col = disc_col = cat_col = None

# ---------------------------------------------------------------------------
# HOME TAB (unchanged but uses df_f)
# ---------------------------------------------------------------------------
if nav == "Home":
    st.title("📊 Catalogue & Smart Deals")
    if df_f.empty: st.info("No data – scrape first."); st.stop()
    trusted = {"samsung","xiaomi","apple","lg","sony","dell","hp","lenovo","huawei","asus"}
    disc_series = df_f[disc_col].fillna(0) if disc_col in df_f else 0
    df_f = df_f.copy()
    if price_col is None: st.error("Price column missing"); st.stop()
    df_f["deal_score"] = disc_series*0.4 + (1/df_f[price_col].replace(0,np.nan)).fillna(0)*10000*0.3 + df_f["brand"].str.lower().apply(lambda b:1 if b in trusted else 0)*0.3
    top5 = df_f.sort_values("deal_score",ascending=False).head(5)

    img_col = get_col(df_f,("image","img")); url_col = get_col(df_f,("link","url"))
    st.subheader("🔥 Top 5 genuine deals")
    for _,row in top5.iterrows():
        with st.container():
            l,r=st.columns([1,4],gap="medium")
            if img_col and pd.notna(row[img_col]): l.image(row[img_col],use_container_width=True)
            else: l.write("*(no image)*")
            pill=f"<span class='pill'>{row[cat_col]}</span>" if cat_col and pd.notna(row[cat_col]) else ""
            r.markdown(f"### {row.get('title','No title')} {pill}",unsafe_allow_html=True)
            r.markdown(f"<span style='font-size:1.3rem;font-weight:600'>{row.get(price_col,np.nan):,.0f} Dhs</span>",unsafe_allow_html=True)
            if url_col and pd.notna(row[url_col]): r.link_button("Open ↗",url=row[url_col])

# ---------------------------------------------------------------------------
# VISUALISATION TAB – NEW
# ---------------------------------------------------------------------------
elif nav == "Visualisation":
    st.title("📈 Visual analytics dashboard")
    if df_f.empty: st.warning("No data after filters."); st.stop()

    # KPI summary
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Rows", len(df_f))
    if price_col: c2.metric("Avg price", f"{df_f[price_col].mean():,.0f} Dhs")
    if disc_col: c3.metric("Avg discount", f"{df_f[disc_col].mean():.1f}%")
    c4.metric("Brands", df_f['brand'].nunique())

    st.divider()

    # plot grids
    colA,colB = st.columns(2)

    # Price distribution histogram
    with colA:
        st.markdown("#### Price distribution")
        fig,ax = plt.subplots(); ax.hist(df_f[price_col].dropna(), bins=30); ax.set_xlabel("Price (Dhs)"); ax.set_ylabel("Count")
        st.pyplot(fig)

    # Discounts vs price scatter
    with colB:
        if disc_col:
            st.markdown("#### Discount vs Price")
            fig = px.scatter(df_f, x=price_col, y=disc_col, color=cat_col, size_max=12, opacity=0.6, labels={price_col:"Price",disc_col:"Discount %"})
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Avg price by category
    if cat_col:
        st.markdown("#### Average price by category")
        pvt = df_f.groupby(cat_col)[price_col].mean().reset_index().sort_values(price_col)
        fig = px.bar(pvt, x=price_col, y=cat_col, orientation='h', labels={price_col:"Avg price (Dhs)", cat_col:"Category"})
        st.plotly_chart(fig, use_container_width=True)

    # Count by type
    if 'type_product' in df_f:
        st.markdown("#### Product count by type")
        cnt = df_f['type_product'].value_counts().reset_index(); cnt.columns=['type','count']
        fig = px.bar(cnt, x='type', y='count', labels={'type':'Type','count':'Count'})
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------------
# PCA TAB (unchanged)
# ---------------------------------------------------------------------------
elif nav == "PCA":
    st.title(" PCA Analysis of product space")
    if df_f.empty: st.warning("No data after filters.")
    else:
        price_col = ensure_numeric(df_f, price_col, price_col)  # ensure exists
        disc_col  = ensure_numeric(df_f, disc_col, disc_col)
        if not price_col or not disc_col: st.error("Need price & discount columns.")
        else:
            base = df_f.dropna(subset=["brand","type_product",price_col,disc_col])
            if len(base)<2: st.warning("Not enough rows for PCA.")
            else:
                pipe=Pipeline([("pre",ColumnTransformer([("num",StandardScaler(),[price_col,disc_col]),("cat",OneHotEncoder(handle_unknown='ignore',sparse_output=False),["brand","type_product"])])),("pca",PCA(n_components=2))])
                coords=pipe.fit_transform(base[[price_col,disc_col,"brand","type_product"]])
                res=pd.DataFrame(coords,columns=["PCA1","PCA2"]); res["type_product"]=base["type_product"].values
                fig=px.scatter(res,x="PCA1",y="PCA2",color="type_product",width=900,height=550)
                st.plotly_chart(fig,use_container_width=True)
                
# ----------------------------------------------------------------------------
# ASK GEMINI TAB -----------------------------------------------------------
# ----------------------------------------------------------------------------

elif nav == "Ask Gemini":
    st.title("🔍 Query Gemini with Jumia catalogue")
    if genai is None: st.error("google-generativeai package not installed.")
    else:
        api_key = st.sidebar.text_input("Google API Key", type="password")
        if api_key:
            try: genai.configure(api_key=api_key); model = genai.GenerativeModel("gemini-1.5-flash"); # st.success("Gemini ready ✔️")
            except Exception as e: st.error(f"API error: {e}"); model=None
        else: model=None; st.info("Enter your Google API key to enable Gemini.")
        if _df.empty: st.warning("Scrape data first.")
        elif model:
            q = st.text_area("Your question about Jumia products:");
            if st.button("Ask Gemini") and q.strip():
                with st.spinner("Gemini is thinking …"):
                    ctx = _df.head(200).to_markdown(index=False)
                    prompt = textwrap.dedent(f"You are an e‑commerce expert. Use ONLY this table:\n{ctx}\nQuestion: {q}\nIf data is insufficient say so.")
                    try: ans = model.generate_content(prompt).text; st.markdown("### Answer from Gemini"); st.markdown(ans)
                    except Exception as e: st.error(f"Gemini error: {e}")

# ---------------------------------------------------------------------------
# ABOUT TAB
# ---------------------------------------------------------------------------
else:
    st.title("ℹ️ About")
    st.write("Open-source dashboard scraping Jumia Morocco, with analytics and AI-powered Q&A.")
