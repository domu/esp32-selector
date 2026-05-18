import streamlit as st
import pandas as pd
from datetime import datetime

# Configurazione Pagina
st.set_page_config(page_title="ESP32 Expert Selector 2026", layout="wide")

# --- TIMESTAMP ---
GEN_TIMESTAMP = "18/05/2026 15:45:00"

# --- LOGICA NUCLEARE DI RESET ---
if 'app_reset_id' not in st.session_state:
    st.session_state.app_reset_id = 0
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Selezione"
if 'active_board' not in st.session_state:
    st.session_state.active_board = None

def nuclear_reset():
    """Distrugge l'intera sessione e cambia l'ID dell'app"""
    for key in list(st.session_state.keys()):
        if key != 'app_reset_id': # Manteniamo solo l'ID di reset
            del st.session_state[key]
    st.session_state.app_reset_id += 1
    st.session_state.current_page = "Selezione"
    st.session_state.active_board = None
    st.rerun()

def select_board_logic(model_name, df):
    """Carica i dati o resetta se è la stessa board"""
    if st.session_state.active_board == model_name:
        nuclear_reset()
    else:
        # Pulizia prima del caricamento
        for key in list(st.session_state.keys()):
            if key.startswith("pill_"):
                del st.session_state[key]
        
        # Caricamento nuovi dati
        st.session_state.active_board = model_name
        for _, row in df.iterrows():
            f_label = str(row['Feature']).strip()
            val = str(row[model_name]).strip()
            if val not in ['✗', 'nan', '', 'None']:
                st.session_state[f"pill_{f_label}"] = val
        
        st.session_state.app_reset_id += 1 # Forza ricostruzione visiva
        st.rerun()

# --- CARICAMENTO DATI ---
def load_data():
    nome_file = "ESP32_Feature_Matrix_2026.csv"
    try:
        df = pd.read_csv(nome_file)
        df.columns = [c.replace('\n', ' ').strip() for c in df.columns]
        df['Feature Category'] = df['Feature Category'].ffill().str.strip()
        df['Feature'] = df['Feature'].str.strip()
        return df
    except Exception as e:
        st.error(f"Errore caricamento CSV: {e}")
        return None

df = load_data()

