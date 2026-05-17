import streamlit as st
import pandas as pd

# Configurazione pagina per un look più "Dark Mode" professionale
st.set_page_config(page_title="ESP32 Advisor 2026", layout="wide")

def load_data():
    nome_file = "ESP32_Feature_Matrix_2026.csv"
    try:
        # Pulizia nomi colonne per gestire eventuali ritorni a capo nel CSV
        df = pd.read_csv(nome_file)
        df.columns = [c.replace('\n', ' ') for c in df.columns]
        return df
    except:
        st.error("File CSV non trovato. Carica 'ESP32_Feature_Matrix_2026.csv' su GitHub.")
        return None

df = load_data()

if df is not None:
    # Estraiamo l'elenco delle caratteristiche (righe) e dei modelli (colonne)
    features_list = df['Feature'].unique().tolist()
    model_names = df.columns[2:] # Esclude le prime due colonne descrittive

    st.title("🛠️ ESP32 Smart Selector")
    
    tab1, tab2 = st.tabs(["🎯 Configurazione Dinamica", "📚 Consigli d'Uso"])

    with tab1:
        st.subheader("Seleziona le caratteristiche desiderate:")
        
        # Creazione dei pulsanti grafici (Toggle)
        # Usiamo le "columns" di Streamlit per distribuire i pulsanti
        cols_buttons = st.columns(4)
        selected_features = []
        
        for i, feature in enumerate(features_list):
            with cols_buttons[i % 4]:
                if st.checkbox(feature, key=f"feat_{i}"):
                    selected_features.append(feature)

        st.divider()

        # Visualizzazione Modelli con logica di colore
        st.subheader("Risultato Selezione:")
        cols_models = st.columns(len(model_names))

        for idx, model in enumerate(model_names):
            # Verifichiamo se il modello soddisfa TUTTE le caratteristiche selezionate
            is_compatible = True
            for f in selected_features:
                # Recuperiamo il valore (✓, ✗, o testo) per quella specifica cella
                val = df[df['Feature'] == f][model].values[0]
                if str(val) == '✗' or str(val).lower() == 'nan':
                    is_compatible = False
                    break
            
            with cols_models[idx]:
                if not selected_features:
                    # Se nulla è selezionato, mostriamo tutto in grigio neutro
                    st.markdown(f"<div style='color: #555; text-align: center; border: 1px solid #333; padding: 10px; border-radius: 5px;'>{model}</div>", unsafe_allow_html=True)
                elif is_compatible:
                    # Se compatibile, "illumina" il modello
                    st.markdown(f"<div style='color: white; background-color: #007bff; text-align: center; border: 1px solid #007bff; padding: 10px; border-radius: 5px; font-weight: bold; box-shadow: 0px 0px 10px #007bff;'>{model}</div>", unsafe_allow_html=True)
                else:
                    # Se non compatibile, grigio chiaro/trasparente
                    st.markdown(f"<div style='color: #222; text-align: center; border: 1px solid #111; padding: 10px; border-radius: 5px; opacity: 0.3;'>{model}</div>", unsafe_allow_html=True)

    with tab2:
        # Manteniamo la tua sezione perfetta, adeguando leggermente i colori
        st.header("Le migliori schede per tipo di progetto")
        st.caption("Consigli basati sulla guida DroneBot Workshop 2026")

        categories = {
            "Sperimentazione / Uso Generale": ["ESP32-S3", "ESP32-C6", "ESP32-C5"],
            "Multimedia / Display / AI": ["ESP32-P4", "ESP32-S3", "Waveshare S3 LCD"],
            "Smart Home (Matter/Zigbee)": ["ESP32-C6", "ESP32-H2", "ESP32-C5"],
            "Budget / Educational": ["ESP32-C3", "ESP32 Original", "XIAO Series"]
        }

        sel_cat = st.radio("Scegli il tuo obiettivo:", list(categories.keys()), horizontal=True)
        
        c1, c2, c3 = st.columns(3)
        picks = categories[sel_cat]
        
        with c1: st.info(f"🥇 **Top 1**\n\n{picks[0]}")
        with c2: st.info(f"🥈 **Top 2**\n\n{picks[1]}")
        with c3: st.info(f"🥉 **Top 3**\n\n{picks[2]}")

# CSS Custom per migliorare l'estetica generale
st.markdown("""
    <style>
    .stCheckbox {
        background-color: #1e1e1e;
        padding: 5px 10px;
        border-radius: 15px;
        border: 1px solid #333;
        margin-bottom: 5px;
    }
    </style>
    """, unsafe_allow_html=True)