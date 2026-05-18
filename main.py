import streamlit as st
import pandas as pd
from datetime import datetime

# Configurazione Pagina
st.set_page_config(page_title="ESP32 Expert Selector 2026", layout="wide")

# --- TIMESTAMP ---
GEN_TIMESTAMP = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

# --- INIZIALIZZAZIONE STATO ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Selezione"
if 'reset_trigger' not in st.session_state:
    st.session_state.reset_trigger = 0
if 'active_board' not in st.session_state:
    st.session_state.active_board = None

# --- FUNZIONI DI LOGICA ---
def perform_reset():
    # Pulizia totale di ogni filtro e dello stato della board attiva
    for key in list(st.session_state.keys()):
        if key.startswith("pill_"):
            del st.session_state[key]
    st.session_state.active_board = None
    st.session_state.reset_trigger += 1 # Forza la rigenerazione dei widget
    st.session_state.current_page = "Selezione"

def toggle_board_features(model_name, df):
    # Se la board è già quella attiva, resettiamo tutto (Deselezione)
    if st.session_state.active_board == model_name:
        perform_reset()
    else:
        # Altrimenti carichiamo i parametri della nuova board
        st.session_state.active_board = model_name
        for key in list(st.session_state.keys()):
            if key.startswith("pill_"):
                del st.session_state[key]
        
        for _, row in df.iterrows():
            f_label = str(row['Feature']).strip()
            val = str(row[model_name]).strip()
            if val not in ['✗', 'nan', '', 'None']:
                st.session_state[f"pill_{f_label}"] = val
        st.session_state.reset_trigger += 1

def load_data():
    nome_file = "ESP32_Feature_Matrix_2026.csv"
    try:
        df = pd.read_csv(nome_file)
        df.columns = [c.replace('\n', ' ').strip() for c in df.columns]
        df['Feature Category'] = df['Feature Category'].ffill().str.strip()
        df['Feature'] = df['Feature'].str.strip()
        return df
    except Exception as e:
        st.error(f"Errore caricamento dati: {e}")
        return None

df = load_data()