if df is not None:
    model_names = df.columns[2:]

    # --- CSS ---
    st.markdown(f"""
        <style>
        .board-line {{
            display: flex; justify-content: space-between; align-items: center;
            padding: 4px 10px; border: 1px solid #333; border-radius: 6px;
            background: #161b22; margin-bottom: 5px;
        }}
        .board-name {{ font-size: 0.85rem; font-weight: bold; flex-grow: 1; }}
        .status-ok {{ color: #007bff; font-weight: bold; font-size: 0.75rem; margin-right: 15px; }}
        /* Pulsante piccolo per la lista laterale */
        div[data-testid="column"] button p {{ font-size: 0.7rem !important; }}
        .feature-table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        .feature-table td, .feature-table th {{ border: 1px solid #333; padding: 8px; font-size: 0.8rem; }}
        .feature-table th {{ background: #007bff; color: white; }}
        .footer {{ position: fixed; left: 0; bottom: 0; width: 100%; background: #0e1117; color: #555; text-align: center; padding: 10px; font-size: 0.7rem; border-top: 1px solid #333; z-index: 999; }}
        </style>
    """, unsafe_allow_html=True)

    # --- CONTENITORE GLOBALE (LA CHIAVE AGGRESSIVA) ---
    with st.container(key=f"global_app_v{st.session_state.app_reset_id}"):
        
        st.title("🛠️ ESP32 Smart Selector")
        
        # NAVIGAZIONE
        n1, n2, n3 = st.columns(3)
        with n1:
            if st.button("🎯 Selezione", type="primary" if st.session_state.current_page == "Selezione" else "secondary"):
                st.session_state.current_page = "Selezione"; st.rerun()
        with n2:
            if st.button("📚 Consigli", type="primary" if st.session_state.current_page == "Consigli" else "secondary"):
                st.session_state.current_page = "Consigli"; st.rerun()
        with n3:
            if st.button("🔗 Link", type="primary" if st.session_state.current_page == "Links" else "secondary"):
                st.session_state.current_page = "Links"; st.rerun()

        active_filters = {}

        # 1. PAGINA SELEZIONE
        if st.session_state.current_page == "Selezione":
            col_l, col_r = st.columns([0.7, 0.3])
            
            with col_l:
                sections = ["ARCHITECTURE", "WIRELESS", "COMMON PERIPHERALS", "ANALOG", "USB & HIGH-SPEED", "DISPLAY & CAMERA", "SECURITY"]
                for sec in sections:
                    rows = df[df['Feature Category'] == sec]
                    if not rows.empty:
                        with st.expander(f"📂 {sec}", expanded=True):
                            sub_cols = st.columns(3)
                            for i, (_, r) in enumerate(rows.iterrows()):
                                f_label = r['Feature']
                                opts = sorted(list(set([str(r[m]).strip() for m in model_names if str(r[m]).strip() not in ['✗', 'nan', '']])))
                                if opts:
                                    with sub_cols[i % 3]:
                                        sel = st.pills(f_label, opts, key=f"pill_{f_label}")
                                        if sel: active_filters[f_label] = sel

            with col_r:
                if st.button("🔄 RESET TOTALE", type="primary", use_container_width=True):
                    nuclear_reset()
                
                st.write("### 📱 ESP32 Boards")
                for m in model_names:
                    # Logica compatibilità
                    match = True
                    for f, v in active_filters.items():
                        if str(df[df['Feature'] == f][m].values[0]).strip() != v:
                            match = False; break
                    
                    comp = match and active_filters
                    is_active = (st.session_state.active_board == m)
                    opac = "1.0" if (comp or not active_filters or is_active) else "0.2"
                    
                    st.markdown(f'<div class="board-line" style="opacity: {opac}; border-color: {"#007bff" if is_active else "#333"};">', unsafe_allow_html=True)
                    cl1, cl2, cl3 = st.columns([0.5, 0.2, 0.3])
                    with cl1: st.markdown(f'<span class="board-name">{m}</span>', unsafe_allow_html=True)
                    with cl2: 
                        if comp: st.markdown('<span class="status-ok">✓ OK</span>', unsafe_allow_html=True)
                    with cl3:
                        btn_label = "Cancella" if is_active else "Carica"
                        if st.button(btn_label, key=f"btn_nav_{m}"):
                            select_board_logic(m, df)
                    st.markdown('</div>', unsafe_allow_html=True)

        # 2. PAGINA CONSIGLI
        elif st.session_state.current_page == "Consigli":
            st.subheader("💡 Top Recommendations")
            recs = {
                "General": ["ESP32-S3", "ESP32-C6", "ESP32-C5 (NEW)"],
                "AI/Display": ["ESP32-P4 (NEW)", "ESP32-S3", "ESP32 (Original)"],
                "IoT/Matter": ["ESP32-C6", "ESP32-H2", "ESP32-C5 (NEW)"],
                "Budget": ["ESP32-C3", "ESP32-C2", "ESP32-S2"]
            }
            cat = st.radio("Ambito:", list(recs.keys()), horizontal=True)
            c_recs = st.columns(3)
            for i, board in enumerate(recs[cat]):
                with c_recs[i]:
                    label = ["🥇 ORO", "🥈 ARGENTO", "🥉 BRONZO"][i]
                    if st.button(f"{label}: {board}"):
                        st.session_state.selected_rec = board
            
            if 'selected_rec' in st.session_state:
                m_sel = st.session_state.selected_rec
                st.write(f"#### Specifiche: {m_sel}")
                b_df = df[['Feature Category', 'Feature', m_sel]]
                b_df = b_df[~b_df[m_sel].isin(['✗', 'nan', 'None', ''])]
                st.table(b_df)

        # 3. PAGINA LINKS
        elif st.session_state.current_page == "Links":
            st.subheader("🔗 Risorse")
            col1, col2 = st.columns(2)
            with col1:
                st.write("### 🛒 Acquisti")
                st.write("- [ESP32-S3 su Amazon](https://amzn.to/3W9XXXX)")
            with col2:
                st.write("### 📄 Documentazione")
                st.write("- [Espressif SOCs](https://www.espressif.com/en/products/socs)")
            st.divider()
            st.video("https://www.youtube.com/watch?v=CfIjInYch7U")

    # --- FOOTER ---
    st.markdown(f"""
        <div class="footer">
            © 2026 Davide Pedretti Biagioni | CC: <a href="https://www.youtube.com/@Dronebotworkshop" style="color: #007bff;">Dronebot Workshop</a> | Aggiornato: {GEN_TIMESTAMP}
        </div>
    """, unsafe_allow_html=True)