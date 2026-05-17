import streamlit as st
import pandas as pd
from datetime import datetime

# Configurazione Pagina
st.set_page_config(page_title="ESP32 Expert Selector 2026", layout="wide")

# --- TIMESTAMP E DATI ---
# Aggiorna qui la data ogni volta che modifichi il file
GEN_TIMESTAMP = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

if 'form_id' not in st.session_state:
    st.session_state.form_id = 0
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0 # Usiamo l'indice per i tab

# --- LOGICA RESET E NAVIGAZIONE ---
def deep_reset():
    # Pulisce tutto lo stato e la cache
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.cache_data.clear()
    st.rerun()

def select_and_jump(model_name, df):
    # 1. Pulisce lo stato precedente per evitare l'errore StreamlitAPIException
    for key in list(st.session_state.keys()):
        if key.startswith("pill_"):
            del st.session_state[key]
    
    # 2. Imposta i nuovi valori basati sulla board scelta
    for _, row in df.iterrows():
        feat_label = str(row['Feature']).strip()
        val = str(row[model_name]).strip()
        if val not in ['✗', 'nan', '', 'None']:
            st.session_state[f"pill_{feat_label}"] = val
    
    # 3. Forza il ritorno al primo Tab e resetta l'ID grafico
    st.session_state.active_tab = 0
    st.session_state.form_id += 1
    st.rerun()

def load_data():
    nome_file = "ESP32_Feature_Matrix_2026.csv"
    try:
        df = pd.read_csv(nome_file)
        df.columns = [c.replace('\n', ' ').strip() for c in df.columns]
        df['Feature Category'] = df['Feature Category'].ffill().str.strip()
        df['Feature'] = df['Feature'].str.strip()
        return df
    except:
        st.error(f"Errore: File '{nome_file}' non trovato.")
        return None

df = load_data()

if df is not None:
    model_names = df.columns[2:]
    sections = ["ARCHITECTURE", "WIRELESS", "COMMON PERIPHERALS", "ANALOG", "USB & HIGH-SPEED", "DISPLAY & CAMERA", "SECURITY", "STATUS"]

    # --- CSS PER LAYOUT ---
    st.markdown("""
        <style>
        /* Stile per le board a destra */
        .board-card {
            display: flex; justify-content: space-between; align-items: center;
            padding: 6px 12px; border: 1px solid #444; border-radius: 6px;
            background: #161b22; margin-bottom: 4px;
        }
        .tag-ok {
            background: #007bff; color: white; font-size: 0.65rem;
            padding: 2px 6px; border-radius: 4px; font-weight: bold;
        }
        /* Footer Sticky */
        .custom-footer {
            position: fixed; left: 0; bottom: 0; width: 100%;
            background-color: #0e1117; text-align: center;
            padding: 10px; font-size: 0.8rem; border-top: 1px solid #333;
            z-index: 1001; color: #888;
        }
        /* Fix per colonna fissa che non deve coprire i tab */
        [data-testid="stColumn"]:nth-child(2) {
            position: sticky; top: 10px; height: fit-content;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- NAVIGAZIONE TAB ---
    tab_titles = ["🎯 Selezione Caratteristiche", "📚 Consigli d'Utilizzo"]
    st.session_state.active_tab = st.tabs(tab_titles)
    
    active_filters = {}

    # --- TAB 1: SELEZIONE ---
    with st.session_state.active_tab[0]:
        # Layout a due colonne solo qui
        col_left, col_right = st.columns([0.7, 0.3])
        
        with col_left:
            st.title("🛠️ ESP32 Smart Selector")
            # Il container con form_id garantisce che al reset i pulsanti tornino grigi
            with st.container(key=f"ui_form_{st.session_state.form_id}"):
                for sec in sections:
                    rows = df[df['Feature Category'] == sec]
                    if not rows.empty:
                        with st.expander(f"📂 {sec}", expanded=True):
                            for _, r in rows.iterrows():
                                f_label = r['Feature']
                                opts = sorted(list(set([str(r[m]).strip() for m in model_names if str(r[m]).strip() not in ['✗', 'nan', '']])))
                                if opts:
                                    sel = st.pills(f_label, opts, key=f"pill_{f_label}")
                                    if sel: active_filters[f_label] = sel

        with col_right:
            st.button("🔄 Reset Totale Visivo", use_container_width=True, type="primary", on_click=deep_reset)
            st.write("### 📱 Board Status")
            
            for m in model_names:
                match = True
                for f, v in active_filters.items():
                    if str(df[df['Feature'] == f][m].values[0]).strip() != v:
                        match = False; break
                
                is_active = match and active_filters
                opac = "1.0" if (is_active or not active_filters) else "0.15"
                
                st.markdown(f"""
                    <div class="board-card" style="opacity: {opac}; border-color: {'#00d4ff' if is_active else '#333'};">
                        <span style="font-size: 0.85rem; font-weight: bold;">{m}</span>
                        {"<span class='tag-ok'>✓ COMPATIBILE</span>" if is_active else ""}
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Analizza {m}", key=f"btn_side_{m}", use_container_width=True):
                    select_and_jump(m, df)

    # --- TAB 2: CONSIGLI (PAGINA INTERA SENZA COLONNA BOARD) ---
    with st.session_state.active_tab[1]:
        st.title("💡 Raccomandazioni Strategiche")
        st.write("Seleziona una categoria per vedere i modelli suggeriti e clicca sul nome per caricarne i dettagli tecnici.")
        
        recs = {
            "General / DIY": ["ESP32-S3", "ESP32-C6", "ESP32-C5"],
            "AI / Multimedia": ["ESP32-P4", "ESP32-S3", "ESP32 (Original)"],
            "IoT / Automation": ["ESP32-C6", "ESP32-H2", "ESP32-C5"],
            "Budget / Low Power": ["ESP32-C3", "ESP32-C2", "ESP32-S2"]
        }
        
        cat_choice = st.radio("Seleziona ambito d'uso:", list(recs.keys()), horizontal=True)
        st.write("")
        
        c1, c2, c3 = st.columns(3)
        p = recs[cat_choice]
        
        # Pulsanti interattivi Oro, Argento, Bronzo
        with c1:
            if st.button(f"🥇 ORO\n\n{p[0]}", use_container_width=True, type="primary", key="gold_btn"):
                select_and_jump(p[0], df)
        with c2:
            if st.button(f"🥈 ARGENTO\n\n{p[1]}", use_container_width=True, key="silver_btn"):
                select_and_jump(p[1], df)
        with c3:
            if st.button(f"🥉 BRONZO\n\n{p[2]}", use_container_width=True, key="bronze_btn"):
                select_and_jump(p[2], df)
        
        st.divider()
        st.subheader("🎥 Approfondimento DroneBot Workshop")
        st.video("https://www.youtube.com/watch?v=CfIjInYch7U")

    # --- FOOTER COPYRIGHT ---
    st.markdown(f"""
        <div class="custom-footer">
            © 2026 Davide Pedretti Biagioni | CC: <a href="https://www.youtube.com/@Dronebotworkshop" style="color: #007bff; text-decoration: none;">Dronebot Workshop</a> | Generato il: {GEN_TIMESTAMP}
        </div>
    """, unsafe_allow_html=True)