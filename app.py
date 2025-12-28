import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIGURAZIONE PAGINA APPLE STYLE ---
st.set_page_config(page_title="Titanium CFO", layout="centered")

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

# --- CONNESSIONE API CON SCOPE TOTALI ---
# Questa riga è quella che risolve l'errore 403
scopes = [
"https://www.googleapis.com/auth/spreadsheets",
"https://www.googleapis.com/auth/drive"
]

def get_data():
try:
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
client = gspread.authorize(creds)

# Apri il file (assicurati che il nome sia esatto)
kb = client.open("CFO_2026_DATABASE")
sheet_saldi = kb.worksheet("Tabella saldi")
sheet_live = kb.worksheet("Live_Mese")

# Recupero Saldo (B2) e Extra (B3)
saldo = float(sheet_saldi.acell('B2').value.replace('€', '').replace('.', '').replace(',', '.'))
extra = float(sheet_saldi.acell('B3').value.replace('€', '').replace('.', '').replace(',', '.'))

# Calcolo Fissi Rimanenti
fissi_rimanenti = 0.0
data_fissi = sheet_live.get_all_values()
for row in data_fissi[1:]:
try:
importo = float(row[1].replace('€', '').replace('.', '').replace(',', '.'))
if len(row) < 3 or row[2] != '✅':
fissi_rimanenti += importo
except:
continue

return saldo, extra, fissi_rimanenti
except Exception as e:
st.error(f"Errore di connessione al database: {e}")
return None, None, None

saldo, extra, fissi = get_data()

if saldo is not None:
surplus = saldo - extra - fissi
st.title("💎 Titanium CFO")

col1, col2 = st.columns(2)
with col1:
st.metric("SALDO CONTO", f"€ {saldo:,.2f}")
with col2:
st.metric("BUDGET EXTRA", f"€ {extra:,.2f}")

st.markdown(f"""
<div class="surplus-box">
<p style="opacity:0.6; margin:0; font-size: 14px;">DISPONIBILE PER BUDDYBANK</p>
<h1 style="font-size: 55px; margin:15px 0;">€ {max(0, surplus):,.2f}</h1>
</div>
""", unsafe_allow_html=True)

if st.button("CONFERMA OPERAZIONE"):
st.balloons()
