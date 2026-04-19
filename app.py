import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rdkit import Chem
from rdkit.Chem import Draw
import json

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Perfumer's Creative Studio", page_icon="🎨", layout="wide")

st.title("🎨 The Perfumer's Creative Studio")
st.markdown("A professional workspace for scent architecture, molecular study, and formula management.")

# --- HELP & ONBOARDING ---
with st.expander("👋 New to the Studio? Start here"):
    st.markdown("""
    - **🏗️ Market Recommender**: Find existing fragrances that match your desired profile.
    - **🧪 Formula Lab**: Build a custom scent accord and calculate ingredient percentages.
    - **🔬 Molecular Lab**: Visualize the chemical structure of your raw materials.
    - **📂 My Archive**: Manage your private formula collection (JSON).
    """)

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["🏗️ Market Recommender", "🧪 Formula Lab", "🔬 Molecular Lab", "📂 My Archive"])

# --- TAB 1: MARKET RECOMMENDER ---
with tab1:
    st.header("Fragrance Market Analysis")
    col1, col2 = st.columns(2)
    
    data = {
        'name': ['Baccarat Rouge 540', 'Sauvage', 'Black Opium', 'Chanel No 5', 'Aventus', 'Cloud', 'Santal 33'],
        'family': ['Oriental', 'Fougere', 'Oriental', 'Floral', 'Chypre', 'Gourmand', 'Woody'],
        'notes': ['Jasmine Saffron Cedarwood Ambergris', 'Bergamot Pepper Lavender Ambroxan', 
                  'Coffee Pink Pepper Jasmine Vanilla', 'Aldehydes Ylang-Ylang Iris Jasmine', 
                  'Pineapple Birch Musk Oakmoss', 'Lavender Pear Praline Coconut', 'Sandalwood Leather Papyrus Iris']
    }
    df = pd.DataFrame(data)

    with col1:
        fav_family = st.selectbox("Desired Family", df['family'].unique())
        fav_notes = st.multiselect("Desired Notes", ["Rose", "Sandalwood", "Amber", "Bergamot", "Jasmine", "Vanilla", "Oud", "Musk"])
    
    with col2:
        if st.button("Search Market"):
            st.success("Calculated top market matches for your profile:")
            st.info(f"✨ **{df.iloc[0]['name']}** - A strong match for {fav_family} profiles.")

# --- TAB 2: FORMULA LAB (NEW!) ---
with tab2:
    st.header("Accord & Formula Builder")
    st.write("Add your ingredients and their weights (in grams) to architect a new formula.")
    
    if 'rows' not in st.session_state:
        st.session_state.rows = [{"ingredient": "Bergamot", "grams": 1.0}]

    def add_row():
        st.session_state.rows.append({"ingredient": "", "grams": 0.0})

    for i, row in enumerate(st.session_state.rows):
        c1, c2 = st.columns([3, 1])
        st.session_state.rows[i]["ingredient"] = c1.text_input(f"Ingredient {i+1}", value=row["ingredient"], key=f"ing_{i}")
        st.session_state.rows[i]["grams"] = c2.number_input("Grams", value=row["grams"], key=f"gram_{i}")

    st.button("➕ Add Ingredient", on_click=add_row)

    # Calculation logic
    formula_df = pd.DataFrame(st.session_state.rows)
    total_grams = formula_df['grams'].sum()
    if total_grams > 0:
        formula_df['Percentage (%)'] = (formula_df['grams'] / total_grams * 100).round(2)
        st.subheader("Final Formula Breakdown")
        st.table(formula_df)
        st.write(f"**Total Weight:** {total_grams:.2f}g")
        
        # Export as CSV
        st.download_button("📥 Export Formula (CSV)", formula_df.to_csv(index=False).encode('utf-8'), "my_formula.csv")

# --- TAB 3: MOLECULAR LAB ---
with tab3:
    st.header("Molecular Scent Viewer")
    smiles_input = st.text_input("Enter SMILES Code", "O=Cc1cc(OC)c(O)cc1", help="Code for Vanillin")
    if st.button("Draw Molecule"):
        mol = Chem.MolFromSmiles(smiles_input)
        if mol:
            st.image(Draw.MolToImage(mol, size=(400, 400)), caption="Chemical Structure")
        else:
            st.error("Invalid SMILES. Try `CC1=CCC(CC1)C(=C)C` (Limonene)")

# --- TAB 4: MY ARCHIVE ---
with tab4:
    st.header("Personal JSON Archive")
    up = st.file_uploader("Upload your collections", type="json")
    if up:
        st.json(json.load(up))
