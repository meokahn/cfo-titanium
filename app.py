import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# --- 1. CONFIGURAZIONE PAGINA APPLE STYLE ---
st.set_page_config(page_title="Titanium CFO", page_icon="💎", layout="centered")

st.markdown("""
<style>
.main { background-color: #000000; }
[data-testid="stMetricValue"] { font-size: 28px !important; color: #ffffff !important; }
[data-testid="stMetricLabel"] { color: #8e8e93 !important; }
.stMetric {
background-color: #1c1c1e;
padding: 20px;
border-radius: 18px;
border: 1px solid #3a3a3c;
}
.surplus-card {
background: linear-gradient(180deg, #2c2c2e 0%, #1c1c1e 100%);
padding: 40px;
border-radius: 28px;
text-align: center;
border: 1px solid #3a3a3c;
margin: 20px 0;
box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}
div.stButton > button {
background-color: #ffffff;
color: #000000;
border-radius: 14px;
height: 55px;
font-weight: bold;
width: 100%;
border: none;
margin-top: 10px;
}
h1, h2, h3 { color: #ffffff !important; font-family: 'SF Pro Display', -apple-system, sans-serif; }
</style>
""", unsafe_allow_html=True)

# --- 2. CONNESSIONE AL DATABASE (API) ---
scope = [
"https://www.googleapis.com/auth/spreadsheets",
"https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def get_gspread_client():
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
return gspread.authorize(creds)

try:
client = get_gspread_client()
# Apri il foglio (Assicurati che il nome su Google Drive sia ESATTAMENTE questo)
sh = client.open("CFO_2026_DATABASE")
sheet_saldi = sh.worksheet("Tabella saldi")
sheet_live = sh.worksheet("Live_Mese")

# --- 3. RECUPERO DATI REALI ---
# Saldo Principale (B2) e Budget Extra (B3)
val_saldo = sheet_saldi.acell('B2').value.replace('€', '').replace('.', '').replace(',', '.')
val_extra = sheet_saldi.acell('B3').value.replace('€', '').replace('.', '').replace(',', '.')

saldo_principale = float(val_saldo)
budget_extra = float(val_extra)

# Scansione Fissi (Calcola quelli senza ✅)
data_fissi = sheet_live.get_all_values()
fissi_rimanenti = 0.0
for row in data_fissi[1:]: # Salta intestazione
try:
importo = float(row[1].replace('€', '').replace('.', '').replace(',', '.'))
# Se la colonna C (indice 2) non ha la spunta, è un debito residuo
if len(row) < 3 or row[2] != '✅':
fissi_rimanenti += importo
except:
continue

surplus_buddybank = saldo_principale - budget_extra - fissi_rimanenti

# --- 4. VISUALIZZAZIONE DASHBOARD ---
st.write("### 💎 Titanium CFO")
st.caption("DASHBOARD FINANZIARIA PERSONALE")

col1, col2 = st.columns(2)
with col1:
st.metric("SALDO CONTO", f"€ {saldo_principale:,.2f}")
with col2:
st.metric("BUDGET EXTRA", f"€ {budget_extra:,.2f}")

st.markdown(f"""
<div class="surplus-card">
<p style="margin:0; opacity:0.6; font-size:13px; letter-spacing:1px; text-transform:uppercase;">Disponibile per Buddybank</p>
<h1 style="font-size: 52px; margin:15px 0; font-weight:700;">€ {max(0, surplus_buddybank):,.2f}</h1>
</div>
""", unsafe_allow_html=True)

if st.button("CONFERMA SPOSTAMENTO FONDI"):
st.balloons()
st.success("Grande! Obiettivo 10k più vicino.")

with st.expander("📝 Dettaglio Spese Fisse"):
if fissi_rimanenti == 0:
st.write("✅ Tutte le 22 spese di Dicembre risultano pagate.")
else:
st.write(f"⚠️ Hai ancora € {fissi_rimanenti:,.2f} di spese fisse da coprire.")

except Exception as e:
st.error(f"Errore di connessione: {e}")
st.info("Verifica che l'email del Service Account sia Editor nel foglio Google e che i Secrets siano corretti.")
