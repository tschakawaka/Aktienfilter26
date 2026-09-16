import streamlit as st
import pandas as pd

st.set_page_title_config(page_title="AI Stock Agent", layout="wide")

st.title("🤖 AI Daily Stock Agent")
st.markdown("Automatisierter Screener nach deinen Kriterien (Market Cap, ROIC, Piotroski, EV/FCF, Crossovers).")

# Beispiel-Daten (später verbunden mit deinem Screening-Skript)
if st.button("🚀 Screening jetzt starten"):
    with st.spinner("Durchsuche den Markt und berechne Bilanzen..."):
        # Hier läuft dein Screening-Code...
        st.success("Screening abgeschlossen!")
        
        # Beispiel-Tabelle anzeigen
        data = {
            "Ticker": ["ANET", "URI", "DECK", "PH"],
            "Unternehmen": ["Arista Networks", "United Rentals", "Deckers Outdoor", "Parker-Hannifin"],
            "EV/FCF": [31.2, 16.4, 22.1, 21.5],
            "Piotroski": ["9/9", "7/9", "8/9", "8/9"],
            "Status": ["🟢 🌟 Weekly Crossover", "🟢 🌟 Weekly Crossover", "🟢 🌟 Golden Cross", "🟢 🌟 Weekly Crossover"]
        }
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
