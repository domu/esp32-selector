import streamlit as st
import pandas as pd

# Configurazione Pagina
st.set_page_config(page_title="ESP32 Expert Selector 2026", layout="wide")

def load_data():
    nome_file = "ESP32_Feature_Matrix_2026.csv"
    try:
        df = pd.read_csv(nome_file)
        # Pulizia nomi colonne e riempimento categorie (fondamentale per le righe successive)
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
    main_sections = [
        "ARCHITECTURE", "WIRELESS", "COMMON PERIPHERALS", 
        "ANALOG", "USB & HIGH-SPEED", "DISPLAY & CAMERA", 
        "SECURITY", "STATUS"
    ]

    # --- SEZIONE FISSA IN ALTO (RISULTATI) ---
    # Usiamo un container che rimarrà bloccato in alto grazie al CSS
    header = st.container()
    
    with header:
        st.title("🛠️ ESP32 Smart Configurator")
        st.subheader("Modelli Corrispondenti")
        
        # Placeholder per i risultati che verranno aggiornati dopo il calcolo dei filtri
        result_placeholder = st.empty()
        st.divider()

    # --- SEZIONE SCORREVOLE (FILTRI) ---
    tab1, tab2 = st.tabs(["🎯 Filtro Tecnico Avanzato", "📚 Consigli d'Uso"])

    with tab1:
        col_title, col_reset = st.columns([4, 1])
        with col_reset:
            if st.button("🔄 Reset Selezione", use_container_width=True, type="primary"):
                st.rerun()

        active_filters = {}

        for section in main_sections:
            cat_rows = df[df['Feature Category'] == section]
            if not cat_rows.empty:
                with st.expander(f"📂 {section}", expanded=True):
                    for _, row in cat_rows.iterrows():
                        feature_label = row['Feature']
                        
                        # Estrazione valori unici escludendo '✗' e nulli
                        possible_values = []
                        for model in model_names:
                            val = str(row[model]).strip()
                            if val not in ['✗', 'nan', '', 'None']:
                                if val not in possible_values:
                                    possible_values.append(val)
                        
                        if possible_values:
                            possible_values.sort()
                            selected = st.pills(feature_label, possible_values, key=f"pill_{feature_label}")
                            if selected:
                                active_filters[feature_label] = selected

        # --- LOGICA DI CALCOLO COMPATIBILITÀ ---
        # Creiamo i box dei modelli per il placeholder in alto
        with result_placeholder:
            cols_res = st.columns(len(model_names))
            for idx, model in enumerate(model_names):
                is_compatible = True
                for f_name, f_value in active_filters.items():
                    model_value = str(df[df['Feature'] == f_name][model].values[0]).strip()
                    if model_value != f_value:
                        is_compatible = False
                        break
                
                with cols_res[idx]:
                    base_style = "text-align: center; padding: 10px; border-radius: 8px; min-height: 60px; display: flex; align-items: center; justify-content: center; border: 1px solid "
                    
                    if not active_filters:
                        st.markdown(f"<div style='{base_style} #333; color: #777; font-size: 0.8em;'>{model}</div>", unsafe_allow_html=True)
                    elif is_compatible:
                        st.markdown(f"<div style='{base_style} #00d4ff; background-color: #007bff; color: white; font-weight: bold; box-shadow: 0px 0px 15px rgba(0,123,255,0.6); font-size: 0.8em;'>{model}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div style='{base_style} #111; color: #222; opacity: 0.15; font-size: 0.8em;'>{model}</div>", unsafe_allow_html=True)

    with tab2:
        # (Sezione consigli invariata)
        st.header("Le migliori schede per tipo di progetto")
        rec_categories = {
            "Sperimentazione / General Purpose": ["ESP32-S3", "ESP32-C6", "ESP32-C5"],
            "Multimedia / Display / AI": ["ESP32-P4", "ESP32-S3", "LilyGo T-Display"],
            "Smart Home (Matter/Zigbee)": ["ESP32-C6", "ESP32-H2", "ESP32-C5"],
            "Budget / Educational": ["ESP32-C3", "ESP32 Original", "XIAO C3"]
        }
        sel_cat = st.radio("Seleziona area:", list(rec_categories.keys()), horizontal=True)
        c1, c2, c3 = st.columns(3)
        picks = rec_categories[sel_cat]
        with c1: st.info(f"🥇 {picks[0]}")
        with c2: st.info(f"🥈 {picks[1]}")
        with c3: st.info(f"🥉 {picks[2]}")
        st.divider()
        st.video("https://www.youtube.com/watch?v=CfIjInYch7U")

# --- CSS PER BLOCCARE L'HEADER IN ALTO ---
st.markdown("""
    <style>
    /* Rende il container dell'header fisso in alto */
    [data-testid="stVerticalBlock"] > div:first-child {
        position: sticky;
        top: 2rem;
        background-color: #0e1117;
        z-index: 999;
        padding-bottom: 10px;
    }
    .stExpander { border: none !important; border-bottom: 1px solid #222 !important; }
    [data-testid="stMarkdownContainer"] p { font-size: 0.85rem; font-weight: 600; color: #d1d1d1; margin-bottom: 2px; }
    </style>
    """, unsafe_allow_html=True)