import streamlit as st
import pandas as pd

# Configurazione Pagina
st.set_page_config(page_title="ESP32 Expert Selector 2026", layout="wide")

# --- LOGICA RESET AVANZATA ---
# Funzione per pulire tutti i widget salvati nello stato della sessione
def reset_all_filters():
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

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

    # --- HEADER FISSO (STRETTAMENTE CONTROLLATO) ---
    # Creiamo un contenitore che resterà bloccato in alto
    header_container = st.container()

    # Inizializziamo il dizionario dei filtri
    active_filters = {}

    # --- SEZIONE FILTRI (SOTTO L'HEADER) ---
    tab1, tab2 = st.tabs(["🎯 Filtro Tecnico Avanzato", "📚 Consigli d'Uso"])

    with tab1:
        # Pulsante Reset con nuova logica
        col_t, col_r = st.columns([4, 1])
        with col_r:
            st.button("🔄 Reset Selezione", use_container_width=True, type="primary", on_click=reset_all_filters)

        # Generazione dei filtri
        for section in main_sections:
            cat_rows = df[df['Feature Category'] == section]
            if not cat_rows.empty:
                with st.expander(f"📂 {section}", expanded=True):
                    for _, row in cat_rows.iterrows():
                        feat_label = row['Feature']
                        
                        # Pulizia valori unici (escludendo ✗)
                        possible_values = sorted(list(set([str(row[m]).strip() for m in model_names if str(row[m]).strip() not in ['✗', 'nan', '', 'None']])))
                        
                        if possible_values:
                            # Usiamo il parametro 'key' collegato alla sessione per il reset
                            res = st.pills(feat_label, possible_values, key=f"pill_{feat_label}")
                            if res:
                                active_filters[feat_label] = res

    # --- AGGIORNAMENTO HEADER FISSO ---
    with header_container:
        st.title("🛠️ ESP32 Smart Configurator")
        st.write("I modelli si illuminano in tempo reale in base ai filtri selezionati sotto.")
        
        # Grid per i modelli nell'header
        cols_res = st.columns(len(model_names))
        for idx, model in enumerate(model_names):
            is_compatible = True
            for f_name, f_val in active_filters.items():
                model_val = str(df[df['Feature'] == f_name][model].values[0]).strip()
                if model_val != f_val:
                    is_compatible = False
                    break
            
            with cols_res[idx]:
                style = "text-align: center; padding: 10px; border-radius: 8px; min-height: 55px; display: flex; align-items: center; justify-content: center; border: 1px solid "
                if not active_filters:
                    st.markdown(f"<div style='{style} #333; color: #666; font-size: 0.75rem;'>{model}</div>", unsafe_allow_html=True)
                elif is_compatible:
                    st.markdown(f"<div style='{style} #00d4ff; background-color: #007bff; color: white; font-weight: bold; box-shadow: 0px 0px 12px rgba(0,123,255,0.7); font-size: 0.75rem;'>{model}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='{style} #111; color: #222; opacity: 0.1; font-size: 0.75rem;'>{model}</div>", unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    with tab2:
        # Sezione Consigli
        rec_cat = {"Sperimentazione": ["ESP32-S3", "ESP32-C6", "ESP32-C5"], "Multimedia": ["ESP32-P4", "ESP32-S3", "Waveshare S3"], "Smart Home": ["ESP32-C6", "ESP32-H2", "ESP32-C5"], "Budget": ["ESP32-C3", "ESP32", "XIAO C3"]}
        sel = st.radio("Seleziona area:", list(rec_cat.keys()), horizontal=True)
        c1, c2, c3 = st.columns(3)
        picks = rec_cat[sel]
        with c1: st.info(f"🥇 {picks[0]}")
        with c2: st.info(f"🥈 {picks[1]}")
        with c3: st.info(f"🥉 {picks[2]}")
        st.video("https://www.youtube.com/watch?v=CfIjInYch7U")

# --- CSS FIX: Z-INDEX E STICKY ---
st.markdown("""
    <style>
    /* Forza l'header a stare sopra tutto con sfondo pieno */
    [data-testid="stVerticalBlock"] > div:first-child {
        position: sticky;
        top: 0;
        background-color: #0e1117; /* Colore di sfondo scuro di Streamlit */
        z-index: 1000;
        padding-top: 10px;
        border-bottom: 2px solid #333;
    }
    
    /* Gestione spazio expander */
    .stExpander { border: none !important; border-bottom: 1px solid #222 !important; }
    
    /* Testo delle etichette filtri */
    [data-testid="stMarkdownContainer"] p { font-size: 0.8rem; font-weight: bold; color: #ddd; }
    
    /* Fix per sovrapposizione pills durante lo scroll */
    [data-testid="stExpander"] {
        z-index: 1;
    }
    </style>
    """, unsafe_allow_html=True)