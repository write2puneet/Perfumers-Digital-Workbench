import os

# --- CRITICAL: STREAMLIT CLOUD PERMISSION FIX ---
# This must run BEFORE importing pyrfume to prevent [Errno 13]
tmp_dir = "/tmp/pyrfume-data"
if not os.path.exists(tmp_dir):
    os.makedirs(tmp_dir, exist_ok=True)

# Create a dummy config file in a writable location
tmp_config = os.path.join(tmp_dir, "config.ini")
if not os.path.exists(tmp_config):
    with open(tmp_config, "w") as f:
        f.write("[main]\n")

# Set environment variables to redirect pyrfume's internal paths
os.environ['PYRFUME_DATA'] = tmp_dir

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
with st.expander("👋 New here? Click to see how to use this Lab"):
    st.markdown("""
    1. **🏗️ Formula Architect**: Design scent profiles and find matching fragrances.
    2. **📚 Ingredient Library**: Browse 20,000+ molecules and scientific odor ratings.
    3. **🔬 Molecular Lab**: See the chemical "skeleton" of ingredients using SMILES codes.
    4. **📂 My Archive**: Upload and manage your personal JSON scent collections.
    """)

# --- HELPER FUNCTIONS ---
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

# --- TABS FOR NAVIGATION ---
tab1, tab2, tab3, tab4 = st.tabs(["🏗️ Formula Architect", "📚 Ingredient Library", "🔬 Molecular Lab", "📂 My Archive"])

# --- TAB 1: FORMULA ARCHITECT ---
with tab1:
    st.header("Fragrance Formula Architect")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Your Design Profile")
        fav_family = st.selectbox("Select Olfactory Family", 
                                ["Floral", "Woody", "Oriental", "Fougere", "Chypre", "Gourmand", "Citrus"],
                                help="The main character or category of your perfume.")
        fav_notes = st.multiselect("Select Key Notes", 
                                 ["Rose", "Sandalwood", "Amber", "Bergamot", "Jasmine", "Vanilla", "Oud", "Musk"],
                                 help="Specific ingredients you want to feature in your formula.")
        
    # Sample Dataset for Recommender
    data = {
        'name': ['Baccarat Rouge 540', 'Sauvage', 'Black Opium', 'Chanel No 5', 'Aventus', 'Cloud', 'Santal 33'],
        'family': ['Oriental', 'Fougere', 'Oriental', 'Floral', 'Chypre', 'Gourmand', 'Woody'],
        'notes': ['Jasmine Saffron Cedarwood Ambergris', 'Bergamot Pepper Lavender Ambroxan', 
                  'Coffee Pink Pepper Jasmine Vanilla', 'Aldehydes Ylang-Ylang Iris Jasmine', 
                  'Pineapple Birch Musk Oakmoss', 'Lavender Pear Praline Coconut', 'Sandalwood Leather Papyrus Iris']
    }
    df = pd.DataFrame(data)

    with col2:
        st.subheader("AI Market Analysis")
        if st.button("Find Similar Market Fragrances", help="Calculates similarity based on your selected notes."):
            df['soup'] = df['family'] + " " + df['notes']
            user_soup = f"{fav_family} {' '.join(fav_notes)}"
            cv = CountVectorizer(stop_words='english')
            temp_df = pd.concat([df, pd.DataFrame([{'name': 'YOU', 'soup': user_soup}])], ignore_index=True)
            count_matrix = cv.fit_transform(temp_df['soup'])
            sig = cosine_similarity(count_matrix)
            user_idx = len(temp_df) - 1
            scores = sorted(list(enumerate(sig[user_idx])), key=lambda x: x, reverse=True)
            
            for i in range(1, 4):
                match = df.iloc[scores[i]]
                st.info(f"✨ **{match['name']}** ({match['family']})\nNotes: {match['notes']}")

# --- TAB 2: INGREDIENT LIBRARY ---
with tab2:
    st.header("Global Ingredient Library")
    st.info("💡 This section pulls from professional scientific archives (Pyrfume) to show you how different molecules behave.")
    
    dataset_choice = st.selectbox("Select Study/Library", 
                                ["bushdid_2014", "keller_2016", "snitz_2013"],
                                help="Different studies offer unique data, from molecular weights to sensory ratings.")
    file_type = st.radio("What data would you like to see?", 
                        ["molecules.csv", "behavior.csv", "stimuli.csv"], 
                        horizontal=True,
                        help="'molecules' shows chemistry data; 'behavior' shows sensory/rating data.")
    
    if st.button("Unbottle Data"):
        try:
            with st.spinner("Fetching directly from GitHub archives..."):
                path = f"{dataset_choice}/{file_type}"
                # Use remote=True to bypass local file permission issues entirely
                results = pyrfume.load_data(path, remote=True) 
                st.success(f"Viewing data for: {dataset_choice}")
                st.dataframe(results, use_container_width=True)
                
                # Download Option
                st.download_button(
                    label="📥 Download this data as CSV",
                    data=convert_df(results),
                    file_name=f"{dataset_choice}_{file_type}",
                    mime='text/csv'
                )
        except Exception as e:
            st.error(f"Search failed. This study might not have that specific file. Error: {e}")

# --- TAB 3: MOLECULAR LAB ---
with tab3:
    st.header("Molecular Structure Visualizer")
    st.write("Convert chemical codes (SMILES) into visual structures.")
    col_a, col_b = st.columns(2)
    
    with col_a:
        molecule_name = st.text_input("Ingredient Name", "Vanillin")
        smiles_input = st.text_input("SMILES String", "O=Cc1cc(OC)c(O)cc1", 
                                   help="Standard chemical code. RDKit uses this to 'draw' the molecule.")
        st.caption("Try Limonene (Citrus): `CC1=CCC(CC1)C(=C)C` or Linalool (Lavender): `CC(=CCCC(C)(C=C)O)C`")

    with col_b:
        if st.button("Draw Molecule"):
            mol = Chem.MolFromSmiles(smiles_input)
            if mol:
                img = Draw.MolToImage(mol, size=(400, 400))
                st.image(img, caption=f"Chemical Structure of {molecule_name}")
            else:
                st.error("Please enter a valid chemical SMILES code.")

# --- TAB 4: MY ARCHIVE ---
with tab4:
    st.header("Private Collection Management")
    uploaded_file = st.file_uploader("Upload your 'my_fragrances.json'", type="json", 
                                   help="Access your private library saved from previous sessions.")
    if uploaded_file:
        try:
            user_data = json.load(uploaded_file)
            st.success("Archive loaded!")
            st.json(user_data)
        except Exception as e:
            st.error(f"The file format is incorrect. Error: {e}")