if df is not None:
    model_names = df.columns[2:]
    
    # --- CSS PERSONALIZZATO ---
    st.markdown(f"""
        <style>
        .stButton button {{ border-radius: 8px; }}
        .board-line {{
            display: flex; justify-content: space-between; align-items: center;
            padding: 2px 8px; border: 1px solid #333; border-radius: 5px;
            background: #161b22; margin-bottom: 4px;
        }}
        .board-name {{ font-size: 0.85rem; font-weight: bold; flex-grow: 1; }}
        .status-ok {{ color: #007bff; font-weight: bold; font-size: 0.75rem; margin-right: 10px; }}
        /* Rimpiccioliamo il font del pulsante inline */
        div[data-testid="column"] button {{
            font-size: 0.7rem !important; padding: 2px 5px !important; height: auto !important;
        }}
        .feature-table {{ width: 100%; border-collapse: collapse; color: #e0e0e0; }}
        .feature-table th, .feature-table td {{ border: 1px solid #3e444d; padding: 8px; text-align: left; font-size: 0.85rem; }}
        .feature-table th {{ background-color: #007bff; color: white; }}
        .footer {{ position: fixed; left: 0; bottom: 0; width: 100%; background: #0e1117; color: #666; text-align: center; padding: 8px; font-size: 0.7rem; border-top: 1px solid #333; z-index: 100; }}
        </style>
    """, unsafe_allow_html=True)

    # --- NAVBAR ---
    st.title("🛠️ ESP32 Smart Selector")
    n1, n2, n3 = st.columns(3)
    with n1:
        if st.button("🎯 Selezione Caratteristiche", type="primary" if st.session_state.current_page == "Selezione" else "secondary"):
            st.session_state.current_page = "Selezione"; st.rerun()
    with n2:
        if st.button("📚 Consigli d'Utilizzo", type="primary" if st.session_state.current_page == "Consigli" else "secondary"):
            st.session_state.current_page = "Consigli"; st.rerun()
    with n3:
        if st.button("🔗 Link & Risorse", type="primary" if st.session_state.current_page == "Links" else "secondary"):
            st.session_state.current_page = "Links"; st.rerun()

    # --- PAGINA SELEZIONE ---
    if st.session_state.current_page == "Selezione":
        col_left, col_right = st.columns([0.7, 0.3])
        active_filters = {}
        
        with col_left:
            # Il reset_trigger cambia la key e forza la ricostruzione pulita dei widget
            with st.container(key=f"ui_grid_{st.session_state.reset_trigger}"):
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

        with col_right:
            if st.button("🔄 RESET FILTRI", type="primary", use_container_width=True):
                perform_reset()
                st.rerun()
            
            st.write("### 📱 ESP32 Boards")
            for m in model_names:
                match = True
                for f, v in active_filters.items():
                    if str(df[df['Feature'] == f][m].values[0]).strip() != v:
                        match = False; break
                
                is_compatible = match and active_filters
                is_active = (st.session_state.active_board == m)
                opac = "1.0" if (is_compatible or not active_filters or is_active) else "0.2"
                
                # Container della riga
                st.markdown(f'<div class="board-line" style="opacity: {opac}; border-color: {"#007bff" if is_active else "#333"};">', unsafe_allow_html=True)
                c_name, c_status, c_btn = st.columns([0.5, 0.25, 0.25])
                with c_name:
                    st.markdown(f'<span class="board-name">{m}</span>', unsafe_allow_html=True)
                with c_status:
                    if is_compatible:
                        st.markdown('<span class="status-ok">✓ OK</span>', unsafe_allow_html=True)
                with c_btn:
                    label = "Cancella" if is_active else "Carica"
                    if st.button(label, key=f"btn_{m}"):
                        toggle_board_features(m, df)
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    # --- PAGINA CONSIGLI ---
    elif st.session_state.current_page == "Consigli":
        st.subheader("💡 Top Picks per Categoria")
        recs = {
            "General / DIY": ["ESP32-S3", "ESP32-C6", "ESP32-C5 (NEW)"],
            "AI / Multimedia": ["ESP32-P4 (NEW)", "ESP32-S3", "ESP32 (Original)"],
            "IoT / Matter": ["ESP32-C6", "ESP32-H2", "ESP32-C5 (NEW)"],
            "Budget": ["ESP32-C3", "ESP32-C2", "ESP32-S2"]
        }
        cat = st.radio("Ambito:", list(recs.keys()), horizontal=True)
        c1, c2, c3 = st.columns(3)
        p = recs[cat]
        
        for i, board in enumerate(p):
            with [c1, c2, c3][i]:
                prefix = ["🥇 ORO", "🥈 ARGENTO", "🥉 BRONZO"][i]
                if st.button(f"{prefix}: {board}", type="primary" if st.session_state.selected_recommendation == board else "secondary"):
                    st.session_state.selected_recommendation = board

        if st.session_state.selected_recommendation:
            model = st.session_state.selected_recommendation
            st.markdown(f"#### 🔍 Specifiche: {model}")
            b_data = df[['Feature Category', 'Feature', model]]
            b_data = b_data[~b_data[model].isin(['✗', 'nan', 'None', ''])]
            
            html = "<table class='feature-table'><tr><th>Categoria</th><th>Feature</th><th>Dettaglio</th></tr>"
            for _, row in b_data.iterrows():
                html += f"<tr><td>{row['Feature Category']}</td><td>{row['Feature']}</td><td>{row[model]}</td></tr>"
            st.markdown(html + "</table>", unsafe_allow_html=True)

    # --- PAGINA LINKS ---
    elif st.session_state.current_page == "Links":
        st.subheader("🔗 Risorse e Video")
        l1, l2 = st.columns(2)
        with l1:
            st.markdown("### 🛒 Amazon Affiliate Links")
            st.write("- [ESP32-S3 DevKit](https://amzn.to/3W9XXXX)")
            st.write("- [ESP32-C6 Wi-Fi 6](https://amzn.to/3W8YYYY)")
        with l2:
            st.markdown("### 📄 Documentazione")
            st.write("- [Espressif SOC Comparison](https://www.espressif.com/en/products/socs)")
        
        st.divider()
        st.video("https://www.youtube.com/watch?v=CfIjInYch7U")

    # --- FOOTER ---
    st.markdown(f"""
        <div class="footer">
            © 2026 Davide Pedretti Biagioni | CC: <a href="https://www.youtube.com/@Dronebotworkshop" style="color: #007bff; text-decoration: none;">Dronebot Workshop</a> | Creato: {GEN_TIMESTAMP}
        </div>
    """, unsafe_allow_html=True)