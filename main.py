import streamlit as st
import pandas as pd

# Configurazione Pagina
st.set_page_config(page_title="ESP32 Expert Selector 2026", layout="wide")

def load_data():
    nome_file = "ESP32_Feature_Matrix_2026.csv"
    try:
        df = pd.read_csv(nome_file)
        # Pulizia nomi colonne: rimuoviamo i ritorni a capo e gli spazi superflui
        df.columns = [c.replace('\n', ' ').strip() for c in df.columns]
        # Puliamo anche i dati nelle colonne descrittive
        df['Feature Category'] = df['Feature Category'].ffill().str.strip()
        df['Feature'] = df['Feature'].str.strip()
        return df
    except Exception as e:
        st.error(f"Errore nel caricamento del file: {e}")
        return None

df = load_data()

if df is not None:
    model_names = df.columns[2:]
    
    # Lista ordinata delle categorie principali come da tua richiesta
    main_sections = [
        "ARCHITECTURE", "WIRELESS", "COMMON PERIPHERALS", 
        "ANALOG", "USB & HIGH-SPEED", "DISPLAY & CAMERA", 
        "SECURITY", "STATUS"
    ]

    st.title("🛠️ ESP32 Smart Configurator")

    tab1, tab2 = st.tabs(["🎯 Filtro Tecnico Avanzato", "📚 Consigli d'Uso"])

    with tab1:
        col_title, col_reset = st.columns([4, 1])
        with col_reset:
            if st.button("🔄 Reset Selezione", use_container_width=True, type="primary"):
                st.rerun()

        active_filters = {}

        # 1. GENERAZIONE DEI FILTRI PER OGNI RIGA DI OGNI SEZIONE
        for section in main_sections:
            # Prendiamo TUTTE le righe che appartengono a questa sezione
            cat_rows = df[df['Feature Category'] == section]
            
            if not cat_rows.empty:
                with st.expander(f"📂 {section}", expanded=True):
                    # Iteriamo su ogni riga (Feature) della sezione
                    for _, row in cat_rows.iterrows():
                        feature_label = row['Feature']
                        
                        # Estraiamo i valori unici dai modelli per questa specifica riga
                        # Escludiamo '✗', valori nulli o celle vuote
                        possible_values = []
                        for model in model_names:
                            val = str(row[model]).strip()
                            if val not in ['✗', 'nan', '', 'None']:
                                if val not in possible_values:
                                    possible_values.append(val)
                        
                        # Se la riga ha dei valori selezionabili, creiamo il filtro
                        if possible_values:
                            # Ordiniamo i valori (es. frequenze o nomi architetture)
                            possible_values.sort()
                            selected = st.pills(feature_label, possible_values, key=f"pill_{feature_label}")
                            if selected:
                                active_filters[feature_label] = selected

        st.divider()

        # 2. LOGICA DI FILTRAGGIO E VISUALIZZAZIONE MODELLI
        st.subheader("Risultato Selezione")
        cols_res = st.columns(len(model_names))

        for idx, model in enumerate(model_names):
            is_compatible = True
            
            # Un modello resta "acceso" solo se soddisfa TUTTI i filtri attivi
            for f_name, f_value in active_filters.items():
                model_value = str(df[df['Feature'] == f_name][model].values[0]).strip()
                if model_value != f_value:
                    is_compatible = False
                    break
            
            with cols_res[idx]:
                # Stile grafico dei box modelli
                base_style = "text-align: center; padding: 10px; border-radius: 8px; min-height: 70px; display: flex; align-items: center; justify-content: center; border: 1px solid "
                
                if not active_filters:
                    # Default: Grigio
                    st.markdown(f"<div style='{base_style} #333; color: #777;'>{model}</div>", unsafe_allow_html=True)
                elif is_compatible:
                    # Compatibile: Blu brillante
                    st.markdown(f"<div style='{base_style} #00d4ff; background-color: #007bff; color: white; font-weight: bold; box-shadow: 0px 0px 15px rgba(0,123,255,0.6);'>{model}</div>", unsafe_allow_html=True)
                else:
                    # Non compatibile: Opaco
                    st.markdown(f"<div style='{base_style} #111; color: #222; opacity: 0.15;'>{model}</div>", unsafe_allow_html=True)

    with tab2:
        st.header("Le migliori schede per tipo di progetto")
        st.caption("Consigli basati sulla guida DroneBot Workshop 2026")

        rec_categories = {
            "Sperimentazione / General Purpose": ["ESP32-S3", "ESP32-C6", "ESP32-C5"],
            "Multimedia / Display / AI": ["ESP32-P4", "ESP32-S3", "LilyGo T-Display"],
            "Smart Home (Matter/Zigbee)": ["ESP32-C6", "ESP32-H2", "ESP32-C5"],
            "Budget / Educational": ["ESP32-C3", "ESP32 Original", "XIAO C3"]
        }

        sel_cat = st.radio("Seleziona la tua area di interesse:", list(rec_categories.keys()), horizontal=True)
        
        c1, c2, c3 = st.columns(3)
        picks = rec_categories[sel_cat]
        
        with c1: st.info(f"🥇 **Top Choice**\n\n{picks[0]}")
        with c2: st.info(f"🥈 **Alternative**\n\n{picks[1]}")
        with c3: st.info(f"🥉 **Entry Level**\n\n{picks[2]}")

        st.divider()
        st.markdown("### 🎥 Approfondimento Video")
        st.video("https://www.youtube.com/watch?v=CfIjInYch7U")

# CSS Custom
st.markdown("""
    <style>
    .stExpander { border: none !important; border-bottom: 1px solid #222 !important; }
    [data-testid="stMarkdownContainer"] p { font-size: 0.85rem; font-weight: 600; color: #d1d1d1; margin-bottom: 2px; }
    </style>
    """, unsafe_allow_html=True)