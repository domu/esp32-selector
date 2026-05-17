import streamlit as st
import pandas as pd

# Configurazione Pagina
st.set_page_config(page_title="ESP32 Expert Selector 2026", layout="wide")

# --- GESTIONE STATO E RESET ---
if 'form_id' not in st.session_state:
    st.session_state.form_id = 0

def trigger_reset():
    st.session_state.form_id += 1
    for key in list(st.session_state.keys()):
        if key.startswith("pill_"):
            del st.session_state[key]
    st.rerun()

def select_board_features(model_name, df):
    st.session_state.form_id += 1
    for _, row in df.iterrows():
        feat_label = row['Feature']
        val = str(row[model_name]).strip()
        if val not in ['✗', 'nan', '', 'None']:
            st.session_state[f"pill_{feat_label}"] = val

def load_data():
    nome_file = "ESP32_Feature_Matrix_2026.csv"
    try:
        df = pd.read_csv(nome_file)
        df.columns = [c.replace('\n', ' ').strip() for c in df.columns]
        df['Feature Category'] = df['Feature Category'].ffill().str.strip()
        df['Feature'] = df['Feature'].str.strip()
        return df
    except:
        st.error("Assicurati che il file 'ESP32_Feature_Matrix_2026.csv' sia nel repository.")
        return None

df = load_data()

if df is not None:
    model_names = df.columns[2:]
    sections = ["ARCHITECTURE", "WIRELESS", "COMMON PERIPHERALS", "ANALOG", "USB & HIGH-SPEED", "DISPLAY & CAMERA", "SECURITY", "STATUS"]

    # --- CSS PER LAYOUT COMPATTO ---
    st.markdown("""
        <style>
        [data-testid="stColumn"]:nth-child(1) { width: 68% !important; }
        [data-testid="stColumn"]:nth-child(2) { 
            position: fixed; right: 1%; top: 40px; width: 28% !important;
            background: #0e1117; z-index: 1000; padding: 10px;
            border-left: 1px solid #333; height: 95vh; overflow-y: auto;
        }
        .board-box {
            display: flex; justify-content: space-between; align-items: center;
            padding: 4px 10px; border: 1px solid #444; border-radius: 4px;
            background: #161b22; margin-bottom: 2px;
        }
        .comp-tag {
            background: #007bff; color: white; font-size: 0.6rem;
            padding: 1px 5px; border-radius: 3px; font-weight: bold;
        }
        .stButton button { padding: 2px 10px; font-size: 0.8rem; }
        </style>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([0.7, 0.3])

    active_filters = {}

    with col_left:
        st.title("🛠️ ESP32 Selector")
        # Il contenitore cambia ID al reset, forzando la pulizia visiva
        with st.container(key=f"main_form_{st.session_state.form_id}"):
            t1, t2 = st.tabs(["🎯 Selezione", "📚 Consigli"])
            
            with t1:
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
            
            with t2:
                recs = {
                    "General / DIY": ["ESP32-S3", "ESP32-C6", "ESP32-C5"],
                    "AI / Display": ["ESP32-P4", "ESP32-S3", "LilyGo S3"],
                    "IoT / Matter": ["ESP32-C6", "ESP32-H2", "ESP32-C5"],
                    "Low Cost": ["ESP32-C3", "ESP32 Original", "ESP32-C2"]
                }
                cat = st.radio("Ambito:", list(recs.keys()), horizontal=True)
                c1, c2, c3 = st.columns(3)
                with c1: st.info(f"🥇 **Oro**\n\n{recs[cat][0]}")
                with c2: st.info(f"🥈 **Argento**\n\n{recs[cat][1]}")
                with c3: st.info(f"🥉 **Bronzo**\n\n{recs[cat][2]}")
                st.video("https://www.youtube.com/watch?v=CfIjInYch7U")

    with col_right:
        st.button("🔄 Reset Filtri", use_container_width=True, type="primary", on_click=trigger_reset)
        st.write("### Board Status")
        
        for m in model_names:
            match = True
            for f, v in active_filters.items():
                if str(df[df['Feature'] == f][m].values[0]).strip() != v:
                    match = False; break
            
            active = match and active_filters
            opac = "1.0" if (active or not active_filters) else "0.2"
            
            st.markdown(f"""
                <div class="board-box" style="opacity: {opac}; border-color: {'#00d4ff' if active else '#333'};">
                    <span style="font-size: 0.8rem; font-weight: bold;">{m}</span>
                    {"<span class='comp-tag'>✓ OK</span>" if active else ""}
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Carica {m}", key=f"btn_{m}", use_container_width=True):
                select_board_features(m, df)
                st.rerun()