import streamlit as st
import pandas as pd

# Caricamento dati dal file Excel (convertito in CSV per comodità nel codice)
def load_data():
    # Carica il foglio della matrice (ESP32-Feature-Matrix-2026.csv)
    df = pd.read_csv('ESP32-Feature-Matrix-2026.xlsx - ESP32 Feature Matrix.csv')
    return df

df = load_data()

st.title("ESP32 Selector Assistant 2026")

tab1, tab2 = st.tabs(["Filtro Caratteristiche", "Consigli per Utilizzo"])

with tab1:
    st.header("Seleziona le caratteristiche richieste")
    
    # Filtri basati sulle righe del tuo Excel
    wifi_req = st.multiselect("Standard Wi-Fi", ["Wi-Fi 4", "Wi-Fi 6", "5 GHz Support"])
    cpu_req = st.radio("Core CPU", ["Qualsiasi", "Single", "Dual"])
    peripherals = st.multiselect("Periferiche Necessarie", ["USB OTG", "Matter Support", "AI / Vector Instructions", "Touch Switches"])

    # Logica di filtraggio (semplificata per l'esempio)
    # Nota: nel tuo file le colonne sono i modelli (ESP32-S3, C6, ecc.)
    model_cols = df.columns[2:] # Salta 'Feature Category' e 'Feature'
    
    st.subheader("Modelli Compatibili:")
    # Qui il codice analizzerebbe le righe corrispondenti alle feature scelte
    st.write("In base alla tua selezione, i modelli più indicati sono evidenziati nella matrice sottostante.")
    st.dataframe(df)

with tab2:
    st.header("Le migliori schede per tipo di progetto")
    st.caption("Basato sulle raccomandazioni di DroneBot Workshop (2026)")

    # Definizione delle categorie basate sul video [00:13:17 - 00:39:02]
    categories = {
        "Sperimentazione / Uso Generale": {
            "Scelta #1": "ESP32-S3 (Il più versatile, molti GPIO, acceleratore AI)",
            "Scelta #2": "ESP32-C6 (Per chi vuole Wi-Fi 6 e protocolli moderni)",
            "Scelta #3": "ESP32-C5 (Unico con Wi-Fi a 5GHz)"
        },
        "Multimedia / Display / AI": {
            "Scelta #1": "ESP32-P4 (Potentissimo, 400MHz, supporto H.264, ma richiede chip companion per Wi-Fi)",
            "Scelta #2": "ESP32-S3 (Ottimo per telecamere e display LCD standard)",
            "Scelta #3": "Waveshare ESP32-S3 Touch LCD (Modulo pronto all'uso con display 2\")"
        },
        "Smart Home / IoT (Basso Consumo)": {
            "Scelta #1": "ESP32-C6 (Supporto nativo Matter, Zigbee e Thread)",
            "Scelta #2": "ESP32-H2 (Ideale come endpoint Zigbee/Thread, senza Wi-Fi per risparmio energetico)",
            "Scelta #3": "ESP32-C5 (Per ambienti IoT affollati grazie ai 5GHz)"
        },
        "Budget / Principianti": {
            "Scelta #1": "ESP32-C3 (Il miglior rapporto qualità/prezzo su architettura RISC-V)",
            "Scelta #2": "ESP32 (Originale) (Economico e con supporto Bluetooth Classic)",
            "Scelta #3": "Seeed Studio XIAO Series (Form factor piccolissimo e costi ridotti)"
        }
    }

    selected_cat = st.selectbox("Seleziona la tua categoria di progetto:", list(categories.keys()))
    
    col1, col2, col3 = st.columns(3)
    cat_data = categories[selected_cat]
    
    with col1:
        st.success("**TOP 1**")
        st.write(cat_data["Scelta #1"])
    with col2:
        st.info("**TOP 2**")
        st.write(cat_data["Scelta #2"])
    with col3:
        st.warning("**TOP 3**")
        st.write(cat_data["Scelta #3"])

    st.markdown("---")
    st.markdown(f"[Guarda il video originale per approfondire](https://www.youtube.com/watch?v=CfIjInYch7U&t=1407s)")