import streamlit as st
import pandas as pd

# Configurazione Pagina
st.set_page_config(page_title="ESP32 Expert Selector 2026", layout="wide")

# --- LOGICA RESET AVANZATA ---
if 'reset_key' not in st.session_state:
    st.session_state.reset_key = 0

def reset_all_filters():
    st.session_state.reset_key += 1
    for key in list(st.session_state.keys()):
        if key.startswith("pill_"):
            del st.session_state[key]
    st.rerun()

# --- LOGICA SELEZIONE BOARD (Inversa) ---
def select_board_features(model_name, df):
    st.session_state.reset_key += 1 
    for _, row in df.iterrows():
        feat_label = row['Feature']
        val_to_set = str(row[model_name]).strip()
        if val_to_set not in ['✗', 'nan', '', 'None']:
            st.session_state[f"pill_{feat_label}"] = val_to_set

def load_data():
    # NOME FILE CORRETTO (Quello caricato su GitHub)
    nome_file = "ESP32_Feature_Matrix_2026.csv"
    try:
        df = pd.read_csv(nome_file)
        df.columns = [c.replace('\n', ' ').strip() for c in df.columns]
        df['Feature Category'] = df['Feature Category'].ffill().str.strip()
        df['Feature'] = df['Feature'].str.strip()
        return df
    except Exception as e:
        st.error(f"File '{nome_file}' non trovato o errore: {e}")
        return None

df = load_data()

if df is not None:
    model_names = df.columns[2:]
    main_sections = ["ARCHITECTURE", "WIRELESS", "COMMON PERIPHERALS", "ANALOG", "USB & HIGH-SPEED", "DISPLAY & CAMERA", "SECURITY", "STATUS"]

    # --- CSS PER LAYOUT A COLONNE FISSE ---
    st.markdown(f"""
        <style>
        /* Colonna sinistra scorrevole */
        [data-testid="stColumn"]:nth-child(1) {{
            width: 62% !important;
            max-width: 62% !important;
        }}
        /* Colonna destra fissa */
        [data-testid="stColumn"]:nth-child(2) {{
            position: fixed;
            right: 2%;
            top: 60px;
            width: 30% !important;
            max-height: 85vh;
            overflow-y: auto;
            background-color: #0e1117;
            padding: 15px;
            border-left: 1px solid #333;
            z-index: 1000;
        }}
        .board-card {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 12px;
            border-radius: 6px;
            border: 1px solid #444;
            background-color: #161b22;
            margin-bottom: 2px;
        }}
        .compatible-tag {{
            background-color: #007bff;
            color: white;
            font-size: 0.6rem;
            padding: 2px 8px;
            border-radius: 4px;
            font-weight: bold;
        }}
        </style>
    """, unsafe_allow_html=True)

    col_filters, col_results = st.columns([0.65, 0.35])

    active_filters = {}

    with col_filters:
        st.title("🛠️ ESP32 Smart Selector")
        # Container con chiave dinamica per reset totale visivo
        with st.container(key=f"filters_main_{st.session_state.reset_key}"):
            tab1, tab2 = st.tabs(["🎯 Filtri Dinamici", "📚 Info & Video"])
            
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

    # --- COLONNA DESTRA RISULTATI ---
    with col_results:
        st.button("🔄 Reset Totale", use_container_width=True, type="primary", on_click=reset_all_filters)
        st.subheader("Modelli ESP32")
        
        for model in model_names:
            # Calcolo compatibilità
            is_compatible = True
            for f_name, f_val in active_filters.items():
                model_val = str(df[df['Feature'] == f_name][model].values[0]).strip()
                if model_val != f_val:
                    is_compatible = False
                    break
            
            is_active = is_compatible and active_filters
            opacity = "1.0" if (is_active or not active_filters) else "0.15"
            border_color = "#00d4ff" if is_active else "#333"
            
            # Card grafica
            st.markdown(f"""
                <div class="board-card" style="opacity: {opacity}; border-color: {border_color};">
                    <span style="font-size: 0.85rem; font-weight: bold; color: white;">{model}</span>
                    {"<span class='compatible-tag'>✓ COMPATIBILE</span>" if is_active else ""}
                </div>
            """, unsafe_allow_html=True)
            
            # Pulsante selezione board
            if st.button(f"Vedi specifiche: {model}", key=f"btn_{model}", use_container_width=True):
                select_board_features(model, df)
                st.rerun()