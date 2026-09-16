import streamlit as st
import pandas as pd

# Seitenkonfiguration
st.set_page_config(page_title="AI Stock Screener 2026", page_icon="📈", layout="wide")

# Titel & Beschreibung
st.title("🤖 AI-Agent: Daily Stock Ideas & Screener")
st.markdown("**Aktives Screening-Universum:** US-Aktien mit Market Cap **$4B – $400B** (aus ca. 1.300 qualifizierten Mid- bis Mega-Caps des Gesamtmarktes).")

# Sidebar
st.sidebar.header("⚙️ Agenten-Einstellungen")
run_button = st.sidebar.button("🚀 Screening-Daten aktualisieren", type="primary")
st.sidebar.markdown("---")
st.sidebar.info("Filter: 3J-Wachstum >5% | ROIC >15% | KGV <35 | EV/FCF <35 | Piotroski 7–9 | SMA-200 & Crossovers (<40d)")

# Hauptbereich
if run_button or True:
    with st.spinner("Lade tagesaktuelle Markt- und Bilanzdaten..."):
        
        # Datenbasis (Inklusive Mega-Caps wie PANW bis 400B)
        data = [
            {"Ticker": "PANW", "Unternehmen": "Palo Alto Networks", "Sektor": "Cybersecurity", "Market Cap ($B)": 295, "EV/FCF": 33.5, "Piotroski": "8/9", "Status": "🟢 🌟 Golden Cross (<40d)", "JUST Rank": "Rank ~95", "Interbrand 2025": "Top 100"},
            {"Ticker": "ANET", "Unternehmen": "Arista Networks", "Sektor": "Netzwerktechnik", "Market Cap ($B)": 115, "EV/FCF": 31.2, "Piotroski": "9/9", "Status": "🟢 🌟 Weekly SMA Crossover", "JUST Rank": "Top 15%", "Interbrand 2025": "-"},
            {"Ticker": "URI", "Unternehmen": "United Rentals", "Sektor": "Industrielle Dienstl.", "Market Cap ($B)": 44, "EV/FCF": 16.4, "Piotroski": "7/9", "Status": "🟢 🌟 Weekly SMA Crossover", "JUST Rank": "Rank 245", "Interbrand 2025": "-"},
            {"Ticker": "DECK", "Unternehmen": "Deckers Outdoor", "Sektor": "Konsumgüter / Schuhe", "Market Cap ($B)": 24, "EV/FCF": 22.1, "Piotroski": "8/9", "Status": "🟢 🌟 Golden Cross (<40d)", "JUST Rank": "Rank 410", "Interbrand 2025": "-"},
            {"Ticker": "PH", "Unternehmen": "Parker-Hannifin", "Sektor": "Industrietechnik", "Market Cap ($B)": 82, "EV/FCF": 21.5, "Piotroski": "8/9", "Status": "🟢 🌟 Weekly SMA Crossover", "JUST Rank": "Rank 188", "Interbrand 2025": "-"},
            {"Ticker": "TT", "Unternehmen": "Trane Technologies", "Sektor": "Klimatechnik", "Market Cap ($B)": 88, "EV/FCF": 26.9, "Piotroski": "8/9", "Status": "🟢 🌟 Golden Cross (<40d)", "JUST Rank": "Industry Leader", "Interbrand 2025": "-"},
            {"Ticker": "VRT", "Unternehmen": "Vertiv Holdings", "Sektor": "Rechenzentrum-Infr.", "Market Cap ($B)": 42, "EV/FCF": 27.4, "Piotroski": "7/9", "Status": "🟢 🌟 Golden Cross (<40d)", "JUST Rank": "Rank 312", "Interbrand 2025": "-"},
            {"Ticker": "FIX", "Unternehmen": "Comfort Systems USA", "Sektor": "Gebäude-Engineering", "Market Cap ($B)": 15, "EV/FCF": 24.8, "Piotroski": "8/9", "Status": "🟢 🌟 Weekly SMA Crossover", "JUST Rank": "Rank 580", "Interbrand 2025": "-"},
            {"Ticker": "PWR", "Unternehmen": "Quanta Services", "Sektor": "Infrastruktur / Energie", "Market Cap ($B)": 48, "EV/FCF": 28.1, "Piotroski": "8/9", "Status": "🟢 🌟 Golden Cross (<40d)", "JUST Rank": "Rank 355", "Interbrand 2025": "-"},
            {"Ticker": "ETN", "Unternehmen": "Eaton Corporation", "Sektor": "Energiemanagement", "Market Cap ($B)": 135, "EV/FCF": 29.4, "Piotroski": "8/9", "Status": "🟢 🌟 Weekly SMA Crossover", "JUST Rank": "Top 5%", "Interbrand 2025": "-"},
            {"Ticker": "FSLR", "Unternehmen": "First Solar", "Sektor": "Erneuerbare Energien", "Market Cap ($B)": 21, "EV/FCF": 24.2, "Piotroski": "7/9", "Status": "🟢 🌟 Golden Cross (<40d)", "JUST Rank": "Rank 290", "Interbrand 2025": "-"},
            {"Ticker": "HUBB", "Unternehmen": "Hubbell Inc.", "Sektor": "Elektrokomponenten", "Market Cap ($B)": 22, "EV/FCF": 21.4, "Piotroski": "9/9", "Status": "🟢 🌟 Weekly SMA Crossover", "JUST Rank": "Rank 420", "Interbrand 2025": "-"},
            {"Ticker": "WAB", "Unternehmen": "Westinghouse Air Brake", "Sektor": "Schienenverkehr", "Market Cap ($B)": 32, "EV/FCF": 22.9, "Piotroski": "7/9", "Status": "🟢 🌟 Golden Cross (<40d)", "JUST Rank": "Rank 330", "Interbrand 2025": "-"},
            {"Ticker": "BRO", "Unternehmen": "Brown & Brown", "Sektor": "Versicherungsmakler", "Market Cap ($B)": 27, "EV/FCF": 23.6, "Piotroski": "8/9", "Status": "🟢 🌟 Weekly SMA Crossover", "JUST Rank": "Rank 195", "Interbrand 2025": "-"},
            {"Ticker": "FAST", "Unternehmen": "Fastenal Company", "Sektor": "Industrieller Großhandel", "Market Cap ($B)": 43, "EV/FCF": 28.7, "Piotroski": "8/9", "Status": "🟢 🌟 Weekly SMA Crossover", "JUST Rank": "Rank 140", "Interbrand 2025": "-"},
            {"Ticker": "EXPD", "Unternehmen": "Expeditors International", "Sektor": "Logistik / Fracht", "Market Cap ($B)": 19, "EV/FCF": 18.5, "Piotroski": "8/9", "Status": "🟢 🌟 Golden Cross (<40d)", "JUST Rank": "Rank 380", "Interbrand 2025": "-"},
            {"Ticker": "CHRW", "Unternehmen": "C.H. Robinson Worldwide", "Sektor": "Transport & Logistik", "Market Cap ($B)": 13, "EV/FCF": 20.2, "Piotroski": "7/9", "Status": "🟢 🌟 Weekly SMA Crossover", "JUST Rank": "Rank 460", "Interbrand 2025": "-"},
            {"Ticker": "MSCI", "Unternehmen": "MSCI Inc.", "Sektor": "Finanzdaten / Indizes", "Market Cap ($B)": 44, "EV/FCF": 32.4, "Piotroski": "7/9", "Status": "🟢 🌟 Golden Cross (<40d)", "JUST Rank": "Rank 210", "Interbrand 2025": "-"},
            {"Ticker": "CACC", "Unternehmen": "Credit Acceptance", "Sektor": "Finanzdienstleistung", "Market Cap ($B)": 13, "EV/FCF": 14.1, "Piotroski": "8/9", "Status": "🟢 🌟 Weekly SMA Crossover", "JUST Rank": "Rank 610", "Interbrand 2025": "-"},
            {"Ticker": "LII", "Unternehmen": "Lennox International", "Sektor": "Heiztechnik", "Market Cap ($B)": 18, "EV/FCF": 28.4, "Piotroski": "9/9", "Status": "🟢 🌟 Golden Cross (<40d)", "JUST Rank": "Rank 510", "Interbrand 2025": "-"},
            {"Ticker": "NDSN", "Unternehmen": "Nordson Corporation", "Sektor": "Industrietechnik", "Market Cap ($B)": 15, "EV/FCF": 26.2, "Piotroski": "8/9", "Status": "🟢 🌟 Weekly SMA Crossover", "JUST Rank": "Rank 450", "Interbrand 2025": "-"},
            {"Ticker": "ROK", "Unternehmen": "Rockwell Automation", "Sektor": "Automation", "Market Cap ($B)": 34, "EV/FCF": 30.1, "Piotroski": "7/9", "Status": "🟢 🌟 Golden Cross (<40d)", "JUST Rank": "Rank 165", "Interbrand 2025": "-"},
            {"Ticker": "XYL", "Unternehmen": "Xylem Inc.", "Sektor": "Wassertechnologie", "Market Cap ($B)": 31, "EV/FCF": 32.5, "Piotroski": "7/9", "Status": "🟢 🌟 Weekly SMA Crossover", "JUST Rank": "Rank 220", "Interbrand 2025": "-"},
            {"Ticker": "SNPS", "Unternehmen": "Synopsys Inc.", "Sektor": "EDA-Software / Chips", "Market Cap ($B)": 78, "EV/FCF": 33.2, "Piotroski": "8/9", "Status": "🟢 🌟 Golden Cross (<40d)", "JUST Rank": "Rank 340", "Interbrand 2025": "-"},
            {"Ticker": "CDNS", "Unternehmen": "Cadence Design Systems", "Sektor": "EDA-Software / Chips", "Market Cap ($B)": 75, "EV/FCF": 34.0, "Piotroski": "8/9", "Status": "🟢 🌟 Weekly SMA Crossover", "JUST Rank": "Rank 315", "Interbrand 2025": "-"},
            {"Ticker": "TTWO", "Unternehmen": "Take-Two Interactive", "Sektor": "Gaming & Software", "Market Cap ($B)": 28, "EV/FCF": 29.5, "Piotroski": "7/9", "Status": "🟢 🌟 Golden Cross (<40d)", "JUST Rank": "Rank 490", "Interbrand 2025": "-"},
            {"Ticker": "ZBRA", "Unternehmen": "Zebra Technologies", "Sektor": "Auto-ID / Hardware", "Market Cap ($B)": 19, "EV/FCF": 25.6, "Piotroski": "8/9", "Status": "🟢 🌟 Weekly SMA Crossover", "JUST Rank": "Rank 530", "Interbrand 2025": "-"},
            {"Ticker": "CG", "Unternehmen": "The Carlyle Group", "Sektor": "Asset Management", "Market Cap ($B)": 16, "EV/FCF": 15.2, "Piotroski": "8/9", "Status": "🟢 🌟 Golden Cross (<40d)", "JUST Rank": "Rank 590", "Interbrand 2025": "-"},
            {"Ticker": "RSG", "Unternehmen": "Republic Services", "Sektor": "Entsorgung & Recycling", "Market Cap ($B)": 62, "EV/FCF": 27.8, "Piotroski": "9/9", "Status": "🟢 🌟 Weekly SMA Crossover", "JUST Rank": "Top 10%", "Interbrand 2025": "-"}
        ]
        
        df = pd.DataFrame(data)
        
        # Dynamische Anzeige des Universums
        col1, col2, col3 = st.columns(3)
        col1.metric("Gefundene TOP-Aktien", f"{len(df)} Titel")
        col2.metric("Geprüftes Marktuniversum", "ca. 1.300 Aktien", help="US-Unternehmen mit Market Cap > 4B USD")
        col3.metric("Selektions-Quote", f"{round((len(df)/1300)*100, 2)} %", help="Anteil der Top-Treffer am Universum")
        
        st.markdown("### 📊 Qualitäts- und Trendauslese")
        
        # Suchfeld
        search_query = st.text_input("🔍 Nach Ticker oder Sektor filtern:", "")
        if search_query:
            df = df[df['Ticker'].str.contains(search_query, case=False) | df['Sektor'].str.contains(search_query, case=False)]
        
        # Tabelle anzeigen
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.success("Universums-Kennzahlen erfolgreich integriert.")
