import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIGURAZIONE API ---
scope = ["https://www.googleapis.com/auth/spreadsheets"]
# Prende le chiavi dai Secrets di Streamlit
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(creds)

# Apre il tuo database (Nome esatto del file su Google Drive)
try:
    workbook = client.open("CFO_2026_DATABASE")
    sheet_saldi = workbook.worksheet("Tabella saldi")
    sheet_live = workbook.worksheet("Live_Mese")
except Exception as e:
    st.error(f"Errore di connessione al database: {e}")
    st.stop()

# --- RECUPERO DATI ---
# Saldi (B2 e B3)
saldo_principale = float(sheet_saldi.acell('B2').value.replace('€', '').replace('.', '').replace(',', '.'))
budget_extra = float(sheet_saldi.acell('B3').value.replace('€', '').replace('.', '').replace(',', '.'))

# Calcolo Fissi Rimanenti (Scansiona la colonna delle spunte ✅)
fissi_data = sheet_live.get_all_values()
fissi_rimanenti = 0.0
for row in fissi_data[1:]: # Salta l'intestazione
    try:
        importo = float(row[1].replace('€', '').replace('.', '').replace(',', '.'))
        # Se la colonna 3 non ha la spunta, aggiungi al totale da pagare
        if len(row) < 3 or row[2] != '✅':
            fissi_rimanenti += importo
    except:
        continue

surplus_buddy = saldo_principale - budget_extra - fissi_rimanenti

# --- INTERFACCIA APPLE STYLE ---
st.set_page_config(page_title="CFO Titanium", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #000000; color: white; }
    .stMetric { background: #1c1c1e; padding: 20px; border-radius: 20px; border: 1px solid #3a3a3c; }
    .surplus-box {
        background: linear-gradient(180deg, #2c2c2e 0%, #1c1c1e 100%);
        padding: 40px; border-radius: 25px; text-align: center;
        border: 1px solid #3a3a3c; margin: 25px 0;
    }
    div.stButton > button { 
        background-color: #ffffff; color: black; border-radius: 15px; 
        height: 55px; font-weight: bold; width: 100%; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("💎 Titanium CFO")
st.write("SITUAZIONE REAL-TIME")

col1, col2 = st.columns(2)
with col1:
    st.metric("CONTO PRINCIPALE", f"€ {saldo_principale:,.2f}")
with col2:
    st.metric("BUDGET EXTRA", f"€ {budget_extra:,.2f}")

st.markdown(f"""
    <div class="surplus-box">
        <p style="opacity:0.6; margin:0; font-size: 14px; letter-spacing: 1px;">DISPONIBILE PER BUDDYBANK</p>
        <h1 style="font-size: 55px; margin:15px 0;">€ {max(0, surplus_buddy):,.2f}</h1>
    </div>
    """, unsafe_allow_html=True)

if st.button("CONFERMA BONIFICO"):
    st.balloons()

with st.expander("📉 DETTAGLIO FISSI DA PAGARE"):
    if fissi_rimanenti == 0:
        st.success("Tutte le spese di Dicembre sono state saldate! ✅")
    else:
        st.write(f"Totale ancora da uscire: € {fissi_rimanenti:,.2f}")
