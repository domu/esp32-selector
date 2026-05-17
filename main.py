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
    # Preparazione dati
    model_names = df.columns[2:]
    categories = df['Feature Category'].dropna().unique()

    st.title("🛠️ ESP32 Smart Configurator")

    tab1, tab2 = st.tabs(["🎯 Filtro per Aree", "📚 Consigli d'Uso"])

    with tab1:
        # Riga superiore con Titolo e Reset
        col_title, col_reset = st.columns([4, 1])
        with col_reset:
            if st.button("🔄 Reset Selezione", use_container_width=True, type="primary"):
                st.rerun()

        # Generazione dinamica dei pulsanti divisi per Area
        selected_features = []
        
        for cat in categories:
            with st.expander(f"🔹 {cat}", expanded=True):
                # Filtriamo le feature appartenenti a questa categoria
                cat_features = df[df['Feature Category'] == cat]['Feature'].tolist()
                
                # Distribuiamo le feature su più colonne all'interno dell'expander
                cols = st.columns(4)
                for i, feat in enumerate(cat_features):
                    with cols[i % 4]:
                        if st.checkbox(feat, key=f"check_{feat}"):
                            selected_features.append(feat)

        st.divider()

        # Area Visualizzazione Risultati
        st.subheader("Modelli Corrispondenti")
        cols_res = st.columns(len(model_names))

        for idx, model in enumerate(model_names):
            is_compatible = True
            for f in selected_features:
                val = df[df['Feature'] == f][model].values[0]
                # Se la cella contiene '✗', il modello non è compatibile
                if str(val) == '✗':
                    is_compatible = False
                    break
            
            with cols_res[idx]:
                if not selected_features:
                    # Stato iniziale: tutto in grigio
                    st.markdown(f"<div style='color: #666; text-align: center; border: 1px solid #333; padding: 10px; border-radius: 8px; font-size: 0.8em;'>{model}</div>", unsafe_allow_html=True)
                elif is_compatible:
                    # Modello "Illuminato"
                    st.markdown(f"<div style='color: white; background-color: #007bff; text-align: center; border: 2px solid #00d4ff; padding: 10px; border-radius: 8px; font-weight: bold; box-shadow: 0px 0px 15px rgba(0,123,255,0.6);'>{model}</div>", unsafe_allow_html=True)
                else:
                    # Modello non compatibile: quasi invisibile
                    st.markdown(f"<div style='color: #222; text-align: center; border: 1px solid #111; padding: 10px; border-radius: 8px; opacity: 0.2;'>{model}</div>", unsafe_allow_html=True)

    with tab2:
        st.header("Le migliori schede per tipo di progetto")
        st.caption("Analisi basata sulle tendenze hardware del 2026")

        # Layout a card per i consigli
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
        # Ripristino del link video
        st.markdown("### 🎥 Approfondimento Video")
        st.video("https://www.youtube.com/watch?v=CfIjInYch7U")
        st.write("Guarda la guida completa di **DroneBot Workshop** per i dettagli su ogni variante.")

# CSS per pulire l'estetica degli expander e checkbox
st.markdown("""
    <style>
    .streamlit-expanderHeader {
        background-color: #121212;
        border-radius: 5px;
    }
    .stCheckbox {
        padding: 2px;
    }
    </style>
    """, unsafe_allow_html=True)