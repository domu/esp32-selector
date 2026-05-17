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
def select_board_features(model_name, df):
    # Reset preventivo delle pillole
    for key in list(st.session_state.keys()):
        if key.startswith("pill_"):
            del st.session_state[key]
    
    # Imposta i valori delle pillole basandosi sul modello cliccato
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
        st.error(f"Errore caricamento dati: {e}")
        return None

df = load_data()

if df is not None:
    model_names = df.columns[2:]
    main_sections = ["ARCHITECTURE", "WIRELESS", "COMMON PERIPHERALS", "ANALOG", "USB & HIGH-SPEED", "DISPLAY & CAMERA", "SECURITY", "STATUS"]

    # --- CSS PER BLOCCO FISSO E LAYOUT ---
    st.markdown("""
        <style>
        /* Rende la colonna di destra fissa */
        [data-testid="stColumn"]:nth-child(2) {
            position: fixed;
            right: 2rem;
            width: 25% !important;
            max-height: 90vh;
            overflow-y: auto;
            z-index: 100;
        }
        /* Spazio per evitare che la colonna sinistra sia troppo larga */
        [data-testid="stColumn"]:nth-child(1) {
            width: 70% !important;
        }
        .board-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 5px 10px;
            border-radius: 5px;
            margin-bottom: 5px;
            border: 1px solid #333;
        }
        .compatible-tag {
            background-color: #007bff;
            color: white;
            font-size: 0.65rem;
            padding: 2px 6px;
            border-radius: 10px;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

    # Creazione Colonne
    col_filters, col_results = st.columns([0.7, 0.3])

    active_filters = {}

    with col_filters:
        st.title("🛠️ Configuratore ESP32")
        tab1, tab2 = st.tabs(["🎯 Filtri Tecnici", "📚 Consigli & Video"])
        
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

    # --- COLONNA DESTRA (RISULTATI FISSI) ---
    with col_results:
        st.button("🔄 Reset Selezione", use_container_width=True, type="primary", on_click=reset_all_filters)
        st.subheader("Modelli")
        st.caption("Clicca il nome per caricare le specifiche")

        for model in model_names:
            # Calcolo compatibilità
            is_compatible = True
            for f_name, f_val in active_filters.items():
                model_val = str(df[df['Feature'] == f_name][model].values[0]).strip()
                if model_val != f_val:
                    is_compatible = False
                    break
            
            # Rendering grafico
            is_active = is_compatible and active_filters
            opacity = "1.0" if (is_active or not active_filters) else "0.2"
            border_color = "#00d4ff" if is_active else "#333"
            
            # Container personalizzato con HTML/CSS
            st.markdown(f"""
                <div class="board-container" style="opacity: {opacity}; border-color: {border_color};">
                    <span style="font-size: 0.85rem; font-weight: bold;">{model}</span>
                    {"<span class='compatible-tag'>✓ COMPATIBILE</span>" if is_active else ""}
                </div>
            """, unsafe_allow_html=True)
            
            # Pulsante invisibile sopra il div per catturare il click e attivare la selezione inversa
            if st.button(f"Seleziona {model}", key=f"btn_{model}", use_container_width=True, help=f"Vedi specifiche di {model}"):
                select_board_features(model, df)
                st.rerun()

    with tab2:
        # Nota: I consigli vengono visualizzati correttamente anche se cliccati nel tab principale
        pass