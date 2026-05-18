import streamlit as st
import pandas as pd
from datetime import datetime

# Configurazione Pagina
st.set_page_config(page_title="ESP32 Expert Selector 2026", layout="wide")

# --- TIMESTAMP ---
GEN_TIMESTAMP = "18/05/2026 18:30:00"

# --- INIZIALIZZAZIONE STATO ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Selezione"
if 'reset_counter' not in st.session_state:
    st.session_state.reset_counter = 0

# --- FUNZIONE RESET ---
def perform_reset():
    # Svuota tutti i widget selezionati (anche eventuali chiavi namespaced)
    keys_to_clear = [k for k in list(st.session_state.keys()) if k.startswith("pill_") or "pill_" in k]
    for key in keys_to_clear:
        del st.session_state[key]
    # Incrementa il contatore per forzare la rigenerazione dei widget
    st.session_state.reset_counter += 1
    st.rerun()

# --- CARICAMENTO DATI ---
def load_data():
    nome_file = "ESP32_Feature_Matrix_2026.csv"
    try:
        df = pd.read_csv(nome_file)
        # Pulizia intestazioni
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
            padding: 6px 12px; border: 1px solid #333; border-radius: 6px;
            background: #161b22; margin-bottom: 5px;
        }}
        .board-name {{ font-size: 0.9rem; font-weight: bold; }}
        .status-ok {{ color: #007bff; font-weight: bold; font-size: 0.8rem; }}
        .feature-table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        .feature-table td, .feature-table th {{ border: 1px solid #333; padding: 8px; font-size: 0.8rem; }}
        .feature-table th {{ background: #007bff; color: white; }}
        .footer {{ position: fixed; left: 0; bottom: 0; width: 100%; background: #0e1117; color: #555; text-align: center; padding: 10px; font-size: 0.7rem; border-top: 1px solid #333; z-index: 999; }}
        </style>
    """, unsafe_allow_html=True)

    # --- TITOLO ---
    st.title("🛠️ ESP32 Smart Selector")

    # --- NAVIGAZIONE ---
    n1, n2, n3 = st.columns(3)
    with n1:
        if st.button("🎯 Selezione", type="primary" if st.session_state.current_page == "Selezione" else "secondary", use_container_width=True):
            st.session_state.current_page = "Selezione"
            st.rerun()
    with n2:
        if st.button("📚 Consigli", type="primary" if st.session_state.current_page == "Consigli" else "secondary", use_container_width=True):
            st.session_state.current_page = "Consigli"
            st.rerun()
    with n3:
        if st.button("🔗 Link & Risorse", type="primary" if st.session_state.current_page == "Links" else "secondary", use_container_width=True):
            st.session_state.current_page = "Links"
            st.rerun()

    active_filters = {}

    # --- PAGINA 1: SELEZIONE ---
    if st.session_state.current_page == "Selezione":
        col_l, col_r = st.columns([0.7, 0.3])
        
        with col_l:
            # Contenitore con key dinamica per il reset visivo
            with st.container(key=f"selection_grid_{st.session_state.reset_counter}"):
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
                                        pill_key = f"pill_{st.session_state.reset_counter}_{f_label}"
                                        sel = st.pills(f_label, opts, key=pill_key)
                                        if sel: active_filters[f_label] = sel

        with col_r:
            if st.button("🔄 RESET FILTRI", type="primary", use_container_width=True):
                perform_reset()
            
            st.write("### 📱 ESP32 Boards")
            for m in model_names:
                match = True
                for f, v in active_filters.items():
                    if str(df[df['Feature'] == f][m].values[0]).strip() != v:
                        match = False; break
                
                comp = match and active_filters
                opac = "1.0" if (comp or not active_filters) else "0.15"
                
                st.markdown(f"""
                    <div class="board-line" style="opacity: {opac}; border-color: {'#007bff' if comp else '#333'};">
                        <span class="board-name">{m}</span>
                        {"<span class='status-ok'>✓ OK</span>" if comp else ""}
                    </div>
                """, unsafe_allow_html=True)

    # --- PAGINA 2: CONSIGLI ---
    elif st.session_state.current_page == "Consigli":
        st.subheader("💡 Raccomandazioni Strategiche")
        recs = {
            "General / DIY": ["ESP32-S3", "ESP32-C6", "ESP32-C5 (NEW)"],
            "AI / Multimedia": ["ESP32-P4 (NEW)", "ESP32-S3", "ESP32 (Original)"],
            "IoT / Matter": ["ESP32-C6", "ESP32-H2", "ESP32-C5 (NEW)"],
            "Budget": ["ESP32-C3", "ESP32-C2", "ESP32-S2"]
        }
        cat = st.radio("Seleziona ambito d'uso:", list(recs.keys()), horizontal=True)
        st.write("")
        
        c_recs = st.columns(3)
        for i, board in enumerate(recs[cat]):
            with c_recs[i]:
                label = ["🥇 ORO", "🥈 ARGENTO", "🥉 BRONZO"][i]
                st.info(f"**{label}**\n\n{board}")

                # Mostra le caratteristiche tecniche del modello consigliato dal CSV
                board_col = board
                if board not in model_names:
                    # Mappa fallback tra etichetta "friendly" e colonna reale del CSV
                    board_map = {
                        "ESP32 (Original)": "ESP32 (Original)",
                        "ESP32-C5 (NEW)": "ESP32-C5 (NEW)",
                        "ESP32-P4 (NEW)": "ESP32-P4 (NEW)"
                    }
                    board_col = board_map.get(board, board)

                if board_col in model_names:
                    with st.expander(f"📋 Specifiche {board}", expanded=False):
                        spec_rows = []
                        for _, row in df.iterrows():
                            feature_name = str(row["Feature"]).strip()
                            feature_category = str(row["Feature Category"]).strip()
                            feature_value = str(row[board_col]).strip()
                            if feature_value not in ["", "nan", "None", "✗", "—"]:
                                spec_rows.append({
                                    "Categoria": feature_category,
                                    "Caratteristica": feature_name,
                                    "Valore": feature_value
                                })

                        if spec_rows:
                            st.dataframe(
                                pd.DataFrame(spec_rows),
                                use_container_width=True,
                                hide_index=True
                            )
                        else:
                            st.caption("Nessuna specifica disponibile per questo modello.")
                else:
                    st.caption("Specifiche non trovate nel file CSV per questo modello.")
                
        st.info("Nota: La funzione di caricamento automatico delle specifiche è temporaneamente disabilitata per manutenzione.")

    # --- PAGINA 3: LINKS ---
    elif st.session_state.current_page == "Links":
        st.subheader("🔗 Risorse e Link Utili")
        col1, col2 = st.columns(2)
        with col1:
            st.write("### 🛒 Link Amazon (Affiliazione)")
            st.write("- [ESP32-S3 DevKit](https://amzn.to/3W9XXXX)")
            st.write("- [ESP32-C6 Wi-Fi 6](https://amzn.to/3W8YYYY)")
        with col2:
            st.write("### 📄 Documentazione")
            st.write("- [Espressif SOCs Comparison](https://www.espressif.com/en/products/socs)")
        
        st.divider()
        st.subheader("🎥 Video Approfondimento")
        st.video("https://www.youtube.com/watch?v=CfIjInYch7U")

    # --- FOOTER ---
    st.markdown(f"""
        <div class="footer">
            © 2026 Davide Pedretti Biagioni | CC: <a href="https://www.youtube.com/@Dronebotworkshop" style="color: #007bff; text-decoration: none;">Dronebot Workshop</a> | Aggiornato: {GEN_TIMESTAMP}
        </div>
    """, unsafe_allow_html=True)
