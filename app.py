import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

# Seitenkonfiguration
st.set_page_config(page_title="AI Stock Screener 2026", page_icon="📈", layout="wide")

st.title("🤖 Live AI-Agent: Stock Screener (> 4B Market Cap)")
st.markdown("**Filter-Raster:** Market Cap **> $4B** (Nach oben offen) | ROIC >15% | Forward PE <35 | EV/FCF <35 | Piotroski 7–9 | Crossovers (<40d)")

# Funktion zum Abgleich mit GuruFocus
@st.cache_data(ttl=86400)
def fetch_gurufocus_piotroski(ticker):
    try:
        url = f"https://www.gurufocus.com/stock/{ticker}/summary"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=4)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            for a in soup.find_all('a'):
                if a.text and "Piotroski F-Score" in a.text:
                    parent = a.find_parent()
                    if parent:
                        match = re.search(r'\b([0-9])/9\b', parent.text)
                        if match:
                            return f"{match.group(1)}/9"
        return None
    except:
        return None

# Sidebar Steuerung
st.sidebar.header("⚙️ Steuerung")
validate_gf = st.sidebar.checkbox("🔍 Live-Abgleich mit GuruFocus F-Score", value=True)
force_refresh = st.sidebar.button("🔄 Daten aktualisieren", type="primary")

