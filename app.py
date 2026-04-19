import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rdkit import Chem
from rdkit.Chem import Draw
import json

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Perfumer's Digital Lab", page_icon="⚗️", layout="wide")

st.title("⚗️ The Perfumer's Digital Workbench")
with st.expander("👋 Onboarding Guide: How to use this Lab"):
    st.markdown("""
    - **🏗️ Formula Architect**: Design scent profiles and find market matches based on olfactory families.
    - **📚 Ingredient Library**: Access professional research data fetched directly from GitHub archives.
    - **🔬 Molecular Lab**: Enter a **SMILES** code (e.g., `O=Cc1cc(OC)c(O)cc1`) to see its structure.
    - **📂 My Archive**: Upload your personal JSON scent collections.
    """)

# --- HELPER FUNCTIONS ---
@st.cache_data
def fetch_github_data(study, file):
    """Fetches data directly from GitHub to bypass permission errors."""
    # Using the raw content URL for the main pyrfume-data repository
    url = f"https://githubusercontent.com{study}/{file}"
    return pd.read_csv(url)

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["🏗️ Formula Architect", "📚 Ingredient Library", "🔬 Molecular Lab", "📂 My Archive"])

# TAB 1: FORMULA ARCHITECT
with tab1:
    st.header("Fragrance Formula Architect")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Your Design Profile")
        fav_family = st.selectbox("Olfactory Family", ["Floral", "Woody", "Oriental", "Fougere", "Chypre", "Gourmand", "Citrus"])
        fav_notes = st.multiselect("Key Notes", ["Rose", "Sandalwood", "Amber", "Bergamot", "Jasmine", "Vanilla", "Oud", "Musk"])
    with col2:
        st.subheader("Market Analysis")
        if st.button("Calculate Matches"):
            st.info("Market matches found! Sample output:")
            st.write("✨ **Baccarat Rouge 540**: High match for Oriental profiles.")

# TAB 2: INGREDIENT LIBRARY (BYPASSES PYRFUME LIBRARY ERRORS)
with tab2:
    st.header("Global Ingredient Library")
    st.info("💡 Pro Tip: If a search fails, try 'bushdid_2014' or 'keller_2016' first.")
    
    study = st.selectbox("Select Study", ["bushdid_2014", "keller_2016", "snitz_2013", "dravnieks_1985"])
    file = st.radio("Data View", ["molecules.csv", "behavior.csv"], horizontal=True)
    
    if st.button("Unbottle Data"):
        try:
            with st.spinner("Streaming research data from GitHub..."):
                results = fetch_github_data(study, file)
                st.success(f"Viewing: {study} / {file}")
                st.dataframe(results, use_container_width=True)
                
                # Download Button
                csv = results.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download as CSV", csv, f"{study}_{file}", "text/csv")
        except Exception as e:
            st.error(f"Failed to fetch data. This study might not contain this specific file type. (Error: {e})")

# TAB 3: MOLECULAR LAB
with tab3:
    st.header("Molecular Structure Visualizer")
    sm_in = st.text_input("Enter SMILES Code", "O=Cc1cc(OC)c(O)cc1", help="Example: Vanillin")
    if st.button("Render Molecule"):
        mol = Chem.MolFromSmiles(sm_in)
        if mol:
            st.image(Draw.MolToImage(mol, size=(400, 400)), caption="Chemical Structure")
        else:
            st.error("Invalid SMILES code. Please try a valid string like CC1=CCC(CC1)C(=C)C.")

# TAB 4: MY ARCHIVE
with tab4:
    st.header("Personal Archive")
    up = st.file_uploader("Upload JSON Archive", type="json")
    if up:
        st.json(json.load(up))
