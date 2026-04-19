import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pyrfume
from rdkit import Chem
from rdkit.Chem import Draw
import json
import os

# --- STREAMLIT CLOUD PERMISSION FIX ---
# Redirect pyrfume to a writable directory to avoid [Errno 13]
os.environ['PYRFUME_DATA'] = '/tmp/pyrfume-data'
if not os.path.exists('/tmp/pyrfume-data'):
    os.makedirs('/tmp/pyrfume-data')

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Perfumer's Digital Lab", page_icon="⚗️", layout="wide")

st.title("⚗️ The Perfumer's Digital Workbench")
with st.expander("👋 New here? Learn how to navigate the Lab"):
    st.markdown("""
    - **🏗️ Formula Architect**: Design scent profiles and find market matches.
    - **📚 Ingredient Library**: Access professional research data on 20,000+ molecules.
    - **🔬 Molecular Lab**: Visualize the chemical structure of your ingredients.
    - **📂 My Archive**: Upload and manage your private fragrance collections.
    """)

# --- HELPER FUNCTIONS ---
@st.cache_data
def convert_df(df):
    """Converts a dataframe into a downloadable CSV format."""
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
                                help="The primary category of your perfume.")
        fav_notes = st.multiselect("Select Key Notes", 
                                 ["Rose", "Sandalwood", "Amber", "Bergamot", "Jasmine", "Vanilla", "Oud", "Musk"],
                                 help="Main ingredients you want to feature.")
        
    data = {
        'name': ['Baccarat Rouge 540', 'Sauvage', 'Black Opium', 'Chanel No 5', 'Aventus', 'Cloud', 'Santal 33'],
        'family': ['Oriental', 'Fougere', 'Oriental', 'Floral', 'Chypre', 'Gourmand', 'Woody'],
        'notes': ['Jasmine Saffron Cedarwood Ambergris', 'Bergamot Pepper Lavender Ambroxan', 
                  'Coffee Pink Pepper Jasmine Vanilla', 'Aldehydes Ylang-Ylang Iris Jasmine', 
                  'Pineapple Birch Musk Oakmoss', 'Lavender Pear Praline Coconut', 'Sandalwood Leather Papyrus Iris']
    }
    df = pd.DataFrame(data)

    with col2:
        st.subheader("Market Analysis")
        if st.button("Calculate Matches", help="Finds similar fragrances based on your chosen notes."):
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
    st.info("💡 Access professional odorant research archives (Pyrfume) to see how molecules behave.")
    
    dataset_choice = st.selectbox("Select Research Library", 
                                ["bushdid_2014", "keller_2016", "snitz_2013"],
                                help="Each library contains different data types like sensory ratings or chemical specs.")
    file_type = st.radio("Select Data View", 
                        ["molecules.csv", "behavior.csv", "stimuli.csv"], 
                        horizontal=True,
                        help="'molecules' for chemistry, 'behavior' for sensory ratings.")
    
    if st.button("Unbottle Data"):
        try:
            with st.spinner("Fetching data from digital archives..."):
                path = f"{dataset_choice}/{file_type}"
                results = pyrfume.load_data(path)
                st.success(f"Viewing: {dataset_choice} / {file_type}")
                st.dataframe(results, use_container_width=True)
                
                # --- NEW DOWNLOAD BUTTON ---
                csv_data = convert_df(results)
                st.download_button(
                    label="📥 Download this data as CSV",
                    data=csv_data,
                    file_name=f"{dataset_choice}_{file_type}",
                    mime='text/csv',
                    help="Save this research data to your computer for offline analysis."
                )
        except Exception as e:
            st.error(f"Data unavailable for this specific search. Error: {e}")

# --- TAB 3: MOLECULAR LAB ---
with tab3:
    st.header("Scent Molecule Visualizer")
    st.write("Visualise chemical 'skeletons' from standard SMILES codes.")
    col_a, col_b = st.columns(2)
    
    with col_a:
        molecule_name = st.text_input("Common Ingredient Name", "Vanillin")
        smiles_input = st.text_input("Chemical SMILES Code", "O=Cc1cc(OC)c(O)cc1")
        st.caption("Try Limonene (Citrus): `CC1=CCC(CC1)C(=C)C` or Linalool (Lavender): `CC(=CCCC(C)(C=C)O)C`")

    with col_b:
        if st.button("Render 2D Structure"):
            mol = Chem.MolFromSmiles(smiles_input)
            if mol:
                img = Draw.MolToImage(mol, size=(400, 400))
                st.image(img, caption=f"Structure of {molecule_name}")
            else:
                st.error("Invalid SMILES code entered.")

# --- TAB 4: MY ARCHIVE ---
with tab4:
    st.header("Personal Archive")
    uploaded_file = st.file_uploader("Upload 'my_fragrances.json'", type="json")
    if uploaded_file:
        try:
            user_data = json.load(uploaded_file)
            st.success("Archive loaded successfully!")
            st.json(user_data)
        except Exception as e:
            st.error(f"Error reading your archive: {e}")
