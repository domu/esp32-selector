import streamlit as st
import pandas as pd

# Configurazione Pagina
st.set_page_config(page_title="ESP32 Expert Selector 2026", layout="wide")

# --- LOGICA RESET ---
def reset_all_filters():
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

# --- LOGICA SELEZIONE BOARD (Inversa) ---
def select_board_features(model_name, df, model_names):
    # Reset preventivo per evitare conflitti
    for key in list(st.session_state.keys()):
        if key.startswith("pill_"):
            del st.session_state[key]
    
    # Per ogni riga del DF, impostiamo il valore della pillola su quello del modello scelto
    for _, row in df.iterrows():
        feat_label = row['Feature']
        val_to_set = str(row[model_name]).strip()
        if val_to_set not in ['✗', 'nan', '', 'None']:
            st.session_state[f"pill_{feat_label}"] = val_to_set

def load_data():
    nome_file = "ESP32_Feature_Matrix_2026.csv"
    try:
        df = pd.read_csv(nome_file)
        df.columns = [c.replace('\n', ' ').strip() for c in df.columns]
        df['Feature Category'] = df['Feature Category'].ffill().str.strip()
        df['Feature'] = df['Feature'].str.strip()
        return df
    except Exception as e:
        st.error(f"Errore nel caricamento del file: {e}")
        return None

df = load_data()

if df is not None:
    model_names = df.columns[2:]
    main_sections = ["ARCHITECTURE", "WIRELESS", "COMMON PERIPHERALS", "ANALOG", "USB & HIGH-SPEED", "DISPLAY & CAMERA", "SECURITY", "STATUS"]

    # --- LAYOUT A DUE COLONNE ---
    col_filters, col_results = st.columns([0.7, 0.3])

    active_filters = {}

    with col_filters:
        st.title("🛠️ Configurazione")
        tab1, tab2 = st.tabs(["🎯 Filtri", "📚 Consigli"])
        
        with tab1:
            for section in main_sections:
                cat_rows = df[df['Feature Category'] == section]
                if not cat_rows.empty:
                    with st.expander(f"📂 {section}", expanded=True):
                        for _, row in cat_rows.iterrows():
                            feat_label = row['Feature']
                            possible_values = sorted(list(set([str(row[m]).strip() for m in model_names if str(row[m]).strip() not in ['✗', 'nan', '', 'None']])))
                            
                            if possible_values:
                                res = st.pills(feat_label, possible_values, key=f"pill_{feat_label}")
                                if res:
                                    active_filters[feat_label] = res
        
        with tab2:
            st.video("https://www.youtube.com/watch?v=CfIjInYch7U")

    # --- COLONNA DESTRA FISSA (RISULTATI) ---
    with col_results:
        # Inseriamo tutto in un div con classe 'sticky' tramite CSS
        st.markdown('<div class="sticky-results">', unsafe_allow_html=True)
        
        st.button("🔄 Reset Totale", use_container_width=True, type="primary", on_click=reset_all_filters)
        st.subheader("Modelli ESP32")
        st.caption("Clicca su un nome per vedere le sue specifiche")

        for model in model_names:
            is_compatible = True
            for f_name, f_val in active_filters.items():
                model_val = str(df[df['Feature'] == f_name][model].values[0]).strip()
                if model_val != f_val:
                    is_compatible = False
                    break
            
            # Rendering del box modello
            if not active_filters:
                color, border, opacity, shadow = "#666", "#333", "1.0", "none"
            elif is_compatible:
                color, border, opacity, shadow = "white", "#00d4ff", "1.0", "0px 0px 10px rgba(0,123,255,0.6)"
            else:
                color, border, opacity, shadow = "#333", "#111", "0.3", "none"

            # Pulsante per la selezione inversa
            if st.button(f"{model}", key=f"btn_{model}", use_container_width=True):
                select_board_features(model, df, model_names)
                st.rerun()

            # Estetica del box (sotto il pulsante per mostrare lo stato)
            st.markdown(f"""
                <div style='background-color: {"#007bff" if is_compatible and active_filters else "transparent"}; 
                            border: 1px solid {border}; 
                            color: {color}; 
                            padding: 5px; 
                            border-radius: 5px; 
                            text-align: center; 
                            font-size: 0.8rem; 
                            opacity: {opacity};
                            box-shadow: {shadow};
                            margin-bottom: 10px;
                            margin-top: -5px;'>
                    {"✓ Compatibile" if is_compatible and active_filters else ""}
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# --- CSS PER COLONNA FISSA ---
st.markdown("""
    <style>
    [data-testid="stVerticalBlock"] > div:nth-child(2) [data-testid="stVerticalBlock"] {
        position: sticky;
        top: 2rem;
        z-index: 1000;
    }
    .stButton > button {
        font-weight: bold;
        margin-bottom: 0px;
    }
    [data-testid="stExpander"] {
        border: none !important;
        border-bottom: 1px solid #222 !important;
    }
    </style>
    """, unsafe_allow_html=True)