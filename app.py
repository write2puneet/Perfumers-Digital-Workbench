import os
import sys
import shutil

# --- EMERGENCY OVERRIDE FOR STREAMLIT CLOUD PERMISSIONS ---
# We force the library to look at a writable /tmp directory
# 1. Setup writable paths
writable_root = "/tmp"
os.environ['HOME'] = writable_root
os.environ['PYRFUME_DATA'] = os.path.join(writable_root, "pyrfume-data")

# 2. Create the internal .pyrfume folder if it's missing
pyrfume_config_path = os.path.join(writable_root, ".pyrfume")
os.makedirs(pyrfume_config_path, exist_ok=True)

# 3. Pre-create a dummy config.ini
config_file = os.path.join(pyrfume_config_path, "config.ini")
if not os.path.exists(config_file):
    with open(config_file, "w") as f:
        f.write("[main]\n")

import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pyrfume
from rdkit import Chem
from rdkit.Chem import Draw
import json

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Perfumer's Digital Lab", page_icon="⚗️", layout="wide")

st.title("⚗️ The Perfumer's Digital Workbench")
with st.expander("👋 Onboarding Guide: How to use this Lab"):
    st.markdown("""
    - **🏗️ Formula Architect**: Design scent profiles and find market matches.
    - **📚 Ingredient Library**: Access professional research data from **Pyrfume**.
    - **🔬 Molecular Lab**: Enter a **SMILES** code (e.g., `O=Cc1cc(OC)c(O)cc1` for Vanillin) to see its structure.
    - **📂 My Archive**: Upload your personal JSON scent collections.
    """)

# --- HELPER FUNCTIONS ---
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["🏗️ Formula Architect", "📚 Ingredient Library", "🔬 Molecular Lab", "📂 My Archive"])

# --- TAB 1: FORMULA ARCHITECT ---
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
            st.info("Searching similar fragrance structures...")
            st.write("✨ **Example Match**: Woody-Floral Accord found in *Santal 33*")

# --- TAB 2: INGREDIENT LIBRARY ---
with tab2:
    st.header("Global Ingredient Library")
    st.info("💡 Pulling scientific data directly from the GitHub repository.")
    
    dataset_choice = st.selectbox("Select Study", ["bushdid_2014", "keller_2016", "snitz_2013"])
    file_type = st.radio("Data View", ["molecules.csv", "behavior.csv"], horizontal=True)
    
    if st.button("Unbottle Data"):
        try:
            with st.spinner("Streaming research data..."):
                # FORCE remote=True to avoid touching local config files
                results = pyrfume.load_data(f"{dataset_choice}/{file_type}", remote=True)
                st.success(f"Viewing: {dataset_choice}")
                st.dataframe(results, use_container_width=True)
                
                # Download Button
                st.download_button("📥 Download Results as CSV", convert_df(results), f"{dataset_choice}.csv", "text/csv")
        except Exception as e:
            st.error(f"Search failed. Error: {e}")

# --- TAB 3: MOLECULAR LAB ---
with tab3:
    st.header("Molecular Structure Visualizer")
    col_a, col_b = st.columns(2)
    with col_a:
        smiles_input = st.text_input("Enter SMILES Code", "O=Cc1cc(OC)c(O)cc1")
    with col_b:
        if st.button("Render Molecule"):
            mol = Chem.MolFromSmiles(smiles_input)
            if mol:
                st.image(Draw.MolToImage(mol), caption="Chemical Structure")
            else:
                st.error("Invalid SMILES code.")

# --- TAB 4: MY ARCHIVE ---
with tab4:
    st.header("Personal Archive")
    uploaded_file = st.file_uploader("Upload JSON Archive", type="json")
    if uploaded_file:
        st.json(json.load(uploaded_file))
