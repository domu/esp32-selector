import streamlit as st
import pandas as pd
from datetime import datetime

# Configurazione Pagina
st.set_page_config(page_title="ESP32 Expert Selector 2026", layout="wide")

# --- TIMESTAMP DI GENERAZIONE ---
# Aggiornato al momento della creazione del file
GEN_TIMESTAMP = "18/05/2026 23:35:00"

# --- LOGICA DI STATO E NAVIGAZIONE ---
if 'form_id' not in st.session_state:
    st.session_state.form_id = 0
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "🎯 Selezione Caratteristiche"

def deep_reset():
    # Incrementa l'ID del form per distruggere e ricreare i widget (pulisce il rosso/blu visivo)
    st.session_state.form_id += 1
    # Svuota lo stato della sessione
    for key in list(st.session_state.keys()):
        if key.startswith("pill_") or key.startswith("btn_"):
            del st.session_state[key]
    st.rerun()

def select_and_jump(model_name, df):
    # Forza il cambio di tab e ricarica le caratteristiche
    st.session_state.active_tab = "🎯 Selezione Caratteristiche"
    st.session_state.form_id += 1 # Reset grafico per pulizia
    
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
        st.error("Errore: Assicurati che il file 'ESP32_Feature_Matrix_2026.csv' sia presente.")
        return None

df = load_data()

if df is not None:
    model_names = df.columns[2:]
    sections = ["ARCHITECTURE", "WIRELESS", "COMMON PERIPHERALS", "ANALOG", "USB & HIGH-SPEED", "DISPLAY & CAMERA", "SECURITY", "STATUS"]

    # --- CSS PER LAYOUT E RESET VISIVO ---
    st.markdown("""
        <style>
        /* Layout Colonne */
        [data-testid="stColumn"]:nth-child(1) { width: 68% !important; }
        [data-testid="stColumn"]:nth-child(2) { 
            position: fixed; right: 1%; top: 40px; width: 28% !important;
            background: #0e1117; z-index: 1000; padding: 15px;
            border-left: 1px solid #333; height: 90vh; overflow-y: auto;
        }
        /* Box Board Status */
        .board-card {
            display: flex; justify-content: space-between; align-items: center;
            padding: 5px 12px; border: 1px solid #444; border-radius: 6px;
            background: #161b22; margin-bottom: 4px;
        }
        .tag-ok {
            background: #007bff; color: white; font-size: 0.6rem;
            padding: 2px 6px; border-radius: 4px; font-weight: bold;
        }
        /* Footer */
        .footer {
            position: fixed; left: 0; bottom: 0; width: 100%;
            background: #0e1117; color: gray; text-align: center;
            padding: 10px; font-size: 0.75rem; border-top: 1px solid #333;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- CONTENUTO PRINCIPALE ---
    col_left, col_right = st.columns([0.7, 0.3])
    
    active_filters = {}

    with col_left:
        st.title("🛠️ ESP32 Smart Selector")
        st.caption(f"File generato il: {GEN_TIMESTAMP}")

        # Uso di session_state.active_tab per permettere il "salto" dai consigli
        tabs = ["🎯 Selezione Caratteristiche", "📚 Consigli d'Utilizzo"]
        idx_tab = tabs.index(st.session_state.active_tab)
        
        tab_sel, tab_cons = st.tabs(tabs)
        
        # TAB 1: SELEZIONE
        with tab_sel:
            # Il container con 'form_id' assicura che al reset i widget vengano distrutti visivamente
            with st.container(key=f"selection_form_{st.session_state.form_id}"):
                for sec in sections:
                    rows = df[df['Feature Category'] == sec]
                    if not rows.empty:
                        with st.expander(f"📂 {sec}", expanded=True):
                            for _, r in rows.iterrows():
                                f_label = r['Feature']
                                opts = sorted(list(set([str(r[m]).strip() for m in model_names if str(r[m]).strip() not in ['✗', 'nan', '']])))
                                if opts:
                                    res = st.pills(f_label, opts, key=f"pill_{f_label}")
                                    if res: active_filters[f_label] = res

        # TAB 2: CONSIGLI
        with tab_cons:
            st.subheader("💡 Raccomandazioni per categoria")
            recs = {
                "General / DIY": ["ESP32-S3", "ESP32-C6", "ESP32-C5"],
                "AI / Multimedia": ["ESP32-P4", "ESP32-S3", "ESP32 Original"],
                "IoT / Home Automation": ["ESP32-C6", "ESP32-H2", "ESP32-C5"],
                "Budget / Low Power": ["ESP32-C3", "ESP32-C2", "ESP32-S2"]
            }
            cat_choice = st.radio("Seleziona ambito:", list(recs.keys()), horizontal=True)
            
            st.write("### Seleziona un modello per analizzarne i dettagli:")
            c1, c2, c3 = st.columns(3)
            p = recs[cat_choice]
            
            # Pulsanti interattivi nei consigli
            with c1:
                if st.button(f"🥇 ORO\n\n{p[0]}", use_container_width=True, type="primary"):
                    select_and_jump(p[0], df)
            with c2:
                if st.button(f"🥈 ARGENTO\n\n{p[1]}", use_container_width=True):
                    select_and_jump(p[1], df)
            with c3:
                if st.button(f"🥉 BRONZO\n\n{p[2]}", use_container_width=True):
                    select_and_jump(p[2], df)
            
            st.divider()
            st.video("https://www.youtube.com/watch?v=CfIjInYch7U")

    # --- COLONNA DESTRA (STATUS BOARD - SOLO IN TAB SELEZIONE) ---
    with col_right:
        st.button("🔄 Reset Totale Visivo", use_container_width=True, type="primary", on_click=deep_reset)
        st.write("### 📱 Board Status")
        
        for m in model_names:
            match = True
            for f, v in active_filters.items():
                if str(df[df['Feature'] == f][m].values[0]).strip() != v:
                    match = False
                    break
            
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

    # --- FOOTER COPYRIGHT ---
    st.markdown(f"""
        <div class="footer">
            © 2026 Davide Pedretti Biagioni | CC: <a href="https://www.youtube.com/@Dronebotworkshop" style="color: #007bff; text-decoration: none;">Dronebot Workshop</a> | {GEN_TIMESTAMP}
        </div>
    """, unsafe_allow_html=True)