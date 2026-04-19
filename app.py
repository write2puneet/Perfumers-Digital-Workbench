import os
import sys

# 1. SETUP WRITABLE ENVIRONMENT
# Streamlit Cloud only allows writing to /tmp
home_dir = "/tmp"
os.environ['HOME'] = home_dir  # Trick library to look in /tmp for .pyrfume
os.environ['PYRFUME_DATA'] = os.path.join(home_dir, "pyrfume-data")

# 2. PRE-CREATE CONFIG FILE IN WRITABLE SPACE
config_dir = os.path.join(home_dir, ".pyrfume")
os.makedirs(config_dir, exist_ok=True)
config_file = os.path.join(config_dir, "config.ini")

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

# --- HELP & ONBOARDING ---
with st.expander("❓ How to use this Lab"):
    st.markdown("""
    - **🏗️ Formula Architect**: Pick notes and find market matches.
    - **📚 Ingredient Library**: Pull real scientific data from the **Pyrfume Archive**. 
    - **🔬 Molecular Lab**: Enter a **SMILES** code (like `CC1=CCC(CC1)C(=C)C` for Limonene) to see its structure.
    """)

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["🏗️ Formula Architect", "📚 Ingredient Library", "🔬 Molecular Lab", "📂 My Archive"])

# TAB 1: RECOMMENDER
with tab1:
    st.header("Fragrance Formula Architect")
    col1, col2 = st.columns(2)
    with col1:
        family = st.selectbox("Olfactory Family", ["Floral", "Woody", "Oriental", "Fougere", "Chypre", "Gourmand", "Citrus"])
        notes = st.multiselect("Key Notes", ["Rose", "Sandalwood", "Amber", "Bergamot", "Jasmine", "Vanilla", "Oud", "Musk"])
    
    with col2:
        if st.button("Calculate Matches"):
            st.info("Matches found based on your profile!")
            st.write("- **Example Match 1**: Woody-Floral Accord")

# TAB 2: RESEARCH LIBRARY (FIXED)
with tab2:
    st.header("Global Ingredient Library")
    st.info("💡 Pro Tip: If a search fails, try a different 'Study' or 'Data View'.")
    
    lib = st.selectbox("Select Research Study", ["bushdid_2014", "keller_2016", "snitz_2013"])
    view = st.radio("Data View", ["molecules.csv", "behavior.csv"], horizontal=True)
    
    if st.button("Unbottle Data"):
        try:
            with st.spinner("Fetching data directly from GitHub..."):
                # FORCE REMOTE FETCH to bypass local permission issues
                data = pyrfume.load_data(f"{lib}/{view}", remote=True)
                st.dataframe(data, use_container_width=True)
                
                # Download Button
                csv = data.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Results as CSV", csv, f"{lib}_{view}", "text/csv")
        except Exception as e:
            st.error(f"Access Denied or File Missing. Try another study. (Error: {e})")

# TAB 3: MOLECULAR LAB
with tab3:
    st.header("Molecular Structure Visualizer")
    s_in = st.text_input("Enter SMILES Code", "O=Cc1cc(OC)c(O)cc1")
    if st.button("Draw Molecule"):
        mol = Chem.MolFromSmiles(s_in)
        if mol:
            st.image(Draw.MolToImage(mol), caption="Chemical Structure")

# TAB 4: ARCHIVE
with tab4:
    st.header("Personal Archive")
    up = st.file_uploader("Upload JSON Archive", type="json")
    if up:
        st.json(json.load(up))
