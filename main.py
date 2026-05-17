import streamlit as st
import pandas as pd

# Configurazione Pagina
st.set_page_config(page_title="ESP32 Expert Selector 2026", layout="wide")

def load_data():
    nome_file = "ESP32_Feature_Matrix_2026.csv"
    try:
        df = pd.read_csv(nome_file)
        # Pulizia nomi colonne e gestione valori nulli
        df.columns = [c.replace('\n', ' ') for c in df.columns]
        df = df.fillna('✗')
        return df
    except:
        st.error("File CSV non trovato nel repository!")
        return None

df = load_data()

if df is not None:
    model_names = df.columns[2:]
    # Otteniamo le categorie uniche (es. ARCHITECTURE, WIRELESS, etc.)
    feature_categories = df['Feature Category'].unique()

    st.title("🛠️ ESP32 Smart Configurator")

    tab1, tab2 = st.tabs(["🎯 Filtro Tecnico Avanzato", "📚 Consigli d'Uso"])

    with tab1:
        col_title, col_reset = st.columns([4, 1])
        with col_reset:
            if st.button("🔄 Reset Selezione", use_container_width=True, type="primary"):
                st.rerun()

        # Dizionario per salvare i filtri attivi: { "FeatureName": "SelectedValue" }
        active_filters = {}

        # 1. GENERAZIONE DINAMICA DEI FILTRI
        for cat in feature_categories:
            if pd.isna(cat): continue
            
            with st.expander(f"🔹 {cat}", expanded=True):
                # Righe appartenenti a questa categoria
                cat_rows = df[df['Feature Category'] == cat]
                
                for _, row in cat_rows.iterrows():
                    feature_name = row['Feature']
                    # Estraiamo i valori unici dalle colonne dei modelli per questa riga
                    # Es: per "CPU Cores" otterremo ["Dual", "Single"]
                    possible_values = sorted(list(set([str(row[m]) for m in model_names if str(row[m]) != '✗'])))
                    
                    if possible_values:
                        # Creiamo una riga di selezione per ogni Feature
                        selected = st.pills(feature_name, possible_values, key=f"pill_{feature_name}")
                        if selected:
                            active_filters[feature_name] = selected

        st.divider()

        # 2. LOGICA DI FILTRAGGIO E VISUALIZZAZIONE
        st.subheader("Risultato Selezione")
        cols_res = st.columns(len(model_names))

        for idx, model in enumerate(model_names):
            is_compatible = True
            
            # Un modello è compatibile solo se possiede TUTTI i valori selezionati
            for f_name, f_value in active_filters.items():
                model_value = str(df[df['Feature'] == f_name][model].values[0])
                if model_value != f_value:
                    is_compatible = False
                    break
            
            with cols_res[idx]:
                if not active_filters:
                    # Stato neutro (nessun filtro)
                    st.markdown(f"<div style='color: #666; text-align: center; border: 1px solid #333; padding: 10px; border-radius: 8px; font-size: 0.8em; min-height: 60px; display: flex; align-items: center; justify-content: center;'>{model}</div>", unsafe_allow_html=True)
                elif is_compatible:
                    # Modello che soddisfa i requisiti
                    st.markdown(f"<div style='color: white; background-color: #007bff; text-align: center; border: 2px solid #00d4ff; padding: 10px; border-radius: 8px; font-weight: bold; box-shadow: 0px 0px 15px rgba(0,123,255,0.6); min-height: 60px; display: flex; align-items: center; justify-content: center;'>{model}</div>", unsafe_allow_html=True)
                else:
                    # Modello escluso
                    st.markdown(f"<div style='color: #222; text-align: center; border: 1px solid #111; padding: 10px; border-radius: 8px; opacity: 0.2; min-height: 60px; display: flex; align-items: center; justify-content: center;'>{model}</div>", unsafe_allow_html=True)

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

# CSS per pulire lo stile delle "pills" e degli expander
st.markdown("""
    <style>
    .stExpander { border: none !important; box-shadow: none !important; }
    [data-testid="stMarkdownContainer"] p { font-size: 0.9rem; font-weight: 600; margin-bottom: 0px; }
    </style>
    """, unsafe_allow_html=True)