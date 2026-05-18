import streamlit as st
import pandas as pd
from datetime import datetime

# Configurazione Pagina
st.set_page_config(page_title="ESP32 Expert Selector 2026", layout="wide")

# --- TIMESTAMP DI GENERAZIONE ---
GEN_TIMESTAMP = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

# --- INIZIALIZZAZIONE STATO ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Selezione"
if 'reset_trigger' not in st.session_state:
    st.session_state.reset_trigger = 0
if 'selected_recommendation' not in st.session_state:
    st.session_state.selected_recommendation = None

# --- FUNZIONI DI LOGICA ---
def perform_reset():
    # Pulisce tutti i filtri e resetta l'ID dei widget
    for key in list(st.session_state.keys()):
        if key.startswith("pill_") or key == 'selected_recommendation':
            del st.session_state[key]
    st.session_state.reset_trigger += 1
    st.session_state.current_page = "Selezione"

def select_board_features(model_name, df):
    # Pulisce i filtri attuali prima di applicare quelli della board selezionata
    for key in list(st.session_state.keys()):
        if key.startswith("pill_"):
            del st.session_state[key]
    
    # Carica le caratteristiche del modello selezionato nello stato delle pills
    for _, row in df.iterrows():
        f_label = str(row['Feature']).strip()
        val = str(row[model_name]).strip()
        if val not in ['✗', 'nan', '', 'None']:
            st.session_state[f"pill_{f_label}"] = val
    
    st.session_state.current_page = "Selezione"
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
    st.markdown("""
        <style>
        .stButton button { width: 100%; border-radius: 8px; }
        .board-card {
            display: flex; justify-content: space-between; align-items: center;
            padding: 4px 10px; border: 1px solid #444; border-radius: 6px;
            background: #161b22; margin-bottom: 2px;
        }
        .tag-ok {
            background: #007bff; color: white; font-size: 0.6rem;
            padding: 1px 5px; border-radius: 3px; font-weight: bold;
        }
        .feature-table {
            width: 100%; border-collapse: collapse; margin-top: 20px; color: #e0e0e0;
        }
        .feature-table th, .feature-table td {
            border: 1px solid #3e444d; padding: 10px; text-align: left;
        }
        .feature-table th { background-color: #007bff; color: white; }
        .footer {
            position: fixed; left: 0; bottom: 0; width: 100%;
            background: #0e1117; color: #666; text-align: center;
            padding: 8px; font-size: 0.7rem; border-top: 1px solid #333; z-index: 100;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- NAVBAR ---
    st.title("🛠️ ESP32 Smart Selector")
    n1, n2, n3 = st.columns(3)
    with n1:
        if st.button("🎯 Selezione Caratteristiche", type="primary" if st.session_state.current_page == "Selezione" else "secondary"):
            st.session_state.current_page = "Selezione"
            st.rerun()
    with n2:
        if st.button("📚 Consigli d'Utilizzo", type="primary" if st.session_state.current_page == "Consigli" else "secondary"):
            st.session_state.current_page = "Consigli"
            st.rerun()
    with n3:
        if st.button("🔗 Link & Risorse", type="primary" if st.session_state.current_page == "Links" else "secondary"):
            st.session_state.current_page = "Links"
            st.rerun()

    # --- LOGICA PAGINE ---
    
    if st.session_state.current_page == "Selezione":
        col_left, col_right = st.columns([0.72, 0.28])
        active_filters = {}
        
        with col_left:
            with st.container(key=f"grid_{st.session_state.reset_trigger}"):
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
            if st.button("🔄 RESET FILTRI", type="primary"):
                perform_reset()
                st.rerun()
            
            st.write("### 📱 ESP32 Boards")
            for m in model_names:
                match = True
                for f, v in active_filters.items():
                    if str(df[df['Feature'] == f][m].values[0]).strip() != v:
                        match = False; break
                
                is_active = match and active_filters
                opac = "1.0" if (is_active or not active_filters) else "0.15"
                st.markdown(f"""
                    <div class="board-card" style="opacity: {opac}; border-color: {'#00d4ff' if is_active else '#333'};">
                        <span style="font-size: 0.8rem; font-weight: bold;">{m}</span>
                        {"<span class='tag-ok'>✓ OK</span>" if is_active else ""}
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f"Carica {m}", key=f"load_{m}"):
                    select_board_features(m, df)
                    st.rerun()

    elif st.session_state.current_page == "Consigli":
        st.subheader("💡 Top Picks per Categoria")
        recs = {
            "General / DIY": ["ESP32-S3", "ESP32-C6", "ESP32-C5 (NEW)"],
            "AI / Multimedia": ["ESP32-P4 (NEW)", "ESP32-S3", "ESP32 (Original)"],
            "IoT / Matter": ["ESP32-C6", "ESP32-H2", "ESP32-C5 (NEW)"],
            "Budget": ["ESP32-C3", "ESP32-C2", "ESP32-S2"]
        }
        cat = st.radio("Ambito d'uso:", list(recs.keys()), horizontal=True)
        c1, c2, c3 = st.columns(3)
        p = recs[cat]
        
        with c1:
            if st.button(f"🥇 ORO: {p[0]}", type="primary" if st.session_state.selected_recommendation == p[0] else "secondary", key="gold"):
                st.session_state.selected_recommendation = p[0]
        with c2:
            if st.button(f"🥈 ARGENTO: {p[1]}", type="primary" if st.session_state.selected_recommendation == p[1] else "secondary", key="silver"):
                st.session_state.selected_recommendation = p[1]
        with c3:
            if st.button(f"🥉 BRONZO: {p[2]}", type="primary" if st.session_state.selected_recommendation == p[2] else "secondary", key="bronze"):
                st.session_state.selected_recommendation = p[2]

        if st.session_state.selected_recommendation:
            model = st.session_state.selected_recommendation
            st.markdown(f"### 🔍 Specifiche Tecniche: {model}")
            
            board_data = df[['Feature Category', 'Feature', model]]
            board_data = board_data[~board_data[model].isin(['✗', 'nan', 'None', ''])]
            
            # Generazione Tabella HTML
            html_table = "<table class='feature-table'><thead><tr><th>Categoria</th><th>Caratteristica</th><th>Valore</th></tr></thead><tbody>"
            for _, row in board_data.iterrows():
                html_table += f"<tr><td>{row['Feature Category']}</td><td>{row['Feature']}</td><td>{row[model]}</td></tr>"
            html_table += "</tbody></table>"
            
            st.markdown(html_table, unsafe_allow_html=True)

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