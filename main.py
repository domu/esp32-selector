import streamlit as st
import pandas as pd
from datetime import datetime

# Configurazione Pagina
st.set_page_config(page_title="ESP32 Expert Selector 2026", layout="wide")

# --- TIMESTAMP DI GENERAZIONE ---
# Questo valore viene aggiornato ogni volta che il file viene salvato/generato
GEN_TIMESTAMP = "18/05/2026 10:45:00"

# --- LOGICA RESET E CACHE ---
def deep_reset():
    # Pulisce la cache di sistema di Streamlit
    st.cache_data.clear()
    st.cache_resource.clear()
    # Reset dello stato dei widget
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

def select_board_features(model_name, df):
    # Reset preventivo per caricare la nuova scheda
    for key in list(st.session_state.keys()):
        if key.startswith("pill_"):
            del st.session_state[key]
    
    for _, row in df.iterrows():
        feat_label = row['Feature']
        val = str(row[model_name]).strip()
        if val not in ['✗', 'nan', '', 'None']:
            st.session_state[f"pill_{feat_label}"] = val
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
        st.error("Errore: File CSV non trovato.")
        return None

df = load_data()

if df is not None:
    model_names = df.columns[2:]
    sections = ["ARCHITECTURE", "WIRELESS", "COMMON PERIPHERALS", "ANALOG", "USB & HIGH-SPEED", "DISPLAY & CAMERA", "SECURITY", "STATUS"]

    # --- CSS PERSONALIZZATO ---
    st.markdown(f"""
        <style>
        .board-box {{
            display: flex; justify-content: space-between; align-items: center;
            padding: 6px 12px; border: 1px solid #444; border-radius: 6px;
            background: #161b22; margin-bottom: 4px;
        }}
        .comp-tag {{
            background: #007bff; color: white; font-size: 0.65rem;
            padding: 2px 6px; border-radius: 4px; font-weight: bold;
        }}
        footer {{visibility: hidden;}}
        .custom-footer {{
            position: fixed; left: 0; bottom: 0; width: 100%;
            background-color: #0e1117; text-align: center;
            padding: 10px; font-size: 0.8rem; border-top: 1px solid #333;
            z-index: 999;
        }}
        </style>
    """, unsafe_allow_html=True)

    # --- TITOLO CON TIMESTAMP ---
    st.title(f"🛠️ ESP32 Selector")
    st.caption(f"Ultima generazione: {GEN_TIMESTAMP}")

    # Definizione dei Tab
    tab_selection, tab_tips = st.tabs(["🎯 Selezione Caratteristiche", "📚 Consigli d'Utilizzo"])

    active_filters = {}

    # --- TAB 1: SELEZIONE (CON COLONNA BOARD) ---
    with tab_selection:
        col_left, col_right = st.columns([0.7, 0.3])
        
        with col_left:
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
            st.button("🔄 Reset Profondo (Clear Cache)", use_container_width=True, type="primary", on_click=deep_reset)
            st.write("### 📱 Board Status")
            
            for m in model_names:
                match = True
                for f, v in active_filters.items():
                    if str(df[df['Feature'] == f][m].values[0]).strip() != v:
                        match = False
                        break
                
                is_active = match and active_filters
                opac = "1.0" if (is_active or not active_filters) else "0.2"
                
                st.markdown(f"""
                    <div class="board-box" style="opacity: {opac}; border-color: {'#00d4ff' if is_active else '#333'};">
                        <span style="font-size: 0.85rem; font-weight: bold;">{m}</span>
                        {"<span class='comp-tag'>✓ OK</span>" if is_active else ""}
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Carica {m}", key=f"btn_{m}", use_container_width=True):
                    select_board_features(m, df)

    # --- TAB 2: CONSIGLI (A PAGINA INTERA) ---
    with tab_tips:
        st.subheader("💡 Raccomandazioni Strategiche")
        recs = {
            "General / DIY": ["ESP32-S3", "ESP32-C6", "ESP32-C5"],
            "AI / Multimedia": ["ESP32-P4", "ESP32-S3", "LilyGo S3"],
            "IoT / Matter": ["ESP32-C6", "ESP32-H2", "ESP32-C5"],
            "Low Cost": ["ESP32-C3", "ESP32 (Original)", "ESP32-C2"]
        }
        
        cat = st.radio("Scegli ambito:", list(recs.keys()), horizontal=True)
        st.write("")
        
        c1, c2, c3 = st.columns(3)
        with c1: st.success(f"🥇 **ORO**\n\n{recs[cat][0]}")
        with c2: st.info(f"🥈 **ARGENTO**\n\n{recs[cat][1]}")
        with c3: st.warning(f"🥉 **BRONZO**\n\n{recs[cat][2]}")
        
        st.divider()
        st.video("https://www.youtube.com/watch?v=CfIjInYch7U")

    # --- FOOTER COPYRIGHT ---
    st.markdown(f"""
        <div class="custom-footer">
            © 2026 Davide Pedretti Biagioni | CC: <a href="https://www.youtube.com/@Dronebotworkshop" style="color: #007bff;">Dronebot Workshop</a>
        </div>
    """, unsafe_allow_html=True)