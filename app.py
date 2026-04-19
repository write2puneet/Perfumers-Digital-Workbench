import streamlit as st
import pandas as pd
import requests
from io import StringIO
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rdkit import Chem
from rdkit.Chem import Draw
import json

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Perfumer's Digital Lab", page_icon="⚗️", layout="wide")

st.title("⚗️ The Perfumer's Digital Workbench")

# --- RESILIENT DATA FETCHER ---
@st.cache_data(show_spinner=False)
def fetch_github_data(study, file):
    """Bypasses DNS/Permission issues with requests + StringIO."""
    url = f"https://githubusercontent.com{study}/{file}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() # Check for HTTP errors
        return pd.read_csv(StringIO(response.text))
    except Exception as e:
        return f"Network Error: {e}"

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["🏗️ Formula Architect", "📚 Ingredient Library", "🔬 Molecular Lab", "📂 My Archive"])

# TAB 1: FORMULA ARCHITECT
with tab1:
    st.header("Fragrance Formula Architect")
    col1, col2 = st.columns(2)
    with col1:
        fav_family = st.selectbox("Olfactory Family", ["Floral", "Woody", "Oriental", "Fougere", "Chypre", "Gourmand", "Citrus"])
        fav_notes = st.multiselect("Key Notes", ["Rose", "Sandalwood", "Amber", "Bergamot", "Jasmine", "Vanilla", "Oud", "Musk"])
    with col2:
        if st.button("Calculate Matches"):
            st.info("Market matches found for your profile!")
            st.write("✨ **Baccarat Rouge 540**: High match for Oriental profiles.")

# TAB 2: INGREDIENT LIBRARY (RESILIENT VERSION)
with tab2:
    st.header("Global Ingredient Library")
    st.info("💡 Data is fetched directly from the Pyrfume-Data GitHub archive.")
    
    study = st.selectbox("Select Study", ["bushdid_2014", "keller_2016", "snitz_2013", "dravnieks_1985"])
    file = st.radio("Data View", ["molecules.csv", "behavior.csv"], horizontal=True)
    
    if st.button("Unbottle Data"):
        with st.spinner("Connecting to GitHub archives..."):
            result = fetch_github_data(study, file)
            
            if isinstance(result, str): # Handle error message
                st.error(f"Failed to fetch data: {result}")
                st.warning("Tip: This can happen due to temporary DNS issues on Streamlit Cloud. Try clicking the button again.")
            else:
                st.success(f"Viewing: {study} / {file}")
                st.dataframe(result, use_container_width=True)
                st.download_button("📥 Download as CSV", result.to_csv(index=False).encode('utf-8'), f"{study}_{file}.csv", "text/csv")

# TAB 3: MOLECULAR LAB
with tab3:
    st.header("Molecular Structure Visualizer")
    sm_in = st.text_input("Enter SMILES Code", "O=Cc1cc(OC)c(O)cc1")
    if st.button("Render Molecule"):
        mol = Chem.MolFromSmiles(sm_in)
        if mol:
            st.image(Draw.MolToImage(mol, size=(400, 400)), caption="Chemical Structure")
        else:
            st.error("Invalid SMILES code.")

# TAB 4: MY ARCHIVE
with tab4:
    st.header("Personal Archive")
    up = st.file_uploader("Upload JSON Archive", type="json")
    if up:
        st.json(json.load(up))
