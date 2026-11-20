import importlib.metadata
import re
from datetime import datetime

import pandas as pd
import requests
import streamlit as st
import yfinance as yf
from bs4 import BeautifulSoup
from finvizfinance import screener
from finvizfinance.quote import finvizfinance

# Seitenkonfiguration
st.set_page_config(page_title="AI Stock Screener 2026 (Live)", page_icon="📈", layout="wide")

# 🔴 Roter, kursiver Disclaimer ganz oben
st.markdown(
    """
    <div style="background-color: #ffe6e6; padding: 10px; border-radius: 5px; border-left: 5px solid #ff4d4d; margin-bottom: 20px;">
        <p style="color: #cc0000; font-style: italic; font-weight: bold; margin: 0;">
            ⚠️ Achtung, ist nur eine Testumgebung von Mag. Ralph Gollner, der erstmals einen KI-Agent aufgesetzt hat. Alle Angaben ohne Gewähr und keine Aktienempfehlung(en)!
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.title("🤖 Live AI-Agent: Reiner Echtzeit-Screener (ohne Anker-Liste)")
st.markdown(
    "**Harte Filter:** Market Cap **> $4B** | 6M-Perf > 0% | 3J-Umsatz- & Gewinn-CAGR **> 5% p.a.** | "
    "**ROIC > 15%** | **FCF > 0** | **EV/FCF < 35** | **Forward PE < Limit** | **Kurs > SMA-200** | **Piotroski ≥ 7**"
)

try:
    fv_version = importlib.metadata.version("finvizfinance")
except Exception:
    fv_version = "unbekannt"

# ⚙️ Sidebar Steuerung
st.sidebar.header("⚙️ Live-Filter Einstellungen")
max_fwd_pe = st.sidebar.slider("📉 Max. Forward PE", min_value=15, max_value=60, value=40, step=1)
min_piotroski = st.sidebar.selectbox("🏛️ Min. Piotroski F-Score", options=[7, 8, 9], index=0)
scan_limit = st.sidebar.slider("🔎 Max. Finviz-Vorkandidaten prüfen", min_value=20, max_value=150, value=60, step=10)

st.sidebar.markdown("---")
st.sidebar.subheader("Zusatz-Filter (optional)")
moat_filter = st.sidebar.checkbox("🏰 Nur Wide-Moat ETF (MOAT = JA)", value=False)
ethical_filter = st.sidebar.checkbox("🌱 Nur Global Ethical Values (GEVX = JA)", value=False)
glassdoor_filter = st.sidebar.checkbox("🏢 Nur Glassdoor Best Places (JA)", value=False)
validate_gf = st.sidebar.checkbox("🔍 GuruFocus F-Score Live-Check (langsam)", value=False)

if st.sidebar.button("🔄 Cache leeren & Live neu scannen", type="primary"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.caption(f"Installierte finvizfinance-Version: `{fv_version}`")


# --- HILFSFUNKTIONEN ---

def normalize_company_name(name: str) -> str:
    if not name:
        return ""
    s = name.lower()
    s = re.sub(r"[^\w\s]", " ", s)
    stop_words = {
        "inc", "incorporated", "corp", "corporation", "co", "company",
        "llc", "ltd", "limited", "plc", "ag", "se", "sa", "nv", "group",
        "holdings", "holding", "the", "and"
    }
    tokens = [t for t in s.split() if t not in stop_words]
    return " ".join(tokens).strip()


def parse_mcap_to_billions(val) -> float:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return 0.0
    if isinstance(val, (int, float)):
        if val > 1e7:
            return float(val) / 1e9
        if val > 100:
            return float(val) / 1e3
        return float(val)
    s = str(val).strip().upper().replace(",", "")
    try:
        if s.endswith("T"):
            return float(s.replace("T", "")) * 1000.0
        if s.endswith("B"):
            return float(s.replace("B", ""))
        if s.endswith("M"):
            return float(s.replace("M", "")) / 1000.0
        num = float(s)
        return num / 1e9 if num > 1e7 else num
    except Exception:
        return 0.0


@st.cache_data(ttl=86400)
def fetch_gevx_universe():
    """Lädt tagesaktuell die Einzelwerte des Global Ethical Values Index (Börse Hannover)."""
    url = "https://www.boerse-hannover.de/nachhaltigkeit/gevx/gevx-einzelwerte/"
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if resp.status_code != 200:
            return set(), f"HTTP {resp.status_code}"
        soup = BeautifulSoup(resp.text, "lxml")
        names = set()
        for row in soup.find_all(["tr", "li"]):
            cells = [c.get_text(" ", strip=True) for c in row.find_all(["td", "th"])]
            text = cells.pop(0) if cells else row.get_text(" ", strip=True)
            norm = normalize_company_name(text)
            if len(norm) >= 3:
                names.add(norm)
        return names, f"Geladen ({len(names)} Einträge)"
    except Exception as e:
        return set(), f"Fehler ({e})"


@st.cache_data(ttl=86400)
def fetch_glassdoor_universe():
    """Versucht, die Glassdoor Best Places to Work Liste abzurufen."""
    url = "https://www.glassdoor.com/Award/Best-Places-to-Work-LST_KQ0,19.htm"
    try:
        resp = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept-Language": "en-US,en;q=0.9",
            },
            timeout=8,
        )
        if resp.status_code != 200:
            return set(), f"Blockiert (HTTP {resp.status_code})"
        soup = BeautifulSoup(resp.text, "lxml")
        names = set()
        for tag in soup.find_all(["h2", "h3", "a", "span"]):
            txt = tag.get_text(" ", strip=True)
            if 3 <= len(txt) <= 60:
                norm = normalize_company_name(txt)
                if norm:
                    names.add(norm)
        if not names:
            return set(), "Keine Daten geparst"
        return names, f"Geladen ({len(names)} Einträge)"
    except Exception:
        return set(), "Blockiert/Timeout"


@st.cache_data(ttl=86400)
def fetch_gurufocus_piotroski(ticker: str):
    try:
        url = f"https://www.gurufocus.com/stock/{ticker}/summary"
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=6)
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.text, "lxml")
        text = soup.get_text(" ", strip=True)
        match = re.search(r"Piotroski\s*F-Score\s*[:\-]?\s*(\d)\s*/\s*9", text, re.IGNORECASE)
        if match:
            return f"{match.group(1)}/9"
        return None
    except Exception:
        return None


@st.cache_data(ttl=1800)
def fetch_finviz_prefiltered(limit: int):
    """
    Holt dynamisch US-Aktien (exkl. Fonds) von Finviz, die die Basisfilter erfüllen:
    - Market Cap > $2B (exakte >= $4B Prüfung folgt)
    - ROI > 15%
    - Positives 5J Umsatz- und Gewinnwachstum
    - Kurs > SMA-200
    - 6M-Performance positiv
    """
    finviz_url = (
        "https://finviz.com/screener.ashx?v=111"
        "&f=cap_midover,fa_roi_o15,fa_sales5years_pos,fa_eps5years_pos,ta_sma200_pa,ta_perf_26wup,ind_stocksonly"
    )
    try:
        if hasattr(screener, "from_url"):
            fscreen = screener.from_url(finviz_url)
        else:
            from finvizfinance.screener.overview import Overview
            fscreen = Overview()
            fscreen.set_filter(
                filters_dict={
                    "Market Cap.": "+Mid (over $2bln)",
                    "Return on Investment": "Over +15%",
                    "200-Day Simple Moving Average": "Price above SMA200",
                    "Performance": "Half Year Up",
                }
            )

        try:
            df = fscreen.screener_view(order="Market Cap.", ascend=False, limit=limit, verbose=0)
        except Exception:
            df = fscreen.screener_view(limit=limit, verbose=0)

        if df is None or df.empty:
            return pd.DataFrame(), None
        return df, None
    except Exception as e:
        return pd.DataFrame(), str(e)


def get_row_val(df: pd.DataFrame, keys: list, col_idx: int):
    if col_idx >= len(df.columns):
        return None
    col_name = df.columns.tolist().pop(col_idx)
    for k in keys:
        if k in df.index:
            val = df.at[k, col_name]
            if pd.notna(val):
                return float(val)
    return None


def calculate_piotroski_9(fin: pd.DataFrame, bs: pd.DataFrame, cf: pd.DataFrame):
    """Berechnet alle 9 Punkte des Piotroski F-Scores aus den Jahresberichten."""
    if fin.empty or bs.empty or cf.empty:
        return None
    if len(fin.columns) < 2 or len(bs.columns) < 2 or len(cf.columns) < 2:
        return None

    score = 0
    ni_0 = get_row_val(fin, ["Net Income", "Net Income Common Stockholders"], 0)
    ta_0 = get_row_val(bs, ["Total Assets"], 0)
    ta_1 = get_row_val(bs, ["Total Assets"], 1)
    cfo_0 = get_row_val(cf, ["Operating Cash Flow", "Total Cash From Operating Activities"], 0)

    if None in (ni_0, ta_0, ta_1, cfo_0) or ta_0 == 0 or ta_1 == 0:
        return None

    # 1-4: Profitabilität
    if ni_0 > 0:
        score += 1
    if (ni_0 / ta_0) > 0:
        score += 1
    if cfo_0 > 0:
        score += 1
    if cfo_0 > ni_0:
        score += 1

    # 5: Verschuldungsgrad (Long Term Debt / Assets gesunken oder 0)
    ltd_0 = get_row_val(bs, ["Long Term Debt", "Long Term Debt And Capital Lease Obligation"], 0) or 0.0
    ltd_1 = get_row_val(bs, ["Long Term Debt", "Long Term Debt And Capital Lease Obligation"], 1) or 0.0
    if (ltd_0 / ta_0) <= (ltd_1 / ta_1):
        score += 1

    # 6: Liquidität (Current Ratio gestiegen)
    ca_0 = get_row_val(bs, ["Current Assets"], 0)
    cl_0 = get_row_val(bs, ["Current Liabilities"], 0)
    ca_1 = get_row_val(bs, ["Current Assets"], 1)
    cl_1 = get_row_val(bs, ["Current Liabilities"], 1)
    if None not in (ca_0, cl_0, ca_1, cl_1) and cl_0 > 0 and cl_1 > 0:
        if (ca_0 / cl_0) > (ca_1 / cl_1):
            score += 1

    # 7: Keine Aktienverwässerung
    sh_0 = get_row_val(bs, ["Ordinary Shares Number", "Share Issued"], 0)
    sh_1 = get_row_val(bs, ["Ordinary Shares Number", "Share Issued"], 1)
    if sh_0 is not None and sh_1 is not None and sh_0 <= sh_1:
        score += 1

    # 8-9: Operative Effizienz (Gross Margin & Asset Turnover gestiegen)
    gp_0 = get_row_val(fin, ["Gross Profit"], 0)
    gp_1 = get_row_val(fin, ["Gross Profit"], 1)
    rev_0 = get_row_val(fin, ["Total Revenue"], 0)
    rev_1 = get_row_val(fin, ["Total Revenue"], 1)
    if None not in (gp_0, gp_1, rev_0, rev_1) and rev_0 > 0 and rev_1 > 0:
        if (gp_0 / rev_0) > (gp_1 / rev_1):
            score += 1
    if None not in (rev_0, rev_1) and (rev_0 / ta_0) > (rev_1 / ta_1):
        score += 1

    return score


def calculate_roic(fin: pd.DataFrame, bs: pd.DataFrame):
    """Berechnet ROIC = NOPAT / Invested Capital in %."""
    ebit = get_row_val(fin, ["EBIT", "Operating Income"], 0)
    if ebit is None:
        return None

    tax_prov = get_row_val(fin, ["Tax Provision"], 0)
    pretax = get_row_val(fin, ["Pretax Income"], 0)
    if tax_prov is not None and pretax is not None and pretax > 0:
        tax_rate = max(0.0, min(0.35, tax_prov / pretax))
    else:
        tax_rate = 0.21

    nopat = ebit * (1.0 - tax_rate)

    inv_cap = get_row_val(bs, ["Invested Capital"], 0)
    if inv_cap is None or inv_cap <= 0:
        debt = get_row_val(bs, ["Total Debt"], 0) or 0.0
        equity = get_row_val(bs, ["Stockholders Equity", "Common Stock Equity"], 0)
        cash = get_row_val(bs, ["Cash And Cash Equivalents"], 0) or 0.0
        if equity is None:
            return None
        inv_cap = debt + equity - cash

    if inv_cap <= 0:
        return None
    return (nopat / inv_cap) * 100.0


def calculate_3y_cagr_and_trend(df_stmt: pd.DataFrame, row_keys: list):
    """Berechnet die echte 3-Jahres-CAGR (p.a.) und prüft auf durchgängiges Wachstum."""
    vals = []
    for idx in range(min(4, len(df_stmt.columns))):
        v = get_row_val(df_stmt, row_keys, idx)
        if v is None:
            return None, None
        vals.append(v)

    if len(vals) < 4:
        return None, None

    v_now = vals.pop(0)
    v_1 = vals.pop(0)
    v_2 = vals.pop(0)
    v_3y = vals.pop(0)
    if v_3y <= 0 or v_now <= 0:
        return None, None

    cagr = ((v_now / v_3y) ** (1.0 / 3.0) - 1.0) * 100.0
    monotonic = (v_now > v_1 > v_2 > v_3y)
    trend_label = f"📈 +{cagr:.1f}% p.a." if monotonic else f"🔄 +{cagr:.1f}% (Zyklisch)"
    return cagr, trend_label


@st.cache_data(ttl=3600)
def evaluate_candidate(ticker: str, finviz_mcap_b: float, finviz_company: str, finviz_sector: str, max_fpe: float, min_f_score: int):
    """Prüft einen einzelnen Ticker streng gegen alle quantitativen & technischen Regeln."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info or {}

        # 1. Market Cap (>= 4B USD)
        mcap_yf_raw = info.get("marketCap", 0) or 0
        mcap_yf_b = mcap_yf_raw / 1e9
        if mcap_yf_b < 4.0:
            return None
        if finviz_mcap_b > 0 and finviz_mcap_b < 4.0:
            return None

        # 2. Forward PE (Vorabprüfung via yfinance)
        fwd_pe_yf = info.get("forwardPE")
        if fwd_pe_yf is not None and (fwd_pe_yf <= 0 or fwd_pe_yf > max_fpe):
            return None

        # 3. Historie & Chartsignale (Kurs > SMA-200, 6M-Perf > 0%, Golden Cross < 40d, Weekly SMA 15/30)
        hist = stock.history(period="3y")
        if hist.empty or len(hist) < 220:
            return None
        closes = hist["Close"].dropna()
        if len(closes) < 220:
            return None

        curr_price = float(closes.tail(1).item())
        sma_50 = closes.rolling(window=50).mean()
        sma_200 = closes.rolling(window=200).mean()

        curr_sma50 = float(sma_50.tail(1).item())
        curr_sma200 = float(sma_200.tail(1).item())

        if pd.isna(curr_sma200) or curr_price <= curr_sma200:
            return None

        # 6M Performance (> 0%) & 2Y Performance
        p_6m = float(closes.tail(126).head(1).item())
        perf_6m = ((curr_price - p_6m) / p_6m) * 100.0
        if perf_6m <= 0:
            return None

        p_2y = float(closes.tail(504).head(1).item())
        perf_2y = ((curr_price - p_2y) / p_2y) * 100.0

        # RSI 14
        delta = closes.diff()
        gain = delta.clip(lower=0).rolling(window=14).mean()
        loss = -delta.clip(upper=0).rolling(window=14).mean()
        rs = gain / loss.replace(0, 1e-9)
        rsi = float((100.0 - (100.0 / (1.0 + rs))).tail(1).item())

        # Golden Cross in den letzten 40 Handelstagen
        diff_daily = (sma_50 - sma_200).tail(40)
        gc_40d = bool(((diff_daily.shift(1) <= 0) & (diff_daily > 0)).any())

        # Weekly SMA 15 / 30 Check
        weekly_closes = closes.resample("W-FRI").last().dropna()
        weekly_cross = False
        weekly_bullish = False
        if len(weekly_closes) >= 35:
            w_sma15 = weekly_closes.rolling(window=15).mean()
            w_sma30 = weekly_closes.rolling(window=30).mean()
            weekly_bullish = bool(w_sma15.tail(1).item() > w_sma30.tail(1).item())
            w_diff = w_sma15 - w_sma30
            weekly_cross = bool(((w_diff.shift(1) <= 0) & (w_diff > 0)).tail(10).any())

        is_bullish_chart = (curr_price > curr_sma50 > curr_sma200) and (50.0 <= rsi <= 72.0)

        # 4. Jahresabschlüsse laden und absteigend nach Datum sortieren (Spalte 0 = neuestes Jahr)
        fin = stock.financials
        bs = stock.balance_sheet
        cf = stock.cashflow
        if fin.empty or bs.empty or cf.empty:
            return None

        fin = fin.sort_index(axis=1, ascending=False)
        bs = bs.sort_index(axis=1, ascending=False)
        cf = cf.sort_index(axis=1, ascending=False)

        # 5. Free Cash Flow (> 0) & EV/FCF (< 35)
        fcf = get_row_val(cf, ["Free Cash Flow"], 0)
        if fcf is None:
            cfo = get_row_val(cf, ["Operating Cash Flow", "Total Cash From Operating Activities"], 0)
            capex = get_row_val(cf, ["Capital Expenditure"], 0)
            if cfo is not None and capex is not None:
                fcf = cfo - abs(capex)
        ev = info.get("enterpriseValue")
        if fcf is None or fcf <= 0 or not ev or ev <= 0:
            return None
        ev_fcf = ev / fcf
        if ev_fcf >= 35.0:
            return None

        # 6. 3-Jahres Umsatz- & Gewinnwachstum (> 5% p.a.)
        rev_cagr, rev_label = calculate_3y_cagr_and_trend(fin, ["Total Revenue"])
        ni_cagr, ni_label = calculate_3y_cagr_and_trend(fin, ["Net Income", "Net Income Common Stockholders"])
        if rev_cagr is None or ni_cagr is None:
            return None
        if rev_cagr <= 5.0 or ni_cagr <= 5.0:
            return None

        # 7. ROIC (> 15%)
        roic = calculate_roic(fin, bs)
        if roic is None or roic <= 15.0:
            return None

        # 8. Piotroski F-Score (>= min_f_score)
        p_score = calculate_piotroski_9(fin, bs, cf)
        if p_score is None or p_score < min_f_score:
            return None

        # 9. Finviz Quote Cross-Check für Finalisten (Forward PE, Market Cap, Wide-Moat ETF Holders)
        fwd_pe_finviz = None
        moat_etf = "N/A"
        mcap_cross = "✅ yf"
        try:
            fq = finvizfinance(ticker)
            fund = fq.ticker_fundament()
            fpe_str = fund.get("Forward P/E", "-")
            if fpe_str and fpe_str != "-":
                fwd_pe_finviz = float(fpe_str)
            fv_mcap_b = parse_mcap_to_billions(fund.get("Market Cap", "0"))
            if fv_mcap_b > 0:
                diff_pct = abs(mcap_yf_b - fv_mcap_b) / mcap_yf_b * 100.0
                mcap_cross = "✅ Finviz & yf" if diff_pct < 10.0 else f"⚠️ Diff {diff_pct:.0f}%"
            etf_holders = fq.ticker_etf_holders()
            if isinstance(etf_holders, (list, tuple)):
                moat_etf = "JA" if "MOAT" in [str(x).upper() for x in etf_holders] else "NEIN"
            else:
                moat_etf = "NEIN"
        except Exception:
            pass

        final_fwd_pe = fwd_pe_finviz if fwd_pe_finviz is not None else fwd_pe_yf
        if final_fwd_pe is None or final_fwd_pe <= 0 or final_fwd_pe > max_fpe:
            return None

        # Status-Text bauen
        signals = []
        if gc_40d:
            signals.append("🌟 Golden Cross (<40d)")
        if weekly_cross:
            signals.append("🌟 Weekly SMA 15/30 Cross")
        elif weekly_bullish:
            signals.append("W-SMA 15>30")
        if is_bullish_chart:
            status_text = "🟢 BULLISCH: " + (" | ".join(signals) if signals else f"RSI {rsi:.0f}")
        else:
            status_text = "⚪ ÜBER SMA200: " + (" | ".join(signals) if signals else f"RSI {rsi:.0f}")

        company_name = finviz_company or info.get("shortName", ticker)
        return {
            "Ticker": ticker,
            "Unternehmen": company_name,
            "Sektor": finviz_sector or info.get("sector", "N/A"),
            "Market Cap ($B)": round(mcap_yf_b, 1),
            "MCap Check": mcap_cross,
            "Forward PE": round(final_fwd_pe, 1),
            "EV/FCF": round(ev_fcf, 1),
            "ROIC (%)": round(roic, 1),
            "Umsatz (3J)": rev_label,
            "Earnings (3J)": ni_label,
            "6M Perf. (%)": f"+{perf_6m:.1f}%",
            "2Y Perf. (%)": f"{'+' if perf_2y > 0 else ''}{perf_2y:.1f}%",
            "Piotroski": f"{p_score}/9",
            "Wide-Moat ETF": moat_etf,
            "Status": status_text,
        }
    except Exception:
        return None


# --- HAUPTPROGRAMM ---

with st.spinner("1/3 Lade externe Vergleichs-Indizes (Börse Hannover GEVX & Glassdoor)..."):
    gevx_names, gevx_status = fetch_gevx_universe()
    gd_names, gd_status = fetch_glassdoor_universe()

with st.spinner(f"2/3 Frage Finviz Live-Screener ab (max. {scan_limit} Top-Kandidaten nach Market Cap)..."):
    df_finviz, fv_error = fetch_finviz_prefiltered(scan_limit)

if fv_error or df_finviz.empty:
    st.error(
        f"Finviz Live-Abfrage lieferte aktuell keine Daten ({fv_error or '0 Treffer / Rate-Limit'}). "
        f"(finvizfinance-Version: {fv_version}). Es werden bewusst KEINE statischen Beispiel-Aktien als Ersatz angezeigt."
    )
    st.stop()

st.caption(
    f"Finviz-Vorfilter lieferte **{len(df_finviz)}** US-Kandidaten (> $2B, ROI > 15%, Kurs > SMA-200, 6M > 0%). "
    "Prüfe nun streng auf Market Cap ≥ $4B, 3J-CAGR > 5%, ROIC > 15%, EV/FCF < 35, Forward PE und Piotroski F-Score..."
)

results = []
progress = st.progress(0.0)
total = len(df_finviz)

for i, (_, fv_row) in enumerate(df_finviz.iterrows()):
    ticker = str(fv_row.get("Ticker", "")).strip()
    fv_mcap_b = parse_mcap_to_billions(fv_row.get("Market Cap", 0))
    fv_comp = str(fv_row.get("Company", "")).strip()
    fv_sec = str(fv_row.get("Sector", "")).strip()

    res = evaluate_candidate(ticker, fv_mcap_b, fv_comp, fv_sec, max_fwd_pe, min_piotroski)
    if res is not None:
        norm_comp = normalize_company_name(res["Unternehmen"])
        if gevx_names:
            res["Global Ethical Values"] = "JA" if any(norm_comp in g or g in norm_comp for g in gevx_names) else "NEIN"
        else:
            res["Global Ethical Values"] = f"N/A ({gevx_status})"

        if gd_names:
            res["Glassdoor 100"] = "JA" if any(norm_comp in g or g in norm_comp for g in gd_names) else "NEIN"
        else:
            res["Glassdoor 100"] = f"N/A ({gd_status})"

        if validate_gf:
            gf_score = fetch_gurufocus_piotroski(ticker)
            res["Piotroski (GuruFocus)"] = gf_score if gf_score else "Nicht abrufbar"

        results.append(res)

    progress.progress((i + 1) / total)

progress.empty()
df_final = pd.DataFrame(results)

# Optionale Zusatzfilter in der Sidebar anwenden
if not df_final.empty:
    if moat_filter:
        df_final = df_final[df_final["Wide-Moat ETF"] == "JA"]
    if ethical_filter:
        df_final = df_final[df_final["Global Ethical Values"] == "JA"]
    if glassdoor_filter:
        df_final = df_final[df_final["Glassdoor 100"] == "JA"]

# Metrik-Leiste
col1, col2, col3, col4 = st.columns(4)
col1.metric("Qualifizierte Aktien (Live)", f"{len(df_final)} Titel")
col2.metric("Geprüfte Finviz-Kandidaten", f"{total} (aus ~1.500 >$4B)")
col3.metric("Max. Forward PE", f"≤ {max_fwd_pe}")
col4.metric("Min. Piotroski Score", f"≥ {min_piotroski}/9")

st.markdown("### 📊 Echte Live-Auslese (100% dynamisch berechnet)")

search = st.text_input("🔍 Tabelle nach Ticker, Unternehmen oder Sektor filtern:", "")
if search and not df_final.empty:
    mask = (
        df_final["Ticker"].str.contains(search, case=False, na=False)
        | df_final["Unternehmen"].str.contains(search, case=False, na=False)
        | df_final["Sektor"].str.contains(search, case=False, na=False)
    )
    df_final = df_final[mask]

if not df_final.empty:
    st.dataframe(df_final, use_container_width=True, hide_index=True)
    st.success(f"Live-Screening erfolgreich abgeschlossen am {datetime.now().strftime('%d.%m.%Y um %H:%M Uhr')}.")
else:
    st.warning(
        "0 Aktien aus den geprüften Finviz-Kandidaten haben aktuell ALLE harten Kriterien gleichzeitig bestanden. "
        "Erhöhe ggf. die Anzahl der geprüften Finviz-Kandidaten oder lockere das Forward-PE- bzw. Piotroski-Limit."
    )

# Fußnote
st.markdown("---")
st.markdown(
    f"""
    <div style="font-size: 0.85rem; color: #555;">
        <p><b>* Hinweise zu den dynamischen Prüfquellen:</b><br>
        - <b>Wide-Moat ETF (MOAT):</b> Live-Abfrage der ETF-Halter via Finviz (<code>ticker_etf_holders</code>).<br>
        - <b>Global Ethical Values (GEVX):</b> Live-Abgleich mit <a href="https://www.boerse-hannover.de/nachhaltigkeit/gevx/gevx-einzelwerte/" target="_blank">Börse Hannover</a> (Status: {gevx_status}).<br>
        - <b>Glassdoor Best Places to Work:</b> Live-Abruf von <a href="https://www.glassdoor.com/Award/Best-Places-to-Work-LST_KQ0,19.htm" target="_blank">Glassdoor</a> (Status: {gd_status}).</p>
    </div>
    """,
    unsafe_allow_html=True,
)
