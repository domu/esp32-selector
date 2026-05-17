import streamlit as st
import pandas as pd

# Configurazione Pagina
st.set_page_config(page_title="ESP32 Expert Selector 2026", layout="wide")

# --- GESTIONE STATO E RESET ---
if 'form_id' not in st.session_state:
    st.session_state.form_id = 0

def trigger_reset():
    st.session_state.form_id += 1
    # Rimuoviamo tutte le chiavi relative alle pillole nello stato della sessione
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
        st.error("File 'ESP32_Feature_Matrix_2026.csv' non trovato.")
        return None

df = load_data()

if df is not None:
    model_names = df.columns[2:]
    sections = ["ARCHITECTURE", "WIRELESS", "COMMON PERIPHERALS", "ANALOG", "USB & HIGH-SPEED", "DISPLAY & CAMERA", "SECURITY", "STATUS"]

    # --- CSS PER SEPARAZIONE NETTA E LAYOUT FISSO ---
    st.markdown("""
        <style>
        /* Forza la colonna sinistra a non occupare troppo spazio */
        [data-testid="stColumn"]:nth-child(1) { width: 68% !important; }
        
        /* Colonna destra fissa: solo per lo stato delle board */
        [data-testid="stColumn"]:nth-child(2) { 
            position: fixed; right: 1%; top: 40px; width: 28% !important;
            background: #0e1117; z-index: 1000; padding: 15px;
            border-left: 1px solid #333; height: 95vh; overflow-y: auto;
        }
        
        .board-box {
            display: flex; justify-content: space-between; align-items: center;
            padding: 6px 12px; border: 1px solid #444; border-radius: 6px;
            background: #161b22; margin-bottom: 4px;
        }
        
        .comp-tag {
            background: #007bff; color: white; font-size: 0.65rem;
            padding: 2px 6px; border-radius: 4px; font-weight: bold;
        }
        
        /* Riduzione padding per far stare le board in una schermata */
        .stButton button { margin-top: -5px; margin-bottom: 10px; }
        </style>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([0.7, 0.3])

    active_filters = {}

    # --- COLONNA SINISTRA (FILTRI E CONSIGLI) ---
    with col_left:
        st.title("🛠️ ESP32 Selector")
        
        # Il contenitore cambia ID al reset, forzando la pulizia visiva totale
        with st.container(key=f"main_form_{st.session_state.form_id}"):
            t1, t2 = st.tabs(["🎯 Selezione Caratteristiche", "📚 Consigli d'Utilizzo"])
            
            with t1:
                for sec in sections:
                    rows = df[df['Feature Category'] == sec]
                    if not rows.empty:
                        with st.expander(f"📂 {sec}", expanded=True):
                            for _, r in rows.iterrows():
                                f_label = r['Feature']
                                opts = sorted(list(set([str(r[m]).strip() for m in model_names if str(r[m]).strip() not in ['✗', 'nan', '']])))
                                if opts:
                                    # Widget pill con chiave legata allo stato per reset preciso
                                    sel = st.pills(f_label, opts, key=f"pill_{f_label}")
                                    if sel: 
                                        active_filters[f_label] = sel
            
            with t2:
                st.subheader("💡 Raccomandazioni Expert")
                recs = {
                    "General / DIY": ["ESP32-S3", "ESP32-C6", "ESP32-C5"],
                    "AI / Multimedia": ["ESP32-P4", "ESP32-S3", "LilyGo S3"],
                    "IoT / Home Automation": ["ESP32-C6", "ESP32-H2", "ESP32-C5"],
                    "Budget / Entry Level": ["ESP32-C3", "ESP32 (Original)", "ESP32-C2"]
                }
                
                cat = st.radio("Scegli il tuo ambito:", list(recs.keys()), horizontal=True)
                st.write("")
                
                c1, c2, c3 = st.columns(3)
                with c1: 
                    st.success(f"🥇 **ORO**\n\n{recs[cat][0]}")
                with c2: 
                    st.info(f"🥈 **ARGENTO**\n\n{recs[cat][1]}")
                with c3: 
                    st.warning(f"🥉 **BRONZO**\n\n{recs[cat][2]}")
                
                st.divider()
                st.subheader("🎥 Video Tutorial")
                st.video("https://www.youtube.com/watch?v=CfIjInYch7U")

    # --- COLONNA DESTRA (STATUS BOARD - SEMPRE VISIBILE) ---
    with col_right:
        st.button("🔄 Reset Totale Filtri", use_container_width=True, type="primary", on_click=trigger_reset)
        st.markdown("### 📱 Board Status")
        st.caption("I modelli si illuminano in base ai filtri a sinistra")
        
        for m in model_names:
            # Calcolo logico della compatibilità
            match = True
            for f, v in active_filters.items():
                if str(df[df['Feature'] == f][m].values[0]).strip() != v:
                    match = False
                    break
            
            # Stato visivo
            is_active = match and active_filters
            opacity = "1.0" if (is_active or not active_filters) else "0.2"
            border_col = "#00d4ff" if is_active else "#333"
            
            # Box Grafico Board
            st.markdown(f"""
                <div class="board-box" style="opacity: {opacity}; border-color: {border_col};">
                    <span style="font-size: 0.85rem; font-weight: bold; color: white;">{m}</span>
                    {"<span class='comp-tag'>✓ COMPATIBILE</span>" if is_active else ""}
                </div>
            """, unsafe_allow_html=True)
            
            # Pulsante per caricare le caratteristiche (Selezione Inversa)
            if st.button(f"Carica {m}", key=f"btn_{m}", use_container_width=True):
                select_board_features(m, df)
                st.rerun()