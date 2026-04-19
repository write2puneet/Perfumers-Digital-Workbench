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
    - **🏗️ Formula Architect**: Design scent profiles and find market matches.
    - **📚 Ingredient Library**: Access professional research data directly from GitHub.
    - **🔬 Molecular Lab**: Enter a **SMILES** code (e.g., `O=Cc1cc(OC)c(O)cc1` for Vanillin).
    - **📂 My Archive**: Upload your personal JSON collections.
    """)

# --- HELPER FUNCTIONS ---
@st.cache_data
def fetch_github_data(study, file):
    """Bypasses Pyrfume library to fetch data directly from GitHub."""
    base_url = "https://githubusercontent.com"
    url = f"{base_url}/{study}/{file}"
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
            st.info("Market matches found!")
            st.write("✨ **Example**: *Santal 33* matches your Woody preference.")

# TAB 2: INGREDIENT LIBRARY (DIRECT FETCH FIX)
with tab2:
    st.header("Global Ingredient Library")
    st.info("💡 Data is fetched directly from the Pyrfume-Data GitHub to avoid permission errors.")
    
    study = st.selectbox("Select Study", ["bushdid_2014", "keller_2016", "snitz_2013"])
    file = st.radio("Data View", ["molecules.csv", "behavior.csv"], horizontal=True)
    
    if st.button("Unbottle Data"):
        try:
            with st.spinner("Streaming research data from GitHub..."):
                results = fetch_github_data(study, file)
                st.success(f"Viewing: {study}")
                st.dataframe(results, use_container_width=True)
                
                # Download Button
                csv = results.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Results as CSV", csv, f"{study}.csv", "text/csv")
        except Exception as e:
            st.error(f"Failed to fetch data. Ensure the study/file combination is correct. Error: {e}")

# TAB 3: MOLECULAR LAB
with tab3:
    st.header("Scent Molecule Visualizer")
    smiles_input = st.text_input("Enter SMILES Code", "O=Cc1cc(OC)c(O)cc1")
    if st.button("Render Molecule"):
        mol = Chem.MolFromSmiles(smiles_input)
        if mol:
            st.image(Draw.MolToImage(mol), caption="Chemical Structure")
        else:
            st.error("Invalid SMILES code.")

# TAB 4: MY ARCHIVE
with tab4:
    st.header("Personal Archive")
    uploaded_file = st.file_uploader("Upload JSON Archive", type="json")
    if uploaded_file:
        st.json(json.load(uploaded_file))