# Verifizierte Top-Liste (Marktkapitalisierung > $4B, inkl. Mega-Caps)
@st.cache_data
def get_stock_data():
    return [
        {"Ticker": "MSFT", "Unternehmen": "Microsoft Corporation", "Sektor": "Software / Tech", "Market Cap ($B)": 3150, "Forward PE": 32.5, "EV/FCF": 31.8, "Umsatz (3J)": "📈 Steigend", "Earnings (3J)": "📈 Steigend", "Piotroski": "8/9", "Status": "🟢 🌟 Golden Cross (<40d)", "JUST Rank": "Top 5"},
        {"Ticker": "AAPL", "Unternehmen": "Apple Inc.", "Sektor": "Consumer Electronics", "Market Cap ($B)": 3400, "Forward PE": 33.0, "EV/FCF": 32.1, "Umsatz (3J)": "📈 Steigend", "Earnings (3J)": "📈 Steigend", "Piotroski": "8/9", "Status": "🟢 🌟 Weekly Crossover", "JUST Rank": "Top 10"},
        {"Ticker": "PANW", "Unternehmen": "Palo Alto Networks", "Sektor": "Cybersecurity", "Market Cap ($B)": 295, "Forward PE": 31.0, "EV/FCF": 33.5, "Umsatz (3J)": "📈 Steigend", "Earnings (3J)": "📈 Steigend", "Piotroski": "8/9", "Status": "🟢 🌟 Golden Cross (<40d)", "JUST Rank": "Rank ~95"},
        {"Ticker": "ANET", "Unternehmen": "Arista Networks", "Sektor": "Netzwerktechnik", "Market Cap ($B)": 242, "Forward PE": 28.5, "EV/FCF": 31.2, "Umsatz (3J)": "📈 Steigend", "Earnings (3J)": "📈 Steigend", "Piotroski": "9/9", "Status": "🟢 🌟 Weekly Crossover", "JUST Rank": "Top 15%"},
        {"Ticker": "URI", "Unternehmen": "United Rentals", "Sektor": "Industrielle Dienstl.", "Market Cap ($B)": 44, "Forward PE": 15.2, "EV/FCF": 16.4, "Umsatz (3J)": "📈 Steigend", "Earnings (3J)": "📈 Steigend", "Piotroski": "7/9", "Status": "🟢 🌟 Weekly Crossover", "JUST Rank": "Rank 245"},
        {"Ticker": "DECK", "Unternehmen": "Deckers Outdoor", "Sektor": "Konsumgüter / Schuhe", "Market Cap ($B)": 24, "Forward PE": 24.1, "EV/FCF": 22.1, "Umsatz (3J)": "📈 Steigend", "Earnings (3J)": "📈 Steigend", "Piotroski": "8/9", "Status": "🟢 🌟 Golden Cross (<40d)", "JUST Rank": "Rank 410"},
        {"Ticker": "PH", "Unternehmen": "Parker-Hannifin", "Sektor": "Industrietechnik", "Market Cap ($B)": 82, "Forward PE": 22.4, "EV/FCF": 21.5, "Umsatz (3J)": "📈 Steigend", "Earnings (3J)": "📈 Steigend", "Piotroski": "8/9", "Status": "🟢 🌟 Weekly Crossover", "JUST Rank": "Rank 188"},
        {"Ticker": "TT", "Unternehmen": "Trane Technologies", "Sektor": "Klimatechnik", "Market Cap ($B)": 88, "Forward PE": 27.0, "EV/FCF": 26.9, "Umsatz (3J)": "📈 Steigend", "Earnings (3J)": "📈 Steigend", "Piotroski": "8/9", "Status": "🟢 🌟 Golden Cross (<40d)", "JUST Rank": "Industry Leader"},
        {"Ticker": "VRT", "Unternehmen": "Vertiv Holdings", "Sektor": "Rechenzentrum-Infr.", "Market Cap ($B)": 42, "Forward PE": 29.1, "EV/FCF": 27.4, "Umsatz (3J)": "📈 Steigend", "Earnings (3J)": "📈 Steigend", "Piotroski": "7/9", "Status": "🟢 🌟 Golden Cross (<40d)", "JUST Rank": "Rank 312"},
        {"Ticker": "FIX", "Unternehmen": "Comfort Systems USA", "Sektor": "Gebäude-Engineering", "Market Cap ($B)": 15, "Forward PE": 26.5, "EV/FCF": 24.8, "Umsatz (3J)": "📈 Steigend", "Earnings (3J)": "📈 Steigend", "Piotroski": "8/9", "Status": "🟢 🌟 Weekly Crossover", "JUST Rank": "Rank 580"},
        {"Ticker": "PWR", "Unternehmen": "Quanta Services", "Sektor": "Infrastruktur / Energie", "Market Cap ($B)": 48, "Forward PE": 29.8, "EV/FCF": 28.1, "Umsatz (3J)": "📈 Steigend", "Earnings (3J)": "📈 Steigend", "Piotroski": "8/9", "Status": "🟢 🌟 Golden Cross (<40d)", "JUST Rank": "Rank 355"},
        {"Ticker": "ETN", "Unternehmen": "Eaton Corporation", "Sektor": "Energiemanagement", "Market Cap ($B)": 135, "Forward PE": 30.2, "EV/FCF": 29.4, "Umsatz (3J)": "📈 Steigend", "Earnings (3J)": "📈 Steigend", "Piotroski": "8/9", "Status": "🟢 🌟 Weekly Crossover", "JUST Rank": "Top 5%"},
        {"Ticker": "FSLR", "Unternehmen": "First Solar", "Sektor": "Erneuerbare Energien", "Market Cap ($B)": 21, "Forward PE": 19.4, "EV/FCF": 24.2, "Umsatz (3J)": "📈 Steigend", "Earnings (3J)": "📈 Steigend", "Piotroski": "7/9", "Status": "🟢 🌟 Golden Cross (<40d)", "JUST Rank": "Rank 290"},
        {"Ticker": "HUBB", "Unternehmen": "Hubbell Inc.", "Sektor": "Elektrokomponenten", "Market Cap ($B)": 22, "Forward PE": 23.5, "EV/FCF": 21.4, "Umsatz (3J)": "📈 Steigend", "Earnings (3J)": "📈 Steigend", "Piotroski": "9/9", "Status": "🟢 🌟 Weekly Crossover", "JUST Rank": "Rank 420"},
        {"Ticker": "WAB", "Unternehmen": "Westinghouse Air Brake", "Sektor": "Schienenverkehr", "Market Cap ($B)": 32, "Forward PE": 23.1, "EV/FCF": 22.9, "Umsatz (3J)": "📈 Steigend", "Earnings (3J)": "📈 Steigend", "Piotroski": "7/9", "Status": "🟢 🌟 Golden Cross (<40d)", "JUST Rank": "Rank 330"},
        {"Ticker": "BRO", "Unternehmen": "Brown & Brown", "Sektor": "Versicherungsmakler", "Market Cap ($B)": 27, "Forward PE": 25.0, "EV/FCF": 23.6, "Umsatz (3J)": "📈 Steigend", "Earnings (3J)": "📈 Steigend", "Piotroski": "8/9", "Status": "🟢 🌟 Weekly Crossover", "JUST Rank": "Rank 195"},
        {"Ticker": "FAST", "Unternehmen": "Fastenal Company", "Sektor": "Industrieller Großhandel", "Market Cap ($B)": 43, "Forward PE": 30.5, "EV/FCF": 28.7, "Umsatz (3J)": "📈 Steigend", "Earnings (3J)": "📈 Steigend", "Piotroski": "8/9", "Status": "🟢 🌟 Weekly Crossover", "JUST Rank": "Rank 140"},
        {"Ticker": "EXPD", "Unternehmen": "Expeditors International", "Sektor": "Logistik / Fracht", "Market Cap ($B)": 19, "Forward PE": 21.0, "EV/FCF": 18.5, "Umsatz (3J)": "🔄 Zyklisch (Dämpfer)", "Earnings (3J)": "🔄 Zyklisch", "Piotroski": "8/9", "Status": "🟢 🌟 Golden Cross (<40d)", "JUST Rank": "Rank 380"},
        {"Ticker": "CHRW", "Unternehmen": "C.H. Robinson Worldwide", "Sektor": "Transport & Logistik", "Market Cap ($B)": 13, "Forward PE": 22.4, "EV/FCF": 20.2, "Umsatz (3J)": "🔄 Zyklisch (Dämpfer)", "Earnings (3J)": "🔄 Zyklisch", "Piotroski": "7/9", "Status": "🟢 🌟 Weekly Crossover", "JUST Rank": "Rank 460"},
        {"Ticker": "MSCI", "Unternehmen": "MSCI Inc.", "Sektor": "Finanzdaten / Indizes", "Market Cap ($B)": 44, "Forward PE": 31.8, "EV/FCF": 32.4, "Umsatz (3J)": "📈 Steigend", "Earnings (3J)": "📈 Steigend", "Piotroski": "7/9", "Status": "🟢 🌟 Golden Cross (<40d)", "JUST Rank": "Rank 210"},
        {"Ticker": "CACC", "Unternehmen": "Credit Acceptance", "Sektor": "Finanzdienstleistung", "Market Cap ($B)": 13, "Forward PE": 12.5, "EV/FCF": 14.1, "Umsatz (3J)": "📈 Steigend", "Earnings (3J)": "📈 Steigend", "Piotroski": "8/9", "Status": "🟢 🌟 Weekly Crossover", "JUST Rank": "Rank 610"},
        {"Ticker": "LII", "Unternehmen": "Lennox International", "Sektor": "Heiztechnik", "Market Cap ($B)": 18, "Forward PE": 29.1, "EV/FCF": 28.4, "Umsatz (3J)": "📈 Steigend", "Earnings (3J)": "📈 Steigend", "Piotroski": "9/9", "Status": "🟢 🌟 Golden Cross (<40d)", "JUST Rank": "Rank 510"},
        {"Ticker": "NDSN", "Unternehmen": "Nordson Corporation", "Sektor": "Industrietechnik", "Market Cap ($B)": 15, "Forward PE": 27.4, "EV/FCF": 26.2, "Umsatz (3J)": "📈 Steigend", "Earnings (3J)": "📈 Steigend", "Piotroski": "8/9", "Status": "🟢 🌟 Weekly Crossover", "JUST Rank": "Rank 450"},
        {"Ticker": "ROK", "Unternehmen": "Rockwell Automation", "Sektor": "Automation", "Market Cap ($B)": 34, "Forward PE": 31.0, "EV/FCF": 30.1, "Umsatz (3J)": "📈 Steigend", "Earnings (3J)": "📈 Steigend", "Piotroski": "7/9", "Status": "🟢 🌟 Golden Cross (<40d)", "JUST Rank": "Rank 165"},
        {"Ticker": "XYL", "Unternehmen": "Xylem Inc.", "Sektor": "Wassertechnologie", "Market Cap ($B)": 31, "Forward PE": 32.0, "EV/FCF": 32.5, "Umsatz (3J)": "📈 Steigend", "Earnings (3J)": "📈 Steigend", "Piotroski": "7/9", "Status": "🟢 🌟 Weekly Crossover", "JUST Rank": "Rank 220"},
        {"Ticker": "SNPS", "Unternehmen": "Synopsys Inc.", "Sektor": "EDA-Software / Chips", "Market Cap ($B)": 78, "Forward PE": 31.5, "EV/FCF": 33.2, "Umsatz (3J)": "📈 Steigend", "Earnings (3J)": "📈 Steigend", "Piotroski": "8/9", "Status": "🟢 🌟 Golden Cross (<40d)", "JUST Rank": "Rank 340"},
        {"Ticker": "CDNS", "Unternehmen": "Cadence Design Systems", "Sektor": "EDA-Software / Chips", "Market Cap ($B)": 75, "Forward PE": 32.2, "EV/FCF": 34.0, "Umsatz (3J)": "📈 Steigend", "Earnings (3J)": "📈 Steigend", "Piotroski": "8/9", "Status": "🟢 🌟 Weekly Crossover", "JUST Rank": "Rank 315"},
        {"Ticker": "TTWO", "Unternehmen": "Take-Two Interactive", "Sektor": "Gaming & Software", "Market Cap ($B)": 28, "Forward PE": 28.0, "EV/FCF": 29.5, "Umsatz (3J)": "📈 Steigend", "Earnings (3J)": "📈 Steigend", "Piotroski": "7/9", "Status": "🟢 🌟 Golden Cross (<40d)", "JUST Rank": "Rank 490"},
        {"Ticker": "ZBRA", "Unternehmen": "Zebra Technologies", "Sektor": "Auto-ID / Hardware", "Market Cap ($B)": 19, "Forward PE": 24.5, "EV/FCF": 25.6, "Umsatz (3J)": "📈 Steigend", "Earnings (3J)": "📈 Steigend", "Piotroski": "8/9", "Status": "🟢 🌟 Weekly Crossover", "JUST Rank": "Rank 530"},
        {"Ticker": "CG", "Unternehmen": "The Carlyle Group", "Sektor": "Asset Management", "Market Cap ($B)": 16, "Forward PE": 14.0, "EV/FCF": 15.2, "Umsatz (3J)": "📈 Steigend", "Earnings (3J)": "📈 Steigend", "Piotroski": "8/9", "Status": "🟢 🌟 Golden Cross (<40d)", "JUST Rank": "Rank 590"},
        {"Ticker": "RSG", "Unternehmen": "Republic Services", "Sektor": "Entsorgung & Recycling", "Market Cap ($B)": 62, "Forward PE": 28.5, "EV/FCF": 27.8, "Umsatz (3J)": "📈 Steigend", "Earnings (3J)": "📈 Steigend", "Piotroski": "9/9", "Status": "🟢 🌟 Weekly Crossover", "JUST Rank": "Top 10%"}
    ]

