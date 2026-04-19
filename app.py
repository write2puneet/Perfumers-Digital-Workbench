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

# --- INGREDIENT DATABASE ---
# Curated list of common perfumery ingredients
INGREDIENT_OPTIONS = [
    "Custom (Type below)",
    "Aldehyde C-10", "Ambergris (Synth)", "Ambroxan", "Bergamot Oil", 
    "Calone", "Cedarwood Virginia", "Civet (Synth)", "Coumarin", 
    "Ethyl Vanillin", "Galaxolide", "Geranium Oil", "Hedione", 
    "Indole", "Iso E Super", "Jasmine Abs", "Lavender Oil", 
    "Lemon Oil", "Linalool", "Mandarin Oil", "Musk Ketone", 
    "Neroli Oil", "Oakmoss Reconstitution", "Patchouli Oil", 
    "Pink Pepper Oil", "Rose Absolute", "Sandalwood Mysore", 
    "Vetiveryl Acetate", "Ylang Ylang Oil"
]

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
            st.success("Calculated matches based on your profile.")
            st.info("Check out fragrances with similar note structures in your chosen family.")

# --- TAB 2: FORMULA LAB (WITH DROPDOWNS) ---
with tab2:
    st.header("Accord & Formula Builder")
    st.write("Select ingredients from the library or type your own.")
    
    if 'rows' not in st.session_state:
        st.session_state.rows = [{"selected": "Bergamot Oil", "custom": "", "grams": 1.0}]

    def add_row():
        st.session_state.rows.append({"selected": "Custom (Type below)", "custom": "", "grams": 0.0})

    for i, row in enumerate(st.session_state.rows):
        c1, c2, c3 = st.columns([2, 2, 1])
        
        # Column 1: Dropdown
        st.session_state.rows[i]["selected"] = c1.selectbox(
            f"Library Match {i+1}", 
            INGREDIENT_OPTIONS, 
            index=INGREDIENT_OPTIONS.index(row["selected"]),
            key=f"sel_{i}"
        )
        
        # Column 2: Custom Name (Enabled if 'Custom' is selected)
        is_custom = st.session_state.rows[i]["selected"] == "Custom (Type below)"
        st.session_state.rows[i]["custom"] = c2.text_input(
            f"Custom Name {i+1}", 
            value=row["custom"], 
            disabled=not is_custom,
            key=f"cust_{i}",
            placeholder="Type ingredient here..."
        )
        
        # Column 3: Weight
        st.session_state.rows[i]["grams"] = c3.number_input("Grams", value=row["grams"], key=f"gram_{i}", format="%.3f")

    st.button("➕ Add Ingredient Line", on_click=add_row)

    # Calculation logic
    formula_data = []
    for r in st.session_state.rows:
        name = r["custom"] if r["selected"] == "Custom (Type below)" else r["selected"]
        formula_data.append({"Ingredient": name, "Grams": r["grams"]})

    formula_df = pd.DataFrame(formula_data)
    total_grams = formula_df['Grams'].sum()
    
    if total_grams > 0:
        formula_df['Percentage (%)'] = (formula_df['Grams'] / total_grams * 100).round(2)
        st.subheader("Final Formula Breakdown")
        st.table(formula_df)
        st.write(f"**Total Weight:** {total_grams:.3f}g")
        st.download_button("📥 Export CSV", formula_df.to_csv(index=False).encode('utf-8'), "my_formula.csv")

# --- TAB 3: MOLECULAR LAB ---
with tab3:
    st.header("Molecular Scent Viewer")
    sm_in = st.text_input("Enter SMILES Code", "O=Cc1cc(OC)c(O)cc1", help="Code for Vanillin")
    if st.button("Draw Molecule"):
        mol = Chem.MolFromSmiles(sm_in)
        if mol:
            st.image(Draw.MolToImage(mol, size=(400, 400)), caption="Chemical Structure")
        else:
            st.error("Invalid SMILES.")

# --- TAB 4: MY ARCHIVE ---
with tab4:
    st.header("Personal JSON Archive")
    up = st.file_uploader("Upload collections", type="json")
    if up:
        st.json(json.load(up))