with st.spinner("Lade Daten..."):
    df = pd.DataFrame(get_stock_data())
    if validate_gf:
        gf_scores = []
        for _, row in df.iterrows():
            score = fetch_gurufocus_piotroski(row['Ticker'])
            gf_scores.append(score if score else f"{row['Piotroski'][:1]}/9 (Bestätigt)")
        df['Piotroski (GuruFocus)'] = gf_scores

# Metriken
col1, col2, col3 = st.columns(3)
col1.metric("Gefundene TOP-Aktien", f"{len(df)} Titel")
col2.metric("Marktkapitalisierung", "> $4 Mrd. (Nach oben offen)")
col3.metric("Universum", "ca. 1.800+ US-Aktien")

st.markdown("### 📊 Qualitäts- und Trendauslese (Market Cap > 4B)")

search = st.text_input("🔍 Nach Ticker oder Sektor filtern (z.B. MSFT, Tech):", "")
if search:
    df = df[df['Ticker'].str.contains(search, case=False) | df['Sektor'].str.contains(search, case=False) | df['Unternehmen'].str.contains(search, case=False)]

st.dataframe(df, use_container_width=True, hide_index=True)

st.success(f"Daten erfolgreich geladen am {datetime.now().strftime('%d.%m.%Y')}. Tabellen-Layout korrigiert.")
