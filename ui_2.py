import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import importlib.util, sys, os, copy, time
from pathlib import Path

st.set_page_config(
    page_title="Kit Atama Opt. — TürkTraktör",
    page_icon="🏭", layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@300;400;500&family=JetBrains+Mono:wght@400;600&family=Inter:wght@300;400;500;600&display=swap');

:root {
  --navy:       #0A1628;
  --navy-mid:   #1B2A4A;
  --navy-light: #243554;
  --orange:     #E85C1A;
  --orange-hi:  #FF7A3D;
  --orange-glow:rgba(232,92,26,.35);
  --slate:      #8FAECB;
  --slate-dim:  #4A6280;
  --ice:        #F0F4FA;
  --white:      #FFFFFF;
  --success:    #22c55e;
  --warn:       #f59e0b;
  --danger:     #ef4444;
}

* { box-sizing: border-box; }

/* ══ SCROLLBAR ══ */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--navy); }
::-webkit-scrollbar-thumb { background: var(--orange); border-radius: 4px; }

/* ══ BODY ══ */
.stApp {
    background: var(--ice);
    color: var(--navy-mid);
    font-family: 'Inter', sans-serif;
    font-size: 14px;
}
header[data-testid="stHeader"] { background: transparent !important; }

/* ══ SIDEBAR ══ */
section[data-testid="stSidebar"] {
    background: linear-gradient(170deg, #08111F 0%, #0F1E38 35%, #162542 70%, #0A1628 100%) !important;
    border-right: 2px solid rgba(232,92,26,.6) !important;
    box-shadow: 4px 0 30px rgba(0,0,0,.5) !important;
    overflow: hidden !important;
    position: relative !important;
}
section[data-testid="stSidebar"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--orange), var(--orange-hi), transparent);
}
section[data-testid="stSidebar"] > div:first-child,
div[data-testid="stSidebarContent"] {
    overflow-y: auto !important;
    overflow-x: hidden !important;
    height: 100vh !important;
    padding-bottom: 80px !important;
    scrollbar-width: thin !important;
    scrollbar-color: var(--orange) var(--navy) !important;
}
section[data-testid="stSidebar"] > div:first-child::-webkit-scrollbar { width: 4px; }
section[data-testid="stSidebar"] > div:first-child::-webkit-scrollbar-thumb { background: var(--orange); border-radius: 2px; }
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"],
section[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] { overflow: visible !important; }

section[data-testid="stSidebar"] * { color: #C8D8EA !important; }
section[data-testid="stSidebar"] label {
    color: var(--slate) !important;
    font-size: 10px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 600 !important;
    letter-spacing: .1em !important;
    text-transform: uppercase !important;
}
section[data-testid="stSidebar"] .stSlider > div > div { background: rgba(232,92,26,.15) !important; }
section[data-testid="stSidebar"] .stSlider > div > div > div {
    background: var(--orange) !important;
    border: 2px solid var(--orange-hi) !important;
    box-shadow: 0 0 8px var(--orange-glow) !important;
}
section[data-testid="stSidebar"] input {
    background: rgba(255,255,255,.06) !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(255,255,255,.12) !important;
    border-radius: 6px !important;
}

/* ══ KPI KARTLARI ══ */
.kpi {
    flex: 1;
    background: var(--white);
    border: 1px solid #E0E8F0;
    border-top: 3px solid #CBD8E8;
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 1px 3px rgba(10,22,40,.06), 0 4px 16px rgba(10,22,40,.04);
    transition: transform .2s ease, box-shadow .2s ease;
    position: relative;
    overflow: hidden;
}
.kpi::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(10,22,40,.08), transparent);
}
.kpi:hover { box-shadow: 0 4px 16px rgba(10,22,40,.1); }
.kpi .lbl {
    font-size: 9px;
    color: var(--slate-dim);
    text-transform: uppercase;
    letter-spacing: .18em;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    margin-bottom: 8px;
}
.kpi .val {
    font-size: 22px;
    font-weight: 500;
    color: var(--navy-mid);
    font-family: 'DM Mono', 'JetBrains Mono', monospace;
    line-height: 1;
    letter-spacing: 0;
    font-variant-numeric: tabular-nums;
}
.kpi.green  { border-top-color: var(--success); } .kpi.green .val  { color: #16a34a; }
.kpi.yellow { border-top-color: var(--warn); }    .kpi.yellow .val { color: #d97706; }
.kpi.red    { border-top-color: var(--danger); }  .kpi.red .val    { color: #dc2626; }
.kpi.orange { border-top-color: var(--orange); }  .kpi.orange .val { color: var(--orange); }
.kpi.blue   { border-top-color: var(--navy-mid); }.kpi.blue .val   { color: var(--navy-mid); }

/* ══ BÖLÜM BAŞLIĞI ══ */
.slabel {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    font-weight: 700;
    color: var(--orange);
    text-transform: uppercase;
    letter-spacing: .24em;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(232,92,26,.3);
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 6px;
}
section[data-testid="stSidebar"] .slabel {
    color: var(--orange) !important;
    border-bottom-color: rgba(232,92,26,.25) !important;
}

/* ══ BADGE ══ */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    letter-spacing: .04em;
}
.b-opt  { background: rgba(34,197,94,.12);  color: #15803d; border: 1px solid rgba(34,197,94,.3); }
.b-uyg  { background: rgba(245,158,11,.12); color: #b45309; border: 1px solid rgba(245,158,11,.3); }
.b-err  { background: rgba(239,68,68,.12);  color: #dc2626; border: 1px solid rgba(239,68,68,.3); }

/* ══ BUTONLAR ══ */
.stButton > button {
    background: linear-gradient(135deg, var(--orange) 0%, var(--orange-hi) 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', 'Inter', sans-serif !important;
    font-weight: 700 !important;
    font-size: 12px !important;
    letter-spacing: .02em !important;
    text-transform: uppercase !important;
    padding: 12px 14px !important;
    transition: background .12s ease, box-shadow .12s ease, border-color .12s ease !important;
    box-shadow: 0 2px 8px var(--orange-glow) !important;
    position: relative !important;
    overflow: visible !important;
    min-height: 52px !important;
    white-space: nowrap !important;
    word-break: normal !important;
    overflow-wrap: normal !important;
    hyphens: none !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    line-height: 1.15 !important;
}

.stButton > button p,
.stButton > button span,
.stDownloadButton > button p,
.stDownloadButton > button span {
    white-space: nowrap !important;
    word-break: normal !important;
    overflow-wrap: normal !important;
    hyphens: none !important;
    line-height: 1.15 !important;
    margin: 0 !important;
}


/* Streamlit buton içindeki markdown p tag'i bazen metni kırpıyor; bunu engeller */
.stButton > button div[data-testid="stMarkdownContainer"],
.stDownloadButton > button div[data-testid="stMarkdownContainer"] {
    width: 100% !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    overflow: visible !important;
}

/* Dar kolonlardaki kısa aksiyon butonları için okunabilirlik */
.stButton > button p {
    font-size: inherit !important;
    letter-spacing: inherit !important;
}

.stButton > button::before {
    content: '';
    position: absolute;
    top: 0; left: -100%; right: 100%; bottom: 0;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,.15), transparent);
    transition: none;
}
.stButton > button:hover::before { left: -100%; right: 100%; }
.stButton > button:hover {
    background: linear-gradient(135deg, var(--orange-hi) 0%, #FFB08A 100%) !important;
    box-shadow: 0 4px 20px rgba(232,92,26,.55) !important;
}
.run-btn > .stButton > button {
    background: linear-gradient(135deg, var(--orange) 0%, var(--orange-hi) 100%) !important;
    box-shadow: 0 2px 12px var(--orange-glow) !important;
    font-size: 13px !important;
    padding: 14px 20px !important;
    border: none !important;
    letter-spacing: .12em !important;
    color: #FFFFFF !important;
    text-shadow: 0 1px 2px rgba(0,0,0,.2) !important;
}
.run-btn > .stButton > button p,
.run-btn > .stButton > button span,
.run-btn > .stButton > button div[data-testid="stMarkdownContainer"] {
    color: #FFFFFF !important;
    opacity: 1 !important;
    font-weight: 700 !important;
}
.run-btn > .stButton > button:hover {
    background: linear-gradient(135deg, var(--orange-hi) 0%, #FFB08A 100%) !important;
    box-shadow: 0 4px 20px rgba(232,92,26,.55) !important;
}


/* Hover sırasında sayfanın titremesini engeller:
   transform/ölçek/yer değiştirme kapatıldı, buton boyutu sabit tutuldu. */
.stButton > button,
.stButton > button:hover,
.stButton > button:focus,
.stButton > button:active,
.stDownloadButton > button,
.stDownloadButton > button:hover,
.stDownloadButton > button:focus,
.stDownloadButton > button:active {
    transform: none !important;
    will-change: auto !important;
    backface-visibility: hidden !important;
    min-height: 46px !important;
}

.stButton > button::before,
.stDownloadButton > button::before {
    pointer-events: none !important;
}

/* Primary button type — turuncu, diğer butonlarla aynı */
button[kind="primary"] {
    background: linear-gradient(135deg, var(--orange) 0%, var(--orange-hi) 100%) !important;
    border: none !important;
    color: #FFFFFF !important;
}
button[kind="primary"]:hover {
    background: linear-gradient(135deg, var(--orange-hi) 0%, #FFB08A 100%) !important;
    box-shadow: 0 4px 20px rgba(232,92,26,.55) !important;
}


/* ══ FORM BUTONLARI: Listeye Ekle / Tümünü Sil turuncu kalsın ══ */
[data-testid="stForm"] [data-testid="stFormSubmitButton"] > button,
.stFormSubmitButton > button,
div[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(135deg, var(--orange) 0%, var(--orange-hi) 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', 'Inter', sans-serif !important;
    font-weight: 700 !important;
    font-size: 11px !important;
    letter-spacing: .04em !important;
    text-transform: uppercase !important;
    padding: 10px 14px !important;
    min-height: 46px !important;
    box-shadow: 0 2px 8px var(--orange-glow) !important;
    transition: background .12s ease, box-shadow .12s ease, border-color .12s ease !important;
    transform: none !important;
}

[data-testid="stForm"] [data-testid="stFormSubmitButton"] > button:hover,
.stFormSubmitButton > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover {
    background: linear-gradient(135deg, var(--orange-hi) 0%, #FF8A4F 100%) !important;
    box-shadow: 0 4px 14px rgba(232,92,26,.42) !important;
    transform: none !important;
}

[data-testid="stForm"] [data-testid="stFormSubmitButton"] > button p,
[data-testid="stForm"] [data-testid="stFormSubmitButton"] > button span,
.stFormSubmitButton > button p,
.stFormSubmitButton > button span,
div[data-testid="stFormSubmitButton"] > button p,
div[data-testid="stFormSubmitButton"] > button span {
    color: #FFFFFF !important;
    opacity: 1 !important;
    white-space: nowrap !important;
    word-break: normal !important;
    overflow-wrap: normal !important;
}

/* ══ SEKMELER ══ */
div[data-testid="stTabs"] { border-bottom: 1px solid #E0E8F0 !important; }
div[data-testid="stTabs"] button {
    font-family: 'DM Sans', 'Inter', sans-serif !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    color: var(--slate-dim) !important;
    letter-spacing: .08em !important;
    text-transform: uppercase !important;
    padding: 12px 22px !important;
    transition: color .2s !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--orange) !important;
    border-bottom: 2px solid var(--orange) !important;
}
div[data-testid="stTabs"] button:hover { color: var(--navy-mid) !important; }

/* ══ INPUT ETİKETLERİ ══ */
div[data-testid="stSlider"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stTextInput"] label {
    font-size: 10px !important;
    color: var(--slate-dim) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: .1em !important;
}

/* ══ METRİK KARTLARI ══ */
.metric-card {
    background: var(--white);
    border: 1px solid #E0E8F0;
    border-radius: 10px;
    padding: 16px;
    text-align: center;
    box-shadow: 0 1px 3px rgba(10,22,40,.05);
    transition: box-shadow .2s;
}
.metric-card:hover { box-shadow: 0 4px 16px rgba(10,22,40,.1); }
.metric-card .mc-label {
    font-size: 9px;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    color: var(--slate-dim);
    text-transform: uppercase;
    letter-spacing: .18em;
    margin-bottom: 8px;
}
.metric-card .mc-value {
    font-size: 32px;
    font-weight: 800;
    font-family: 'DM Sans', 'Inter', sans-serif;
    color: var(--navy-mid);
    line-height: 1;
    letter-spacing: -.02em;
}
.metric-card .mc-unit {
    font-size: 10px;
    color: #9AACC5;
    margin-top: 5px;
    font-family: 'Inter', sans-serif;
}

/* ══ BAŞLIKLAR ══ */
h1, h2, h3 {
    font-family: 'DM Sans', 'Inter', sans-serif !important;
    color: var(--navy-mid) !important;
    font-weight: 800 !important;
    letter-spacing: -.01em !important;
}
h3 { font-size: 18px !important; }
p, li { color: #334155; line-height: 1.6; }

/* ══ TABLO / DATAFRAME ══ */
.stDataFrame {
    border-radius: 10px !important;
    overflow: hidden !important;
    border: 1px solid #E0E8F0 !important;
    box-shadow: 0 1px 3px rgba(10,22,40,.05) !important;
}
[data-testid="stDataFrameResizable"] th {
    background: var(--navy-mid) !important;
    color: var(--white) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: .06em !important;
    text-transform: uppercase !important;
}
[data-testid="stDataFrameResizable"] tbody tr:hover { background: rgba(10,22,40,.03) !important; }

/* ══ RADIO ══ */
div[data-testid="stRadio"] label {
    font-size: 13px !important;
    color: var(--navy-mid) !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
}

/* ══ ALERTS ══ */
.stSuccess { background: rgba(34,197,94,.06) !important; border-left: 3px solid var(--success) !important; border-radius: 8px !important; }
.stError   { background: rgba(239,68,68,.06) !important; border-left: 3px solid var(--danger) !important;  border-radius: 8px !important; }
.stWarning { background: rgba(245,158,11,.06) !important; border-left: 3px solid var(--warn) !important;   border-radius: 8px !important; }
.stInfo    { background: rgba(59,130,246,.06) !important; border-left: 3px solid #3b82f6 !important;        border-radius: 8px !important; }

/* ══ EXPANDER ══ */
[data-testid="stExpander"] {
    border: 1px solid #E0E8F0 !important;
    border-radius: 10px !important;
    background: var(--white) !important;
    box-shadow: 0 1px 3px rgba(10,22,40,.04) !important;
}
[data-testid="stExpander"] summary {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    color: var(--navy-mid) !important;
    letter-spacing: .06em !important;
}

/* ══ SELECT / INPUT ══ */
[data-testid="stSelectbox"] > div > div,
[data-testid="stTextInput"] > div > div > input,
[data-testid="stNumberInput"] > div > div > input {
    border: 1px solid #D8E2EE !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    color: var(--navy-mid) !important;
    background: var(--white) !important;
    transition: border-color .2s, box-shadow .2s !important;
}
[data-testid="stSelectbox"] > div > div:focus-within,
[data-testid="stTextInput"] > div > div:focus-within,
[data-testid="stNumberInput"] > div > div:focus-within {
    border-color: var(--orange) !important;
    box-shadow: 0 0 0 3px rgba(232,92,26,.1) !important;
}


/* ══ ÖZEL UYARI STİLİ: ALT GRUP ADI / KODU ══ */
@keyframes dangerPulse {
    0% {
        border-color: rgba(239,68,68,.45);
        box-shadow: 0 0 0 1px rgba(239,68,68,.14) inset, 0 0 0 0 rgba(239,68,68,0);
    }
    50% {
        border-color: rgba(239,68,68,.98);
        box-shadow: 0 0 0 1px rgba(239,68,68,.28) inset, 0 0 0 3px rgba(239,68,68,.10), 0 0 14px rgba(239,68,68,.22);
    }
    100% {
        border-color: rgba(239,68,68,.45);
        box-shadow: 0 0 0 1px rgba(239,68,68,.14) inset, 0 0 0 0 rgba(239,68,68,0);
    }
}

input[aria-label="Alt grup adı / kodu"] {
    border: 1.6px solid rgba(239,68,68,.88) !important;
    animation: dangerPulse 1.15s ease-in-out infinite !important;
}

input[aria-label="Alt grup adı / kodu"]:focus {
    border: 1.8px solid rgba(239,68,68,1) !important;
    box-shadow: 0 0 0 3px rgba(239,68,68,.14), 0 0 18px rgba(239,68,68,.20) !important;
}

/* ══ SELECTBox MOBİL KLAVYE ENGELLEMESİ ══
   Streamlit selectbox mobilde input gibi davranıp klavyeyi açar.
   Tüm selectbox input'larına inputmode=none ve readonly set ederiz. */

/* ══ RESPONSIVE ══ */
section[data-testid="stSidebar"][aria-expanded="false"] {
    min-width: 0 !important; width: 0 !important;
    overflow: hidden !important; border-right: none !important;
}
.main .block-container,
div[data-testid="stMainBlockContainer"],
div.block-container {
    max-width: 100% !important; width: 100% !important;
    padding-top: .65rem !important;
    padding-left: 2rem !important; padding-right: 2rem !important;
    padding-bottom: 1.25rem !important;
    transition: padding .3s ease !important;
}
div[data-testid="stAppViewContainer"] { display: flex !important; flex-direction: row !important; align-items: flex-start !important; }
div[data-testid="stAppViewContainer"] > section[data-testid="stMain"],
div[data-testid="stAppViewContainer"] > div.main { flex: 1 1 0% !important; min-width: 0 !important; overflow: hidden !important; }

@media (max-width: 900px) {
    .main .block-container, div[data-testid="stMainBlockContainer"] {
        padding-top: .5rem !important;
        padding-left: .6rem !important; padding-right: .6rem !important;
    }
    .kpi { padding: 10px 12px !important; }
    .kpi .val { font-size: 18px !important; }
    section[data-testid="stSidebar"] { min-width: 260px !important; }

    /* Butonlar: tablette font küçült, taşmayı engelle */
    .stButton > button {
        font-size: 10px !important;
        padding: 10px 8px !important;
        letter-spacing: .01em !important;
        white-space: normal !important;
        word-break: break-word !important;
        hyphens: auto !important;
        min-height: 44px !important;
        line-height: 1.2 !important;
    }
    div[data-testid="stFormSubmitButton"] > button,
    .stFormSubmitButton > button {
        font-size: 10px !important;
        padding: 9px 7px !important;
        white-space: normal !important;
        word-break: break-word !important;
    }
    .run-btn > .stButton > button {
        font-size: 11px !important;
        padding: 11px 10px !important;
        letter-spacing: .06em !important;
    }

    /* Senaryo Analizi tab4: iki sütun (form + harita) mobilde alt alta gelsin */
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
        min-width: 100% !important;
        width: 100% !important;
        flex: 0 0 100% !important;
    }

    /* KPI kartları mobilde sarılsın */
    div[style*="display:flex"][style*="gap:10px"] {
        flex-wrap: wrap !important;
    }
    .kpi { min-width: 130px !important; flex: 1 1 130px !important; }
}

/* ══ MOBİL UYUMLULUK — TABLET / TELEFON ══ */
@media (max-width: 900px) {
    html, body, [data-testid="stAppViewContainer"] {
        overflow-x: hidden !important;
    }

    .main .block-container,
    div[data-testid="stMainBlockContainer"],
    div.block-container {
        padding-top: .45rem !important;
        padding-left: .65rem !important;
        padding-right: .65rem !important;
        max-width: 100% !important;
    }

    section[data-testid="stSidebar"] {
        min-width: 270px !important;
        max-width: 82vw !important;
    }

    /* Üst başlık kartı mobilde alt alta gelsin */
    .app-header {
        flex-direction: column !important;
        align-items: flex-start !important;
        gap: 14px !important;
        padding: 16px 16px !important;
        margin-top: -4px !important;
        border-radius: 14px !important;
    }

    .app-header-left {
        gap: 12px !important;
        width: 100% !important;
    }

    .app-logo-wrap {
        width: 46px !important;
        height: 46px !important;
        min-width: 46px !important;
        border-radius: 11px !important;
    }

    .app-logo-wrap img {
        height: 34px !important;
    }

    .app-title {
        font-size: 18px !important;
        line-height: 1.18 !important;
        letter-spacing: .01em !important;
    }

    .app-subtitle {
        font-size: 10px !important;
        line-height: 1.55 !important;
        flex-wrap: wrap !important;
        gap: 5px !important;
        margin-top: 6px !important;
    }

    .app-status {
        width: 100% !important;
        text-align: left !important;
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        gap: 10px !important;
    }

    .app-status-label {
        margin-bottom: 0 !important;
        font-size: 7.5px !important;
    }

    /* KPI kartları ve formlar mobilde taşmasın */
    .kpi {
        padding: 12px 12px !important;
        border-radius: 12px !important;
    }

    .kpi .val {
        font-size: 20px !important;
    }

    [data-testid="stMetric"] {
        width: 100% !important;
    }

    /* Plotly haritalar mobilde yatay kaydırılabilir alanda kalsın */
    [data-testid="stPlotlyChart"] {
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch !important;
    }

    [data-testid="stPlotlyChart"] > div {
        min-width: 720px !important;
    }

    /* Butonlar mobilde okunaklı ve tam genişlik */
    .stButton > button,
    [data-testid="stForm"] [data-testid="stFormSubmitButton"] > button,
    .stFormSubmitButton > button,
    div[data-testid="stFormSubmitButton"] > button {
        width: 100% !important;
        min-height: 48px !important;
        font-size: 11px !important;
        padding: 10px 10px !important;
        white-space: normal !important;
        line-height: 1.25 !important;
    }

    .stButton > button p,
    .stButton > button span,
    [data-testid="stFormSubmitButton"] > button p,
    [data-testid="stFormSubmitButton"] > button span {
        white-space: normal !important;
        line-height: 1.25 !important;
    }

    /* Select/input genişlikleri */
    [data-testid="stSelectbox"],
    [data-testid="stTextInput"],
    [data-testid="stNumberInput"] {
        width: 100% !important;
    }

    /* Tab menüsü sıkışmasın, yatay kaydırılabilsin */
    div[data-baseweb="tab-list"] {
        gap: 4px !important;
        overflow-x: auto !important;
        white-space: nowrap !important;
        -webkit-overflow-scrolling: touch !important;
    }

    div[data-baseweb="tab"] {
        padding-left: 8px !important;
        padding-right: 8px !important;
        font-size: 10px !important;
        flex: 0 0 auto !important;
    }
}

@media (max-width: 520px) {
    .app-header {
        padding: 14px 14px !important;
    }

    .app-title {
        font-size: 16px !important;
    }

    .app-subtitle span {
        width: 3px !important;
        height: 3px !important;
    }

    .app-status {
        flex-direction: column !important;
        align-items: flex-start !important;
    }

    [data-testid="stPlotlyChart"] > div {
        min-width: 680px !important;
    }
}

</style>
"""
, unsafe_allow_html=True)

# ── SABITLER ─────────────────────────────────────────────────────────────────
ALAN_RENK  = {"A":"#06b6d4","B":"#a855f7","C":"#22c55e","D":"#eab308"}
ALAN_RGBA  = {"A":"rgba(6,182,212,.08)","B":"rgba(168,85,247,.08)","C":"rgba(34,197,94,.08)","D":"rgba(234,179,8,.08)"}
KAT_RENK   = ["#ef4444","#f97316","#eab308","#22c55e","#06b6d4","#3b82f6","#8b5cf6",
               "#ec4899","#14b8a6","#f59e0b","#84cc16","#6366f1","#e11d48","#0891b2",
               "#d946ef","#0ea5e9","#a3e635"]

# Plotly grafiklerinin tarayıcıda daha hızlı yüklenmesi için ortak ayar.
# staticPlot=True hover/zoom gibi etkileşimleri kapatır; depo haritası çok sayıda shape içerdiği için ilk açılışı belirgin hızlandırır.
FAST_PLOTLY_CONFIG = {
    "displayModeBar": False,
    "displaylogo": False,
    "scrollZoom": False,
    "staticPlot": True,
    "responsive": True,
}

# Harita indirme butonu olan config
HARITA_DOWNLOAD_CONFIG = {
    "displayModeBar": True,
    "displaylogo": False,
    "scrollZoom": False,
    "modeBarButtonsToRemove": [
        "zoom2d", "pan2d", "select2d", "lasso2d",
        "zoomIn2d", "zoomOut2d", "autoScale2d",
        "resetScale2d", "hoverClosestCartesian",
        "hoverCompareCartesian", "toggleSpikelines"
    ],
    "toImageButtonOptions": {
        "format": "png",
        "filename": "depo_haritasi",
        "height": 900,
        "width": 1400,
        "scale": 2
    },
    "responsive": True,
}

W, H = 46, 170   # Tablet için bloklar büyütüldü
BLOK_LAYOUT = {
    # Alan B (sol üst)
    8: {"x":20, "y":30, "w":W,"h":H,"alan":"B"},
    9: {"x":76, "y":30, "w":W,"h":H,"alan":"B"},
    # Alan A (sol alt)
    4: {"x":20, "y":316,"w":W,"h":H,"alan":"A"},
    5: {"x":76, "y":316,"w":W,"h":H,"alan":"A"},
    6: {"x":132,"y":316,"w":W,"h":H,"alan":"A"},
    7: {"x":206,"y":316,"w":W,"h":H,"alan":"A"},
    1: {"x":20, "y":500,"w":W,"h":H,"alan":"A"},
    2: {"x":76, "y":500,"w":W,"h":H,"alan":"A"},
    3: {"x":132,"y":500,"w":W,"h":H,"alan":"A"},
    # Alan C (üst orta-sağ)
    15:{"x":295,"y":30, "w":W,"h":H,"alan":"C"},
    16:{"x":351,"y":30, "w":W,"h":H,"alan":"C"},
    17:{"x":407,"y":30, "w":W,"h":H,"alan":"C"},
    18:{"x":463,"y":30, "w":W,"h":H,"alan":"C"},
    19:{"x":519,"y":30, "w":W,"h":H,"alan":"C"},
    20:{"x":575,"y":30, "w":W,"h":H,"alan":"C"},
    21:{"x":631,"y":30, "w":W,"h":H,"alan":"C"},
    10:{"x":295,"y":214,"w":W,"h":H,"alan":"C"},
    11:{"x":351,"y":214,"w":W,"h":H,"alan":"C"},
    12:{"x":407,"y":214,"w":W,"h":H,"alan":"C"},
    13:{"x":463,"y":214,"w":W,"h":H,"alan":"C"},
    14:{"x":519,"y":214,"w":W,"h":H,"alan":"C"},
    22:{"x":690,"y":70, "w":W,"h":H,"alan":"C"},
    23:{"x":746,"y":70, "w":W,"h":H,"alan":"C"},
    24:{"x":802,"y":70, "w":W,"h":H,"alan":"C"},
    25:{"x":858,"y":70, "w":W,"h":H,"alan":"C"},
    # Alan D (sağ alt)
    26:{"x":910,"y":488,"w":74,"h":40,"alan":"D"},
    29:{"x":994,"y":488,"w":74,"h":40,"alan":"D"},
    27:{"x":910,"y":538,"w":74,"h":40,"alan":"D"},
    30:{"x":994,"y":538,"w":74,"h":40,"alan":"D"},
    28:{"x":910,"y":588,"w":74,"h":40,"alan":"D"},
    31:{"x":994,"y":588,"w":74,"h":40,"alan":"D"},
}
ALAN_BOUNDS = {
    "B":(10,136,15,215),
    "A":(10,268,300,690),
    "C":(282,920,15,400),
    "D":(896,1082,472,645),
}
C_SHIFT_X = 0  # C shift artık layout içinde dahil edildi

# ── BACKEND ───────────────────────────────────────────────────────────────────
_dosya_adi = os.path.join(os.path.dirname(__file__), "..", "kit_atama_model (1).py")
_spec = importlib.util.spec_from_file_location("kit_atama_model", _dosya_adi)
_mod  = importlib.util.module_from_spec(_spec)
sys.modules["kit_atama_model"] = _mod
_spec.loader.exec_module(_mod)

def model_calistir(dosya_bytes, b_max, max_kor, t_limit, mip_gap):
    return _mod.model_calistir(dosya_bytes, b_max=b_max, max_kor=max_kor,
                               t_limit=t_limit, mip_gap=mip_gap/100.0)

# ── YARDIMCI: Harita figürü ───────────────────────────────────────────────────
@st.cache_data(show_spinner=False, max_entries=8, hash_funcs={dict: lambda d: str(sorted(str(d)[:200])), list: lambda l: str(l[:50]), tuple: lambda t: str(t)})
def harita_ciz(sonuc_kat, blok_ozet, I, K, kat_renk, key_suffix="", show_legend=False, vurgula_bloklar=()):
    # Not: Model çıktısı, blok koordinatları ve atama mantığı değiştirilmedi.
    # Bu fonksiyonda yalnızca Plotly görsel stili profesyonelleştirildi.
    blok_katlar = {}
    for i in I:
        for k in sonuc_kat[i]["bloklar"]:
            blok_katlar.setdefault(k, [])
            if sonuc_kat[i]["birincil"] == k:
                blok_katlar[k].insert(0, i)
            else:
                blok_katlar[k].append(i)

    def hex_to_rgba(hex_color, alpha=1.0):
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f"rgba({r},{g},{b},{alpha})"

    fig = go.Figure()

    # ── Arka plan ────────────────────────────────────────────────────────────
    fig.add_shape(
        type="rect", x0=-10, y0=0, x1=920, y1=760,
        fillcolor="#526B7E", line=dict(color="#526B7E", width=0), layer="below"
    )
    # Grid kaldırıldı — her biri ayrı SVG path oluşturuyor, tablet GPU'sunu zorluyor

    # ── Alt referans çizim: doğrudan görsel değil, Plotly shape/line ile çizilmiş fabrika planı ──
    # Amaç: gerçek hat mantığını gösteren sade CAD hissi vermek; model ve veri akışı değişmez.
    # Bu versiyonda kullanıcı talebine göre ALAN A aşağı, montaj hattı referans paneli yukarı alınmıştır.
    plan_x0, plan_x1 = 300, 880
    plan_y0, plan_y1 = 425, 660

    # Plan paneli
    fig.add_shape(type="rect", x0=plan_x0, y0=plan_y0, x1=plan_x1, y1=plan_y1,
                  fillcolor="rgba(15,23,42,0.18)",
                  line=dict(color="rgba(226,232,240,0.42)", width=1.1), layer="below")
    fig.add_annotation(x=plan_x0+10, y=plan_y0+14, text="<b>REFERANS HAT PLANI</b>",
                       font=dict(color="rgba(255,255,255,0.99)", size=11, family="JetBrains Mono"),
                       showarrow=False, xanchor="left", yanchor="middle")

    # İki ana montaj hattı
    line_specs = [(plan_y0+82, "UTILITY HAREKETLİ HAT"), (plan_y0+145, "ŞANZIMAN MONTAJ HATTI")]
    for yy, label in line_specs:
        fig.add_shape(type="rect", x0=plan_x0+40, y0=yy-16, x1=plan_x1-40, y1=yy+16,
                      fillcolor="rgba(15,23,42,0.14)",
                      line=dict(color="rgba(147,197,253,0.46)", width=1.0), layer="below")
        fig.add_shape(type="line", x0=plan_x0+52, y0=yy, x1=plan_x1-52, y1=yy,
                      line=dict(color="rgba(147,197,253,0.40)", width=1.0, dash="dot"), layer="below")
        fig.add_annotation(x=(plan_x0+plan_x1)/2, y=yy, text=label,
                           font=dict(color="rgba(255,255,255,0.98)", size=12, family="Barlow"),
                           showarrow=False)
        # İstasyon modülleri kaldırıldı — her biri ayrı shape, tablet performansını düşürüyordu

    # Sol/sağ load-unload kutuları
    for x, txt in [(plan_x0+18, "UNLOAD"), (plan_x1-55, "LOAD")]:
        for yy in [plan_y0+82, plan_y0+145]:
            fig.add_shape(type="rect", x0=x, y0=yy-14, x1=x+38, y1=yy+14,
                          fillcolor="rgba(239,68,68,0.16)",
                          line=dict(color="rgba(248,113,113,0.70)", width=0.9), layer="below")
            fig.add_annotation(x=x+19, y=yy, text=txt,
                               font=dict(color="rgba(255,255,255,0.96)", size=7.4, family="JetBrains Mono"),
                               showarrow=False)

    # Üst fonksiyon alanları: utility hattının üstünde, alt kutularla aynı mantıkta okunur referanslar
    upper_cells = [
        (plan_x0+18,  plan_y0+28, 78, 30, "UTILITY\nLİFT ALANI"),
        (plan_x0+116, plan_y0+28, 86, 30, "UTILITY\nŞANZIMAN"),
        (plan_x0+222, plan_y0+28, 50, 30, "SPS"),
        (plan_x0+328, plan_y0+28, 112, 30, "UTILITY\nTRANSMİSYON"),
    ]
    for x, y, w, h, label in upper_cells:
        fig.add_shape(type="rect", x0=x, y0=y, x1=x+w, y1=y+h,
                      fillcolor="rgba(15,23,42,0.14)",
                      line=dict(color="rgba(147,197,253,0.40)", width=0.8), layer="below")
        fig.add_annotation(x=x+w/2, y=y+h/2, text=label,
                           font=dict(color="rgba(255,255,255,0.96)", size=8.6, family="Barlow"),
                           showarrow=False)

    # Küçük parça referansları: utility hattının üstünde yardımcı kutular olarak kalır
    small_upper_cells = [
        # Utility hareketli hat yazısının üstüne binmemesi için kutular biraz yukarı taşındı.
        (plan_x0+108, plan_y0+52, 44, 13, "VİTES\nKAPAĞI"),
        (plan_x0+170, plan_y0+52, 46, 13, "KUYRUK\nKAPAĞI"),
    ]
    for x, y, w, h, label in small_upper_cells:
        fig.add_shape(type="rect", x0=x, y0=y, x1=x+w, y1=y+h,
                      fillcolor="rgba(15,23,42,0.10)",
                      line=dict(color="rgba(147,197,253,0.32)", width=0.65), layer="below")
        fig.add_annotation(x=x+w/2, y=y+h/2, text=label,
                           font=dict(color="rgba(255,255,255,0.95)", size=6.3, family="JetBrains Mono"),
                           showarrow=False)

    # Alt depo/utility grupları
    lower_cells = [
        (plan_x0+18, plan_y1-50, 72, 34, "HAT SONU\nMUAYENE"),
        (plan_x0+115, plan_y1-50, 74, 34, "REDÜKTÖR"),
        (plan_x0+215, plan_y1-50, 82, 34, "DİFERANSİYEL"),
        (plan_x0+325, plan_y1-50, 68, 34, "ŞANZIMAN"),
        (plan_x0+420, plan_y1-50, 52, 34, "TRANS."),
    ]
    for x, y, w, h, label in lower_cells:
        fig.add_shape(type="rect", x0=x, y0=y, x1=x+w, y1=y+h,
                      fillcolor="rgba(15,23,42,0.14)",
                      line=dict(color="rgba(147,197,253,0.40)", width=0.8), layer="below")
        fig.add_annotation(x=x+w/2, y=y+h/2, text=label,
                           font=dict(color="rgba(255,255,255,0.96)", size=8.6, family="Barlow"),
                           showarrow=False)

    # Hat bağlantı/akış vurguları: çizim gibi kalsın diye ince teknik renkler
    fig.add_shape(type="line", x0=plan_x0+55, y0=plan_y0+82, x1=plan_x1-55, y1=plan_y0+82,
                  line=dict(color="rgba(236,72,153,0.70)", width=1.15), layer="below")
    fig.add_shape(type="line", x0=plan_x0+55, y0=plan_y0+145, x1=plan_x1-55, y1=plan_y0+145,
                  line=dict(color="rgba(34,211,238,0.55)", width=1.0), layer="below")
    for sx in [plan_x0+75, plan_x0+185, plan_x0+310, plan_x1-80]:
        fig.add_shape(type="circle", x0=sx-3, y0=plan_y0+79, x1=sx+3, y1=plan_y0+85,
                      fillcolor="rgba(236,72,153,0.50)",
                      line=dict(color="rgba(244,114,182,0.80)", width=0.6), layer="below")

    # 22-25 bloklarının altında ve ALAN C'nin içinde AutoCAD tarzında çizilmiş redüktör alt grup şeması
    # Tamamen çizgisel üretildi; görsel yapıştırma hissini azaltmak için dolgu kullanılmadı.
    rs_x0, rs_y0 = 562 + C_SHIFT_X, 214
    rs_w, rs_h = 146, 114
    cad_main = "rgba(37,99,235,0.96)"
    cad_dim = "rgba(147,197,253,0.48)"

    # Ayrı çerçeve/panel: alt grup referansını ana alandan ayırır ama AutoCAD çizim hissini korur.
    outer_pad = 10
    fig.add_shape(type="rect",
                  x0=rs_x0-outer_pad, y0=rs_y0-outer_pad,
                  x1=rs_x0+rs_w+outer_pad, y1=rs_y0+rs_h+outer_pad,
                  fillcolor="rgba(15,23,42,0.20)",
                  line=dict(color="rgba(147,197,253,0.42)", width=1.0), layer="below")

    # dış kılavuz çerçeve ve eksenler
    fig.add_shape(type="rect", x0=rs_x0, y0=rs_y0, x1=rs_x0+rs_w, y1=rs_y0+rs_h,
                  fillcolor="rgba(0,0,0,0)", line=dict(color="rgba(147,197,253,0.28)", width=0.85), layer="below")
    fig.add_shape(type="line", x0=rs_x0+73, y0=rs_y0+8, x1=rs_x0+73, y1=rs_y0+82,
                  line=dict(color=cad_dim, width=0.8, dash="dot"), layer="below")
    fig.add_shape(type="line", x0=rs_x0+16, y0=rs_y0+46, x1=rs_x0+128, y1=rs_y0+46,
                  line=dict(color=cad_dim, width=0.7, dash="dot"), layer="below")

    # üst ana kiriş
    fig.add_shape(type="rect", x0=rs_x0+36, y0=rs_y0+18, x1=rs_x0+104, y1=rs_y0+25,
                  fillcolor="rgba(0,0,0,0)", line=dict(color=cad_main, width=1.15), layer="below")

    # ana gövde/housing
    fig.add_shape(type="rect", x0=rs_x0+61, y0=rs_y0+31, x1=rs_x0+93, y1=rs_y0+61,
                  fillcolor="rgba(0,0,0,0)", line=dict(color=cad_main, width=1.0), layer="below")
    fig.add_shape(type="line", x0=rs_x0+61, y0=rs_y0+46, x1=rs_x0+93, y1=rs_y0+46,
                  line=dict(color=cad_main, width=0.85), layer="below")
    fig.add_shape(type="line", x0=rs_x0+77, y0=rs_y0+31, x1=rs_x0+77, y1=rs_y0+61,
                  line=dict(color=cad_dim, width=0.7), layer="below")

    # sol redüktör/motor tarafı
    fig.add_shape(type="rect", x0=rs_x0+30, y0=rs_y0+37, x1=rs_x0+44, y1=rs_y0+55,
                  fillcolor="rgba(0,0,0,0)", line=dict(color=cad_main, width=1.0), layer="below")
    fig.add_shape(type="line", x0=rs_x0+44, y0=rs_y0+46, x1=rs_x0+61, y1=rs_y0+46,
                  line=dict(color=cad_main, width=1.0), layer="below")
    for dx, dy in [(0,0), (-7,-6), (-7,6), (-14,0), (-14,-12)]:
        fig.add_shape(type="circle", x0=rs_x0+23+dx-1.8, y0=rs_y0+46+dy-1.8, x1=rs_x0+23+dx+1.8, y1=rs_y0+46+dy+1.8,
                      fillcolor="rgba(0,0,0,0)", line=dict(color=cad_main, width=0.85), layer="below")

    # sağ mil ve yarım kapak/yay
    fig.add_shape(type="line", x0=rs_x0+93, y0=rs_y0+46, x1=rs_x0+114, y1=rs_y0+46,
                  line=dict(color=cad_main, width=1.0), layer="below")
    fig.add_shape(type="path", path=f'M {rs_x0+114},{rs_y0+31} Q {rs_x0+136},{rs_y0+46} {rs_x0+114},{rs_y0+61}',
                  line=dict(color=cad_main, width=1.0), layer="below")

    # çapraz taşıyıcılar
    fig.add_shape(type="line", x0=rs_x0+40, y0=rs_y0+73, x1=rs_x0+61, y1=rs_y0+31,
                  line=dict(color=cad_dim, width=0.8), layer="below")
    fig.add_shape(type="line", x0=rs_x0+104, y0=rs_y0+73, x1=rs_x0+93, y1=rs_y0+31,
                  line=dict(color=cad_dim, width=0.8), layer="below")

    # alt şase ve kaideler
    fig.add_shape(type="rect", x0=rs_x0+34, y0=rs_y0+73, x1=rs_x0+108, y1=rs_y0+80,
                  fillcolor="rgba(0,0,0,0)", line=dict(color=cad_main, width=1.1), layer="below")
    fig.add_shape(type="rect", x0=rs_x0+37, y0=rs_y0+88, x1=rs_x0+105, y1=rs_y0+95,
                  fillcolor="rgba(0,0,0,0)", line=dict(color=cad_main, width=1.1), layer="below")
    for xx in [rs_x0+42, rs_x0+87]:
        fig.add_shape(type="rect", x0=xx, y0=rs_y0+95, x1=xx+12, y1=rs_y0+102,
                      fillcolor="rgba(0,0,0,0)", line=dict(color=cad_main, width=1.0), layer="below")

    # ölçülendirme / yardımcı AutoCAD çizgileri
    fig.add_shape(type="line", x0=rs_x0+34, y0=rs_y0+106, x1=rs_x0+108, y1=rs_y0+106,
                  line=dict(color=cad_dim, width=0.7), layer="below")
    fig.add_shape(type="line", x0=rs_x0+34, y0=rs_y0+102, x1=rs_x0+34, y1=rs_y0+110,
                  line=dict(color=cad_dim, width=0.7), layer="below")
    fig.add_shape(type="line", x0=rs_x0+108, y0=rs_y0+102, x1=rs_x0+108, y1=rs_y0+110,
                  line=dict(color=cad_dim, width=0.7), layer="below")
    fig.add_annotation(x=rs_x0+73, y=rs_y0+108, text="REDUCTION HOUSING SUBGROUP",
                       font=dict(color="rgba(255,255,255,0.96)", size=7.8, family="JetBrains Mono"),
                       showarrow=False)

    # ── Alan sınırları ───────────────────────────────────────────────────────
    for alan, (x0, x1, y0, y1) in ALAN_BOUNDS.items():
        r = ALAN_RENK[alan]
        # Zone shadow kaldırıldı — tablet performansı için
        fig.add_shape(type="rect", x0=x0, y0=y0, x1=x1, y1=y1,
                      fillcolor=hex_to_rgba(r, 0.075),
                      line=dict(color=hex_to_rgba(r, 0.82), width=1.8, dash="dot"),
                      layer="below")
        fig.add_annotation(
            x=(x0+x1)/2, y=y1+12, text=f"<b>Alan {alan}</b>",
            font=dict(color=r, size=15, family="JetBrains Mono, Barlow"),
            showarrow=False, bgcolor="rgba(75,85,99,0.84)", bordercolor=hex_to_rgba(r, 0.40),
            borderwidth=1, borderpad=4
        )

    # ── Bloklar ─────────────────────────────────────────────────────────────
    for blok_no, lo in BLOK_LAYOUT.items():
        bx, by, bw, bh = lo["x"], lo["y"], lo["w"], lo["h"]
        ozet = blok_ozet.get(blok_no, {})
        kap  = ozet.get("kapasite", 1)
        tip  = ozet.get("tip", "Mevcut")
        dash = "dash" if tip == "Aday" else "solid"
        katlar = blok_katlar.get(blok_no, [])

        # Ortak gölge kaldırıldı — 31 blok × 1 shape = 31 shape tasarrufu

        if not katlar:
            # Boş blok: gri dolgu yerine daha profesyonel, teknik/CAD hissi veren saydam iskelet görünümü.
            fig.add_shape(type="rect", x0=bx, y0=by, x1=bx+bw, y1=by+bh,
                          fillcolor="rgba(10,25,40,0.10)",
                          line=dict(color="rgba(173,216,230,0.72)", width=1.1, dash=dash), layer="above")
            inset = 2.0
            fig.add_shape(type="line", x0=bx+inset, y0=by+inset, x1=bx+bw-inset, y1=by+bh-inset,
                          line=dict(color="rgba(0,240,255,0.66)", width=1.0, dash="solid"), layer="above")
            fig.add_shape(type="line", x0=bx+bw-inset, y0=by+inset, x1=bx+inset, y1=by+bh-inset,
                          line=dict(color="rgba(0,240,255,0.66)", width=1.0, dash="solid"), layer="above")
            if bw >= 30 and bh >= 70:
                fig.add_shape(type="line", x0=bx+bw*0.42, y0=by+bh*0.50, x1=bx+bw*0.58, y1=by+bh*0.50,
                              line=dict(color="rgba(120,235,255,0.58)", width=0.95), layer="above")
            fig.add_annotation(x=bx+bw/2, y=by+bh/2, text=f"<b>{blok_no}</b>",
                               font=dict(color="rgba(240,248,255,0.98)", size=16, family="JetBrains Mono"),
                               showarrow=False)
        elif len(katlar) == 1:
            i0 = katlar[0]
            fill = kat_renk[i0]
            kodlar = "+".join(sonuc_kat[i0]["kodlar"])
            yuklu  = sonuc_kat[i0]["u"].get(blok_no, 0)
            dol    = yuklu / kap * 100 if kap > 0 else 0

            # Ana blok
            fig.add_shape(type="rect", x0=bx, y0=by, x1=bx+bw, y1=by+bh,
                          fillcolor=fill,
                          line=dict(color="rgba(255,255,255,0.74)", width=1.15, dash=dash), layer="above")
            # Doluluk strip ve highlight kaldırıldı — blok başına 2 shape azaltıldı

            if bh >= 60:
                fig.add_annotation(x=bx+bw/2, y=by+bh/2-20, text=f"<b>{blok_no}</b>",
                                   font=dict(color="rgba(255,255,255,0.99)", size=19, family="JetBrains Mono"), showarrow=False)
                fig.add_annotation(x=bx+bw/2, y=by+bh/2+4, text=kodlar[:8],
                                   font=dict(color="rgba(255,255,255,0.99)", size=13, family="JetBrains Mono"), showarrow=False)
                fig.add_annotation(x=bx+bw/2, y=by+bh/2+22, text=f"<b>{dol:.0f}%</b>",
                                   font=dict(color="rgba(255,255,255,0.98)", size=13, family="JetBrains Mono"), showarrow=False)
            else:
                kod_kisa = kodlar[:6]
                fig.add_annotation(x=bx+bw/2, y=by+bh/2-6, text=f"<b>{blok_no} {kod_kisa}</b>",
                                   font=dict(color="rgba(255,255,255,0.99)", size=10.4, family="JetBrains Mono"), showarrow=False)
                fig.add_annotation(x=bx+bw/2, y=by+bh/2+8, text=f"<b>{dol:.0f}%</b>",
                                   font=dict(color="rgba(255,255,255,0.98)", size=9.3, family="JetBrains Mono"), showarrow=False)
        else:
            # Birden fazla kategori aynı blokta: bölünmüş blok yapısı korunur, sadece daha okunur hale getirildi
            n = len(katlar)
            dw = bw / n
            for idx, i0 in enumerate(katlar):
                dx0 = bx + idx * dw
                dx1 = bx + (idx + 1) * dw
                fill = kat_renk[i0]
                kodlar = "+".join(sonuc_kat[i0]["kodlar"])
                fig.add_shape(type="rect", x0=dx0, y0=by, x1=dx1, y1=by+bh,
                              fillcolor=fill,
                              line=dict(color="rgba(255,255,255,0.82)", width=0.8, dash=dash), layer="above")
                fig.add_annotation(x=(dx0+dx1)/2, y=by+bh/2+6, text=kodlar[:6],
                                   font=dict(color="rgba(255,255,255,0.99)", size=7.2, family="JetBrains Mono"), showarrow=False)
            fig.add_shape(type="rect", x0=bx, y0=by, x1=bx+bw, y1=by+bh,
                          fillcolor="rgba(0,0,0,0)",
                          line=dict(color="rgba(255,255,255,0.72)", width=1.0, dash=dash), layer="above")
            fig.add_annotation(x=bx+bw/2, y=by+8, text=f"<b>{blok_no}</b>",
                               font=dict(color="rgba(255,255,255,0.99)", size=9.6, family="JetBrains Mono"), showarrow=False)

        kull = "<br>".join(f"Kat.{ki}: {uv:.0f}/{kap:.0f} ({uv/kap*100:.0f}%)"
                           for ki, uv in ozet.get("kullananlar", []))
        fig.add_trace(go.Scatter(
            x=[bx+bw/2], y=[by+bh/2], mode="markers",
            marker=dict(size=max(bw, bh)*0.85, opacity=0), showlegend=False,
            hovertemplate=(
                f"<b>Blok {blok_no}</b><br>"
                f"Doluluk: {ozet.get('doluluk',0):.1f}%<br>"
                f"Tip: {tip}<br>{kull}<extra></extra>"
            )
        ))

    # Legend trace'leri yalnızca istenirse görünür olacak şekilde tanımlanır.
    for i in I:
        s = sonuc_kat[i]
        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode="markers",
            marker=dict(size=11, color=kat_renk[i], symbol="square", line=dict(color="white", width=0.8)),
            name=f"Kat.{i} — {'+'.join(s['adlar'])[:28]}", showlegend=show_legend
        ))

    # ── Yeni alt grup vurgusu: parlayan turuncu çerçeve ──────────────────────
    for _vk in vurgula_bloklar:
        if _vk in BLOK_LAYOUT:
            _lo = BLOK_LAYOUT[_vk]
            _bx, _by, _bw, _bh = _lo["x"], _lo["y"], _lo["w"], _lo["h"]
            _pad = 5
            # Dış parlama (glow etkisi için iki katman)
            fig.add_shape(type="rect",
                x0=_bx-_pad*2, y0=_by-_pad*2, x1=_bx+_bw+_pad*2, y1=_by+_bh+_pad*2,
                fillcolor="rgba(232,92,26,0.18)",
                line=dict(color="rgba(232,92,26,0.5)", width=2), layer="above")
            # İç keskin turuncu çerçeve
            fig.add_shape(type="rect",
                x0=_bx-_pad, y0=_by-_pad, x1=_bx+_bw+_pad, y1=_by+_bh+_pad,
                fillcolor="rgba(0,0,0,0)",
                line=dict(color="#FF7A3D", width=3), layer="above")
            # "YENİ" etiketi — bloğun üstünde
            fig.add_annotation(
                x=_bx+_bw/2, y=_by-_pad*2-8,
                text="<b>⬆ YENİ</b>",
                font=dict(color="#FF7A3D", size=11, family="JetBrains Mono"),
                showarrow=False,
                bgcolor="rgba(10,22,40,0.85)",
                bordercolor="#FF7A3D", borderwidth=1, borderpad=3
            )

    x_domain = [0.0, 0.82] if show_legend else [0.0, 1.0]
    right_margin = 180 if show_legend else 6

    fig.update_layout(
        height=720,
        margin=dict(l=6, r=right_margin, t=10, b=6),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#526B7E",
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[-10, 1100], fixedrange=True, domain=x_domain),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False, range=[0, 720], autorange="reversed", fixedrange=True),
        showlegend=show_legend,
        legend=dict(
            title=dict(text="<b>Kit Kategorileri</b>", font=dict(color="#1B2A4A", size=12, family="Barlow")),
            bgcolor="rgba(255,255,255,0.97)",
            bordercolor="#D8E2EE", borderwidth=1,
            font=dict(color="#1B2A4A", size=10.2, family="JetBrains Mono"),
            x=0.835, y=0.985, xanchor="left", yanchor="top",
            itemsizing="constant",
            tracegroupgap=4
        ),
        hoverlabel=dict(
            bgcolor="#111827", bordercolor="rgba(255,255,255,0.18)",
            font=dict(color="rgba(255,255,255,0.99)", size=16, family="JetBrains Mono")
        ),
        font=dict(family="JetBrains Mono", color="#1E293B"),
    )

    fig.update_xaxes(constrain="domain")
    # Görsel okunurluk için harita artık panel alanını doldurur; koordinatlar/model aynı kalır.
    return fig

# ── SAYFA BAŞLIĞI ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div class='app-header' style='
  display:flex;align-items:center;justify-content:space-between;
  background:linear-gradient(135deg,#08111F 0%,#0F1E38 40%,#162542 70%,#0A1628 100%);
  border-radius:16px;padding:22px 32px;margin-top:-8px;margin-bottom:22px;
  box-shadow:0 4px 30px rgba(0,0,0,.35),0 1px 0 rgba(255,255,255,.04) inset;
  border:1px solid rgba(255,255,255,.05);
  border-left:4px solid #E85C1A;
  position:relative;overflow:hidden;'>
  <!-- Arka plan doku efekti -->
  <div style='position:absolute;top:0;right:0;bottom:0;left:0;
    background:repeating-linear-gradient(0deg,transparent,transparent 39px,rgba(255,255,255,.015) 39px,rgba(255,255,255,.015) 40px);
    pointer-events:none'></div>
  <!-- Sol: logo + başlık -->
  <div class='app-header-left' style='display:flex;align-items:center;gap:20px;position:relative'>
    <div class='app-logo-wrap' style='
      width:54px;height:54px;
      background:rgba(255,255,255,.07);
      border:1px solid rgba(255,255,255,.12);
      border-radius:12px;
      display:flex;align-items:center;justify-content:center;
      box-shadow:0 2px 12px rgba(0,0,0,.3)'>
      <img src='data:image/png;base64,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'
           style='height:40px;object-fit:contain;background:transparent;filter:none'>
    </div>
    <div>
      <div class='app-title' style='
        font-family:DM Sans,Inter,sans-serif;
        font-size:22px;font-weight:800;
        color:#FFFFFF;
        letter-spacing:.02em;
        text-shadow:0 2px 12px rgba(0,0,0,.4)'>
        Kit Atama Optimizasyon Sistemi
      </div>
      <div class='app-subtitle' style='
        font-size:11px;color:rgba(143,174,203,.85);
        margin-top:5px;font-family:Inter;
        letter-spacing:.04em;
        display:flex;align-items:center;gap:8px'>
        <span style='display:inline-block;width:4px;height:4px;background:#E85C1A;border-radius:50%'></span>
        TürkTraktör Fabrikası
        <span style='display:inline-block;width:4px;height:4px;background:#E85C1A;border-radius:50%'></span>
        Depo Yerleşim Optimizasyonu
        <span style='display:inline-block;width:4px;height:4px;background:#E85C1A;border-radius:50%'></span>
        Gazi Üniversitesi
      </div>
    </div>
  </div>
  <!-- Sağ: durum badge -->
  <div class='app-status' style='text-align:right;position:relative'>
    <div class='app-status-label' style='
      font-family:JetBrains Mono,monospace;
      font-size:8px;color:rgba(143,174,203,.7);
      letter-spacing:.15em;
      margin-bottom:6px'>Sistem Durumu</div>
    <div style='
      display:inline-flex;align-items:center;gap:7px;
      background:rgba(34,197,94,.08);
      border:1px solid rgba(34,197,94,.25);
      border-radius:24px;padding:6px 14px;
      backdrop-filter:blur(4px)'>
      <div style='
        width:7px;height:7px;
        background:#22c55e;border-radius:50%;
        box-shadow:0 0 8px #22c55e,0 0 16px rgba(34,197,94,.4);
        animation:pulse 2s infinite'></div>
      <span style='
        font-family:JetBrains Mono,monospace;
        font-size:10px;color:#86efac;
        font-weight:700;letter-spacing:.1em'>AKTİF</span>
    </div>
  </div>
</div>
<style>
@keyframes pulse {{
  0%,100% {{ box-shadow:0 0 8px #22c55e,0 0 16px rgba(34,197,94,.4); }}
  50%       {{ box-shadow:0 0 12px #22c55e,0 0 24px rgba(34,197,94,.6); }}
}}
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:14px 4px 8px'>
      <div style='display:flex;align-items:center;gap:12px'>
        <img src='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAASwAAAEsCAYAAAB5fY51AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAALiMAAC4jAXilP3YAAAAZdEVYdFNvZnR3YXJlAEFkb2JlIEltYWdlUmVhZHlxyWU8AADBI0lEQVR4XuydBVwU2xfHfwtKKJJiY3e3YHd3d3d3vr/ts7v12d3dnYDdiVgoCtJICez/nruzwLIzyy4CAu73fXjMDMjuztx77jnnnpBBj54YZC3XP92vNCbZf0GW3cDQMHNkZERWA5mBrVyOjDLIbdivWEIGS3aegX03lcllGeQyubEMMlPFXxBHDnkw+91QuQyB7O8Eswv+gMxXDviwH3vLZHIvdvxdFmnwTW4gc4+UR35N/+vnV/f7G4IUf0GPHjZihO96/iIsqg6yMgw3KRBpgIIyubwAEz4F2EjII5MjL2SyTMKvJQ/k8GTC7h17f67s/bkyofbKQC53iTDBa79ry32F39Lzl6AXWKmZGtPS2IQF5JcjooQcsjJyuawkkwBlZDJZVvbTlP7smZyVf4Vc9kgmw2N29tjAQP7YK63lO1ybES78jp5Uhl5gpSIyVRqe+ZfMsAw7rMxMLwemndizyZyenf8tz1nOpNhP9mkdmdnpyISZY5g84uFP5xXfhZ/rSeHoBVYKhgRUmKGBPTOVajINqj4z7wozk85A+LEegqmXzIx0YYL7fKQcV4wiDB097y76JvxUTwpDL7BSELlqTDPxDwsoC3lEQ8CgGbtUgj1BQ8VP/xxpDA1gxL4UyGBinJYEBULCfrFzdsAIi4hEOPv64zABxv73jB2dYF9n00P2wM1paTD/mZ5kj15gJXPMyo3OaGSEWpGIbMkmWzOZTJZB+FGiYGqUFhZmprCxSIesGS2QydYcmSzN2LkZrK3NkNE8HawypIMl+25mZgIL9ns0iAyYCqPEwIAZZOy7nKk0SiLJ48S++/kFITAwBL7+QfAOCIIXffcJhLdvIL77/oSHpx/cf/jBi/2eH/t58K/EdUex9+TP/neKvf8jv8JDLwfcXe0l/EhPMkQvsJIh6R3GZEoTGd5YZiDrIJPLarGnZCz8KEEwTmOIjFYZkDe7DQrmzoy8OTKigJ0tCuXNiow2GWCU1hCGURrTnyGCaWNhTFh5/gjAmw/f8eajB1zdPPH2gwc+fPOGp3cAQhJamMkRKpfJr7Cj3eGGEWcDb670VPxAT3JBL7CSCTaVx2WQM1OPaSI92EOpm1BCKkM6Y+TKYo3She1QsmB2lGXfC+bLinSmaZkmlDLdXZFMcwsOCcNrF3fcf/UZT998wZPXbnj/1QsBwaHCb/0mJLyAiwYy+VYmPc9731npL/xEzx9EL7D+JOX6p7UyNi0vl8v6sAnS/nfNPUMmgLJYZ0C5orlQsURuVC+XH3lzZWLCyUj4jdRNUHAYXJkmdv2BC5yfvMeDl5/wzcsfETFM0/hAZqNMLj8EmcF/PkYZ7ujDJv4ceoH1B+Amnzy8MxNQg2SQFRQu6wz5jTIx086hVB7UqlAItewLIYutxR8355ILZFZ+/e6LK86vcf3eW9x+/A4ePoHcnxZP5JDLXZlquiZtRPguD324RJKjF1hJRbt2htafc5SLlMlHsLNWcaWySGFilAZlCtqhrkNhNKlRAnlz2iJNmqTfKKQdv0j6YtpLRKRi94++xxYFNMBI8yPoOznkDZhApZ3FpCY8PBKunzxw5voznHd8iYevPyMkLH7KklwuD2HfjhrI5cu8G1rexYwZyWALNPWjF1iJTY0eJlZhNq2AyDHsdpdlV3S+5+bpjFGjXEE0r1kStSsXhpUFxYImPCR8fv0Kh39gCNzcvfGVmVPfPfzw3TsAnkwz+e7hCy+/n/D+GczNr9DQcCa4IhDGJj0JKiknuEnaNPxDGzNha2hoCGPjNDA1MYJNelNktDKDbUZzZGKmbGb6YhpidnaePas1zM1MkJb9WxJyiYGPXxAuM8F14uoTXLn7Jr7+L9r+vA9Z5BIfP8tDeDEjTLiuJxHQC6xEwqrcBAsYhfaTQzaC3eQcwmWtMTM1Rt1KhdG2XhnUqFQI6ZnQSijIVPLzD8Kb99/x6v03uHz2xCsXd7z/7oMfXgEICEkgx/VvkoEJNVsbc+TKbIVC+bKgYM5MfFeTviwt0yeolhYUFMbMxjc4cPY+zju9xM8Q3eUOk1xfZJEGSxAeuMnn/gY/4bKeBEQvsBIY8k8ZySOGsVs7lN1dS+GyVtAErF4mPzo3qYgGVYshffrfF1KkNbl99caj1254/OozHr78xITUd3z3CVAz31IKNGjJd1eICa6yRXOiVKEcKFvEjmtlCaGN/fwZirM3nmHP6bu4/tBF94BXOXwhk6/+ZWSwLPDakh/CVT0JgF5gJRBmVYfZpokwHMcOB8sg08lmy5vNBt2b2aN9o/LIkslCuBo/fv2KwMPnn+D0xBVOj13x4OVnePgGCj9N3WSyMOMCzL5UHlQunQ+li9r9tn/P/bsv9p+9h10n78Dli26yRy6XB7AZts4oMnKx3kGfMOgF1m9ibj/Kmi3qE9jwHKKLoDJiE6lptRLo2dIBVSsUEK7qTmRkJJ6++oJrd9/g2r23cH76HkE8JUZPemMj2JfMg6pl86MGu8clC9vFWwOjjcXb912w9ehtnLzxFKFsYdAWJrjYiiFbFZ4mfIk+GPX30AuseGJbY7DZr5C0I9gMGM9uorlwOU6yZTRn2pQDerZyQCZ2HB98fH9yAXX+9ktcdHyJH/4/hZ/o0YRNhnSoV7kI6jkUQc2KhWBlGb/NC/LzbTlyG9uPO+HLD+1dVUzm+bP/LzKIiFiuD0SNH3qBpStF2xlZWWTvKYdsJrt5mYWrGqGbXKpAdgxoXx1tGpSNl5nyzcMPZ28+x4krj3Hj4TuEC6EEeuJHGgMDVCmdF81qlkLDasWQLbNO7kZOeHgEDp9/iLV7r+GxyxfhqhbI5R5sVEz18Tffot9V1A29wNIemZXDiPpMUC1hpl9R4ZpGKLCzOjNHRnatg2oVCyJGfrBWUB7dqWtPcPjiQzgyU+93I7Y1kS2jBbo0rsB3EDcdc4Rf4N9TwICeU6ViudChUQU0ql4ctja6JRyQuXjjzmss23kZ1+6/1Xozg/3eS1lk5Bgf5+VnhEt64kAvsLTApvKIQhGRBovZuG7MTuO8Z7R612dmx6gedVGueC7hqnYEB4fxyOxdJ5xx4c6rJCnJktbQAHf3TkLO7FSyHTh05j76zdrFj/82aKe2fqUi6NSkAmo7FObxYtpCguvxi0+Yv+kcf3a0Q6sFVMfirKFMPsrr9vLXwjU9EugFlgZsa0wzCw/1m8BUo/HsNM6RSw5dGuxT+jdCsULZhavaQXFQu07d4btRvj+TVruxtUiPl6dmRjmkn77+ghq9FvPjvxkrM1N0blwRnZtWROF8WXXSkJ+8dMPcjWdwkQkuLTXjUKZyLUhjHLrA89qav2NbNx7oBZYocplV5dGN5JFYywZpTuGiJGRSVCmVF9MGN0UZZlpoO7BDQ3/h/M0XWLfvOpyff/idHLff5tzaYahQKg/taGHBhrOYv+2C8BM99Hwrsuc6sH111K9aDCYmaYWfaIYe58PnHzFz7SncePSO39s4kcs/shcc7HN7KZmJf25AJFP0AisWGauNzBoejqUyyNqz0zjvT4l82TCdCaqa9oWYoNLudnp6BWA306TWH7iBb97JY7MonbERGlUrxpOFnZ590G5yMbo2KA8j07Tw8g2Ct3cgfAOD4BccqkjbCY9QpPokVMmXZEBmqwwY0K4aujSrpLWvi+7lNec3mL76BJ68+ypc1QT9C9mBtOGhIzzvrtGXc46BXmApadfO0MrNrj0bK6vZXbESrkqS1cYck/s2REdmLmhbHcH1kyc2MG1qBzP9gpN5rJRx2jSwMk8HU6M0eO/uLVxVp3n1EujHJrB96bwq94Gc9xTE+p595lp9liIsQjpuyaF4bmSytYAXE3hePgEKgRemEHiUsPwzNPltpJkap0WnhuUxpFNN5MlpK1zVDN2Tg2fuY9aG0/iqTTiEXO7DBNdQXyfzvYA+uZrQCywGaVUR4bL17JDqpGuEBmr/1lUwtk8DrfL7SFF54/oNi7acx/HrT/GLTcLkBAnenJmtYJfNGjmzWCN/rkwomicLctll5A7odbuvYs7mc8Jvi0ODqG2dMlg3s1uUOezywQPtR2+Am6dvnBsHJPSGd62N0kVzRvnRSNhRxdEHTz+ixah1/FpyJK2hIVrUKIGRPeqiaIFswlXNUOL4ok3nsP7QTQSHxrlwkap70kCWZqDX7YXaqGepmr9dYMksKo1oxSbJRnZoLVwThcy9WuUKYOHYNlqtqApB5Y4568/grOOLJNntiw8LR7RC09qlYGWRDkZMm1Jy7vozjFl4kFds0Aby89zeMQ4F82bh53cfv0eDQSv5sTbQQJw1uBkGd63Fd9dW7biMrccc8dnDN6p8jRgk7N5+8sAbpslp+r3EhkrnNK5SFBOY1q2t4CLtc/ziw7h87w03AjXCtC2ZzGCAt+Pig+xuaWevp0L+WoFlXXGYudzQcDm7BT3Yqcb7QDFK/45oiWa1S2rlp3r30QNzN5zhGtWfEFQW6U3QpFoJZlb9wqHLj4Sr0pCwKZDDFrf2jGcajsKsm7nyBJbtofLm2jOxdwOM79uAHwcEhqBo8+k6VT04umwgqlcsiNNXnqDblK1aeZwHt62Gf4Y0hbuHH45ffozTN57hydsvCE3oeu9aQoKrRY2SmNivIfLnjruJNgmqU+zzTlx2VBszkd0S+S6EGQ/1uT//r6wG8VcKLBuHMRUi5RF7mPTJJ1wShUyi7k0rYdqQZshgZiJclea7pz8W/HcWO8/cTXLTj3xOlUvkQYfGFdC4RnF8/+GPXlO24RnT8rTl9fEZsM2ocCRvOXQLYxYf4sfaUraQHS5sHhVlFrYbvg6XmPagDcWYGXpt5ziEM1Owcuf5cP2qffOaormz4OiqwchobcbPvXwCccXpNU6xBYPyK/1+Bif5dhvlinZpVIEJ8IbIbBt3ChbVIJu56gS2nXTWRlN0lUWgi/edpU7C+V/DH+9pl6SQY92iwWg55DvZrNJo1+XLnhE75vRE73ZVeeE5TVCw54odl9B32g44P/+obcBggkDa39zhLbF4fDv0alMFxZg58uqdOxoOWMn9R7pQp0Ih5M6RkR9TvuL+8w/4sbZQcb8+rarAVKghHxQUinOOL/lxXEwf1AQlC+XAqatPseW4o3BVO7z9f2JwhxpRPkUqKFisQHaeBjWQXa9VoSAszUz5Z6IYt7isr4SAYq8evXHDNmbWRvyKROkidkibVnq60RijkIlqpfLhztP37DMFCT8RxQpsLTW1sw8JcWvAhNa1pJbHf4y/RmBZVB1klc7Peg87HMa+JCUQqfSDmJmxZU6POH1VNPCPXXyIrhM24yQzRcL+gENdxv6zMk/PJvoTHi5RtlhOeLOJuf7gTZ21ivJFcvF/z2Fq0sYDNxTHWkKTNB8TeKUK2/Fz6l24UYv3YZfJEsundOKVJ/r+bzt+MMGnC0XzZMXQLrWizPXJS49g6Ow9vMwO7TJWKJEbTWuVRL/21dChfnnkZYuRPEKO717++JXIJjuNiRsPXbCPad1ZrM3jDEClzY+uTKsPZsKeSgNpuHds7srqm9qFljXOV+lM6EdnKtmc6vkrTEILh9FlDBDJ7BtZHuGSKDRxVrGJU02Lci+v333DBGYyXX/0Trjy58lokR7Pjk1DmjQGqNhuLlzddesJOpAJ6n9Ht+LH/gHBKNJsus7hF40rF8PORX34MW3jV2z3L95/kw6LIGYLzvaTlx+j+z/bhKvaM6xjTcwY3pwf0+5i8eYz4OkXHSxuaCBD2cI50YhpMPUrF0XRggqnOBXqK916FrwCNGozCUrlknmxcExrFNHCMX/j7lsMnbMXnz18hCsSyOEaKZO19XNc8lC4kmpJ+k4ASYxFpRE9ZfLI23EJK9qWv7FjXJzCikrpzlp9EtV7Lk5WwoogzeTs9Wfccd61WSXhqva4fo4u1UQ+Owst/HaxoSRtCkcgKC6LGmVowpppYT2ZKUua0Nz/zgpXdaNxteLCEfDSxR0//FUzW0jzu/viI2ZuOI1qvRbhs5tCkJNWmpTCirj9xBU1ey/B9JXH+VjSBI3FGzvGol3dMpo1CxnyyhB5y7LyqK7ClVRL6hVYRacZWdmPWsYm72ZmKkjOPGrwsHZyJ2yY1Q3mGTQ3srl06yWqdJ2PpbsuM1Miccy/9CZGPB+RnLbxYd/Ze/x789qluHmrC5+++0T5d8i8KmgX9y5XbHyYALh9z0U4AxpUKSYcidOzuQPvm3j2+lO8/KB7UU5bSzNUKB29Fp2//SIOH5WMt9inoNQFW84L15IWMkNX7LkKh87z+ZjSBI3JdTO6Ye0/ndlYlV5AZJCZyuTYbukwaglqTNPsdE3BpEqBRVVALc39T7CnSC21JBcnSqu5vGk0OjStoLgggbdPIAZP34X24zbi47c41PN4YGqUlju8V05oj5cnZmDv0n64vnUsNx90hZqIkjmXxy4jSubXLh5ICe0sRsQQxEUKZBWOdOMkEz5KyhTLybtPi0HCeVDHGnyTYsm2i8JV3ahZvgAPy1By/Mpj4Uga0kD3nLij9U4kBbNSe/+Ehky9dmxMDZmxm+9sSkEfr33j8riyZTSvq6YB+tVRlmF+p8lnK1xLVaQ6gZWhwuiCBpA7sidXX7ikBmkPPZpWwvn/RiJvLmnHOq3UZ649hUOXBdh7/n6ibI1bm6XD/X2TsfZ/ndG8TmmYCY0nCubNjONrhmDF+PbcN6UtFPd09MJD/hm7NK0oXNUOn8Bg+PlHV4rIk02xY6grl51fc/8VQdpTFQnBS6ktNtZmuHjrBR691aEAXgxianBu7j5xamkk2shUXaRDcneZAjlwbesYHjgsufr9BnvO3UNlNsYoWFcTtAid+28Eerdw0Pg+mLZVTxZh7JSh0vD4195OpqQqgWVlP7JKmjSRTFhJd1OmVX31xA5YOrkD748nhR/TUobP2oOuk7fCMxGbOHgHBqFE21ko0nI6qrBBGzN+i1b2ri3t4bRnIjo1KMedx9pw4IIiHKFx9RI6m5YUEqEkrxDioCtkWlLepBIxPxbFuA3prIhqnxdP3xVpPfWrRNdSvEqCMo4YJqqIUbrVTB5Bry0PXn/GwXMPcHDFQOya25sH2SY0NMY6T9rMxxxpyFIYpU2DRRPaYR0zEdNpqNXFhFbBNAaGjpaVR1YTLqUKUo3AsnYY2ZapFVfYo5JMscmVxRqn1wxFx2aaNQ9KK6nZYzF2nb3LtKzE0KtUIW2EHMMUN3XxxgvhajTWlumxeloXHF8xGIVzxV2V+e7zj/ju6cc78OhqVr6N4XinFT0+kFA4djnaNKtVqbCasG1RsxRy5bD5Le2qUok83B+lhEpIi0F2Ujrj6JIw3jpWU6URsHjnJdx78gENaxTHrT0TsGBkK+Sw1b2ssiZoqFHQcQ029u48chWuitOOmYhn1w7jY1oDNoiUnbeqNLqDcJ7iSRUCy9Jh5Aj2sPexQ8lCRVVL5cOlTaNQorB0T1NyxC7ZdB5Nhq7Gxzi24hOL3WzAEiEhv/D2vap541A2H65tH4spfRpyTVEKiv3Zd0bhfNfVLHzvFi2wMlpl4K3x40NM4UGCM38MrYQEyPAutfhisCCOxGpNUIiCEtpl/MI0OzEttFa5grizdxIM6YXjSZ6s1jw5myDtsG/7arh3YDLPf6SO1QkJjb1mw9ZgyeYLGlO7ihfKjstbRqFaaemEDfaRTSCT77K2HzWSicT434BkQsoOHJ02zcAqtMxMZgLOYU9GVPiSL6dnM3tsnN09yj8khscPf/SctBXbT92Js5Ae7daM7VEXzWqWxHOXrwgIEq/3RJn81MdcF9yZZtS3TVXu++k4ZiM+f/VBuWI5uSlAkP+lMhNcbeuWwdsPHvgg4Tj28vnJO/Nkz2zFgze1TRWyMTdDm/rUUZ+9f2ZybTp8Cz+DdS/v4uMfhF4tK/Ood3oG7t/94PT0Pf9Z3QqFMLRbbVx3foNlu3XLV4zJgtGtozrfkPncvaUDujSuyOPpSIBRAC3drz0L+uLWw3c8uDc+kJxbMq6dSlLz0Om78MMnEN3Ya/ZrWw0G7DFTs9qEyh2lMUgbKE7sfddhGqpUZRAq4dy2fjl4eQXg8Rs34WosZEwxkaGBid2ZdCEOOa/gxQvdBmUyIuUKrBrT0li99lvBRtMYdia6clCt8ukDm+KfwU1UajXFxvHBO7Qcvg7Ptci7oxfaPKMbureqzJt2li6QI0orikmebDZsovTB45efeZdlbSHtKG9WG5QqYodQpmVR7BB1ZqE27bmZCUWTn7AwT4e2DcuhUM7MuMNMlcBYRfK8/AK5UMua2RLPXrrh1UftQgbI59W7TRV+TELg7NVnOvl7lFBXHzJfSQsgqCzPTrYY0LtfPrED7JjGMmTWHrjF428T5Eca30+RaE3MXXsaJ689hVWGdGjEzDYSXlRor3OjCsidMyPmrDuNd27xa8JcoUhOzBzRIureX7z5AlPXncJ5x5c4ePY+yhS2Q9cW9mheoyScHr+Hhw7POy4+ffPBfvYa5dh7oHsmBo3t+lWLIoOpCRNyb6UWXPbuZVVM/MyzhORrcBYfryVuiH8ikTJNwnL901qF+W1hj2CwcEUNMpn+m94NQ7pGp2zEhhy+6/dcQ4sRa7UeZDSJi+aL3u4vEivVgrbY29cti2vbxuLDFy881SH5WMlBwWnelGlwpOWQidB+7Eb0mbKdt/tSQq/Vqn4ZOO2ZwHc9yVRRQj6x3acUgrSTDmahB1upKVpcSZH88QttIE7F0GhKMVOcaqSXZZO7crn8uH7nNRyfKTSu+BDTHCQf4PYTTvjvyC20HbsBRZvPQPfxm3GOCZYc2awR+DMEt+IZ5EuxbHNGtOTPnSC3wbQ1J/gxQRsMrUevx46jjiiQJzPOrB+G2uUl93ziBY3NliPXYc3OK5J5qjTGB3epyRbT7rx6rBTs1/rzuZN/mLS5kYxJcQIrV40eJpZG6XeyWy8Z1UthAIeXDkCzOqWEK+oEh4RhyIxdmLTymE5qPAkCMrFo4NDXjuNOUYGKFMS4iQnJdTO7ck1izOKD8XLaOz/7gB/eAVw7qlQsN79Gq+bRq49h33k+Nh+4ySeOEgoupF3P06uHonjeaAFz9PIjPpmrls8Pa6Z5aIN3QBAvMKckT/b4Od6J24/fcV8cYcw0rBrlCmBUtzr8fOHm3wvabMA0CiUU3e4RIxWHtM2TN5+h34yd8GD30ZlpPbqUuYlJ02rFUb6k4hkQO485qYVO0D0ev/QIXNh1Mt22/NsT+eO5wyoFmfT/MEE5cNpOlecTm6a1S+LI8oFxPG9ZV6uMafZScLVwIcWQokzCXDWmmfiHGexnwqC1cEkN2rk5vmqIRuc61U5qO2I9Lt7V3FWJNBbyibSoXQrvPnlE+aoozePU5SfYevg2Dl5SxDw1q1YC+5f256YcnVNm/pNXbnitpSkWE9qap9rhFUrm4VpUTE2F6jydd3qJy46vULqQHTLH6B5NzUC7NrOHuYkx7jChR1vljSoXQw5mSnxg5hBVD4gLEq+NHIoie1ZF3KEX+xuHLsYvRS0kLBzVy+RHLqF9GFU3rV6pIDPBXbDgN5pcUL2vBWPbMK1Hsd5SfXzqBxgben7DO9fCdiZkHrz6LFzVHtJUds7rxc1vgmp8dZ+8FUEiwo+eGZlk1SsU5JUXcjGzXqkpJyQv3n/DJWaKkoYpVfIoOxsHlDd57uZz+DPtUhQZCpsah5QIMbc7As8X2jk4kwEpRsMizco/zH8/O5QsY0x+nrPrh2ssnPbk5WfU6bMUD7WYvBN71cfyKR14f8G9C/uqRFQ///CNf9EEp7rnHRqWw9z1Z1C160J8YqYgCS2aVKR1xYdDFx5y7Yx8E+T/ic19NgHr9VuO/y07xkyeaP8VCcqh3Wvj9s7xqFexMG8bRrRvWJ5/14Y3TDgriW8slpITV58IR0DFMnnZfTGId1S7ktoVC6l0zz51LTqyPiak3JLWc0HLEjex6d3SIapXI7GUvW9NMXkBwdHCoSoze6Ui/H+Xx2+/oG6fZXj0/JNwRR0yT0+vG6Y5vUoma2llkX0vuViEK8melCGw2A31C7OmNH5JYUVpKCfXDEW2LNKxMWeuPUOTIavxTcuyvzFjmPIxYSiVyxUU+gtdp2zF5uOOeMWEWD+mttMuFXVVWTGxvYqg05anLl+Z4POGFTNvpXwilM+4ev81XvDu/I3nKuYnlSnZs6QfWtctzc/LlciF7Bkt+HFckDamJIutBUyEHcr4cNFJtaEoxbhdFdGGdKFR1ehkZ/LpPZBYfMjx32joanyIR4gKLTTj+kQ79T9/9cb6gzeEM3HKMI1XCe3ypjNNPDcRdVui0IczV8WFNZE9ixVOrhuKUvk1pfPIWlkZpd+bUvIPk7/Aot1Ao3Sb2ZSntluilCmYA8dXD4mqOBkbmi7/7b+B7kyo6OLL2HvufpR/6iabZH5B2gUcksm4UIjerl+tGN+p0hWabLtPKbSjTk00O80p4LTThE3oOXEr3L9H77qRlmdfVhGjQ877tvUU4Qpx8fF7dL4k+WSsdUgNig3lyymj3kmgUlR7tPjSHdr5reNQWDgDrt3Voh56PBjXo56KyTVr7SmNDSPIb9qybhnhTFHUkb4SExrLVI5nExvbUmS0MsPhlYNQsajGDuStrcL8NgHTkr08SN5vkMdZ+VHddUkHOwmrwysGSlZaoNV9zppTmLD8KPcz6ML2U85oPmgVuo7dhC4TN0cJL21YvucqHjz7yIXG7JEt4opIFuXIpUf8/desVIhXzNQEvbUTN57Cvst8bNh7PSqXLybtmNmqDaHB0ROTtsw3z+rOW5o1i6HZaAttUpwUzEKKFL/24Pe0q0rF80TFXhHnbqlnBvwuhZg23bNNZeEMePfBA0euaK6NP6VfI5UGq/fZs/cPSvyaejSmxy87gjlrT0sKbmowcnD5AN5OTRpZd0t7v1VsJOluDiQhydrpTkGhbMZTnJUoSmGldIrGhnbSxs4/gHVxqPKa+My0DUpXoQjqDOlNeL88baCB5PjIFV2aVoIZ+3dlCuXgpV/iCkqNiW9AMJowIUEOcJo0T5iZGBdhvyJw0fkVjxUqVSg7N+mU2LDV9vjFx5IVPQvY2WLmkGaYPLBxlEP7h1cAfgaH8iBYExMj3HjgorOG9Pi1G45eeIQdJ50RqIOGqySLdQZerz5fdlsM6FAd+XIp/DJUCnnkvP1aVXptXas0crB7EVeFBrLeV03uyH1ASmjCk7n37M0X0XvXpWF5TBzQiC9OBC0WvxNjFh8cn7ji23c/1KtSNCoEIybUEallndJweugq+b7Y+69ganc2TYibU/yjeROZZCuwKN2G3cA57FBU4sclrEiw9P/fDuxPgJ0aipzeMbcXbMzT8wJs2kJ1uX18AtGAmYU5slghJCgsKtpbG0gwUCBn3cpFYME0LLEAVSnIx7Hz5B3++hVL5OZhBTShaKdLbEeNoBQPMoN2HnPGsh2XMXXFMSzafhHbjjvh6JXH/N/pKqwI2i387s0EXzyEFUElkMf0rMfjjKjEsBLqUn3F+TU8fTXH0FEV1A2zu2HjgZtx+i+rl86PyYMaRwkfqoJKJZc7MrN8NHsP1PBCzrRGEgpUDnpCr/qY0D9aWBFrdl3hzXKTGnLGv3X9hobVi6vE5CmhbAkSWrfvu+CLp2TTnaomOey9mdBK+g+gBaLC4E9DicxMEdnHRoGoyUoOdvJZSZmB1Pyg1+RtuHDnlXAlftAYbFGjFJZOao8Xb7/y4D1du+FQ4OHe+X1Qp0oRrhHU77tMK01JSTYbczw8/D9+TOV83bXcMIgJ1RKfN7Ilj0u7z8yy+jr0C0xOUN0wqn/VkGmdtZiZnEMIvSC/HUW5n2fmIS0IMQUjaWaH2ML26as37LvO12jWkxZ5edNIFCuocFIHh/yCQ8d5+OThg2wZzXH/4D8aG5LQIrl860UesqGLJp3Q1K1YCNvn94aJyO4y4ccW0tbD10nvlMsRwQRwJ2/HJQeEK8mGZCewqEQMkxSkkorebQpdoN1AKQf7Tyasuk3Y/Ns7UZTiMXd4C7RvonCYtx22Dpfva9eyKjYUf0Tll6nqAtWCr913qTYdfzn0gKhKQ5Xy+TFtxXGs3HtV8YN4QIL+5fvviVYtNSkhjaZ4niy8dA3FJBVnJjfVsqdA1cuOL3nyNRVb3DGvF1/YqIVWXHmLnRqUx+ppnYUzpintvMKDNQlyCdzbOwm5hDCPE8y0/vLDF5bpTRHO7udr8nNdeoSvXrq3CzQ3NWYakSHv6JNQgq5W+YLYNrcnd0eI4e3zE03YwvU6RghLTORyeYhMblDPx3nJTeFSsiBZCSwqvkf1rNjbEvVQU1AoxVlJhS4klLCqV6kwlk1szyPNldy8+xatRq3jTuT4QIGlW+f15BON0oEowl5bOtYvhzXTu+DZazfU6LUkXmZZaoYGsY1FejStURKNmfldqVRelR0+qjFftvVsjV2sKWbq7p5JyCT0EKRMg/Lt50Y5zuk1brJFh1KxiNlrT2HJjkv8OD5QqEvbOmV4i/6C+bLwv0/j9xozcQ9eeIhzji9+uwuTffE82Lekn2SAKZnUjQas1NDkQu4dHpnWPsB54e9NqAQk2fiwqKyxoYH8EpvQoiHqtG1MEexUQ0kMMgMTQlhN7FEf/xvchCex0q5LRqF0CAUQenkFxitimnj72QO5s9igODM3yhbLhet33mjtlP3q4Yf+7arxMi0nLkk7zf9mKBaOqiVQ8cJ1+67xoErKiaRt/ccv3LDxyC3hN8UZ1aUOGlSPrl46fdVJ3lAjJj1bVkYmG8V4eMjGATVpjQ/kJlg9qSN31FOsHvnD6Iv8jIXyZkGremXQqnZpvGHa8Ef3+Jc5ovH16MUnNGd/i8JaYkOCrC5bnA8zASneHUlmKpNFNDDK4bA71M1JtyJiiUTyEFhFpxmZGoceYsJKNOCIEpn3L+onmW5DvoNek7bi0t34mWwxefbuK5bvvIxDlx7ikuMrdG5SMcpvUbVsfpy88gRe/vETGDfuu6BN3TK8X1/JAtmxnfIQhZ9pggZTucI5+c4VRb2//UjCz5rvCGprWv5NUG4o7exSStP6Azd4tL0mbSVnZitsmt09Knr+jet3jFiwXyXglejVKlpgPX/9BRec4ucjHd+jHgZ0qiGcKXB+5Mq1trW7r+KlqzsKM3N3aNdaSG+UFrfYz2K/F235wATe4xef0bxWKZXsACW0c1y5dF4cOP9ANKdWBpmNAVAhxLzBXnhe++O+hGQhsKzylV3MNOQuwqkKFCi4fmoX1IoRLBgTCl0YMHUnTt8SrzapK7SjpTT7fAOD8dXdB01qluCmHKW9VGDa0Z7Td+NlGlIeIBXlo3iozLYWeP72K94w4RMX7KVRtXQ+3j24RKEc6Nu2KheeL1y/wTWeJVP+FsgnJCashnesyWPLSPD3b18NeXMqQiVIqx4xZ6+ob4eKIWYVwkSev/mKs7d1jwGjbIOtc3uplDvaf+ouL8VNiyUFAVPFWAoBiQyPxMiedVEyf3acvvE03rW23n/14uOuCTOZxcosUQ5q4ZyZuWAX9aHJkMfUJMQqxM0pfrWsE5A/LrB430AD2b/sUM2fRkKC6llRXXMxaNWhOKt9iZBkquTl+2/8YRbOl4WfU1yTjI0b6uYbHz64e6FMQTseS0QJznGFKlDd7rnDWqBH68o8PWT7USeMXnAA87ech0uMcsZ6dIPMR0qiHtS5BorE6C505/F7XoNMbDlqzUwrZSI3CYATMboDaUvXJpV4rJQSSr9qM3q9WgdqEhy3HrvC09MPg7rUQtlCdjjOBEp8hdZrtjDS4kshDzSvYlOQae9mbKxdkSwIIKtgmsP+CxNaiTfZtEA0bCCpoI7MTFitYYfqd5BBNZ4o9kYMGlD/rjuNbWwlSkxo4IxdfBDfYsStjOhRN65UB0loAVu0RVGpwL5MPthaaE6OdiiehwesUsR9+Y5zMW3dSV7eJL7Ofz0KSNtdfeA6KnSYi9U7ryBEMK2dyPwS0zJiEd88wcK5VWvyn2Fma2iM+mOx2XbKGduP3EbtykWw/n9duP8rvuw+dw8zV53kWqQYA5mZ2rOpuHLAYNahbJWNw3Dd88wSkD8msKhvGrWPZ3dBNJiKarDPH9dGdDUgKH+KGpomBV7+QRg2e2+UH4G2z9dO66yxrrom7r/+jHdsxSNHq0MpjQ2pceneawyYvRu3n76P9+qqRxq/nyH435oTPN6KSgaRb4myC+IiZhqOLsQWFt5xbKDQrysLMVIc3aTekt3rtGLF3it8l1oMmmv/jmnN3Q8SGEfCcH+GChPFd76SgD8jsNq1MzSIMNnKbpHobKW8u63/9hTd2SCo6sKkFcckV4rE4DJTlbceit5pymNni1lDJItHaITe9+0HigqYOTKn7H6XFJ9E0fjUrII2BMiENUtnzL/omK6ZGKXlvyPWICK5QAnf3f/Zig6jNqBx1WKiKj/tRCvJkEE8VCAuKA4uJjlihM6IQe9jSCeFlUELZhqD3/fikICmCH4xaINpy5wefCNCgtyGhqHb/lSi9B8ZQVYOoyg/cJHiTBUqmnZm7VDJHUGqZ0UlYuKb5vE70Hu7tnV0VC4bCZ5Oo//DeWfd6y1NH9gEw7vXweTFR7DuUPxzHRMTEjDGadPw+Lc8OW1hx75TDBw5jjPTVyZz3j7LlN0XylWj4EfSGpXaB5lZkRFynlsXGvaL72j+DA2Dp2cAPH744TP7+vrNh2+/f/j8A588ffnvJVdzl/pZdmpeiR+/eecO+24L+bEuUGK1496Jwhnwnn3uCszUlzJD82XPiNt7JvDNpdFz9yeYv5ae24lVQ3hnbjGevnZDw4ErNe1CT/RxXDpfOE4yklxg2TiMqRCJSJqhak4AUklpUEj1DaRKoVR8T9t6VolBucJ2OL1heJT2R/WYqrKBS6WFdWH33N68x13b4etw+d7vh2P8LiRoslplQNmiuVCyUHaULJgDhXJn5sGztDuaFFDc1Fem6bx574Enb9140vQjtkB99faP97Z+QjK6Wx38M6gJP/b8EYBCzafxY125tHGkiqBoOXgNrj8S38RZxeYDVevoOn4zHrF7kpBQBga1vqP4PjH2nbyLwXP3cLNUHXmYLFJe3dt5eeI6kWORpALLuuIwc7mB4QMmmUSN5O5NKmLZlI7CmSpUg73pwFVaVQpNbCb1boBxfaOLu52+8gTdpmzVOgKdkqnv7p/MI5uLNp+O0N+MaI4PtDhQV5uqZfLxEIkKJXJLDtw/DS0K959/5K26bj5wwfP335LUHaCkVIHsuLItunhIwYb/w494xOQpMxeUXLr9Eu3GbhTOoqFo+MHtqmHf+QeJ1n2cqoicXj9cNEeS7vGYeQew9YSTcCUWcvm7NMZhpT2vrUm81uixSMqwBplJzsrr2EypLZyrUCJfNmyf15s7tGNDq+uI2XvjrMGeVDg9eY86FQshKxM8BAV0hoeGw5Fdjwuq3rnt3568q/KiTedx87H21R9+F8p7a1ytOK9zvnhsGwzrVptvsVN0tVTOWXKA3httu9dxKIJeraugd8vKKJE/GzdXafeWYueSAupekyuzFc9WID66eeEh0wLFqFQ8N7o1roibIt16KO+wQ4PysDBX7DflymaDs9efsr+vOu9JJN9hglqshry25GCmO80fqcBZslY+u/1Ak5ol+SIWEzqvUbEgLjKBStU21JDJrCPD09iFuDkdEa4kOkkmsCwqjWgtkxmIxltlMDXGkeWDeJqCGFSQjgriJRfI33CbrfYUBa9scFq1XAFej4hKfEhBCdXbZvdAdTYIqMTH6EUHtdpC/x0opYmi66cNbILFE9qhZd3SfMJJNeZMCdB7L1YgG5rXLsUd0lVK5uWO/a+evonu26SCgUaGBry5bYUSeXDs0iO+0xiT5tVLYPeifrwaqlg5IXrmkRERqCu0KiNznLrcHItR//53ofCHlRPaY/W0LujbpgrvHCSVCvbc9RssTE1QIUZ3ICUUHV+djW0KlqbMCjVkKJnOrvKLYDfHhK+kKEKSmIQZq43MGhGOZ+zlRJOa107uhA5NxcM7nB68Q4sR65JlhYEWNUpi05wefMARtJIt3XIBC7ddUFnRSLVvXKUY/h3Vknewocqb7cZsUBvoCQWVYWlQuQg6NarAy9ooi/ElNuRmii1+6c4ItyfRoTr6VxxfYs+Zezh3+4VEflzCQG28xveqD6M0adBz2nbhKjCwbTXMHtkSXkxbKttujqQApSDNp0enRWlZoUxDL9dWc4K2JqgXJpU+OnJVsftXhJn7t/ZM4McElRWqN3CFcKYO7eIeZUqDfZnoPgYxOXT2PvrP3CXu9pDDM608ooSH8wrdW0TpSOIPpXbtDK3csh9mL9VcuKICZaxvmNVNOFOF2sdX77E4QTvpJjQDW1fFnDGtVNRp6ppz6PwDvqLlzGKFRswMK8jMLvIJ7D91j2tWiTGZyCfVtWkldGlWKWoi/C40QEOZ7A0JlyM4Qs6+07kcoZGK77/YdyYn2Jd0U366M2Tpp2GSy4h9NzJUfDdh302Yjm+ahn1niqoxO0+oAUk1n3aduIOdJ5217nodH+i503MljWb6gMYYwsxsggI0l+3WHCc4f2Qr9GtfTTgD5q0/E+/2ZxWL5cLBZQPQeMBKPHN1R1Zrczw4NIUnVBPnrj1Dp0mb+bEU5IS/unWMqKVDhgD18dx7/r5wJRZy+Ukfp6VsjsukhkGCkOgCy8phRCe2xu5ih2qvRc5nqhMlVoiPtnEpJuaKhuoLubPaIIRN/D+5a0hQ+V0q8idVxoOgFIx/lh/lDT4TEpooVPtoSMcavOdfbD+ELjD5gyAmmPzD5Aigr1+KL9KckgImr2CWVoYM9GUkgzn7no590fX4QsLk5p23WL3vGi7fec2beyQGFLfktGciD+nw9ApAmbZzEBSq2TylMkb7lvYXzhQJ0I0GrxLOdIO0+JvbxsIsvTFvAebhG4gG9kV4ldSPX70wadkRHgAdFzXK5MfBFQNFcw5//gxFtW4LJbsQyeWRPXydlkerm4lAovqwyBSURxicYqJKTSLRRNs2pyd3poqxbMtFbNdQZpYy3rfP74X+7arD9aOHWjfepOTlh2/Yz8yQ9MZGyJbRAunZoCEo0PDhi89YuOk8Rszfn6DvkRzObeqUxn8zuvKUitzMRNFVWJGAIuH0NUgOV/8IvPaNgFtgJH6EMKHFBBVpVkkkqzj0WvSa9Nr0Hr78jMQn9n68QxXvhT5dWia9dDEx6Z5QSaK2DcqhZa1SfNK9/eQBXRuSxAWZ9z4+P1GPmf5kGWw6civOzAQqY0yJ7Ep4ov+BG/Hya5bInx2921ThSfXk8KcmrpQ/SBrmiWtPta7q8ZEJIyM2NysL3ZZiQrF2pQrmwN6z9/hCEBv2WKoZZq+4/dcX50Srf/Qba1dcyGWWDqP2MCW/g3BBhcFM0Mwe1VI4U4V61zUZulrygVNU9Yfz//IbSLi8/45KXebzAU+DYNO0bpi0/Ei8/QG/AwliCyawjAwN4f0zWNxR+RvQLmNrJqgm9GkAuxhNPrWFJr53SCQ8mUDwYt9JaKUkSNuyNjGArYkMNuy7cTyWXCqpvGDTOd7GjXIKEwoSjuTo7ty8Ejbuu46JTKPWdHurl82Po6sGC2cKF0jxVjN1TsGqzzS1zf/25L0QlRw9/xD9Zu6Kl2Amf9aJlYNRQSJtTFPlWybHDvo6LaWWfIkyshJNw7Kq7N+YCSvRJhIUvUvh/2IBiX4BwWgzcj184gjE7Nu6CtIJO12vmcDadVqRbzWeqcAUaLds1xXRVSCxodcMDgvn3WESMmKbBDE5+Skkoktze8nmG2KEMSH1LTgSb5gG9dYvAh5MWP1kpl8Kk1Uces9ktpLA/UzaF/tO18gfJmLFiEKme8NqxdG+flkmJAK4xpVQu7XUOLZsoZxo07Asgpg2d/eFdHfm//VrpFIp4oWLO7ZLxTyJQAJyQOuqvKxzzDgq8t8VZ5qQmXFaXI1HWW8atxTvFrMWXEwcSuXFsUuPeZOV2Mhk8sKm2SvdCfniHL9yJnGQKALLtsY0s4jw0NPsfqolStHE28FMQUr1iA2NmfELDuKGSOxKTGhw3X36EcXyZcUHNy8Mn7uPCziy2RdPbI9NB2/iOrvhqQGy8iqXzIOts3uif8fqvBO0NpCs9GKm1Fu/SG7qeQbLEZKwyl6ygD4TmY+fmfnoH6Zw7JPwovsWFyT0m9cphQYORfD2gwdv6fa70GQ/ce0JiuTOgn4dqiGzpRluP3ZV0bTprfVtWQXDutdReZ8L/zunMSwmJpRpQWWHxvdvGLVLTVACd9Mhq3HJ8SUGdawBF/a5yMzTFaoF993DF43ZIhn7XlKoAwXRUmkkdTnPfluGylaZG2wMdL+W4DtLWjxW3bGyHzmLve9/hFMVerdwwKIJ7YQzVc4wW5sKmcVHM8qfwxaXNo/iq+cb129oP2YjPiXAAPyTUA4f9QlsXre0yqDUBJl8X9nkdWNftIv3N0K7jXZmBsiaTnuTkUJSqPz0/1Yd50X0fhdamCf1aoCh3WvDx/cnth65jYev3Lg7o139cmhUU7Uu1Y27b9F61HqtTDjz9CbYNL0bD1lRQu+fOvbM2XyWHxMk1CiPM77aIznyt8/ugca1SgpXVJm06DDWHxbvUcHm8Hxfp2XRSZMJRIILLJvKIwpFyg0oAk6t9go5pB13TxDdTfP2CYRDlwXxSkGgQmznNoxQceBTHEzPSVtxS4c+gskF8iH0aVUFkwc00jrA8+cvOT4yE+lbEA1Q4eJfDsn4LKYGyJXBAOnTajfUA5kZN3f9aWw6evu3m0AQlYrlwvzRrXkyv9SmyK37Lug6cbNWcXkUab97YV9mSkb3Z6Qkc0qh2XPunnAl4aAik7d2jecdn2LjHxAMh87zRVvPMUM9OE1k2lI/EriBRUKbhDLj7JW3sucSLfoFuENyUgeUlKjCMGb+AZ6GoCu0s7KNmUul2N8ltVuZlEwOyLb1y8KXrW5S6RPJEUpR2j2/D3fcKqPoNUFhB698Ff4pOtbLqmjoXtA9od3GQGackNCiGDBN0EYOpQDVq1QED158godYSooOUMNSKndMIQtpaEPGzJRrXzRWXd57YAEzAyetOKrVLh4VjTy6cpBKIxZamDuP/Q9n4lGuWRso8PWruy+a1irF5rBwUYBivKjE9NHL6m38mV2YNlIWUSDEzWm3cClB0G7Z0RIrhxEN2Lp2hh2q/d3a5QviwPIBoqvMpVsv0X7cxnhNtqEdaqBx9eIYMnsvv7mbZ3ZD5XL5hZ9y1RQ7jzph/LIjCbojlNCQVjW8Uy2M7VM/avdTE+Q0f+cXCc/gSL2Q0hIaeRmZxpXfXDuNi9qDLd50Hst3X0kQbYugV6UyRWT6hWg5HunfUID18n86qjRHJf9Uh7Ebec32xIRMwz1sEa1XNbq0sxKaXx1GbpDI85WzwSlr4uO0NMFqwcf91LSlaDsjS4vsD5lkVftUVMSNgtrEHO1BQWGo0nU+b3oZH2ibn9J2lDtyNPGpsF7f9tVUhCOlw3SbtAXfk2HUPK1SG6Z3RXmRXK7Y0I7fO/8IuOtNv3hDoyJbegPkMzdkGpfimibuP/2IATN2wjWRBYMYVJOMYg7H9Gmg4sekPpndp2zlzvGkgIK8b+2awANTY0PVc6t0Wygq1NkQfekb9rMU7m9IEAd8gpmEVvnr92HCqrdwqgLFXLVi5pkY8zacwVlH3QvgKaHI5Zg+RRJcF51f4Yu7D08uVUbsUmeQtvXK8iYDX3/o3p03sWhTuzT2Lu7HqzdogoQTbeM/8Q6HX5je9PtdlKYiLWoWRpp3FWns0BY/jannru7C1cSHckJXT+6Ivh2qqyy+u445oc+0HbwXo64UsLNF8XzZdN459P8Zgl9h4ahlr969ivxbIUzxiN3HkWDv2tbUIO1XZhomiINNw2PSHtsag81+hRm7sD+mFrZO+Ul39k0SdR5T2/bqPRcnWmJz+SI5sX1eL97pRkkoe8jjFhzEzji61SQ2xkwT/Hd4S/RqW0W4Io1PqJyHJgSySaYn4UmfRobCVoawMo57Ouw46ojxSxPfvZDJygzb/+2FijGCN2n3j1ruU9CmriOB5F2fFpUxY1hzXke+Usd5CNIxn5V8b1c2jUIxobxOTMgBTw09xDbN2Hv9ntYoNH9C1M1KEA3LKGuVsWwFEE1unju8BcqVUDd1SCvq+7/tiWp/kyZ16MJDnhiaPYuiRjXFkDSqUQIZzdPj6t038d7y/R2yZTTHgcUD0LhWCeGKOJRUTIKKHOphugcs69ESSuCm3VUKCbEyNtCY+lOqsB3vlnzZ6RXXOhKDonmy4OjKwShaIDqolFKK+k/dgR2npdPVpCClYfOM7rzBBgVrm5uZQs6E3w0dYxVprrxy+YbOTSuqaHwEOeBpTp0WyZVlv2kWGZHmF9OyfrtG1G8LLGoxz978Afam1FQo2vFaOL6taAzRsYsPsSIJalwFBofyrra2Ful5I1IlZYvlROVSeXGRmaO/UyBNV+yL5+aDMX9uRV14KbxC5Hj0I4JrV3qSBjITvwXJuUM+HdO6pCCNnWKp7j/7gM/ffy9mK5Ml06Rm98SzN1+4dtKoclHsX9JfpWLCV/YabUeslyyjLAV9gta1SmEf+3sk/L57+OHmfRdERkTyndADZ+/pLHSpAgllqlA9stgUzpsFp689Fdey5PJyafJV3hj20VG3WuKx+G2BZWrnMJ3dGLUqoiSB10zuhLy51B3twcFh6Dphc6KtULGhHZnzji/ww9MfNSsWivJr5cxmzfPynB66JnrFBxo8Hdgg3za3l2h1CiUU6+nip0hEDtfLqiSH7vl3pm2RdkvalpRvSxE2U477tahjc3yhne0iuTNj1f86oVrZ/LznZcx0mEcvPqHFsDV49yV+Hb5LFMyBczeeY8rSo5i35RwOMUXh0YvP6Nm6Mg9MPnpFvHuOJh6y99SrZWW11DqaV3my2zAFQb0EDZMHxgYRSMu0rHPCpXjxWwLLrOowWwO5bJcMMrUgUeptNmlAIzXVkVix4xJO3tC9zIq5qfFv1T+neCyKKK5fuUiUT43U4w4Ny+PzF+9Ec6iShjmma13MG9uam6RSUPAnaVWUJ6fnz0IbG/QcrEyodpe41KIJ2rhGccjYKkPpN/Hl5kMX3l28QayuzCcvPUYntrD/zk7g83fuvHt5ALM0lJCrJLsN0xIbl+eVb3XNCAkICuUpUFRlNza5mcC6ec9FPM1JLi+TPme5LcGf78Z7q/63BFa67JWZdiVTa81ME3TTjG58dyU235mW03faDp3jWmzM0+H+gSm8zdcHd91zo5R88fTlxfXsS+SJen8kRKimtbmJEbPr33FbnYYNmW9evj9/q4EpOSoXjmqDYd1riwpvJbSqP/KKSJX5fikV8hu6/4zkBQapTpcY9Eyrli+AbNbmfHc6Pj5R+ifnHV+ietkCyM7GJMU2rdt9DSMWHEi0DakHLz+hezMHVCyRGztOOOv8vh+//oLOjSuo9QKg+0HdrXeeusM/V0zYz9LI5QakZcU7LiveAsus6iSmXYWLalf1KxXB0K40QYULMZi24hic4xHRPqVPQ14LnVTcHcedfstZTn6tfcx+z85U4hLCjge91wol88ChZF48YZrYtIFNMaRzTexmN17bWkKxoZpVG6d2kSz/TNDHcPGPwBs/fQBocoSeiUewnJuI1hpMxFJF7FDQzhZnb73QKh8wNrQonrv5HC3Ywkljov3Yjb+1UMYFmaJUTYIyKigt7j4TYLpACkdAQAgaMq0wNlnYvLr/9ANcv6hvqLGPVso8e8X/fsazZla8BVb6bOUnMYlZVziNgtIPNs/sjkwZzYUr0bh+8uSrhjI5U1uoE/TqqZ25JmRrnYG3fXr0m+k2FK915uYzXnSteoUCKn6tXq0qI0+OjGg3an28tTmKZqbE0UY1pXcCaRJQXJV7kF5UJXfIRKTCghlNDCQroBbOl5VvNJ289jReQos2f24wc6p7C3u4fvTkhSETk3efPdGzhQMz7fJj53FnnRfmF67f0LZuGbUKIiTUi+bNiu3sb5K2GBPSsiJkMjnTsuJVCzpeAsuq3AQLGEbuZnaTWhZzA4eiGNi5hnAWDb3v8QsP6uwnorFBta9pBVNSjuKrmJaVELEwtLJQwcD6lYvCVCiARgJ10LRduP4wfiVquLCa0wN1qqinMiihGukPfkTwiaAnZRDMhtsPpm1lNJEhrYRfK3+uTExoZcUpJrTiU46ZdtjevP+OpjWK48T1p8LVhIVSbeo7FMGu+X14hVJK97HlIQnPhd/QDrJyyMVDnZhik8nGHA+ffhTdLJDJZcVMM9dYF+J+K9qxpiValjyLhVFoPyZJ1BxUdCNG91BTujhU8uV4PB5A6UJ2aN2gLB4//xSlmWW0yYAx3cVfJz5cY4KpXt9l+OGl8AVS55tj1+PXconMwK2zuqN2ZbX87yho+/yupz4QNCVCOZx3PcJ5zXspyHm+hY0BShuLD6eY5j9k7j7hLGHJxyyHfQv6YPeivsgZo2Jt+yYVUIbNNV05deMZn9tijO/bgMsENZjskKcNiy61qgO6C6waPUzkkI0QzlSoViY/ypXIJZxFQ9rV/E1ndbbJKY9qzvDmvHwG5QFSvSwl/TtUR56supcIluKbtz83Oc9df475W88LV3WDHOzr/9cZdUWSRJX4hspxnw34v7VWVWqAnPH3f4RrjJEjobWOjQVl9RBdoZZdCQn1/qQKpzd3jueaPznHlVBD2LCwcCwc05qX+NYF0iLnbhT3oZcuasejBUSRYTCKTlPzf8eFzgLLKsymFfuoajVi6OOP7Cra1JlL4PiEMTRk5mUl9oE37LsOtx9+mL7mJE+tIaiiwfTBTflxQtCsWgn4+AdhAK+DrbswoZ3RBSNb82J7UlA53wdsoOvjq1I+5H98xJ4lBfhKQWOBxoSolpFEkABqWbMUnHZPwKhe9VRivKhJCrUWc+g6H/P/O4uyxXOhSyPpDSIpSCMU07JIKI7rXZ/LhtiQDLE09+8onGqNbuK/XTtDU/8Mm9nLqYW5li6QHVOHNhPdRZm05LDOvivq5LtzXi/up+ozdTvflaAyyNRuvWJJRX4VFeyjrPXPEh1tdYF2DHeecGZ/S/eqEfSRx3ary0MXpKCB/dgrnNn9wgU9KR56lB7BkTBLK12uhlJ5DJhwE2tZn9hQis+mGV0xrFttlaKZ5Fo5e+0ZOo5T1NEiy+fJmy9oVbs06lYuwnfhdfEPky/LyzsQLeqoL9bZs1ji/I3nzIJRD71id4za3P8nnGqFThqW9ecc5djLiJZdGNCeMsqFkxjQzmB8fFfdm1bi5WgWMHUzMDg6dWbx9ot8G5YgCT5reAsV9VaKCkVyYtqAJjwDXozzzi/xNJ4Ry+3rl8PEAY2EM3VIs9ILq9QJPdOn3tKaFg3NMX3rx0tziS+WZqaYP6IlrmwdgyrlVYM7qYZW+xHr0WXyFpXW9dTYd+KSI8hobcZDenTl9K1nPPg6NqThDetcSziLhQzlrSqPsBfOtEIngRUpk5PvSk06UHJlmwbi5WPInNPVHrcxT8/LA794+1WtqgJF/c7dEG0zlymWE+3rib92TFy//EDHxuVxZfMolGOrXkJBwaXLJ3eQFJrks3qkF1apGnq2T9gzlvJpkUlIfQwqlxBvm5VQkHDo3LAC7uydhH4dqqukzgT+DMH0FcdRrcciXJbopHPp7mvuw+3SohK3mHQh9FcElu24JJyp0qRWSV4eXQx5pGy4cKgVWpuE6R3GZDKEfL0MMjUVZWjHmqhWQT1M/wdTAwfN2aOzs/2fvo1QpVx+DJq+mwua2FDuFrW8srEy4+e0k7jlyG2N28gUY/LG9Tt31ndpWhHpjYzg9OR9vLaelVDVBUpklsoNpN3Ah57hKa73nxShIWFwefsJDx68wm3HJ7h65R5u33oER3b87LkrPD28YWJijAzmZlyz+JugR/wjJFLolaj+4WlDpn6VYjh68VGi5NBSFxtqTEyFK2P2JyTz7/C5B+gyYTMXSHHFh714544+baqiZMHs2H36Ljf3tIXiunq3rKxSFZWgGMew0HBcE+viLkNeoxwO60LdnLTKP9JaYKXLUbGfgcxATVekCp/rp3cRrXf134GbPF1BFwraZeJ91q45vcHC7eKxZfQQPn3xQtuGzEJlkMCg4mK34sjnes+EH+VQkVZWqXReNK9ZEocvPOTqsK5QPSsqESNVdUEZZ0WlS1Iynz664+JFZ+zedQZbt57Apct38eDhK7x58xGfP3+H2xcP/uXq6oaHj9gKfd4Rjx+9gV2OzLDJqJ6alZohTYtajmVOZ4A0IrYLCZIqpfLxzsnxiWKvUCQXpvZvzNN4lBtDZI38O6wFb2+nLKGk5MWbr+jzz3as3n+dZ3fEhZmpMVZP6ciLSWbNZIlv333x6I32AdpUp97M2Ei0a3R+O1tsPHhTTUEgBYjdKq8QN6fbwiWNaGcSluuflpk8g4QzFZpUKy4a1U67eev23xDOtIPWpTkjWvBaPf9beUwtSjYm55kgvOoUXUd6SJdayGQVXZJDDPprU1Yd58KOoEJm3nE0bJWCiu+JhXAQfAfJKyLFhi54e/nhyOHLGDVyEcaOW4Z9+y/gDdOswrXMa3vr8gnTpq/H/XuJ0xghOUPPnHYPaQyIUbJIDiwc1Uo4043Hb914qMCuub157uIApgnd3TcJPVpXVinh5OsXhAkLD6FG78Vad42izlP7FvZFjUqF+Dn9jexMaOnKtuNO+BWjB6MSip1sxqwiMeQy9AKmaSWLtNKwrPJUrSSDwXjhVIUFo1qrBKApOcts4R2nnIUz7ahXqTDG9W3IP/C5m8/iTIt5+uYLurd04A+LtmtptRErIBaTX2xlq1m+APLksEXPyVvjVVaGyhrTjqgYJGOVZYxTFOztvn71Adu3n8SGjYfx9KkLAgRhTv65nHaZUb5CMdSuWR4NGlZGowaV4VC5JPLmyY6gwGB4+6jeR1psPL57o06disKVvweK0yJ3QBamaYlZxtQ56uPnH3jGzC9dIK3qJfs3kwc25gs07eiZmESbX9SDcBcTGGT+kbWhrTVnlSEdDi8bgNJFcnIlYM760xgxbz+uiJlwceAfFMJ3JylNKTbUMoySomPD7pGtac7gcyGfneNU57QSWCY5qOaV+u5g3mw2mD2qpXCmyqi5+1V2IbSBKjxkyWQRVT2BylR89ZSuv05pDNmsM7BVJyc/L5o/K87deIbvGlozVS+dD1MGNcHek3d57zldoYYRVINdrIU3QYnMKSk3kATLo4evsXbtfhw4eJGbdzTQaREoWCAXWjaviQED2qBFy5ooX74o8hewQ9asGbm5lyWLDQoWzIXadSpwx/LzF6qrOZnuzZpVF87+LiiNh6w+8mmJUaNCId7unUJ1dIHKtuTNaqNWppiarPSYtAVbmMDS1cWRmc0hsmqGzN6DrSec8OrD93jFIirx8ApA56aV1PyYZLIeu/gIP5hlo44sDTMLjwonksQpsGwqj8sgl0duZqusmpNqWKdasC+dVziL5pWLO2ZtOM1NMF04cuEh3L75MolvilxMa2tZpzQu3n4JDw2dbqibbo8WDlyA0CQrYJeJ+wjEIMcn1ckmXwI1rvwZI1xCG8hft2dBX8mGEVQihqoupBRevXyPlSv24uixq/jBzEAifXpT1GVa0dAhHdG8RQ0uoExN1f2TMSENrEjRPHj44BV8YmhaZmbp0KRJNeHs78OfadlUuVSsNA0FPlPPAWr3rmvlkXvPP7Exb8//hrfvT0xefATjlh0RbWiqDX5MQ77z7AOv4JAQfPvhj1a1S0VtisUkNDQcl8VbguXMmMNhpb+bk8YAsDgFlmkO+xZMZ+sqnEZBk3/1P53U6uEQy3dc5jdAV6g438PXn7GLqY0HztxHBDun/CbxD6iAbrKczLyKCtubqi08Y0Ls7WdPfh6TTg3Lc3t/4X/ncEHHzQBiVJc6kqViePE9rwidhfSf4Ns3L6xfewi7dp/Gjx8KLdjSMgPatK6DESM7oQIz/TIwM0EXSGgFMm3h6bPohPF8eXOgRg3FxsjfCsVnkRNeLFk6a2ZLyJgmc+OhbkGl5ECnXbfa9oUxfuGheNV5T0xIAJPGTSZrbHKx+blu/3URIS0z/SWTPQ9xc9To04nT0cX+cA/hUIXqZfJz8y02VP5418nfu4H0Ud67e2HWxjOYsvq44qIGNhy6ic9fo/1d04c0g3Gs8q0Z0hnjH2YK0u+tYTdMV6hsCDU5FYN868+8I5J9+AKFJRw8cBFjRi+G891n3PTLwLSgzp0aYvXqidzso7CE+EIaVUwKF467z2Jqh8bEE7aQSY2N4d3r8LZburLx8E3eD7BMjComyYkjlx7xHODY0AZd3YrqrcIIZsmpKUax0SiwKPaKrQuiZRGoT5sYV5xfw/dn0jR3VEIxVtNXnRDO2MqeOxP6ta4qnCkY1rEmL3kxc81JnW18MgVXTOrAVXAx3vkp2sQnZ54/e4dx45Zh/4ELPJA3bdo0aNjAAStXTkDLVrX4+e8SEBDtmyCNq1IlzV2B/haoKsdbX/EdVhpTK9nYIotFFyhV7Z8Vx2BfKq+oY/9PQ/7lCzfFd4k7NCovHMVChpoWNUZo3JrUeJfSRIY3Zn9EbcmleI36ErWedp3QbWcwoTh27Ql3PCoZ1bMe3/0gqNg+7ao8ePYRR+JRdL9vqyooVVR8JSOV/1Ng8vRbuX/1xNEjVzBv3hbMnLUR374rwjmKFc2LBfNHoHeflkgnYtLHFxeXz8IRu+fZM8HOTq1N5V8LNW2VSt+hsTWore6bExSPtWK7eHR5cmDnSXFZUI/JjvQm6oUaZJClMww1aCOciqJRYMkMZB2EQxWoL5tZjGRKJZ4/AnDhju6+oYSAbGJacZQ1s6ws0uGf/o346kPfaSX7Z8VREdtZMyTsKE1IDIq1eemTsGVAEoLv37ywZPFOjBq9BLv3nOWR6bQbaM4E+NAhHTB1Wn9kz6G5zZiuBAeH4vGT6G3wOrUr0PgRzvTQqHvBxopUfBa5GyjFTRfob+6/9DBJ/KZNqxWHfTHdTPwbD13ww1u95RdtejWuql5amYiEXFTmKJEUWGblRmeUyWWiWYtt65URjlQ5ff1pvCJ4E4o7Lz7i6PkHwhkzW5tVQtvaZdCmYTmcuvJE51rytC07a2hzpBOJ4ifeMlMwJBk5riIjI3H2zG2MGbsUTs5P+TlB5lmF8sWwZOlYVK9Rlp8nNLRDGCaY2uQXq123Ej/WEw0FlVJTXDGomsLcES2TpXlHUOmZtvXjztmNSUhYOO8/Kkbb+uIyhI1WB+uKwyQlt6TAMjJCLTFz0JxNXmU0bGwOXYgWFn+K2RvO8K1TgkId1s7sylMGpq6O9nFpi0OJPGhWp5Rwpgolun5lan5yITgoBEuZVrV5y7EowUGkS2eCIYPbYey4bjA3V629nVCQ9nbyZPRGRv369jARUflTG6TNBwYGIyRE+0q/X4Mi4S2RJN20dkk+5pIjtOvXoGoxnRe7gxfEBVaVsvmRLlbOIcH+vJlcZiBZ+kRSYEUiUjQitEa5gqJ5g9QYwvHpe+Hsz/HhmzfW7LoinLEPyMySLYdu6dx7jZygc4a3VEl5UEJWJzU6TS66lZeXH6ZOXQvnu6o1ufPny4EFC0YwrapcomhVSih30OWdIkiZhGLz5uo1/VMjq1buRd8+M9C/32ysWLYbvhriBWPympmGYnGZBgYGmD2ihc5VPxMLeh/F8mTF5D4N0b2ZPbJntdK5isOD15/x9Zt6ADlZLY2qFBPOVJEbyCT9WKJ3JleNaSZseDcRTlWghGExzt58/lvRsQnJij1XeEExwssnEAvjUfKYKpBKOdrdAiOTTT12cqxP/d8afPwUXfGRhFOTRlUwc9ZgZMpkLVxNHCIiIrBz12nhDGjdqjZMmVaX2vH1DcCt24+4TzQkNAw3bz/GzJkb8EuLwndUF15qo4ayNlpKzLGkgIQUVX6gtnp3dk/A9Z3juH/N0kKxgSU1/6WgHWlyFYnRpLr4LrJMzqy7hsNE/TCiAss/LIAZqzK1ICsTZmLVriweQ3EiHrtviYXfzxDMWnuKH6/Yfpmf6wI1D/jfYFF5jbAIwDUgeTjav3zxwLRp6+ApBH8SxsZGGD6sI3r0aq6xy3RCcfGCMz4JwjKnXRaeZ/g3QCZ47P0bSmtydtKuWOUH/wg+lsSY2K8hD6VJKkhIlS+cE9MHNMG9fZNwZdsYjGFCigpoxlbMm9bSXZgeuywuG6i9nmg4h0xmY+1jIFprXFz3lEc0FI5UKF0gh1oPMoIyu3WN1k1s9p67h4Ubz2HD4ZvCFe1pXac0cucQT795xwaa1E5PUvLD0wczZmxg9z56F8bGxgKzZg5ClarSdeUTkh+evti9W1FMkcyZ/v1aRfV3TO1kzpIRmUW0V3d39fptYlBdf8o7FSNfrkzo2CBxMwSowYtD8dyYM7Q5Hh2YgvObR2J4jzo8JS425KujVnhXHF/x91Ykl27hKvdefoK3j3r+oLWVGSoWFa14Ios0MGgtHKsgMboMREsR1JNoXXX1zms2iZOPA5qgwLq5W87p3LuQ2nRN6NNAOFOFVHn3oD//OckcmcHMD/quJG+ebPj336HIzb4nBZQsu2bNfgQLDuf69exR8C+KbCff5vDhnVSi+8kUL1RIvOSQGDSWKKVLjJE96sZLyyIBUDK/+BggIUUZKgtGtsLTw1NxasNwDOpck/umYkOVH27dc8GkxYdRquVMNBi0ElOF4OyWtXVbEGkOkowQo7FI52iCKXaiAetqAitTpeEkPtWMS9olaCTxxy84vhSOkgcU2FqmoFpjH62gVuF2IqsM8c4vUtRZmpSEBIdi/rwt+P49OhWpVMmCTIANgpWVbnE8v8PRo1fw7LlCq86WNSO6dmvMj/8mChTMiWVLx6Bnj2ZoyEzhsWO6omSpgsJP44ZMynf+4gsgafita4nvUGsiS0ZzbJzZLap3AQm9OhULYdm4dnh5bDqOrh7Mq5KKpdVRWaerTq8wZt4BFGs2Hc2Gr8H6Qzfx5YciMf7FB3e8++CBJhq6mUtxRqJrVvXyBdXMTkIulxel0CrhNAo1gRVmaGDPxJuaaM/E1DfqahsbivW5mMwE1iSmIXWUCv/XANnyY3rWE85UodQbz+A/q11FslVv2fLdeOf6RbgCVHYoiYkTe3LfVVLx7KkL9u1XbGRQSg9pGkYSzT1SO+YWZmjcpCp6926BChXFF3RN0JiSSusawbSsNGxM6gKVIc6e2Qpb5/TAxqld4HJ6Fg4sG4DurRx4Eb3YUL5fSMgvPH/zFUWaTEPr0Ruw5bgjPHzVAz5JwJI/qmiBbLy0lC5cufsG4SK+FKqbZR0rB5Vg2qqJUZoItfB/tbshk6OmcKiCfcm8ok7cp6++wFO0vk3SQwKnbZ0yGNCxBk5d070PYu0KBVEgj7h97spWwj+pXFGs084dp3jUupJqVUpjxMjOMExCBy1F0S9duov7NYiuXRojb774abN62HNlXzS2xCiYJwtqMQ1EF2iDiRoOU/oLBUyLZaT8DArlvzNg6k4UajwVO445wo6Zhdrk2J4Umhm3risV+CmOT2AQnryKTt1SkiaNAeo6iLuaIg0M1LQHNYElh0y0JEFtoXxLbK7dE+/AkVBQ7XRbtopRTWiqH9TQvgi6NamEkV1qY+bApry77qEl/XFj82h8OD8HG2Z1Q0BgMJye6x4TNriDePwQ+Rl+/GHt6sb1Bzh1JnoDgYTV0GEdud8kqaDyMXOZORrABh9RrWppNGpchR/riT80tsg/Ght6tMO6SLTI0gBVSoiNf0AwjrPrvSdtRUEmpLpM2oIDFx8gIDgUR5nWRH0RGlaW7liu5NFbN15ivJmO4Q2knV12FvdjVS2bXziKhVyupjypjHbyX/2SGXxld0pFkJHm8ujgFLUi90SbYetwRaJtkBgkgCwzpOOS39rMFLZWGWBjbQZr83SwtWTHNmbIZJkeWW0skDmTJTKYGXMHJ01MbSfnpdsv0W7sRuFMOwrnyoxbu8eLvgblgP3JqPb3zAT83//WIEzYQHCwL8E0qy6iQa2JRUhIGP6d8x9evVakN+XJnQ2zZg/+a03BhCZrOgMUs1bXlCnVrWrnBXjz2UO4Ejfm6U3w4vh03ib/NNOIqFPPWccXkhtQtNH0kv3+rQcu6DZlq3BVGurvOaJHHZRrM4eXgdKWqqXy4vjaocJZNFQmp1Ln+ep5vnL2lo1lOQKvLYnaelURTL9khmViCyuCSqhmsRV30jnrGN2+cWpXPDs+jfdOO7dpJHYu6sP7+k0b2gyDu9bkpSdqMRWxcMFssLJMx81Q2jLXRZO4ekd3ra9bMyrpqv4aoRHAtz+4MxjItJklS3ZGCauSJQpg2PBOSSqsKNVn+bLdUcLKxtoCEyb21AurBIQ6SFMt+NhQnNKAdrpVbaU2YpduveRBm1Sb/dj1Jxp3y+lnFEdZrXwB0XSZ2Ch91lI5xVLcef6R+8tiQxsM1mIFI2VMloZEqFTMjC2cRKP+yhfNKRpf8/D5JwTpWFvKLocN/1s6yJ8oyI8TGBgCT68AfPrqjaev3HDV8RWOXXjIiwa6uXtz1fPcLdUUlbigHRWqQS0GaVZ/ameQNjTWrT2I7x6KHcFcObNizNhuSRIQqkQprO4/UAzS9OlMMGlSL1gzoaUn4aAcesqgEKMVEwzaCJKYHLn8kFdFqG8vHugdG/JNkVnYuVFF2GW24hYHWT2xoQ7qSya048et6pJ+ww+1gkKN7osUICB5UD1Wh2olcplMxU+jIoXkMjgIhypUlEjI1FW7IgZM34nXrtFpJIFBoXj/+QfuP/mAizeeY/+Ze1iz6yrmrDmFsfMPoMfErWg1aDXvXHvn8XsUbDoNxVvOQJm2s1Gj9xK0HrMBvabtwLB/92LBpvP45uHL1FTN3XZiQ7a7hbl6M1QSVG5/0BS8cN4Jd4T8QEuLDJjIBEVc9dUTEqWwuiu06zJmk2b8+J7ImUu9I4qe34cWx9hWEUFpMVJ5d1Jcu/cWwcyMb65FzBRZFsqWXvPHtcajw//g4uZRvIu0EgoVmjusBU5vGB61MVUoX1bkyaLbbqHjI/G2Y1SIUAwZZCoyKVpg1ZiWhtmMon3uq4o0RiQcH+ke3f7mkwfq9V3GtCKFYzCICaxhs/eg3sAVaD9hEwbO2o1/Vh/H4p2XsPmYI04wddYnMJjXjr/s9AohbBJRqy4xpcfbJxB3nn5AXN1tYyMVAkFZ9X+qtyA1MN2+Q5FeRKEDo0d34ZHsSQXFe1FNrZjCasyY7rzZRHyg+vzh7EuPNFSqSKrIXxcJC0AKmjPX77xBzUoFubCRwto8Pdb/0xmLJ7aDn38wTl1R7B4WbTYdq/ZfE36LWVlMs8qVzQYb99/A5CVH0G74epRiisMnD92KCtyRUHLKCZ2vRChJfVGF42inu43D6MJMDNDoVFHyqBb6yxMzuHoZE9rWLsq0HbF4DW2gQNRB7arznD3yUf277jRW7r0qKmxGdK6FqUOaonaPxXjs8lW4qg5VMbQyM4WbEOimDRkt0uPVqRn8PcTmsVfEH4m9oia0UyavxKfP3/nD6NatCZomYbssKnW8YP42vH6jUN9JWI1lwqpUad222MN/hcPJ6SmuXLmL9x8UPfiyZcmIevXtUbVq6d8KxyD3wMf3X3lEdq482RLMTKbkZU82CalkjF3OLAlSOloXMpoYoHRG9c9C/qiSLWbiu5YVIYgO9cpi7Yyu6DlxC45LJCBXKJoLo7vXwYGz93HW6SWCmFaWmND8dDk3R82UpF3MQkyeqPva5JGG4QZFftxdwh3TUbNUjggKX1WzSHNlsVYTVoTbV+94CyuCdgRWMwneevg6eLG/M3VoUxxY1A+2luqtgRoydZjaGb388F24Ig510NFFWBGNqhYTFVaUmOoV8mfMwUMHLnJhRZQuXQhNmiZdqyyKs/rfP2tjCCujeAkr0hAnTVqJFSv34umzd4iMiICNlTlPEF69Zj9mzdrIBLP65KASLcoGrpo4fOgyJkxcgUlTVmHSxJUIE2l4oCt+foHss6/ByFGLmPm9EqdP6Z6H+rv4hEbil8iwox2/FjpGvl90fs1rw7XQYBbeffERnSZuxuGrjxNdWBGk+b3/qL7jSf4z8WBUmUFEWkR592MILPHs6NKFxUusPHqtfc99Tdx+4opavZbA+aEratoXwvVtY1Alhj1rySRyqSJ2cHz4jjvtEhqpvChPJqz+hLPd9Z0bTpxSFMOjyp2DBrXjPoak4OXL95g8eRW+uitapBkx7eKfKX10FlbUmHUKm/hKoUsUKZoXCxePwvr1U9C0SVW8YK+1dAkFoCpmJ0XxHztyBUOHzcfw4Qt4z0QpgoJCcOTI5Si3gJvbd/j7SwcvkzUQlzn682cw5szZBNf30VkE1KMxqSEPBPW3FENXgeXF7sndJ+9Rx6GIzk77xOTBS/UAUkLKjyWPjIxypkULLDlE70bxAuKJlI9FolbjC7WLbzFiLf7bd4O3ATqychDGdqvLt3TLMoFJ7bgvOUn3JowvlmxAVq8oPhnd/4Cznfw869cf4mYOQaagpZV6OkVCQ+bVxfNOXOtRBoUSefJkRyEdE5qpO8/CRduZafULHdrVjao8SgKBMGbn3bs3Q8kS+fHg4Ssc2H+Bl2pZuHA7du05yx399LsnT97gvy+Gy9vPUWEeRJeujZHRVrzZih/T3mfOWI/x45ZxU1sMan82lwmrDx9U3Q20I/on+CbhhqhQKg8y6lg1loJIzTOYYEiHGihXOCf/95RfmFSLoBhSyk6JWN2so5AhKko1hi0kFw2qIGebGA9ffhKOEgbSniYsP4JB03Zxe33yoMbcRGzD7HBaHS8y+zqhqV2pkGi4BsVe+YUlvXp17dp9vBcmTaGCuXil0MSGTKm1aw5gw39H1LSQYsXEVzwpyJxbsnQn9wO1b1cPefLmiMofS2MYwy/D5krtOoo2ccePX8f//rc2KmxCSeweh0pIIzt37rZwxgawgYwXMbx4wQnPn7/DVzcP/j48vnvjyeO3vGMQaXMU+CoWu0Z+NopzexOj48+fhjpGi5mFlMZSR8swBSUU4kML4KSBjXFh80i8OTsLr0/MwO0d43iIwp/g2dtoLTYmxfJJ7j5HZVvz2WpRdZAVk7hqv01R6QVF/gjdgFfvNfuT4gOJiP0XH6B+n2V4/8mT147v1Kwib376NZ5tuDVRTyKHyZuZg0ktrqjrzJ495/gx+dR69GgmOsESkq9fPDBlympcZYJSjFKlxNOxpNix/ST3P1WsUAw5cmTGgoXbmMAK545rqvMek9w5FePqF/v5p8/RYS4EZVaQYz42JFzJjFTuXBJk7l246IwNG4/w+mAjRy9G/wGzuWk5e85/eOfqhsyZrZmp21vNgU6a5YYNh/Hwkbj2Tu/tT0CuCKnNngYS7fWkcPcOwFNBo6EF6f7Tj9h8+BbGLzqEZ+8UGyFJzev3qs9bSR67jEgbc2ETkEFmY1Z1mC0dc4FlGG5CUVtqsyMjM0fSmarbvn7+QTrtVujKc/aBavdZitNXFTsbdtmsMapz7QSdwKQSk4YlhqfE1nJicuXyXXZfFZsYpUoWQP4CidvRlyqFTpy4Eh8/iQ/adKYmyKdDUjOlD1GZYAtzM7RtWxerVu/jCxuZVXPmDIG9g2ruWXiEtE+patUyaq9NdetnMNPO+Y4iqZ2i7MuWKYwsmTXHAVWqWJyZmyORQ6RH4kFmjkoJa+JzjHQYEm5JiUew+OvVqFCQ77BrC71vqmPVafRG5Kv/D+oNWM47qt949E7nhsIJxXdmpv/wUpcf1pbpYSGSrM1Iaxwh474JLrAiDSDqyMmTzYav9rF5w7SrxH58lHXefcpW/Lv2FBcu/wxpgkOL+iNzAvl0KJLXNqN6/Shyeib17iCtfCdORHedadlStGBGguDj7Y95/25mGslhXoucoMqZsX0auXNnhZEOjlpHxyd8crRpUxtnz9ziJhj9zT59WrK/pe4Hjdl0NSZZs2ZE7z4thDMF1ORiwoTleCv8m6JF8mDx4tE8kHbR4lGwE+mxSOOWzNLRY7qKtt+/dvU+DhxSNCHNns1WNCziwkUnnD/nyLMNHtxP2n6bfmHimz5WbFJTzXVduMmE0zmnlwjQobtPYvPsrXp4Ej2zonnEzcLwyDQ8cpZLI5lcLhoXXzC3eLPNVxIqXUJDoQ+LdlxCuxHr8YOptjXsC+HatjGoESu7e2SnWnw3UReqlhEPhg0Ik3OhlZQ8ffIWXt6KcAyaPIUKJ3yrJzKdLl+6g1HMZHogmEAkUKjh6YgRndQ0iGJFxe+PFHZ2WZh2lR7lyxfF9ZuK1k7khxMr10yO9TNMqMUmfTpTjBvXPSqan35vx7aT+HfuZr4LSAO6XZu6mDZ9ADfzCNK0Cse6X/TvR4/sgrbt6qoJYoJ2INdvOMSPSfjNmz8cAwe0Vftd2o38b9NRXL5yFxFJbB6SD0uqTpZkdYMUxNuP4i6lYvnFBZZMJufmEBdYbKyKCqx8dtxsVMPls2LbO6m4+uAtD32gVvS0i3h45SCeMW7CBmtDhyK8DX0AG1y6UK2ceO6SVM+4xIS0EyXlyhVNUNOXoJioGdPXY936Q3wSElaWGTB+XA8MGNgWHz+qL0Dlyov796SoVr0M1qydjFevPkQ57+vVVU8op58tW7pLpcsPQZsfFM1Pvi/i3Ts3Hl914tQNLkypv+K4Md3QrkM9lb9JznVn5+jaZyTIZs8ajIr24sX0PL578R1Jeh8krCZN7s1jzajB7MQJPZFVItXEKAkLJCr5IeGacCit22bI70KlletWLMRTcw4s7se/pg9siiK5xWvHacObT+IyJG9OcZnDpBSfsAp7TwbRJV1KYL1ySXpn3RdPPzQZuhqbD9zk5iiVt3i4fzL+m90D1++91anFGAmE8sXFa29T4F5S8yiG07e4jjtzmghgWsnWLccxfsIKvHyliGuiz16zRnksXTY2SihR/FVMzJi2SlHeukI7eIcOXRbOoJZzSIGiJKzu3Vff8TU0NEQu9vsUhrBn91m+GfDZTbEKU3WImTMGolyFaIcz7URSYCeZiv4BihisEsXzY/684ZLvPTg4hGlT23joRpEYwkpJmbKF+X2ZOWMQundtgubNqqNF8xro1LGBqFmb2EiNxfLFtK8b/7tkz2iBM2uGYf+yARjQqQaP6aKv4d1r4/qOcRjTtY6681sL3ksoPVKVTNlr8InBX8vKfuR3tmyp2X+P9k9Bzhyqf4BMiwod5uL9F+26gyQ09IY71C+HhRPaIb0QgT9kxm7sOXePH2tDDvYQnhyfJpxFQ6bgta+/kjRg1NfHH/0HzBHOgDWrJ0nGFGkL5QFeuOCMQ4cvRWlUBLXh6tOnBQ/iVELay8D+c+DjF+0ELV2qICZP6SOcaQf1J1y1Yh9uOUa3dKLJ3rlLYza0FP0TV67cG9VwleppfWHXyOxTQkKL3o8ymJSgevH/m9pfJY+StLgNTFukqHklxkzbpjLF9vYlRPsi0gbAksU7+A5j3jzZMX3GAFHfVnIiDVMnqmdNCzGFu1zr2Xj/Tfskf6pIsm9+b56HG8AWDprHlA5DnoD/rTyGQJEod3KzXPpvJG/3pYn/LTvGs1Z0IV92W9zZP4mPjZi8Y5pXhY5zhbMYyNlUcVpqZZC1XP90YsLKNG0a2GZUd3DTykb+pD8FyZK95++j2aBVvNQr3fhLTro5RMtKJFoG/WKTJQmFFUFVPGMi5nPRFgqNIK2DtvR37DwVJawyZEjHGyXMXzBCRVgR39x/qAgromis34kLElbbtp7gworeP/myiOMnrvGgzcWLdmDM2KVcWFFoQedODbnfaO6/Q2Edo3EG/Z2YworK6cyaPURFWN1l5t/sWRtVhBURygTf2nUHMXjwPBw+dIkHo8aE0p24sGKC8n9T+yV7YUVQCFuQSCVSomwx3WKocmW2QtVKhVCrchE0r1UKLeuURpUy+eBB4UISY27qgCaiwoqSpL8zi0cZ4DxlUGPkl2iLJ4W7py+by+qfjUraUEFBETJYlZtgYfArjYnoloMFG+SUmhEb/8AQXlb1T/PojRuv+PD6nTs8/HTLaZSKqPWXcHImKrEGi8tb3QNyvX744uCBCxgyeC62bjsRlaZCUeZNG1fFihXjeaMEsSDZ58/Vy32UK6e9/4oWsDWr9+PsOUfuAB/QvzXmz2eCkZlcpA8/f+HKQxFIe6L4LDLZWraqxQUbmW5jx3YXfV8krKZN68+FbUzILNy8eTrTsP7BtP/1Q+9ezVGjejlkzZKRb/f/DArG3n3nMWbMEh51T9y7+wKHjlyGXfZMXHP8Eyk38cVXwqdaooBudfSzZFFo7QFs/u45cQcN+y6HfZf5mLv5HAJF5nOuLFbo3EwR3KuEykK1HLwahZpNQ4lWs1C+3b84d/0ZTIzTYnK/RsJvaQfV0fvxQ13xyWBmAlMTkd1pmdxAliYkm2HaHPYl2eDpKVyOgt5wn7ZVhbNo3rA3vf2Es3D2Z6Gdvi8evrigo4Y1rFMtUece1SNKaqGVhi0KFO2t3KXz8PBG9epl+QTXBGlTjx+9xs6dp7F5y3E8Y5NTma5CgqpWjXJs0nbj8U+aKoMeP34tyldEWFqYoVPnhnxHLi4ohWbRQoWZRf+OamVVrFScm2Q1a5ZDtapleIXUhg0qo1v3Jjxyn7rMxMSaaU/0bx8/ecu1ZZLfRQrnYYKlN8xEqlCSoKMqDyamxsiU2Rr5C+RExYrFeJutqlVKcxWc5xYyzfXWzUfchbB1+0lecJB2F5Mi1SkhMTKUwdZU/VlQfbgD5x8IZ3FTtmAONGda1YzVJzBz/WnuExaGnChUSSVm2trb99/RYOBKXh6KKqrQDr5fYDCOXXkMhxJ5eLXSTYduaqxsGptm1YurlV2ncbeXCVQv/9gJ8DJZpIHskIGBoaGoqz+LRO2lxIg4jy93XnzEyavRO2zaQDseBUXalRFS28iJCe1+UaCoEorMnvq/tXj44BU3F3+FhXNnNTnQ37m44dzZ21gwfysGDJiNBQu3cwc2mVKEOTPFWraoiZUrJ6DfgDawstbcp5DMr8ePVctJF2ACIC5hSXzjVR3W4MnTt9w3Rk1cY9bKIsGSJWtGrhEVKpJbowlWt549MxtHsc/Uhn32/lywSKXmSEGvlzWbLY/hWsT+FjWWpeDUvfvPMw3AiCdxW8dxP5IjgRJjkpqy6ISgyL+KUTxTCsrh7dQkWruihWT4v/u4gIoN1Zyfuuo4e75pUVfHtKEvP8RliV1WCcd7JOwMIiMjRAMfMmcSf7jfPXQr3xIfSLUX7bkfC+r2cV3HIoJkH2fNrO7UpmHxJwQW0bVrY15zSglVDKDuNJRiQl8D+s9hk3kOJk1eiU2bj3EhRYGZBJlTJGSGDGrHHfaduzSCRSwtRgqKTv8Zy9dTvHjcMT4UyEkhB+RHKle2COb8OwQZbdUblOgCCZs6dSqiWPF8vx3WQZrXyJFdokzNUqUKcuGZEiEflpgmRM1+JXw9opBgIbRx5xTMmQk5YnSDpooPzs8/CGfqPHH5Cg9m3lUorlv8oPt3X+FIlZzZFTF2sWGjIjMbGwaioppaa4nxPQkc7s1rlsSUPg2Fs4Qlh60l0qZV1yAo4TmpHe5KyJczZXIfZLRRFaQUK0RmV1BwiEoqC/kW8+XNgY7t62P5snE89aVGrfI6RaYTJHhiQlpK2bLSqyRpcvv3nefClN5Ts6bVeKBnUjZx1QbaeVy/7mCUU9jZ+Slv5pESoY8QJjIwSajn06GZqadQuy6dUD1DEzT/aCwo2XlcswuIzMNnb9x0drwr31NspCpSsLuQyYC9luirZBQppEd4+sS/aJ+2yNh/dSsXVblpCYXUFm2IxG5MUlG4SB4sWz4Ww4Z25L6YPLmzw5YJsExMc8nLjiknrk3r2pg8sRfWrZvChMYwtG5bh2sT8eVRLHOQduNsM4n/PaqAMGf2Jhw8dIk9F6BP7xbo1r0pDLTQhJMSMl/WrzuE5zFiy2gH8e2bhK0uklTQqAyWcAtJB1mq4yoEaubPofnfkGXTvmF0yXDqDH1Gi6Yu/sFhoqlumvCUUH4yWovLHjbubJmclouKaWuJf/TdQ1yNk4Kcd1tndMfAttW4c848nYlWyZtF8mdl/64bVo5vhxXj2mHG0GaYMST6a/rgphjeqZbSNNcaO4kYp+CkzscRgZzjFDE+fEQnzF8wHKvXTsKq1RMxjx1Tt5wOHRugNNOAxJzRuvIzMBhvYu1IFimcW9Qce/ncFeMnLMez5+94UcFJTGjWbyDar+SPc+TwZdwQUoNiQpsZKRWp0AY7HRarH/5B+PrNBzUraC7GaF88N3LF0JQou8Rbiwqw2awy8LpbuvBDQvmxtpKo+SWX29DyKDqDM4q0+CG8dGxL37xGSTSvVxr/jm6FU+uH4e2ZWXDcOR7F84rnDBFU94cmTrO6pdGlpQO6tnLAsM61eBdc5dfwrrUxfVgznXv8ZxO2d2MT8mcqifwxyNkeM+aJiO2/Im3lxPFrmDl7I3x9A3iowdy5w1CylG4VSJMKJ8cn2H/ggnCmCn2WlEqwhMDKkVV8LItBO3uUEdKoRnHJOUNlmKcNbsY1aCWHL6oL/5jQr1KMV5GCumcC+AaoO/EJy3TiYSfsLlgasFcU/dRWEqu4t1A5UhuonlbRQooPQk1X7zx6j5U7L2PcokMa8xHTp9c+qK94ft0y1ynVQIw/1R3nT/EgVsE80nrLlIn2X1HYBKXR7Nh5mvuCKjuUwuzZg3/LBE1MPrz/ilWr9kWFh8RG242I5IhUtlgmS91CNPacusurUmyZ05M3X4kJVSFdMLIVypWITvsJYmbecYldeOO0hmhVqxSOLB2Aewen8JrsuuIvsQFAnavFYEPUnHxYop/aUkTDop0G+hDaYsH+hqmxEe4+fo889Sej4eCVmL3xDK4/dEGIFvEaHz7/wIvXX6K+3rxzx2c3L/715auivVB+iYoSUmSWElgSgyI1QprVo1gOdyrrYiH4Lb9+8cSUyavg5PyUx8VQZPqIkZ14eePkiL9fIBYs2Mbj0MTcDeQLzRmP3MjkgtRimlmkG7smbj55h7vMxCtRKDuc907kAqp/m6qYMbgpbjOrp0dr1T7Kxy89EjUH6R7f2T0Rm+b0QPUYVXu9fXSzvqjFn9gCYy7SI1SBzJw0LNGfpheRctQoICxMe9vJ2syUm3c377sgSIeuJnRDvn7zRcXO81C11+KoL/tuC1Gq/Rz+VYZ90Qe2ExpAaotUuMbfpGGRA1qZMKykaLF8fGJTVDiFT1DIAsWIjR/bPSoyPTnCqz8s240fXr6wzWjJu1LHhsZyZh0bfiYnxMolE1YWumk1JBtGz9/PHelWTMPq274a5o1pjWFda6s58KlI58x1p4UzVWhXsFS7OchfbzIqtJmD+n2Xo9OYjZi+6rjwG9pBoTliCrGZeBE/htzcQCaXiWtYluoaFvkBqN66tlgKwX9UQVQXzE2McfbGs6jYETHCmZbw6Yu3qCYoBQWNSnUPkRoUqZG7TCjFpkTxfDh08CJvIEHmIFXypDItZXUsM5PUUGUH2gwwZWNm3LgeKFAgl1opZIoVS+r+ggmJ1Ng0Y59Z13WE5mL/qTs0Kh7UMbrf1J345q05SNz7ZwjeuXvh3ouPOOf4Ejcei3d1lkLRVkxdYpHZKrZAyuUyI2YShqs5jNIwM0DsPpDjThcNS6kqurvr1h323O0XWLnnqnAmDfnTlF1ZtIFqhZOJKobQKyHVQyr4vXuq29Q0OK5euYd9+y/wnxcrmpc718XKCicnyMl+4uR1brYOGtwOufNk47mNMR3sVMWhffv6wlnKJFxiw0ARU6W75nuSKQMN+63gnaHJt6yE5val2y/Zz5bj4p3Er7BKz0nsk6VlzzOtSLgMG6ZmBjKDNGp6pRHt0kmIbvFbJw7Fv/Dvv3SrHf3y43d81KJ0hpmOgZK082hkJL7SSg2K1Ib71x/46q5aGoiElLIKae1aFXg1g/Q6VnBNaqjh67p1iqqhVLeKysoQz565RKUqEY0bV4Vtpt+Lwv/T0NAUG52mpkbxEFcKHr11Q8uR65C3/hQ4tJ+LSm3/RW5m4rUbuxFPk6g5xU+SDzpOO52i/kjD0sZZroS6vBK2Ngmfw0VaQY7MVvDx1d7RR/9Gpd2UgNSASI3cEZo4xIY71zs2wICBbfhxcob8VitW7OXR9sWL5ePJ2sSPH77YsiXaj0IbCW3a1hHOUi40NsXWU774xldiCfwMDcNrN0+8ZQuZLnM7MaFMFAqxEEOnkanrpKaYLWpeKdU9+nfInz0jD279HoedHRMSWGKBkX+LsCJNKmY5ZiXk3xk8qB1atq7N71Fy59DBS3jr8ol36KEgW3rPlI6zdMnOqM0E8oMMGdxeY6WKlI6UtZAakBqFogLLOG3aBBm4vkzDcvvmg/pVEj7Npm39svz7Sy2yz5WQsKKs8r8VTw8ffPyoqu6TsBo3tjuvaZ4SoFb+R49e4eOJam9ZWmbggnjblhNRXXWIVi1roWChpCslnNj8JR6LOBHXsBJQtpy7+RwlC+dApWK6tTzXBAW99WtfjR87PtJtZ+JvhSb1rl1n+JZ0TKi0TekyujVM/VOQKbiOkpojI1GtammUr8g7P+HSxTu4cCk6QZfMxNZtUr4pmNCQkG9cVXHPUiqiAouc5TTAE4Ijlx5zzWb5pPbIkE63XCMxqDPsqskdeTjD8zdf8YlpDdpCuxIUg/K3QY+SGqdSIGhsqPRKSoE+wwemIVKTV0q8Jl6+cMWmzUf5MUENK0aOii4tk1oQ8WToDBk5m2f34PXdExoKGerV1F5ysy6h0Omp0lvR9e08fPMZD59/QoE8mbF3QR/JlB9tMDVOizVTOqJ+NcUqsf3obf5dW0gIR4oEiCbuLf6zyJmQPnLoEu+vF3sRos8dMx0nOUNBhtRUg6BmrZRq8/HDVyxYsD2qjAyFMIxiwooKGf4NxAxJ0IYMxkbc71UlEdqElcifHaN61RPOfh8pdUlm5TBK7Wfp2IdyPf+vmlOPmj4UbPQ/BOu4m0Dm4Ml1Q/mq5+bujbELD+HSnddctdcGktrlithh6YT2KFpAkZv4mf2dSh3n6bSzQX0MX5+YgQwiWeWX3JhWKRynFmgi79h+EqdFmpYS2bLa8pI2KYHr1x/wXEEya5YvG4vv372xfMWeqDpXdH3QwLaoWSu6NEpqwZCtLDWzp1VbWAMDQ5C7wRQ1M18K6/SmcLkwB96+P3m5GX//YPgGBPE5FBgahqCgMGZdhSMgIBhh4eE8gPQns0io046fXxBPfQoOZr/HrlMAuZ+QC0gB3jMGNkG1CgVRqfM8fo3eq6mJEf83mgLAPW8sUtOGaee/SPPp7D2oC2SZpcPIIBlkKkE3VBPn08W5vLh8TOIrsAhqfEq9BJW8ePsVu0/dwY17b+Hy5Qe/ASTA6N6TeknhB9lszFG1XAF0alQelcrk5YOSoInYYdQGXL6nmg8XF5Tg+ezIVGS0UQ/uv/Y1HL9SkWeT+3vWHsT1G9J1vxs1rIxevVXbwidXyHd1+fJdfkwlj0PDVNM6Wjavic5ddWuEkFKgdl81s6mbcR6e/ijScoaa5ixFdmtzPD05XThLOEJCfvHNLLKk6vRbxgO0l49vhxZ1SsPdwxfdJm3B60+qXY6I9EyB+HB5Lv/9mGgSWJSao5YyTRJR7BbQHzaO51bqnP/O4Mi56MlDmtLskS1xbec4vDszG48OTIHTrgk8CfP+vslcE7p/+B8sn9IB9mUVeW4EPZxZq0/pLKwIEojBEj6stKnI5RHGPiP14NMkrIiyOnTH+dPErAkfwrSBmHO0cuVS6NQlcSrUJgfSCmM/NqQBSRtP6oh1wUoIlDvvpJkRBe1s0bl5JV51JX+ezBjVvS6/HhuxECPiF5unpNXFhj3zQAO5DKJVtEgFjA29gDYNCsQgIdh/1m4s33qJVwuICX3gbFmsUCB3ZhTOmwU5s9uIZmyTFjZlyVGs3HtFuKIb1B2aAuXESC0Ci/rxzZu7WbS7ckwo965YsXzCWfIng0RrLkojGjKkfdSClhoRqejNCQyhagfCiRaYC3m3j19+xkXHl7h69w2cHr7Do2cf4eL6HR8//4CXdyB+/gzlVgwt8DRXeQoNe6G4NDkyJwnSjGKmR0n9K0otourCsSHrQOy1ZDJ5mMzKYSRTVWTRbVsE7uycgPx5VXPJSOiUbj0LXz1/rxFFhaK58L8BjVG1gtrLSuL44B2mLD+KR2+/CFfix7Flg1CtovrrPvaKgGewdj615ArVf6cyxi7vFPFINIcd7Evi4wd3fHFXrT9mX6kERo/pKpwlf65fe4BVq/cJZwqoKSp12BHr9JyasDGRoUxGde3o1n0XNBu2RjiLm8ql8+HQ0gEoxswtbaqImjHTm9xD1GGdNjTIp02VFMi1Qj+jTbB0psawskyHkd3qwOnRO3T/33Y+7kZ1qYM+ravA0ycA/afvwpvP6iZhrizWeHBoitpiQ60E7bsuEM5U+GDAxJ9oqLivWl8whW+LHGm/y90XH9F8xFpU7jQfc9aewoVbL/D+owdv8kiEhobD/ZsvbjMhtXTrRdTusRhNhq7+bWFFePwQF7bGKVzD8vMLxLRp66KEFQ2woUM68kjwMJFcTmXuXUohXz7VxqEF8tnhn6n9Ur2wIozJ6y4CdV/WBXMmeC47vdRKWBHkiPdlGvsXL3+4unvh1cfvuPf8I24/dsX5O69w7MZT7Dl/D2v2X8fBGD0SSTlasvMSirWeiZp9looKKyJdOqo2of7ZaDNADKbjBbBpKhMt0i71oTImYFIs3YDFOy6hw7j/UK7TPOSqPxnWlUcja63x/MM2ZUJq1obTCSKolHyWElgSgyIl4OPjj1kzN+LTJ0XUP9WxmjSpN68PT0nCP7xUPzMJs3LJvGxMbKhNV4H8djBlK3qL5jUwfeZAnXsXplSMJXw9HhJdZ6S4wRSAIbP3CmcJC5mXum7GmbNnKYb/T9XWc1HI4WfAhKFo5OUPod15bGwkuumkFKgQvxgmKTQti9rUU+PVT58Vworik2ZMH4iixRSxNrduPVbzB1CwaHJrzRUXtPU959+h2Lp1Jrp0bZyi61vpiqnER/3CrBBdIP+trw4lznXhPNPcBs7aLZxph6VEWWUfiffIxLYvGUKidVx8JMqdZtKxLGty4/N3cYFlmgI1LBJW06evx3ehIwy1Y585cxBy5VY0+CDn5cUYKStKqlBL9xRKKvatS5IujfiH/qRFCaakJA6fvBoZrcSVHy+pUssymZeBTCb3Ek5V8JJowWMr8SIphY9uoh83xWlY5LOaO3dLlLCiJqzTpvXnJVWUvHP5DO9Y1SzIXNTULFVP8oJElZSG9e6jdCOXlICtSDwk4S0he+SQe5BJ+F04V+G7hH2c2Vr8RVIKnzx9RVMayIeVUpSsIGbjz527OcoMpAao1NEmprAiKDo8NtSQNbk2k9CjDgWBG4n4sCjswPWraiHGlIZUh2dPthiLIZPLPA1kkQai9Vk8f4jXmdK1U0dygxK7v4qYhTQkzNImf4n1i73/xYu2w9VVsRFhbW2OqVP7w5oJrZiEBIfi1u3HwpkC2pGpU6eicKYnJUDmoJgZ/MXdJ9kU3IsvWTOLN5D5/FXc1JUbwN1AbiATrYfqLrGbll3HdtTJDQoeffNefJs1QzIXWBTER2WBnz5/x8/NM6RnZuAANc2KePToNYKCVHdbsmWzRYGCqadG1N+A1CL6ViTVJaUh1fHqk7uEwGJy2iBSHvlVOFfhh99PhIt0ZsieNXk20tSFJ2/dhCNVMhglX4FFDs39e89HtWGngL1//ukrKqyI8+edhKNoGtS3/yud1ikZcwmB9dxFdNqmKHKKdKAmd424O0ouT4M0Xw3S//op+sn9A4LxK1xd5TQ3M0GGFO4DefxaXGBJDY7kwI3r93HkmKKTEJX9HT+uB+8SI8Y39x948fK9cKaAakhVr54yqorqicbSWHxMPnmdcLGJf4J0bAzbZlT3hwf+DOGlhNSQyyLDf4Z9N3C/vyGI6Vpq2w0UBOb5I0A4i4biXxKjqURS8vBldCndmKRjAksiRu+PQo1P1284zOOpqEHE4MHtULS4dB7glav3uPkYk6pVSyOdRD6enuQJVWmQCml48PKTcJQyycp94eqfjfeBEKnSwCSWv9/j5TwOi7YLFU6RWLwWaYBKCdC5Mqfstknu3v745qHuo6NdQotkZhb6sPe6aNF23m+PnOZdOzfi1QmkCGWrE1XmjAmV6mnaVFFSWk/KgfxXYgsoKRIfklkMlq7kymot6p74/EU87Ijxgf7HBRYTdKKF0d9+Eo/zKJJfEZiYUqFM8nvPPgpnqlgno6RCElLLlu2Cj69C061bpyKaNNMseO7efY4AoaidEopsp9QWPSkLK4nF8/4L8bGbkshrp9oaX8k7CYElh4wrVXx2yuTiAsvVTVxg5Zd4sZTE7UeiSiWsJHwGf4K9e87i5Su+sPAyKlRsT1MZFTIZT568IZwpoGqtrdvUFs70pCRsTMQXT+cnqv7JlEj+HOIL6PvPEsGwglIlmIQQ7Uv99oP41mnB3Mm7hbk23LzvIhypQjuFySGA9P7dFzh56iY/ts1oyUvBUK89TZCv6/0HVWdskSJ5kD9/TuFMT0qB6rOZS2hY1++9FY5SLgXzZhGOVHkh0XWa3Q4uo7jAMpDLRWfve3cvlUJcSgrlySLiLktZPP/wDZ5e6psKJKysJVa2pIL6B65avZ9rTFRZYey47siQIe7GCidOXOfhD0pIG2vNm6MKF/SkGCyMDET9V76+QXjikrJ3CIni+dV3uGmj6Jm4wJLLEMFblvOZGWGC13SRjmPi6RPIC87HxsIiHTJZpewUHRIGV+/Qx1bH1uTPzXBFG/Y9+BkUzAVOb2YG5smTXfipNO5fPXHn7nPhTEHBAjlRvER+4UxPSsLWVHwMXr/3hgc/p2RsLdKL9lXw9vkpVVomPNRQHu1097u23FcOuVo8VuivcLx+qy7xqJBf4Twp3yw8f1u8jDD5Dv6UyDpy+DJev1E4VatXK4NatSvw47gg31XMMjIk7Lp0aaTR56UneUKala2puJZ/5qbqopQSKZxXfNPuwxcv/IpQD2lgo9o78OZK7tyKvity2SPhSIX7r8RjlsoWTfl+kcvOr7hGExtjwz8T3vDm9UccYgKLyJ7NFn37tebHceHt5YfLVxQdZZSUKJ4fhQrnEc70pCTId8UsQjVorNKYTemULChuMTx/JxG9L5c/EY6iBRZbiFUzZQWevhGPCi9VyE44Srn4BAbj1j1x53vW9OIrXGIRHByKlSv3cjueupsMH94JxrHarElx/Pi1qGaiBBW769q1sd53lULJIqFd3X3yAZ5+ErWiUhAlhN6isdEQvS8isCCuYT19I/5HyhRWrbGdUjl2RVROw5aZhUkZ9b5715mo2lZt29RFnrxx+60I0q4uXFDNG6zsUEoybUdP8oY2fbKkExdYRy4q8khTOhWK5RaOVLkjEa4hk8nuCYcxNawIkmJq3rz3X70QFKzueKck6MwpvFwycerGM9EkbyNmFkrFwSQ0z5+9w3lB6JCjvHnLGvxYGw4zE5LanykxMTHivis9KRMrYwOekhMbSgo+ef2pcJZysTYzRZ5c6nGclLtMDZXVkMsjwyMj7gtn0QLLK63lO7kcavpmADNVXD+qx2NRik6ZIinfj+XpG4grjuLO9xxJYBaSKbh27QHuMCdTcMDAtjxfUBsoyfnS5TvCmYKmTaqr1cbSk3KQGnO37r3FN2/1MJyURtmi4uWN3n3y5Jt86sj8A8JDFNHTjOi7c21GOLMLHYUzFa5KBKo5lFY0Okjp7DkTpXGqQFHvid1NZ//ec/DwVBQUbNy4KuzstN993bPnnIrvKpOtFVq1riWc6UlpmLCxRj0Ixdh5UnVhSqlUKiluDlL7MFFkeIT7G6L61KmIcxnkogLr7rMoAaeCQ6nUIbDO3X4BP5E+jOTDsjNLPC3L5e0nnD57mx9nymSNdu3r8WNtoB1FJ+doE4HCF7r3aPpXdZNJbWRj2pXYRomP70+cZWM0NWBfUlxmOD0WzQ4ky0Mlk191NsplogLr/otPKiu5ktJF7ZA+hbWLEiM47Bd2nRBfwbKmSxzne0REBDZuPMJNQRI2A/u30VrY0E7ili3H+b9VUrZMYVSsWFw405PSIEU+h8TiePjCQwSFitSISmEYs/FdvoS6SUiy5YZEqpxMLr8mHHJU7lCYPOIh5FALTPru7Y+v39V7oFFum33J1BHrs/Oks4oAUEIxWVK7Nr/DubOOeP9BEXdSrWppFC+pfUT65Ut38c41OtyEmov27ddKONOTEslkaiAee8Um88aDipzSlE75ojlFQ3U+fvESb9wsR+gvE0OVAEOVW/TTecV3NmXVRB2lAlxxFk9jqVYudaR+UBfqG3fEfXW52MqXkEqWv18g9u+/wI9NTYx5zJS2+PoGYPfuM8KZgo4d6vPOOXpSJjS2cmcQXxSdH7pKtnpPadQsX1A4UoXCGSJFlAW5TP4u8NoSla1DtbvErJPzwqEKUhni1csXEI5SPmv2qmifUaRPK5NMlYgPFIoQFKzImWrSuCosrbSr4Eoa4OZNxxAYozNukcK50bBRFeFMT0oko4kBH2OxoTm8Ypci8yGlQ5+uZsVCipNYUJt7CdQmpNosJGVKOFTh9uN3ovFKJQvbwSZDOuEsZXP57mu8fS/aphF5zRNGy6IGqJcuKfxl6dOZoGkcBfli4uz0VMXRTjFXAwe14z4wPSkTenJ5LcQXQ5cP33FFejKnKKyYjChVRD3YnPxXlyTSjeRymcIMiYHanTKKMHQU82N5+ATCVaS1EMVj1atcRDhL2YRHRmLZ9kvCmSpUrjZjAmhZVL6YeiMS9evZa11nnSLaN2w4LJwp6NqlsWTXHD0pA9KupNrLrdhxmY/J1EANZomJ1XN79c5d0n8VYSxTrUbJUJuBnncXfWO/zWvPxIRszFPXxCNt6zmkDoFFHL78CG4SfdHy/6aWRavJZSHQk4JD6zeszI/jgv7dqlX7VEzBcmUKo34DB+FMT0qExlJ+Ce3qw+cfOHBRvXN3SqVRVfEdbDIHRdxXxMvY/itCSmU4IXxX4aKTuOpGtmkaLaOzkzsUbbtwk6gbj/sZKFYmvri+c4PnD8Vua/Fi+bR2lFPJmWdC81TCxtoCg4a0F870pFQowV7Md0Us3XYRYaLdY1IeFM5Q217cf3Xuhni5HLmEL11q9p0Vvqvw8PVn+Pipq29WlulRJZVEvRP7LzzAJ4li+PnMDSHReSlOHj6MFviVKmkXM/X40RscPBRtplL6zujRXWFuHncFUj3JFxpDNJbEeM+0q73no9LnUjzli+SEtZV63rG3TyCcJILSZbLIo8KhCqICKz1kD5iW5i+cRhESFo7LEnl3zWtJt55KaZCWNXPNKeFMFUqKziMx0OLi5QtFNjr5yIsWjVvAU67g8uW7eaAoQf7CgQPbokBBfY32lE5uNoYoxk+Mf9efVkloT+k0rVlSOFKFIg9EfXRyePqYR4raw6ICy81paTD7R6Iz9viVqNI0KjSoWgzUoSW1cPzaEzyRaLia00xalZeChM53T4VvzNDQMM62WwEBPzF//tYovxXd2g7tG6BqtTL8XE/KhZqj0hgS49GLzzh6VbzkUUokbRpDNK8trsycvCruE5fL5FdxdmWocKqCpEOGCZ8jwqEKV++9QVCQeppAtsyWqFRMPBM7JUKSf8ryY0zQqHsESXgUtjTUyQEfwVbMkGDFMzAxSsuL7ElBrboXLdyBL1+jWx41bVJNn9icSihsZSia7kWL2j8rjqb4mu0xKVsoB7JmUvfVBgeH4ZyjeH6kTGZwSDhUQ3LW/AoPvUxbi8JpFFRuhgrhi9GhkXb1x1MKt5644vgl0bqGvJKDLg54mYEB16yI4NAw3iRVDOrcvHTpTrx8FV3MrEE9e3Tt1kQ405OSoTFjLdH78tSVp7idCnoOxqRtvbLCkSrX777BT5EGN3K5/CebKaeFUzUkZ1zA3dVeTDUTDSLdf1bcIdioenGk1aA5pET+t+o4M8tEtVMUsDDkJUG0gWJQbGwUEe0UpkDVFmLj7/8T//67GQ8fKtKgKCC0ZYua6N23JT/Wk7KhUkUF2ZgRwz8wGJOWiRo1KRayJFrWE3dhHL0sYfbKcMPr9kLJwl9xSZfdwncVLji9xE+RSWxrkwH1KqWemCzii6cf5q4XF/hUGbIoU++1FSWlSkVv7e7bdy6qAQbFobx4/g4TJ6yI0qzSpkmDXj2bo7O+802qgJ4gjRWxaqLEok3n8dVLbZ8rRVOtTD7YiOwOBgWF4sQ1cV+4PNJgn3AoisbtrjS5K7gbRhoMZ3dbpe4J7WAUzZMFRUWaIVLMxZHL4mZUSuXJmy+oW7EwsojY4qZpZKCMJb+wuP0OVGDv4kVn7qv44eWHx49ew9PTBwcPXOTdcoKCFPmFFGc1dmx3OFQW313Rk/KgumpStdUevfiE4fMVVWdTE9MGNkEhkQ7Pp68+w0GR+vRyyH8aRob3Df5yR9ykYWjUsKgXGLuFF4VTFfacVm0rpaS2Q2FYmWmXbpJSoAC+4XP3IUzC75SfqfmUuhMXmbPY8MoKSo3J5Z0bDh+5wrUqGqxpDA1Ru2Z5LFo8CkWLpZ64tr8dGhvkPhAjNCwcI+ftR4TY9n4KxtbSDPWqFhXOVNl7Rlx2MIl1zfvOSo1qZlwmIQxk8q3CoQrXH7rAXaRGlik1QWhSUThLPTxzdcfC/84JZ6rQjk8JG0NehC0umjarjgH9W/MKo+TXoi9LywyoU7sCFiwYgYGD2yG9lvmFepI/FCBawlp8V5BYse0SnrhI9ONLwbSqXRomIrWvPH7445JEx3WZTL5TOJQkzilmXXGYeaRhms/sF9VqoEzt3xgje9YVzqJ56eKOaj0Wida4SckYMeFyctUQlJeoS/0tKBLPvLUL+CONipzsRIYM6bRuPKEn5UCTqxgTVlIFIB8++4gGA1emmgRnJZSmd2vHOBQQ6Q6/ZtdV/LP6uHAWE7l3erksB48B1UCcs4RUNJlcLhoXsevUHe4wjk3hfFlRMRXFZCkh03DgzF0I/KnwNcWGBmYuiUJssSGz0MLCjH/phVXqhHxWUsKKxtCAmbtTnbAiyhfNhfy51YUVyYpdJ1VKtMdAdiIuYUVoObsM/mP/VxNN7778wG2RWszkohnYvrpwlrpw/eqFsfMPCmfq5Dc3lOx8oufvgWKtClhK72lNXnIELm7RgcGpif5tq3IZEJt7T97j5UfxenNMmm0UjjSilcDyMcpAqpRoW4stRxVdX2JTv2oxZLbKIJylLvZffIDtR0T7dfAHVdw6DdLHN0NaT4qHnn1JmzSS/pY9J+5gp5TjOYWTPaMFGtcS393edPiWcKQK07xe+zhZiE+oWGinYVHPQgODNcKZCqduPMUPL/U4LxOTtBjQTvtqmimNCcuO8LwvMdKyu1o6o6FoUwE9qRsjQxl/9lLxVs/ffMG4JaqFGFMT3ZvZwyitumbp5ROIExL19GR8Y2+GVrax1lMqbUT4Lrlcrua8Cf0VgS1HxLWsLs0qwVRkpyA1QBUdekzeAk+JbrwUn1UmYxrJgasn9UHPurSNIX/2Ynj7/kTXCZtTRcsuMTJQ96b24krKzuPOvJ1ebOSQB4eH/9LKHCS0nk4ezivI+BStUbPtuFNU1HZMKPK9c8PUlV8Yk88evug1eSvCwsTjszIYyVCKmQZaZu/oScHQM6Znbc6euRgUb9Vz0hZ8/K7o8p0aaVO3DKws1Ps7hDGl5r9DEq3K5DhGaYDCWZzotP4byOXL2Dc15/vXH344fF49cpUY3LkmLzGRWqFk1ZH/7mN2uHgIByVJkz9DKg5HT8pHEYeXhj9rMajix/gFB3FTortxaoAyXEZ2qyOcqXLy8mN8YTJCBLnMQL5CONYKnQSWd0PLu0xciWY+r917jW9bxiaPXUa0rJG6U0yoOuSCDaJFWjm0a1jCWi+0UiP0TGlByiixM0xzYvGm89hxWryzeGqhSdViyJnDRjiLhtLQVu4WraFAqs99n9vLnYQzrdDNwzJjRiRkkUuEMxUeu3zBdYlmqyO614FhKo81WrDtguTOIWFrqjcPUxv0LDUJK2LnUUfM2yreIyC1QIGi43s3EM5UuX3/HR6//SKcqSKHfBX/pgM6SxEfP8tD7IVE38GyXZdFtayiBbKhcRXxvKLUAn3ssUsO4dgFcdOYIE2rdMY0fBdRT8qGO9jZs9QkrI5ffITRiw9JugtSCw0ciqBgPvUkZ/rci9lCLga7I26+xha7hFOt0X3qvJgRJos0ENWyrt9/i8cvPglnqkzo2zDVa1nhEZEYOHsPzl0X7wRCkJ+jnG0aXhtJT8qEQhfKMmEl5bMizt94jn4zdqW6pObYpDE0wMR+DYUzVR6/+IzrD6O7PcVEBvlqHi6lI/GTIOGBm5iIVMt8pnVk/ibxBGHSslpJFKNPTVC4Q8//bWNCS621YxSUvV8hUxqtKjzoSV5QUGgFW0PJ3UDiqtNrPgZ+RaSeRhJSNK9eEsUKZhfOoiHtauGW8xLapdzPQJZ2tXCiE/ESWD73N/hBxiSkCBfuvMKTl27CmSrjmZZFbapSOyS0ev1vu0ahZWIIlGealo1J6tY6UxOUbkMLjVScFUGaVeeJm3iHqdQOFQOY3L+RcKbKs9dfcM5JvMOWHPL1mqqKaiLes+WXkcEyJj3VXpS2cOduPCPqy8qfOxO6NCwvnKVuQgShpcmnpfCDGPIOKnpdK/lCz4aeURm2wGgKBCafVbfJW/8KYUV0bFAeeXPZCmfRkFY1b+NZLgtiw4RVkFGkXNSlpA3xDpAK++gYZGLnYMkeZhXhUhQfvnqhbqXCyJrJUrgSTekidth+1DHVdLXVBGXin775HJksMqBUYTvRhFC6RFoWmRpeIexxKi7rSSaQMlXU2hC5MkiXwqbFmXYDh8zdlyqrL4hhZmqEHfN6I306Y+FKNPeffsSM9ackxrJslZfT8njnJv1WRKehXZUnBvLIQTKZzEi4xKEH+MHNCx0al2eTVPUxm7EPGPErEjceqld5SI3QKnPB8SVkEXI4lMmndj+UkD8rczoD+ITKEfZ3jPlkDz0TSq+y1mC20/OlOKt/1pxIdfXfNDGic200rK7evZzux+CZu/Hxm6IHZ0zYchycNjxN+6CvtwOFSzrzWwLrl5vjT5McDuZsDlYVLkXx6bsPKhXLjdw51BuGkpa178xdBARJlm5OVdAwvvnoHb64+6COQxG+syJGWgMZsqY34DXiA379PYM/uUFLCtWyohgrTbu5lG4zdt4BrD5wXbjyd5DNxhyb5vRAWpEk52t33mDRdtGq6uy+Mu3KeYlkz0FtiLcPS0l4mvAlbGqp1WEmO3b66hO8pVVs0jF1cubgZsLZ38MuJqTbDFuLH97SCwzND2q0STE++tCHpIfuOd37QpbSZY0JSmRuN2Jdqo9gF2PqwCZ8Dsfm168ITF15nM/92JC/OwwG84TTePNbGhYR9ulOkImdPVOeZWptib/7BCBvVhsUF9n2pKqkN++9xedUnAwqBiVMH7n4EJVL5kUWW/UuPEqonXl2pm2FRei1raSCmpyWZlpVXOEmVCKm5dA1ePrOXbjy91CxaC78O6aVqGvj0Nn72Hxcok4csNDfaelJ4TTe/LaGRRhERCxnU0q0lOCsDacRFKxeToM+78IxrVNd41VtcGNCq+GgldhxVHPNMtqRIodvWVt9QcDEhBYHusea+gYqoeJ7DQasTNVVF6QgV8aCsW1EhVXAzxBMXyshj+RyD1lkxELh7Lf4bQ2LoD5ipjkcApgYbSpcioL8VJHhEahRMbqJqBIqP/OTfVDnZx+EK38PFAF99tYLvP/oiZrs3hgZScenUdwPaVuGzEbxD5ND75NPGGgNyGNuiOJsUSChpQmqwT52/gHM23L+rwgIFWNAm2ro3Ey8IxZtPJx3fiWcqSKXycb7OC+XqC+jGwm3bBedZmRp4f+I/UG11s9UxO/mtrHIk1M9ZiMoKAwOneczU+nvW7GU5Mlmgw3TuqJcibgbd5CJ6OIfAfegSL4bq0d3aNDT5kY+JqyMtViyqbsNNYxIrTXYtcEukyVu7RwPMzMT4Uo07z56oEq3haKhSmyIvvT1My9NKX3Cpd8iQTQsjue1CNPslVyZvtiZnakIQsqxe8c0iXYNy6mpk7TTUNAuEw5ceCBc+fvwDQjGnjN3IY+Qo0KJ3DDUYCbTj2xNDXgIBAmvoHC91NIWGnm2JrT7Z8g11rjMP9oFXLr5AgbN2YMffoqWbH8jBmzOrp/aBUUKqHd6Jwf7wOm78fazmDCXR7L53ivkwTxx1SseJJzAYoR8cXYxsbOvJIOsgHApig/u3iiaO4to6+q8TPP65OaFZ+9SX0NJbaEYHgp9OHvjOUoXyoGsIm3xY2LEzEMSWiS8fjEbUS+4pFEKquJMUOXMYMCTl+Pi8cvP6DJ+Ew5dfvRXxVeJ0aZ2GYzspd5/lDh15SkW7xAPY5BDdtbXcel04TRBSFCBRaTPWekee6P92KGaU+bO0w/o2swexiL+GofSebHv9D38DEmd9a61xcMnALtP30FgQAjKF88leq9iQtvwJLjoiyJIgpng0osuBSSXqC8g+ajsmKDSJkwkIDAEc9aewvB5+/HNS2PX9L+CTFZm2Lu4H+/oHht/Zhl0HPsfAoPV4ynZGAyKiIxoGfbFWT2C9DdIcIEV/NnZyzSHgxFb1moIl6IgB7y/XxBvARYbuiEFcmbC4UvSuXd/C7Si33n+gQnwu8iRyRIFc2cS3ZmJCWlcmZi2lcOMWubLmOBipvhfKrlMmGDKmcGQaVRpkJUJLG00KqqMefLyE3Qa9x8u3X0jGkv0t2HAxtS6/3VBycI5hCuqTF1xHNckMlZkkC/yc1p+QDhNMBJcYBEZ8pW9Gxlu2IXNMrVkwidvv6JaqXywy2YtXIkmf65M+PLVG09c/l7TMCa0ch2/8hg3775F4TxZRHMzY0Nzk+o0UaS2hTHTuti8C2X/S+3Tjz435WQWtDDkQZ/WJjJ+TRuoXVu/qTuwcu9VBIhoC38rneqXx4ie4qag8yNXjF1yWHxcyeGaHrKO/m5OCZ4FruUj1R2ryqMas2XqJHsJtdfInyMjrm0bC1ORaFlSM2v0WCyai/Q3QyENLaqXxKQBjZCPCXZdIB/X96BIfAuOVIRFpBLpxW4Jr0uVRdiE0LWS6/vPP/Dv+tM4evUxM6f1GlVM8mS1wbXtY2GWXj25OTgkDDXZHJVytLMB1tTHefkZ4UKCkigaFhHy2cnFxM6hKBtTavaft38Qgpl5SHl1sTE2Totyhe2w7+y9v97ZGRO6FS8/fMe2Y45wY1po4bxZYGmu3lJJDNI0aGJTJDeZjIogVBkTZClPeJFQsmaaY64MBihilYZrkvTZtNWmiA9MUE1beRwjFx7As3fu+vCQWFDNut3zevMGMmLMXnMKZ26/EM5UkUN2wNdp2W+n4EiRaAKLyJC17M1ImWEfpmSZCpeiePDyMxxK5EGu7OqdNrJnsWJvTIbrD/6Oig66QJoAFfWn5rUu7z1QgGlbNpZmInqsODSxqV8iOaNzMuGVkWknSmc0+bySmwCj0AMSSOSLys/MvYLM3KMYKl2FFAklFybwp688gdGLDuLhazfRek16gAk966FdY/G6dY4P3vH7Jyrk5fIfv2SGTakognAlwdHhkccPS/tRndlk2skO1V6LHMo3d4yDeQY1ecZjt9qPWI+rD94KV/SIQR1LapQrgBFda8O+bD7JShDaQPOXwiN8Q+Xw/yVHIPuic9p9TOypTYOD3jpFnFMunzn7sjSW8XMy/eILjSPnh65Ysesyrtx989fUq4ovNcsWwIHlA0RjASnav3r3RTxESQQ5oxvTrnRuLKELiS6wgGkGVg7+1DFatDxDu7plsG5GN1ENwcMrgN8g2urXEzcUgNu3TRW0qV8WVpbphau/B62kYUyS0a4jCS8Kmwhlc54c+eQbo69w9nMSdlJCjR4tPd+07H9k0lFVEmMmhUizM02jEFL0nXY6tdUU48LH9ycOX3iIjQdv4s1nD+GqHk1ksTbHtW1jeMpcbGjXdNjMPdh97p5wJRZy+XEfp6Ut2ZNO1LUtCQQWYFN5XLbIyF/P2Gi0Ei5FQW9g7T+d0V6DCtpy5Dr8+gsqlCYU6YzTolGVYujStBKqlMsvWrcooaFRqrSwlN+VmhGt1QkliDRB5U1u3XuLnSfv4OztFwgK/btj+nSB6rMfXjoAldl4EePwuQfoN2OnxKIk90obGVnMw3mFaAGEhCRJBBZh7TC6nRzyfexQ7TXN05ngypbRkk6+NTuv8IqOenQnk6UZWtYujWY1S6BSaWYyxpWPksIgk+/u4/e8ZM/J60/xzVuvjceHWYOaYUg3tQpRnI9uXqjRcxH8xQtuMvVa1snHeQnN7UQnyQQW+1wyK4dR29lLdhUuqFCqQHac+2+EaFcdco4OnLYTB/VBpb9FRvP0qGNfGA0qF0X1CgVhbZUwZmNS4+sbhOv33vBqF5ecXsLzL87zSwjasgVt/Sxyy6iLg9DQcDQZsAIP3oh3wmJKyG5fx2U0pxPVFFSShAILsCo3wQJGYZTlnFdxRZVezR2weGI74UwVqqnVZOBKybbXenSDElppkahaNj/sS+VBuaK5kMnWXPhp8sLzRwDuv/gI5yfvmaB6iycuX/RxUwlEqfzZcXr9MNGYSPJfTlh4EP8dvS1ciY38vSwiorT3nZVJlsOUpAKLsK40ppLcIOI6e2m1O0RvZt0/nSW3VL9+90XdPsuY2q/P8UoMcme2QrliuXiF2OL5syG/nS3sstvwFI2kgMppU937t5888NzlK568/oIHLz/hgz6IOFHIYp0BlzaNQtbM4hkUB07fw8DZu6X8VmGQyWv63F6uuQplApPkAouwchg5lr20aAXCdCZGOLt2GIoXUi+rTDx6/gnNhq3565OkkwpjZqLny2bDK2rYZbZGjqyWyGSZAZltLWBlYQozE2P+zGiFpiKEsQsRhoWF8y/SkClCOjAkFL7+wfjm4cdMuUC4MQFFZbKp/JDr1x+8n6OexCedsRFOrBqEMmyBEuPpKzc0ZBZNcNgv4Ups5JN8HBMvQFSKPyKw4gp1yJXFGpe3jGITQtzHcvbaM3SbspWZBfqYmj+Nwu0hUwwkqdHElmjFKi3nZoaePwvF7v03vSua1y0tXFGFmqTU6b1Usqgme4pnfB2XNeGHSUzi73eLck1unK/SGVm4rD0b5GqhDn6BwXjw7BPaNCgrGsBGHaQzZkiHC07irbD1JD00ckkYiX4pfkVPMoDWlFlDmqFrC3vFhVhQ0cKu4zbhmatEAQK5/GMkZA1C3ZyChStJyh8SWOzGfHQOMbarfIPdge5sfU4rXI6C+hr++BGA+lWLiu5elCmWE+FhEXB84ipc0aNHT1wM71gT4/o2EM5Uod34iQsP4fj1p8IVVZhmFWwoi2zs67T8nXApyfljAosIdXP8ZpLT4SMTR63YqZpUevzGDRlMTVChZG7hiirVyufHt+9++p1DPXq0oHOD8pg/XrzrDbFu9zUs3nlJOIsNxbrLBvg4Lj8lXPgj/FGBRYR8dnpiYudgwW6hg3BJhesP3qJI7iwomCezcCUauvH1qhTFW9dvePUx0YNs9ehJsTSrVhzrZnSFgYF44PDJy48xYuEBbsKLI1vl67g0yZ3ssfnjAosIydfgkklEiAMzDfMJl6KgEjPnbr1AtbL5kV1k+5W23KnH/+MXn+D6xUu4qkePHiX1KxXBln97SqZo3X3yAV0mbsavcPFNLKZbXfL9FdQd7vf/eH5cshBY+Hgt0jh3mZOQG7ZiQkut3gz1gTt97SkaVikGGysz4Wo0VKGgWa1SvHLk+696oaVHj5KqpfNhx4LeMDFRcxNz3r7/jlYj1klWWmXC6k0kZA1D765OFukEyUNgMUI/3QtJm73iOQOZAbUJU6tMR/Eg524+R/OaJWFupl6OJk0aQzRmmpbjQ1feWVmPnr8dElbUQCKdSBQ7QYHYzYashodPoHAlNvIfEfLIOgHOy5ONkzjZCCyCOmyY5LR3hFzWSSZT77rj/zMEl26/Qsu6pUUfAgUtNmeaFgW96TWtvwPSrs3YWAj9pa/mEZO4hJW370+0GLoG78VrW1EoShBkaObvtDxZJfAmK4FFhHx2+mSavZILIGvFbpiah9DL/yeu33mDFrVLw1REzaW2WGQePtabh6maDOmM0bOZPdb80xkOpfLi8KVHwk/0kM+KzEApYUWtzFoxYfX8/TfhSizk8nCZgUEP39tLTwtXkg3JTmARIV+cn6fL4eAPmbwB7QUKl6P47h0AxwcuaMU0rdipIERaZh42r12K2+evP+qLt6UmKFVoSPvq2DqnJxrXKIFbbBws3Hxeg1nzd0G7geRgl/JZUdXQDqM24P7rz8KV2MjlbMKN83Fc+p9wIVmRLAUWEezm5GySw8GEiauqwiUVvv7wg9PDd2hZhwktkZI05NNqUqMk3L/54qm+bViqwL54bhxaOgCtGpTF45du6Dp+EzYcvqUXVgIUZ0WhC1K7gSSs2jNh5fT8g3BFHSau5vs4LZsjnCY7kq3AIkIc7K6a+JlnYUKrnHBJBXKuOz10lRRalNbTkK04IUG/4PxM+iHpSd5QvN2ozrWxdnoXWJinw8zVJzBywQF815fO5pAJMrxTLcwf10YyzipKWGmYB3K5fKOv09JRwIxkm02VrAUWXryQh+RrcNY0IiQveywlhasqkNC6fd8FzWqWhImxuhpMg71GxYKwTGeCq/eoo6/wAz0pAurHuGBkK4zsVRe/foWj58St2HXmrj4/UYASmSk3kNJtpCLYyWdFZqBmzUq+z9fJohdQK1nf2uQtsIiP1yJDTCqcNk1nUJwtJYWFqyp88fTjjvhmzAQUK0RGD7J8idwoljsrzt16jl/UBkZPsoem3z99G2FQl1o8z23Q9F04cUM8z+1vhErErJ/aWTKRmaDdQHKwS/usSFjhoK/dl854sSbZT4zkL7AI7zsRIeYNjpgah5Rg0kdUaH3z8udxWo2ZCZjBzES4qgql99SqUAgXbr/gbeD1JG/qViyMhRPb8QVnz4k7GvLc/j6o+N7Bpf1R0150OnAozopCFyR3Awm5/CQTVm1x4ECKiAtJGQKL8LzGhJbdEVOTDMXZ2qveMprh5fcTJ648Qd1KhUUj4omsmSzQpm4Z3H74jgs5PckTKgp4YEk/WGRIh59Boeg8fhOC9EUbOVTW+PiqwSiQJ4twRR3aIaegUKk4Kw4TVj7+Fm1wbU2KqZoobvQmZ8r1T2tllH4vO2qtuKCONRvkexb2lazyQFDdnxGz92D/xdTb2GJ01zoY3KkmvL0D4e3/E74/g3nwbeDPUFy89QKnHcXbjScH+rSojIUT2vLjHUcceWKuHkXDiOVTOoq6PpRQbmCncf/BOyBIuKKOwgx065hSNCslKUfDUuJ+PzIkX4PDphEhTBrJSglXVaA0noPnH6BwzsyiVR4IipBuUrMkd8bfeOCSKpsaOD/9gDPXnkJmKOP1wyqWzIOi+bOhdBE7XHR8iWfv3IXfTF7Qs9kwrQuvOEubJOMXHeZhLEos0pvwRHhq0Z/WwOCv0Lyob+D0AU0xc2QLpBXZEVdCVRcokVkqN5DgDnbyWaUwYUWkPA0rimkGVvb+K9gnGCJcUIN2UGYMboqBnWpI7qAQFBrRZ+p2uKdiE7FTg/JYPY3SNBWF2oo2nQYPX/H4JeqoU7awHc/bLFckJzOjLeHNfvfNJw9cvfMGp28919oHaMieQQ7277NntOA9EX0CguH65YfGmvzF82bFtR1j+TMLYBphEfZew8Ij0LRqcfRvVw1lS+SKCmOhvoRUXmjZjks4zCZraiybTR2Z/5vRVbLJKUHPdN3uq5i67iQ/lkIRumAxEJiRIm9UChZYBO91OIsdTGIfRTQAheRUz6b2+HdMa562I4WnVwD6T92Baw9dhCupi0WjW6N3W0UM7os3X1G15yJ+HJusNuZYObkjatkX4gP/GhNQ95imZsa0mgZViyJfrkzwYibmhMWHceTKI8nwgmxMQPVq4YAuzSohU0Zzlc47FBP034GbWLTtAoJC1ZscDGxbDf+OppqOwKu37mgyZBU2z+rOu1iTb+bDFy9kY0KwWMFsPEBYyVWn13zh8Qn8I9V7E4WaZQtgPRNWYu3jlZB7YzJ7HltOOAlXxGCiSi6b7+u0ZDKbFSnWnEjhAosjs7QfOVQG2VL2aSRNXEoG3TKnh6QznqA2U8u2XsRCNpFoRU8tkNC+sXUsihbIxs/X77mGSSuP8eOYFMyZCSdWD+GTgzrc9J2yHWdi+Lko5WnOkObo26EaDX/8u+4MFu+4KPxUAZkuQzrUwLg+DSTTQ5TcvPsWrUatV9OKlk1oj+7CVr3zg3cwYCaieYZ06MeE0XNXdy4kaeCWYObthhndVMz+W/dd0HrkuhQfukIa5NhudTCqVz3RvgZKqGFE7ynbcPOxhqrFlBvILGtvp2XL6ExxMWWS8nxYIoS4Od1JZ1f5JZtEzZgZIapGffrmg6OXHqFqmXzIzFZ8MUgLqFw2H2qwVe3mAxf4ppKVmhKF/zewSVTKxrJtl/D2syc/VmJmaoxTa4YiexZFT5AZK09gz7l7/FgJaVyX7r5G+SK5kNfOFlWZxkOVMVxi/K3m1Utiwfi2uP/sI3+df5YdxZLtl3DmylP+GiRclOZ5zuw2XGN6GWvbvRfTykiTI7JltkR69u/q9VumlsxOOaWHLzxEi1olYWmuqEiUM5s11wDvv/zEz1MiebLaYPe83rw/p6aekHTvWw5bK90wgsGkUxAlMifX3EBdkRbdKQxvxyUHZHKDeuwRSe7jUv876rW27+RdriFIUaFUHlzbNhadGpTj/pyUTuHcWaJ2lUiLpC7Ksenfpgpy22Xkxz98ArFJotsvCa3/Me2Mbh9NpgVj28A4hllGDQwa9FuOpkNXY8txR7xjQsaDktWff0CvaduxePN54TcVVGb3OjZC0zAOpZpsP+bEhZMYtBM2dPZelefZr11VHiGf0qD7SfmA17aP5WNQCvqo1OSUxrJUKy4F8h/M+mvoc3vJPuFCiifVCCzCx3nJzfDItPZyyN8Il9QIDv2FwXP3YMy8AwgR8Z8ooeDTVVO7YPvsHshsJe0/SAlUiNEs8/NXb3yP5WwnodyrVRXhjJlhj1wRqqGh6csP39nqroicJo2sTd2y/Jgg8+4B+5nUcrB0xyUEBoYIZ4Cpsfr2fPAv1edyxemVcCTOrSeuuPPovXDGNBSm/aW0Z5bJyoyNtZ5YNa0zzNIbC1fVCQ0N5+3jqSOzdJNTEmryN+GRkZV9by+7IVxKFaQqgUUEOC98GymXObAZc1m4pAatUFtPOKFR/xVw/aRqGsWElKvGzNy4tWs82tYuk2K1rcql8wpHwJ2n6vlktIuXLUt0vXwXDfdEyYPn0SZXkxrFhaO4CQ0PxxdmniuhncfYfPiiqiSTPy0uDpy/LxwpNJWiebMKZ8kbGlM0thx3TUDjmiWEq+J8dPNCkwEr8B/TfqUWBIIJq0uRkDkEOK94K1xKNaQ6gUX4Oy319vE3b8Qe3Sp2KvlsqT1Yrd5LcOjsfS7EpLC2TI/1s7phz/w+sGOTOyVBTvAKJaPNi7siAiuzTYYovxLx82fcIQvffKNNtGL5sqn8e02kMTRElkwW/Jha2B+MIWiUUHu3mOQV/FmaiC2ILdkzS+7QWCJf1YbZ3WCl4f2SuXv43APU6LkID2LdG1X4KF7p+yuoEc0BxbXURaoUWJwXM8J8HJcNZ8+wPzuTnIEBQaHoP3MXhszYpXGi0nysV7Uo07YmYGiHGjy4MSWQxcYcGa0VO6M08G+J7iapChtjY+nwDyVpY3x+Eujaap8N7IvwEjHEyh2X4eYZHRCqxOnJe4TH2KWtUkatmZIa370CuH9OyVd3Tb6dPwvFplHoxq2d41G/WjHhqjgUAjJs5h70m7ET/mysSkFNTplW1cfHcekI3N8gbSumcFKvwFIg93Fa9p8BIqqxY8naGrQs7WUrfbVuC3kQqSbIvzBzRAtc2TQKDsWlHaPJBfJfKbUfSslx/fyDH8fky3dfLsyUFNBCo8lhq9hN5GgprMzTmWDW8Ob8+Nz1Z5i35Rw/jg1Ftd++Hy1YG1QtBhMN0d1ETCd7EJvYTzXsnP1JKhbNhUv/jeRxZmYSSfpKHB+8Q/Xui7D73D2NJiB7eB8NEVnDz3HpFjpTXEydpHaBxfFyXHE3PNy4PHuwJ4VLonz45o1mw9Zg2orjCAnRvEgVK5gdJ9cPxfr/deZR3MmVyqWjtZPHrz4jLEI9vuyrlx9evI2e4JXL5ueliDVRMcYu1i9m2rEVXjgTh0zTLbO6I1eOjDh77Rn6TNupkg4Ve1dv4ZbzURHbFBfWrWklfixFXvZ3lfFK526+4JpzciIb03TXTemEMxuHo2ThHMJVcchnR2Ow+fA1+KApeZnB7vuZCMjK0hgXLqVq/gqBRQTcnefl42TRgj3h8ewxS3pxaZdr5d6rfGW780iztkWaS7tG5XFn3ySM71mPxxklFyjUwNrMFHUcosuPPHghHZtEddGVkAnZv3X0rmFs6lQohDxCCATx3dsf8hjCJzamxmmxfU5P1LQvhI37rqPblC0ICo1+BLSjd33zGBWz8vYTV+w9eUc4A/4Z1AQF7WyFM3U6N6nIv/v6B2Ha6hP8ODlAHX3Gda+HO/sno32TClHarhS0Q1uzx2I+BjXnt9IYlk/ydVzWJLX6q8RIFYGj2nNNHuLmdDtd9koX2EktNnqsFdfV8WYDf/eZu/Dx/omKJXLDWKSaqRIKyKxargA6N66AgIAQvHD9xjtW/wmqMY3qyubRmDKwMYZ3qx0VUElcuPUSjk+it/9jQrt1draWKFFIsfpTAO3zV1/g4qZqQpKjeNvcXrDIEN0b8orza5y4Ll5Yz8YiPfbO78OTr4fP3osVe64yRVf4oUDP5g6wZxrb+oM3VfS0a/feolKx3DwYlNKqGlUrjht336rVcG9dsxQmD2rMU1T6/rMdDzU6ppMG0ii7NKqIHfN6887kUnXWlfgHBGMq06rGLjnMyyRpRv4eMnlzH8flVLXkr0I750MqxLbGYLPwUOM17A50Zaca7wPl1y0Y1RqNa1H9wLhv2ftPnpi59hRO3XiG8D+QjEvmVf7stlwIlC+eG2WL5kT+XJl48vElJrT+/e8sHolMatpI+HdoC/RuV5WHBpBJdv76M1y885qbyEXzZUW3Fvb47umH/DHSYagS6D6R3b5iebNiBxNu5BAfNHMXN7ljQ76pWzvG8fdctsNcNUGfji0US8a1Q9uG5fh7Imf8HqZ53bjvwkti17UvjGZ1SuHD5x8YPHvPH6/dT/eQov0n92+EvLmkNUIl5Ds8deUpJjBB5c401Thgvy3fYxARMcj7zsq/spjbXyuwlFg7jG7HBs1qdic0ji66UWQKzR3dKiptJC7eME1r7sazOHWTCa4/mNtG7z29iRGqlskPh9J5UZEJsYEzduGjRJR0+SI5MbhjTS7wMtuacyFNQbYvXdyxnpl0FZjG2YcJNYLqhRdrPh2BMWKl6Pc7/L+9c4+Kukzj+PcdHO4OF0HEG4GCindEwUtopqmlni2tdu2ypyx3WxfdsnLdPzSPe87WuuGquVure7b2ZMftWFqRaZaJmoLiDVFDQ0EEkvtV7vPu87xAIcLwGy4xwO9zzgwzPwadeX/v7zvP877PZXYIotY8pizOPQfPwtnFQVllni6Oqigfl45xd3dWlhMnMN8gS64pwapn6pgA/PbxCCXA9fmg+QUlSLyagT1fncOuL+M7dYy5MsicySPwx+fnqvVNLSSnZmHNpr30hWA5MLYWmQuzYXl+XNSH/KT2WM+jxwsW0zdshU+VMOygK21+3aFmYVOfwxpWPH0/TA3cIkuwcL2x4wD2fZvYpToU8/Y7C4qJxC6vtFw1gWBrk9dj6pt0vrPrCNZs2aseM2wRvUHW6JKFYVZNrpYEqx5+T2wpMtXV5rsSp39ueD7MJ1f11WfnIGhI8xVAG8Ilc7b+9xC5x99oSbIno0p+ZpTmZVlxW27VHeux6IL1I5KrPjwlIN4k4fppRbkZvN1d8doL85Wr0tL6RD1p6XmqbtPur87Y3C6WFthy2rH2CdUXkOFKAWG//Msd5VxG3OODbz9YXfesFnYtK8hCYyutkkSvnG4cYsFxb1z+uLSsHCkZeVj3dvRd61u2Sm8nB1Vqe+VT98NvYJ+6o5apoi+rPV+ewWv/jMYPzeRG3oGUOTQcfyiI3fQBjX6PtaoaogtWI1wmr+prhHxLwLyIhqfFXdRg/37YELkQM8KGqQtaC4VFt1U9qPc+jcXN7IK6o7YPJ+ZuXbuEPmftbuoza95F9NHEut/WwrXYueVaTm6xuuUWlaKwrAI1ddYQB3d2xrpee8EhLE8vCMdzj91Lbu1PGxqWYME+cuoK1m79FInXtFR55T1XsbsKhsjSE2/qrcsboAtW0wiPsJVzYRDb6GGL0aF8AU8ZE4D1yxdgvArUrPtFC/A37ueHE7B99zGcuphq0xdyRMhQfBi1DPbkIvJC8YZ/fI6/72w2XbNbwetTocF+WLZ4msottddoUfM4nb6Qig1vf45j56+p5y0iQS80/z4/bvN+9UznDnTBsoDvhHXOZcbCtTRKK8hVbHHBinexZoYGYd3v5mteeGV4Hn+fcgv//vhb7Pn6HLKbKV3cGXBs1JK5odi4+lG1nsW7dOvfisa2D2PqXtF9Ybf/4ZnjsHTRVAwlV1frFxELU2JSOl7fvh8HYi9rCnGhV9wWkJtdpNhwM3ZT9ymZ2s7ogqUBr7BXAqsNVVtosB6gIWvRTeSF4VkTh+HV5+ZgXPAgza4iw+s8B49dwvvRcTh69nuUV3ZOByZ+x0MHeSurcc69I9VnyMwqQOSfd+FQfLPVe7o8jvZG3Dt+CJ6cH6ZyR5vqJt4cLFTnL6WpKH0lVBYDP+tR7t+BGnPNyu5YXaG90QVLO8Ij/MU5UiCKBq3JvoiNYeuESzO/8uwDCB8foITMGnhR+5OvzmL3wbM4k5SGqg4u28yxUG4uTir84YmHJuK+ycNVyAEvkL+35zg2vnsQRbd/qmXVXeDSzyHDBmLx7BD8YvZ4i2W0m8JMrjznPr753kEcOZuszfUj6FWXaYq8nH980766QzotoAuWtXBfRKPzUinEazR4TfcQawQP8tjAAYhcch8e4jUQcq2sJeOHAuw7cgGfHDqP+Ms3LBbYsxbe8frPhl9jiJ83Bvh4qLAB3s1jt4ZLEO/aH2+xx11XhHMlOd5s/owxWDhzrGqway2VvAb5TQK27DykShVpRsosmj/rCwpNO7iqSN1RHQ3ogtVKOFK+qsJ+FT1cRe6S5vKW3E3muUem4skFYfCy0AnFEnn5pTh8MglfHE3EN6euIJ/ERNt3etNwqZiolx9FUUmZKrl76WomEpMzupVI8UT36O2M6aGBmDdtFGaGD4OnlZZUPbn5JXj/0zjs+OgY0hv0S2wJsryK6X1sFuaajT01Ur2t6ILVRlynv+TVq1L+iWbjCyRcluuFNIBTUhZMH4OlJF6TxrW+TA0HTyZcTsMhErAj8Vdw8mJqt+r40xaUFRU8mEQqCPdNGoaxIwYqF7c1sJcXn3BdbYx8FnPBYnnixkjIMgHxdiUMr+thCm1DF6x2os+U5f3NZuNqmtfLrBEuZrifj1rkXTwnRPXwawuc83eaROvEuWs4eeE6Tl+60a369FmCq1OEBPupZPXJYwMQOtrPYtK6FrJyirD7wBnsjI7D5VTrAs1JqMhEFe8Yq+3+mn3qb3e2BtJpFbpgtTOc5lNpMKwSUjxPo2tVPWVOnJ01aTgenxeK2VODf0x/aQtsGVxPzcIZssLOJd1E4tV0JF3/4a5GFF0NbzcXDA/wxejA/hgTNAATR94Dfw3JxlrgAoBc2WLXF6fwNVmu1sfHyUISq3fszTJKT6dpX3TB6iA8Jqx2g33FCxJiOQ2y5YptTcDJyg9OG4XFD4zH1JChcHZu31pbHIXOicNXU27hSlo2rtMtNTMfmdkFuG2Fu9ORONsb4evtBr9+HvAf3BeBA70QFNAPo4b2b/X6X3OUlVWqaPS9h86Ty5fQZEfqlqDvhpsCcptBGLflHt+oIfdGx1p0wepoJiwzuhtdfkUDHUmjHVp31Co4oXje1JF4KGI0IiYGtnqxuCXYGiPLADk5xUhNz0E6uUOZtwpUIGt2XrHqV1hQXIaisgplhZSXV6KULnTexi9tQeRYfDhsglN3HOnGAmxycoB7byd40efhqqJeJhf4+rirmluD+/eBtxeLktAcsGktefR5jsRfRfThCzhw4hJKNXTnaQIestN091aBg9tOxKzvnMC5HoIuWD8fwmPKynBpFito1BfSZagtEa0R7DZyXfAHI0YhIjQIw4f4/li94OeERape4GoP1P5olrqZRp9bCZA1wbTtBecxfpecicNkSR04ehGxiSmtToeiz10GKfYKg3lr/vHNseqQToejC1YnYAp/0dMOWCoFnqEToCkItSn4mvd0dcasySMwjdxGrl91T4Pa5j0dFqjU9FycTLiuROrruO9UqAYLbWuhv00SQr5bXV21vfjUtjt75+t0OLpgdSrrDB5TCsIgDb+hS2EBnY5mSzZrgSPrPXs7k+UVSOIVgAnBgzFksLfmul1dHS4znHwjG/EXUxF7/pqqSsoC1fZy1TKPzs1npFbb82PdTgDru265iS6OLlg2gt/0dY5FlQUPSymepLMyo7UuY2M4Fimgfx8lYKODBmAkuZDcQEL1ErQyVchW4FQYDp5NIevpYnIGEpLSlRX1fXpOu2UAkMtXSncxZE297yINe/WEZNtAFywbxG36Sne7CsMiM+TjdIomk+HUrqvsRjs7uLk6ItjfFyOH+iKArDAWtcHkTnqanFW/PM6v60y49A43EeWGDGkkTMl0453MS8kchZ+JIq6A2kTLsrYgJYmUwFFpNvzPTlZ9rEej2x66YNk4npMiTVIY5kmDWCSkmEFnjKuhdth54/ZgTo728HF3xSBfErEBnmr3jlt/eXq4wN3ZCSYXR5hMTkrYOHLcWGepNVd5lcVH/STLiMvTlJSUo6ioTIlOfmkZcsla4h277MISpGXk4UZmnooT413Iio6O2pfIlkIeFsLwkQF2+/RwBNtGF6yuxNxIB898wzizwfAInbhZZBEEWxtV397wbl9923q2yhpPKF49qq8yUVVDNmOb15PaiATXpr4sBb4Uwrw332Q+g/1bu1696h6KLlhdGNcJL3nZ96qJIAGbTUrA617+dEZtp5urLUACRRYU972PkVIcrHEQR0tiou7u16/TJdAFqxvBidjG8pqJUojpZPiEQ4qxENJEp7lnxDlIaabPWkSz+hxZcnFCypgqR7tTukB1H3TB6s5MWGb0Mrj61xgxXprNE+lsjyERG0VixutgbcsK7lzYr6ymuzwSqQR6nECuaXy1ueZ0cXV5Ck7/yzZyi3TaHV2weiDsSjrYV/tXm3uNFEIOo+s/kCZCAE0HrnPTm6wysshI1joVKUlcyWKSvFOXIiGSabZeozf2nUBNYoWdTCk5tjW79rU6PQVdsHTugJO2Ra/y/jV2hn4kF4NogviQJdOX5ItLIXiSq+VBj9nNpJs0SSns6bmmsAuSoBISyEr62yJSo2Kykwrp3y8gbcyl51lCimySykz6/9J7oVdGdWnlrcLzm7tOHzSdDgb4PxbwcqYEyZ0hAAAAAElFTkSuQmCC'
             style='height:38px;object-fit:contain;background:transparent;filter:none' onerror="this.style.display='none'">
        <div>
          <div style='font-family:DM Sans,Inter,sans-serif;font-size:15px;font-weight:700;color:#FFFFFF;letter-spacing:.02em'>Kit Atama</div>
          <div style='font-size:10px;color:#8FAECB;font-family:Inter;margin-top:1px'>TürkTraktör · Gazi Üniversitesi</div>
        </div>
      </div>
    </div>
    <div style='height:1px;background:linear-gradient(90deg,transparent,#E85C1A,transparent);margin:10px 0 14px'></div>
    """, unsafe_allow_html=True)

    # Dosya
    st.markdown("<div class='slabel'>📁 Veri Dosyası</div>", unsafe_allow_html=True)
    yuklenen = st.file_uploader("Excel (.xlsx)", type=["xlsx"], label_visibility="collapsed")
    if yuklenen:
        prev = st.session_state.get("_dosya_adi")
        if prev != yuklenen.name:
            st.session_state["_dosya_bytes"] = yuklenen.read()
            st.session_state["_dosya_adi"]   = yuklenen.name
            if prev:
                st.warning(f"⚠️ **{yuklenen.name}** yüklendi — eski sonucu önce kaydedin.")
        st.markdown(f"<div style='background:#e8f5e9;border:1px solid #86efac;border-radius:6px;padding:7px 11px;font-size:12px;color:#15803d;font-family:JetBrains Mono;margin-top:4px'>✓ {yuklenen.name}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='background:#EEF2F8;border:1px dashed #9AACC5;border-radius:6px;padding:12px;font-size:12px;color:#6B7E9E;text-align:center;margin-top:4px'>Dosya sürükle veya seç</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:1px;background:linear-gradient(90deg,transparent,#E85C1A,transparent);margin:14px 0'></div>", unsafe_allow_html=True)

    # Parametreler
    st.markdown("<div class='slabel'>⚙️ Model Parametreleri</div>", unsafe_allow_html=True)

    b_max   = st.slider("Maks. Blok / Kategori (B_MAX)", 2, 15, 10,
                        help="Bir kategorinin en fazla kaç bloğa dağılabileceği.")
    max_kor = st.slider("Maks. Koridor / Kategori (MAX_KOR)", 1, 4, 2,
                        help="Bir kategorinin kullanabileceği bitişik koridor sayısı.")

    c1, c2 = st.columns(2)
    with c1: t_limit = st.number_input("⏱ Süre (sn)", 30, 3600, 120, 30)
    with c2: mip_gap = st.number_input("🎯 Gap (%)",  0.0, 10.0,  1.0, 0.5)

    # Parametre özeti kartı
    st.markdown(f"""
    <div style='
      background:rgba(255,255,255,.04);
      border:1px solid rgba(255,255,255,.08);
      border-left:2px solid #E85C1A;
      border-radius:10px;
      padding:12px 14px;margin:12px 0;
      font-family:JetBrains Mono,monospace;font-size:11px'>
      <div style='display:flex;justify-content:space-between;align-items:center;padding:4px 0;border-bottom:1px solid rgba(255,255,255,.05)'>
        <span style='color:#8FAECB;letter-spacing:.06em'>B_MAX</span>
        <span style='color:#FFFFFF;font-weight:700;font-size:13px'>{b_max}</span>
      </div>
      <div style='display:flex;justify-content:space-between;align-items:center;padding:4px 0;border-bottom:1px solid rgba(255,255,255,.05)'>
        <span style='color:#8FAECB;letter-spacing:.06em'>MAX_KOR</span>
        <span style='color:#FFFFFF;font-weight:700;font-size:13px'>{max_kor}</span>
      </div>
      <div style='display:flex;justify-content:space-between;align-items:center;padding:4px 0;border-bottom:1px solid rgba(255,255,255,.05)'>
        <span style='color:#8FAECB;letter-spacing:.06em'>T_LIMIT</span>
        <span style='color:#FFFFFF;font-weight:700;font-size:13px'>{t_limit} sn</span>
      </div>
      <div style='display:flex;justify-content:space-between;align-items:center;padding:4px 0'>
        <span style='color:#8FAECB;letter-spacing:.06em'>MIP_GAP</span>
        <span style='color:#E85C1A;font-weight:700;font-size:13px'>{mip_gap}%</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:1px;background:linear-gradient(90deg,transparent,#E85C1A,transparent);margin:10px 0'></div>", unsafe_allow_html=True)

    st.markdown('<div class="run-btn">', unsafe_allow_html=True)
    calistir = st.button("🚀 ÇALIŞTIR", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Son çözüm özeti
    if "sonuc" in st.session_state:
        s = st.session_state["sonuc"]
        dur = s.get("durum","")
        bc  = "b-opt" if dur=="OPTIMAL" else ("b-uyg" if dur=="UYGUN" else "b-err")
        vc  = "#4ade80" if dur=="OPTIMAL" else "#fbbf24"
        st.markdown("<div style='height:1px;background:linear-gradient(90deg,transparent,#E85C1A,transparent);margin:14px 0'></div>", unsafe_allow_html=True)
        st.markdown("<div class='slabel'>📊 Son Çözüm</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='background:#243554;border:1px solid #3A5070;border-radius:10px;padding:14px'>
          <span class='badge {bc}'>● {dur}</span>
          <div style='font-family:DM Mono,JetBrains Mono,monospace;font-size:22px;font-weight:400;color:{vc};margin:8px 0 2px;font-variant-numeric:tabular-nums'>{s.get("obj_val",0):,.0f}</div>
          <div style='font-size:11px;color:#A8BDD6;font-family:JetBrains Mono;margin-bottom:10px'>Amaç Değeri</div>
          <div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px'>
            <div style='background:#1B2A4A;border-radius:6px;padding:6px;text-align:center'>
              <div style='font-size:9px;color:#A8BDD6;font-family:JetBrains Mono'>SÜRE</div>
              <div style='font-size:13px;color:#FFFFFF;font-family:JetBrains Mono'>{s.get("sure",0):.1f}s</div>
            </div>
            <div style='background:#1B2A4A;border-radius:6px;padding:6px;text-align:center'>
              <div style='font-size:9px;color:#A8BDD6;font-family:JetBrains Mono'>GAP</div>
              <div style='font-size:13px;color:#FFFFFF;font-family:JetBrains Mono'>{s.get("mip_gap",0):.3f}%</div>
            </div>
            <div style='background:#1B2A4A;border-radius:6px;padding:6px;text-align:center'>
              <div style='font-size:9px;color:#A8BDD6;font-family:JetBrains Mono'>YENİ</div>
              <div style='font-size:13px;color:#FFFFFF;font-family:JetBrains Mono'>{len(s.get("acik_yeni",[]))}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

# ── MODEL ÇALIŞTIR ────────────────────────────────────────────────────────────
if calistir:
    if not yuklenen:
        st.error("Lütfen önce Excel dosyasını yükleyin!")
    else:
        dosya_bytes = st.session_state.get("_dosya_bytes")
        if not dosya_bytes:
            st.error("Dosya okunamadı — tekrar yükleyin.")
        else:
            with st.spinner("🔄 Gurobi çözüyor..."):
                try:
                    sonuc = model_calistir(dosya_bytes, b_max, max_kor, t_limit, mip_gap)
                    st.session_state["sonuc"] = sonuc
                    if sonuc.get("durum") not in ("COZUM_YOK", None):
                        # D_ik ve F_i kaydet (manuel karşılaştırma için)
                        veri = _mod.excel_oku(dosya_bytes)
                        st.session_state["_D_ik"]     = veri["D_ik"]
                        st.session_state["_F_i"]      = veri["F_i"]
                        st.session_state["_U_i_excel"] = dict(veri["U_i"])  # Excel'deki ham değerler
                        st.session_state["manuel_atama"] = {i: list(sonuc["sonuc_kat"][i]["bloklar"]) for i in sonuc["I"]}
                        st.success(f"✅ {sonuc['durum']} — Amaç: {sonuc['obj_val']:,.0f}  ({sonuc['sure']:.1f}s)")
                        st.session_state["_ac_depo_haritasi"] = True
                    else:
                        st.error("❌ Çözüm bulunamadı!")
                except Exception as e:
                    st.error(f"Hata: {e}")

# ── SONUÇ YOKSA DUR ───────────────────────────────────────────────────────────
if "sonuc" not in st.session_state or st.session_state["sonuc"].get("durum") == "COZUM_YOK":
    st.markdown("""
    <div style='display:flex;flex-direction:column;align-items:center;justify-content:center;
         height:65vh;gap:20px;padding:40px'>
      <div style='width:90px;height:90px;background:linear-gradient(135deg,#1B2A4A,#243554);
           border-radius:20px;display:flex;align-items:center;justify-content:center;
           font-size:44px;box-shadow:0 8px 30px rgba(27,42,74,.25);border:2px solid rgba(232,92,26,.4)'>
        🏭
      </div>
      <div>
        <div style='font-family:DM Sans,Inter,sans-serif;font-size:28px;font-weight:700;
             color:#1B2A4A;text-align:center;letter-spacing:.01em'>
          Kit Atama Optimizasyon Sistemi
        </div>
        <div style='font-size:13px;color:#7B90AA;text-align:center;margin-top:8px;font-family:Inter'>
          TürkTraktör Fabrikası · Gazi Üniversitesi Bitirme Projesi
        </div>
      </div>
      <div style='display:flex;gap:16px;margin-top:8px'>
        <div style='background:#FFFFFF;border:1px solid #D8E2EE;border-top:3px solid #E85C1A;
             border-radius:10px;padding:14px 20px;text-align:center;min-width:120px;
             box-shadow:0 2px 10px rgba(27,42,74,.08)'>
          <div style='font-size:18px;font-weight:600;color:#E85C1A;font-family:DM Mono,monospace;letter-spacing:.02em'>MIP</div>
          <div style='font-size:9px;color:#7B90AA;font-family:JetBrains Mono;text-transform:uppercase;letter-spacing:.1em;margin-top:3px'>Optimizasyon</div>
        </div>
        <div style='background:#FFFFFF;border:1px solid #D8E2EE;border-top:3px solid #1B2A4A;
             border-radius:10px;padding:14px 20px;text-align:center;min-width:120px;
             box-shadow:0 2px 10px rgba(27,42,74,.08)'>
          <div style='font-size:18px;font-weight:600;color:#1B2A4A;font-family:DM Mono,monospace;letter-spacing:.02em'>GUROBI</div>
          <div style='font-size:9px;color:#7B90AA;font-family:JetBrains Mono;text-transform:uppercase;letter-spacing:.1em;margin-top:3px'>Çözücü</div>
        </div>

      </div>
      <div style='background:linear-gradient(135deg,#FFF7F4,#FFF0E8);border:1px solid rgba(232,92,26,.2);
           border-left:3px solid #E85C1A;border-radius:10px;padding:14px 20px;margin-top:8px;max-width:480px'>
        <div style='font-size:12px;color:#7B2D00;font-family:Inter;text-align:center;font-weight:500'>
          ← Sol panelden <strong>Excel dosyasını yükleyin</strong> ve
          <strong>Modeli Çalıştır</strong> butonuna basın
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── VERİ ─────────────────────────────────────────────────────────────────────
sonuc     = st.session_state["sonuc"]
sonuc_kat = sonuc["sonuc_kat"]
blok_ozet = sonuc["blok_ozet"]
I         = sonuc["I"]
K         = sonuc["K"]
alanlar   = sonuc["alanlar"]
K_alan    = sonuc["K_alan"]
kat_renk  = {i: KAT_RENK[idx % len(KAT_RENK)] for idx, i in enumerate(I)}

# Üst metrikler
toplam_kap = sum(blok_ozet[k]["kapasite"] for k in K)
toplam_yuk = sum(blok_ozet[k]["yuklu"]    for k in K)
toplam_dol = toplam_yuk / toplam_kap * 100 if toplam_kap > 0 else 0
dur = sonuc["durum"]

st.markdown(f"""
<div style='display:flex;gap:10px;margin:12px 0 18px'>
  <div class='kpi {"green" if dur=="OPTIMAL" else "yellow"}'>
    <div class='lbl'>Durum</div>
    <div class='val' style='font-size:16px'><span class='badge {"b-opt" if dur=="OPTIMAL" else "b-uyg"}'>● {dur}</span></div>
  </div>
  <div class='kpi blue'>
    <div class='lbl'>F×D Mesafe</div>
    <div class='val'>{sonuc["obj_val"]:,.0f}</div>
  </div>
  <div class='kpi'>
    <div class='lbl'>Toplam Doluluk</div>
    <div class='val'>{toplam_dol:.1f}%</div>
  </div>
  <div class='kpi'>
    <div class='lbl'>MIP Gap</div>
    <div class='val'>{sonuc["mip_gap"]:.3f}%</div>
  </div>
  <div class='kpi'>
    <div class='lbl'>Çözüm Süresi</div>
    <div class='val'>{sonuc["sure"]:.1f}s</div>
  </div>
  <div class='kpi {"yellow" if sonuc["acik_yeni"] else ""}'>
    <div class='lbl'>Yeni Blok</div>
    <div class='val'>{len(sonuc["acik_yeni"])}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── SEKMELER ─────────────────────────────────────────────────────────────────
# Senaryo Analizi ilk sıraya alındı — st.rerun() her zaman ilk sekmeyi açar,
# bu yüzden model çalıştırıldıktan sonra doğrudan Senaryo Analizi görünür.
tab1, tab4, tab5, tab3, tab2 = st.tabs([
    "🏭 Depo Haritası",
    "📈 Senaryo Analizi",
    "🔬 Senaryolar",
    "📊 Blok Doluluk",
    "📦 Kategori Atama",
])

# components.html sekme JS'ini kaldır — artık gerek yok
_ = st.session_state.pop("_sekme_senaryo_ac", None)

# İlk model çalışınca Depo Haritası sekmesini aç (index 1)
if st.session_state.pop("_ac_depo_haritasi", False):
    import streamlit.components.v1 as _cv1
    _cv1.html("""<script>
    (function() {
        function _ac() {
            var tabs = window.parent.document.querySelectorAll('button[data-testid="stTab"]');
            if (tabs && tabs.length > 1) { tabs[1].click(); }
            else { setTimeout(_ac, 100); }
        }
        setTimeout(_ac, 200);
    })();
    </script>""", height=0, scrolling=False)

# ══ TAB 1: DEPO HARİTASI ════════════════════════════════════════════════════
with tab1:
    mod = st.radio("", ["🤖 Optimal Çözüm","⚖️ Optimal vs Manuel Karşılaştırma"],
                   horizontal=True, label_visibility="collapsed")

    # Tab1 haritasını cache'le — sidebar slider/widget değişiminde yeniden çizilmesin
    _tab1_cache_key = ("tab1", id(sonuc_kat), mod == "🤖 Optimal Çözüm")
    if st.session_state.get("_tab1_cache_key") != _tab1_cache_key:
        fig_opt = harita_ciz(sonuc_kat, blok_ozet, I, K, kat_renk, "tab1", show_legend=(mod == "🤖 Optimal Çözüm"))
        st.session_state["_tab1_fig"] = fig_opt
        st.session_state["_tab1_cache_key"] = _tab1_cache_key
    else:
        fig_opt = st.session_state["_tab1_fig"]
    st.session_state["_harita_fig"] = fig_opt

    if mod == "🤖 Optimal Çözüm":
        st.plotly_chart(fig_opt, use_container_width=True, key="harita_opt", config=HARITA_DOWNLOAD_CONFIG)

    else:
        # Manuel karşılaştırma
        D_ik = st.session_state.get("_D_ik")
        F_i  = st.session_state.get("_F_i")
        if D_ik is None:
            st.info("Manuel karşılaştırma için modeli bir kez çalıştırın.")
            st.plotly_chart(fig_opt, use_container_width=True, key="harita_opt2", config=HARITA_DOWNLOAD_CONFIG)
        else:
            if "manuel_atama" not in st.session_state:
                st.session_state["manuel_atama"] = {i: list(sonuc_kat[i]["bloklar"]) for i in I}

            # Maliyet hesapla
            def mesafe_hesapla(atama):
                return sum(F_i.get(i,0) * D_ik.get((i,k),0)
                           for i in I for k in atama.get(i,[]))

            mes_opt = mesafe_hesapla({i: sonuc_kat[i]["bloklar"] for i in I})
            mes_man = mesafe_hesapla(st.session_state["manuel_atama"])
            fark  = mes_man - mes_opt

            # Üst metrik bar
            frenk = "#4ade80" if fark <= 0 else "#f87171"
            fikon = "▼" if fark <= 0 else "▲"
            st.markdown(f"""
            <div style='display:flex;gap:10px;margin-bottom:14px'>
              <div class='kpi green' style='flex:1'><div class='lbl'>Optimal Mesafe</div><div class='val'>{mes_opt:,.0f}</div></div>
              <div class='kpi' style='flex:1;border-color:{frenk}33'><div class='lbl'>Manuel Mesafe</div>
                <div class='val' style='color:{frenk}'>{mes_man:,.0f} <span style='font-size:13px'>{fikon} {abs(fark):,.0f}</span></div></div>
            </div>
            """, unsafe_allow_html=True)

            # ── En uygun boş bloğu bul
            def en_uygun_blok_bul(kat_i, mevcut_atama, hariç_bloklar=None):
                if hariç_bloklar is None: hariç_bloklar = set()
                alan   = sonuc_kat[kat_i]["alan"]
                mesgul = {k for j in I for k in mevcut_atama.get(j,[])}
                adaylar = [k for k in K if sonuc["alan_k"].get(k)==alan
                           and k not in hariç_bloklar and k not in mesgul]
                if not adaylar:
                    adaylar = [k for k in K if k not in hariç_bloklar and k not in mesgul]
                return min(adaylar, key=lambda k: D_ik.get((kat_i,k),9999)) if adaylar else None

            # ── Kontrol paneli — haritaların ÜSTÜNDE tam genişlikte
            ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([3, 2, 1, 1])
            with ctrl1:
                kat_sec = st.selectbox("Düzenlenecek kategori:", I,
                    format_func=lambda i: f"Kat.{i} — {'+'.join(sonuc_kat[i]['kodlar'])}",
                    key="man_kat")
            with ctrl2:
                mevcut_bloklar = st.session_state["manuel_atama"].get(kat_sec, [])
                yeni_bloklar   = st.multiselect(
                    "Bloklar:", K, default=mevcut_bloklar, key=f"mblok_{kat_sec}",
                    format_func=lambda k: f"B{k}({sonuc['alan_k'].get(k,'?')})"
                )
            with ctrl3:
                st.markdown("<div style='margin-top:26px'>", unsafe_allow_html=True)
                if st.button("✅ Uygula", key="man_uygula", use_container_width=True):
                    yeni_atama = dict(st.session_state["manuel_atama"])
                    yeni_atama[kat_sec] = list(yeni_bloklar)
                    eklenenler = set(yeni_bloklar) - set(mevcut_bloklar)
                    tasinan = []
                    for blok in eklenenler:
                        for dk in I:
                            if dk == kat_sec: continue
                            if blok in yeni_atama.get(dk,[]):
                                yeni_atama[dk] = [b for b in yeni_atama[dk] if b != blok]
                                yb = en_uygun_blok_bul(dk, yeni_atama, hariç_bloklar={blok})
                                if yb:
                                    yeni_atama[dk] = yeni_atama.get(dk,[]) + [yb]
                                    tasinan.append((dk, blok, yb))
                    st.session_state["manuel_atama"] = yeni_atama
                    for dk, eb, yb in tasinan:
                        st.toast(f"Kat.{dk}: Blok {eb}→{yb}", icon="🔀")
                    # Buton tıklaması zaten bu çalıştırmada state'i güncelliyor; ekstra rerun kaldırıldı.
                st.markdown("</div>", unsafe_allow_html=True)
            with ctrl4:
                st.markdown("<div style='margin-top:26px'>", unsafe_allow_html=True)
                if st.button("🔄 Sıfırla", key="man_sifirla", use_container_width=True):
                    st.session_state["manuel_atama"] = {i: list(sonuc_kat[i]["bloklar"]) for i in I}
                    st.session_state.pop("manuel_dogrula_sonuc", None)
                    # Ekstra rerun kaldırıldı; harita aynı çalıştırmada güncellenir.
                st.markdown("</div>", unsafe_allow_html=True)

            # Manuel atamayı senaryo olarak kaydet
            man_kat_degisti = any(
                set(st.session_state["manuel_atama"].get(i,[])) != set(sonuc_kat[i]["bloklar"])
                for i in I
            )
            if man_kat_degisti:
                st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
                man_sen_ad = st.text_input(
                    "Manuel senaryo adı:",
                    value=f"Manuel__{yuklenen.name.replace('.xlsx','') if yuklenen else 'dosya'}",
                    key="man_sen_ad"
                )
                if st.button("💾 Manuel Atamayı Senaryo Olarak Kaydet", key="man_kaydet", use_container_width=True):
                    import time as _t
                    man_kat = st.session_state["manuel_atama"]
                    _kat_renk_m = {i: KAT_RENK[idx % len(KAT_RENK)] for idx, i in enumerate(I)}
                    man_sonuc_kat_k = {}
                    for i in I:
                        bl = man_kat.get(i, [])
                        ui = sonuc["U_i"].get(i, 0)
                        n  = max(len(bl), 1)
                        man_sonuc_kat_k[i] = {
                            **sonuc_kat[i], "bloklar": bl,
                            "birincil": bl[0] if bl else None,
                            "u": {k: ui/n for k in bl}
                        }
                    man_blok_ozet_k = {}
                    for k in K:
                        kull  = [(i, sonuc["U_i"].get(i,0)/max(len(man_kat.get(i,[])),1))
                                 for i in I if k in man_kat.get(i,[])]
                        yuklu = sum(uv for _,uv in kull)
                        kap   = sonuc["C_k"].get(k, 1)
                        man_blok_ozet_k[k] = {**blok_ozet[k], "yuklu": yuklu,
                            "doluluk": yuklu/kap*100 if kap>0 else 0, "kullananlar": kull}
                    _man_key = str(hash(str({i: sorted(man_sonuc_kat_k[i]["bloklar"]) for i in I})))[-8:]
                    _fig_m = harita_ciz(man_sonuc_kat_k, man_blok_ozet_k, I, K, _kat_renk_m, _man_key)
                    _tablo_m = []
                    for _i in I:
                        _s = man_sonuc_kat_k[_i]
                        for _k in _s["bloklar"]:
                            _yuklu = _s["u"].get(_k, 0)
                            _kap   = sonuc["C_k"].get(_k, 1)
                            _tablo_m.append({
                                "Kategori":_i,"Kodlar":"+".join(_s["kodlar"]),"Alan":_s["alan"],
                                "Hat":f"l{_s['hat']}","Blok":_k,"Tip":blok_ozet[_k]["tip"],
                                "Kapasite":round(_kap,1),"Yüklenen":round(_yuklu,1),
                                "Doluluk(%)":round(_yuklu/_kap*100,1) if _kap>0 else 0,
                                "Birincil":"✓" if _k==_s["birincil"] else ""
                            })
                    toplam_k = sum(man_blok_ozet_k[k]["kapasite"] for k in K)
                    toplam_y = sum(man_blok_ozet_k[k]["yuklu"] for k in K)
                    if "senaryolar" not in st.session_state:
                        st.session_state["senaryolar"] = []
                    st.session_state["senaryolar"].append({
                        "_meta": {
                            "Ad": man_sen_ad, "Dosya": yuklenen.name if yuklenen else "?",
                            "B_MAX": b_max, "MAX_KOR": max_kor,
                            "Amaç": round(sum(
                                st.session_state.get("_F_i",{}).get(i,0) *
                                st.session_state.get("_D_ik",{}).get((i,k),0)
                                for i in I for k in man_kat.get(i,[])
                            )),
                            "Süre(s)": 0.0, "Durum": "MANUEL",
                            "Gap(%)": 0.0, "YeniBlok": 0,
                            "Doluluk(%)": round(toplam_y/toplam_k*100,1) if toplam_k>0 else 0
                        },
                        "_fig_harita": _fig_m, "_fig_doluluk": None,
                        "_df_atama": pd.DataFrame(_tablo_m)
                    })
                    st.success(f"✅ '{man_sen_ad}' kaydedildi!")
                    st.rerun()

            # Doğrula butonu — tam genişlikte
            st.markdown("<hr style='border:none;border-top:1px solid #1a1a2e;margin:8px 0'>", unsafe_allow_html=True)
            dg_col1, dg_col2 = st.columns([2,1])
            with dg_col1:
                if st.button("🔬 Modelle Doğrula", use_container_width=True, key="dogrula_btn"):
                    dosya_bytes = st.session_state.get("_dosya_bytes")
                    if not dosya_bytes:
                        st.error("Excel dosyası bulunamadı.")
                    else:
                        with st.spinner("🔄 Manuel atama doğrulanıyor..."):
                            try:
                                dg_sonuc = _mod.manuel_dogrula(
                                    dosya_bytes,
                                    st.session_state["manuel_atama"],
                                    b_max=b_max, max_kor=max_kor,
                                    t_limit=t_limit, mip_gap=mip_gap/100.0
                                )
                                st.session_state["manuel_dogrula_sonuc"] = dg_sonuc
                            except Exception as e:
                                st.error(f"Hata: {e}")
            with dg_col2:
                if st.button("🗑️ Sonucu Temizle", key="dg_temizle", use_container_width=True):
                    st.session_state.pop("manuel_dogrula_sonuc", None)
                    st.rerun()

            # Doğrulama sonucu göster
            if "manuel_dogrula_sonuc" in st.session_state:
                dg = st.session_state["manuel_dogrula_sonuc"]
                mes_opt_val = sum(F_i.get(i,0)*D_ik.get((i,k),0)
                                  for i in I for k in sonuc_kat[i]["bloklar"])
                saf = dg.get("saf_mesafe", 0)
                ceza = dg.get("toplam_ceza", 0)
                fark = saf - mes_opt_val
                frenk2 = "#4ade80" if fark <= 0 else "#f87171"
                fikon2 = "▼" if fark <= 0 else "▲"

                if dg["ihlaller"]:
                    st.markdown(f"""
                    <div style='background:#1a0a0a;border:1px solid #7f1d1d;border-radius:8px;padding:10px 14px;margin:8px 0'>
                      <div style='color:#f87171;font-family:JetBrains Mono;font-weight:600;margin-bottom:6px'>⚠️ Kısıt İhlali Tespit Edildi</div>
                      {''.join(f"<div style='color:#fca5a5;font-size:12px'>• {ih}</div>" for ih in dg["ihlaller"])}
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown(f"""
                <div style='background:#FFFFFF;border:1px solid #DDE3ED;border-radius:8px;padding:12px 16px;margin:8px 0;font-family:JetBrains Mono'>
                  <div style='display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:10px'>
                    <div style='text-align:center'>
                      <div style='font-size:10px;color:#A8BDD6'>OPTIMAL MESAFE</div>
                      <div style='font-size:16px;font-weight:600;color:#4ade80'>{mes_opt_val:,.0f}</div>
                    </div>
                    <div style='text-align:center'>
                      <div style='font-size:10px;color:#A8BDD6'>SAF MESAFE</div>
                      <div style='font-size:16px;font-weight:600;color:{frenk2}'>{saf:,.0f} <span style='font-size:11px'>{fikon2} {abs(fark):,.0f}</span></div>
                    </div>
                    <div style='text-align:center'>
                      <div style='font-size:10px;color:#A8BDD6'>CEZA</div>
                      <div style='font-size:16px;font-weight:600;color:{"#f87171" if ceza>0 else "#4ade80"}'>{ceza:,.0f}</div>
                    </div>
                    <div style='text-align:center'>
                      <div style='font-size:10px;color:#A8BDD6'>TOPLAM (SAF+CEZA)</div>
                      <div style='font-size:16px;font-weight:600;color:#e2e2f0'>{(saf+ceza):,.0f}</div>
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

            # Değişen kategoriler özeti
            man_kat = st.session_state["manuel_atama"]
            degisen_katlar = [i for i in I if set(man_kat.get(i,[])) != set(sonuc_kat[i]["bloklar"])]
            if degisen_katlar:
                with st.expander(f"📋 {len(degisen_katlar)} kategori değişti", expanded=False):
                    for di in degisen_katlar:
                        ek  = set(man_kat.get(di,[])) - set(sonuc_kat[di]["bloklar"])
                        cik = set(sonuc_kat[di]["bloklar"]) - set(man_kat.get(di,[]))
                        st.markdown(f"**Kat.{di}** — {'+'.join(sonuc_kat[di]['kodlar'])}")
                        if ek:  st.markdown(f"  ✅ Eklendi: {sorted(ek)}")
                        if cik: st.markdown(f"  ❌ Çıkarıldı: {sorted(cik)}")

            # ── Manuel harita verisi
            man_sonuc_kat = {}
            for i in I:
                bl = man_kat.get(i,[])
                ui = sonuc["U_i"].get(i,0)
                n  = max(len(bl),1)
                man_sonuc_kat[i] = {**sonuc_kat[i], "bloklar":bl,
                    "birincil":bl[0] if bl else None, "u":{k:ui/n for k in bl}}
            man_blok_ozet = {}
            for k in K:
                kull  = [(i, sonuc["U_i"].get(i,0)/max(len(man_kat.get(i,[])),1))
                         for i in I if k in man_kat.get(i,[])]
                yuklu = sum(uv for _,uv in kull)
                kap   = sonuc["C_k"].get(k,1)
                man_blok_ozet[k] = {**blok_ozet[k], "yuklu":yuklu,
                    "doluluk":yuklu/kap*100 if kap>0 else 0, "kullananlar":kull}

            fig_man = harita_ciz(man_sonuc_kat, man_blok_ozet, I, K, kat_renk, "man")
            opt_set = {k for i in I for k in sonuc_kat[i]["bloklar"]}
            man_set = {k for i in I for k in man_kat.get(i,[])}
            for k in opt_set.symmetric_difference(man_set):
                if k in BLOK_LAYOUT:
                    lo = BLOK_LAYOUT[k]
                    fig_man.add_shape(type="rect",
                        x0=lo["x"]-2,y0=lo["y"]-2,x1=lo["x"]+lo["w"]+2,y1=lo["y"]+lo["h"]+2,
                        fillcolor="rgba(0,0,0,0)",line=dict(color="#f97316",width=2.5))

            # ── İKİ HARİTA YAN YANA
            col_opt, col_man = st.columns(2)
            with col_opt:
                st.markdown("<div style='font-size:12px;color:#60a5fa;font-family:JetBrains Mono;margin-bottom:4px;text-align:center'>🤖 OPTİMAL</div>", unsafe_allow_html=True)
                st.plotly_chart(fig_opt, use_container_width=True, key="harita_opt_cmp", config=HARITA_DOWNLOAD_CONFIG)
            with col_man:
                st.markdown("<div style='font-size:12px;color:#fbbf24;font-family:JetBrains Mono;margin-bottom:4px;text-align:center'>✋ MANUEL</div>", unsafe_allow_html=True)
                st.plotly_chart(fig_man, use_container_width=True, key="harita_man", config=HARITA_DOWNLOAD_CONFIG)


# ══ TAB 2: KATEGORİ ATAMA ════════════════════════════════════════════════════
with tab2:
    st.markdown("### 📦 Kategori Bazında Atama Sonuçları")
    for a in alanlar:
        r = ALAN_RENK[a]
        katlar = [i for i in I if sonuc_kat[i]["alan"]==a]
        if not katlar: continue
        st.markdown(f"""
        <div style='background:{ALAN_RGBA[a]};border-left:3px solid {r};border-radius:4px;
             padding:8px 14px;margin:10px 0 6px;font-family:JetBrains Mono;color:{r};font-weight:600'>
          Alan {a}
        </div>""", unsafe_allow_html=True)
        for i in sorted(katlar):
            s = sonuc_kat[i]
            with st.expander(f"Kat.{i:02d} — [{'+'.join(s['kodlar'])}]  →  Hat l{s['hat']}  |  {s['talep']:.0f} raf"):
                tablo = []
                for k in sorted(s["bloklar"]):
                    yuklu = s["u"].get(k,0); kap = sonuc["C_k"][k]
                    dol   = yuklu/kap*100 if kap>0 else 0
                    tablo.append({"Blok":k,"Tip":blok_ozet[k]["tip"],
                                  "Kapasite":f"{kap:.0f}","Yüklenen":f"{yuklu:.1f}",
                                  "Doluluk(%)":f"{dol:.1f}%","Birincil":"✓" if k==s["birincil"] else ""})
                c1,c2 = st.columns([1,3])
                with c1:
                    st.metric("Talep",    f"{s['talep']:.0f} raf")
                    st.metric("Blok Sayısı", len(s["bloklar"]))
                    st.metric("Alan", s["alan"])
                with c2:
                    st.dataframe(pd.DataFrame(tablo), hide_index=True, use_container_width=True)

# ══ TAB 3: BLOK DOLULUK ══════════════════════════════════════════════════════
with tab3:
    st.markdown("### 📊 Blok Doluluk Analizi")
    blok_df = []
    for k in K:
        oz = blok_ozet[k]
        if oz["yuklu"] > 0:
            kullananlar_str = ", ".join(f"Kat.{ki}({uv:.0f})" for ki,uv in oz["kullananlar"])
            blok_df.append({"Blok":f"B{k}","Alan":oz["alan"],"Tip":oz["tip"],
                            "Kapasite":oz["kapasite"],"Yüklenen":oz["yuklu"],
                            "Doluluk(%)":round(oz["doluluk"],1),"Kullananlar":kullananlar_str})
    df_blok = pd.DataFrame(blok_df)
    if not df_blok.empty:
        fig3 = px.bar(df_blok, x="Blok", y="Doluluk(%)", color="Alan",
                      color_discrete_map=ALAN_RENK, text="Doluluk(%)",
                      title="Blok Doluluk Oranları (%)")
        fig3.add_hline(y=90, line_dash="dash", line_color="#f87171", annotation_text="90% kritik")
        fig3.add_hline(y=70, line_dash="dot",  line_color="#fbbf24", annotation_text="70% uyarı")
        fig3.update_traces(texttemplate="%{text:.0f}%", textposition="outside")
        fig3.update_layout(paper_bgcolor="#F2F4F7", plot_bgcolor="#EEF2F8",
                           font=dict(color="#1B2A4A", family="JetBrains Mono"),
                           xaxis=dict(tickangle=-45, gridcolor="#1a1a2e"),
                           yaxis=dict(gridcolor="#1a1a2e"), showlegend=True)
        st.plotly_chart(fig3, use_container_width=True, config=FAST_PLOTLY_CONFIG)

        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Dolu Blok", len(df_blok))
        c2.metric("Ort. Doluluk", f"{df_blok['Doluluk(%)'].mean():.1f}%")
        c3.metric("Kritik (≥90%)", len(df_blok[df_blok["Doluluk(%)"]>=90]))
        c4.metric("Boş Blok", len(K)-len(df_blok))
        st.dataframe(df_blok, hide_index=True, use_container_width=True)

# ══ TAB 4: SENARYOLAR ══════════════════════════════════════════════════════════
with tab4:

    # ── Session state hazırlık ──────────────────────────────────────────────────
    if "senaryolar"       not in st.session_state: st.session_state["senaryolar"]       = []
    if "_U_i_excel"       not in st.session_state: st.session_state["_U_i_excel"]       = dict(sonuc["U_i"])
    if "U_i_override"     not in st.session_state: st.session_state["U_i_override"]     = {}
    if "yeni_altgruplar"  not in st.session_state: st.session_state["yeni_altgruplar"]  = {}

    U_i_excel = st.session_state["_U_i_excel"]

    # Hat → kategori adları (alan modele bırakılır)
    hat_katlar_map = {}
    for _hi in I:
        _hs  = sonuc_kat[_hi]
        _hat = _hs["hat"]
        hat_katlar_map.setdefault(_hat, [])
        hat_katlar_map[_hat].extend(_hs["adlar"] if _hs["adlar"] else _hs["kodlar"])
    mevcut_hatlar = sorted(hat_katlar_map.keys())

    def hat_label(h):
        isimler = list(dict.fromkeys(hat_katlar_map.get(h, [])))
        return f"Hat {h}  —  {', '.join(isimler[:4])}{'...' if len(isimler)>4 else ''}"

    def _slabel(txt):
        return (f"<div style='font-family:JetBrains Mono;font-size:10px;font-weight:700;"
                f"color:#E85C1A;text-transform:uppercase;letter-spacing:.18em;"
                f"padding-bottom:7px;border-bottom:2px solid #E85C1A;margin-bottom:14px'>"
                f"{txt}</div>")

    def _senaryo_kaydet(ad, sonuc_s, blok_ozet_s, I_s, K_s):
        import time as _time
        _kat_renk_s = {i: KAT_RENK[idx % len(KAT_RENK)] for idx, i in enumerate(I_s)}
        _fig = harita_ciz(sonuc_s["sonuc_kat"], blok_ozet_s, I_s, K_s,
                          _kat_renk_s, "sen_s")
        _tablo = []
        for _i in I_s:
            _s = sonuc_s["sonuc_kat"][_i]
            for _k in _s["bloklar"]:
                _yuklu = _s["u"].get(_k, 0); _kap = sonuc_s["C_k"][_k]
                _tablo.append({
                    "Kategori": _i, "Kodlar": "+".join(_s["kodlar"]),
                    "Alan": _s["alan"], "Hat": f"l{_s['hat']}", "Blok": _k,
                    "Tip": blok_ozet_s[_k]["tip"], "Kapasite": _kap,
                    "Yüklenen": _yuklu,
                    "Doluluk(%)": round(_yuklu/_kap*100, 1) if _kap > 0 else 0,
                    "Birincil": "✓" if _k == _s["birincil"] else ""})
        _bd = [{"Blok": f"B{k}", "Alan": blok_ozet_s[k]["alan"],
                "Doluluk(%)": blok_ozet_s[k]["doluluk"],
                "Yüklened": blok_ozet_s[k]["yuklu"],
                "Kapasite": blok_ozet_s[k]["kapasite"]}
               for k in K_s if blok_ozet_s[k]["yuklu"] > 0]
        _fd = None
        if _bd:
            _fd = px.bar(pd.DataFrame(_bd), x="Blok", y="Doluluk(%)", color="Alan",
                         color_discrete_map=ALAN_RENK)
            _fd.update_layout(paper_bgcolor="#F2F4F7", plot_bgcolor="#EEF2F8",
                              font=dict(color="#1B2A4A", family="JetBrains Mono"))
        toplam_k = sum(blok_ozet_s[k]["kapasite"] for k in K_s)
        toplam_y = sum(blok_ozet_s[k]["yuklu"]    for k in K_s)
        dosya_adi_s = yuklenen.name if yuklenen else "bilinmiyor"
        st.session_state["senaryolar"].append({
            "_meta": {"Ad": ad, "Dosya": dosya_adi_s,
                      "B_MAX": sb if "sb" in dir() else b_max,
                      "MAX_KOR": sk if "sk" in dir() else max_kor,
                      "Amaç": round(sonuc_s["obj_val"]),
                      "Süre(s)": round(sonuc_s["sure"], 1),
                      "Durum": sonuc_s["durum"],
                      "Gap(%)": round(sonuc_s["mip_gap"], 3),
                      "YeniBlok": len(sonuc_s["acik_yeni"]),
                      "Doluluk(%)": round(toplam_y/toplam_k*100, 1) if toplam_k > 0 else 0},
            "_fig_harita": _fig, "_fig_doluluk": _fd,
            "_df_atama": pd.DataFrame(_tablo)
        })

    # ══ İKİ SÜTUN LAYOUT ══════════════════════════════════════════════════════
    left_col, right_col = st.columns([0.72, 1.28], gap="large")

    # ════════════════════════════ SOL: FORM ════════════════════════════════════
    with left_col:

        # ── 1. YENİ ALT GRUP ────────────────────────────────────────────────
        st.markdown(_slabel("➕ Yeni Alt Grup Ekle"), unsafe_allow_html=True)
        st.markdown(
            "<p style='font-size:13px;color:#4A6280;margin-bottom:12px'>"
            "Excel'de olmayan malzeme grubunu buradan ekle. "
            "Sadece <b>isim, miktar ve montaj hattını</b> gir — "
            "model bloğu otomatik atar."
            "</p>", unsafe_allow_html=True)

        # Form kullanıldı: yazarken / miktara tıklarken sayfa tekrar tekrar rerun olmaz.
        # Böylece ekranın gri-soluk hale gelmesi ve depo haritasının her tuşta yeniden yüklenmesi engellenir.
        with st.form("yeni_altgrup_form", clear_on_submit=False):
            yeni_kod = st.text_input(
                "Alt grup adı / kodu",
                key="yeni_ag_kod",
                placeholder="örn: UTRDK, MOTOR, SANZIMAN")

            yeni_talep = st.number_input(
                "Miktar (raf birimi)",
                min_value=1.0, max_value=9999.0,
                value=10.0, step=1.0, key="yeni_ag_talep")

            # Montaj hattı form dışında seçilir (klavye tetiklemez)
            # Değer session_state["hat_dropdown_idx"]'te tutulur
            pass  # seçim aşağıda form dışında

            ag_ekle_col, ag_sil_col = st.columns([1.25, 1.25])
            with ag_ekle_col:
                yeni_ag_ekle_submit = st.form_submit_button(
                    "✅ Ekle", use_container_width=True)
            with ag_sil_col:
                yeni_ag_sil_submit = st.form_submit_button(
                    "🗑️ Temizle", use_container_width=True)

        # ── Montaj hattı seçimi — form DIŞINDA: klavyesiz native dropdown ──────
        # Streamlit form içindeki selectbox mobilde klavyeyi tetikler.
        # Form dışına alınca tarayıcı native <select> olarak işler → klavye açılmaz.
        st.markdown(
            "<div style='font-size:10px;font-family:JetBrains Mono,monospace;"
            "font-weight:700;text-transform:uppercase;letter-spacing:.1em;"
            "color:#4A6280;margin-bottom:4px;margin-top:8px'>MONTAJ HATTI</div>",
            unsafe_allow_html=True)
        st.selectbox(
            "Montaj Hattı",
            range(len(mevcut_hatlar)),
            format_func=lambda x: hat_label(mevcut_hatlar[x]),
            key="hat_dropdown_idx",
            label_visibility="collapsed")

        if yeni_ag_ekle_submit:
            # hat seçimini form dışındaki selectbox'tan al
            yeni_hat = mevcut_hatlar[st.session_state.get("hat_dropdown_idx", 0)]
            yeni_kod_temiz = yeni_kod.strip().upper()
            mevcut_k = ["+".join(sonuc["kod_i"][i]) for i in I]
            if not yeni_kod_temiz:
                st.error("Ad / kod boş olamaz!")
            elif yeni_kod_temiz in mevcut_k:
                st.error(f"'{yeni_kod_temiz}' Excel'de zaten mevcut!")
            else:
                st.session_state["yeni_altgruplar"][yeni_kod_temiz] = {
                    "talep": yeni_talep, "hat": yeni_hat}
                st.success(f"✅ '{yeni_kod_temiz}' eklendi — {yeni_talep:.0f} raf")
                st.rerun()

        if yeni_ag_sil_submit:
            st.session_state["yeni_altgruplar"] = {}
            st.rerun()

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        calistir_yeni_ag = st.button(
            "🚀 ÇALIŞTIR",
            key="run_yeni_ag_hizli", use_container_width=True, type="primary")
        st.markdown(
            "<div style='background:#FFFFFF;border:1px solid #D8E2EE;border-left:4px solid #E85C1A;"
            "border-radius:9px;padding:9px 12px;margin:8px 0 10px'>"
            "<div style='font-size:12px;color:#4A6280;font-weight:600'>"
            "Bu buton, Excel verisini ve eklediğin/değiştirdiğin talepleri import edilen matematiksel modele gönderir; sonuç depo haritasında güncellenir.</div>"
            "</div>", unsafe_allow_html=True)

        # Eklenen gruplar listesi
        if st.session_state["yeni_altgruplar"]:
            st.markdown("<div style='margin-top:10px'>", unsafe_allow_html=True)
            for _kod, _b in list(st.session_state["yeni_altgruplar"].items()):
                _hat_isimler = ", ".join(list(dict.fromkeys(
                    hat_katlar_map.get(_b["hat"], [])))[:3])
                c_a, c_b = st.columns([3, 1])
                with c_a:
                    st.markdown(
                        f"<div style='background:#FFFFFF;border:1px solid #D8E2EE;"
                        f"border-left:4px solid #E85C1A;border-radius:8px;"
                        f"padding:10px 14px;margin-bottom:6px'>"
                        f"<div style='font-size:15px;font-weight:800;color:#1B2A4A;"
                        f"font-family:Barlow Condensed,sans-serif'>{_kod}</div>"
                        f"<div style='font-size:12px;color:#E85C1A;font-weight:600;margin-top:2px'>"
                        f"{_b['talep']:.0f} raf</div>"
                        f"<div style='font-size:11px;color:#9AACC5;margin-top:2px'>"
                        f"Hat {_b['hat']}  ·  {_hat_isimler}</div>"
                        f"<div style='font-size:10px;color:#B0C0D4;font-style:italic;margin-top:2px'>"
                        f"Alan ataması modelin kararı</div></div>",
                        unsafe_allow_html=True)
                with c_b:
                    st.markdown("<div style='margin-top:14px'>", unsafe_allow_html=True)
                    if st.button("🗑️", key=f"del_yeni_{_kod}", use_container_width=True):
                        del st.session_state["yeni_altgruplar"][_kod]
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown(
                "<div style='background:linear-gradient(135deg,#FFF7F4,#FFF0E8);"
                "border:1px solid rgba(232,92,26,.25);border-radius:10px;"
                "padding:10px 14px;margin:10px 0 6px'>"
                "<div style='font-size:12px;color:#7B2D00;font-weight:600'>"
                "✅ Eklenen alt gruplar senaryoya dahil edilecek.</div>"
                "</div>", unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # ── 2. MEVCUT ALT GRUP TALEBİ DEĞİŞTİR ─────────────────────────────
        st.markdown(_slabel("⚙️ Mevcut Alt Grup Talebi"), unsafe_allow_html=True)

        sec_i = st.selectbox(
            "Alt grup seç",
            options=I,
            format_func=lambda i: f"Kat.{i}  —  {'+'.join(sonuc['kod_i'][i])}",
            key="talep_sec_i")

        excel_val   = float(U_i_excel.get(sec_i, 0))
        gecerli_val = float(st.session_state["U_i_override"].get(sec_i, excel_val))
        fark_val    = gecerli_val - excel_val
        kat_r       = KAT_RENK[(sec_i - 1) % len(KAT_RENK)]

        mc1, mc2, mc3 = st.columns(3)
        def _mcard(label, val, color="#1B2A4A", bg="#FFFFFF", bl_color="#D8E2EE"):
            return (f"<div style='background:{bg};border:1px solid #D8E2EE;"
                    f"border-left:4px solid {bl_color};border-radius:8px;"
                    f"padding:12px;text-align:center'>"
                    f"<div style='font-size:10px;font-family:JetBrains Mono;font-weight:700;"
                    f"color:#7B90AA;text-transform:uppercase;letter-spacing:.12em;margin-bottom:6px'>{label}</div>"
                    f"<div style='font-size:26px;font-weight:800;color:{color};"
                    f"font-family:DM Sans,Inter,sans-serif;line-height:1'>{val}</div>"
                    f"<div style='font-size:10px;color:#9AACC5;margin-top:4px'>raf birimi</div></div>")

        with mc1:
            st.markdown(_mcard("Excel Değeri", f"{excel_val:.1f}", bl_color=kat_r),
                        unsafe_allow_html=True)
        with mc2:
            c2 = "#b45309" if abs(fark_val)>0.001 else "#15803d"
            bg2 = "#fffbeb" if abs(fark_val)>0.001 else "#f0fdf4"
            bl2 = "#f59e0b" if abs(fark_val)>0.001 else "#22c55e"
            st.markdown(_mcard("Güncel Değer", f"{gecerli_val:.1f}", c2, bg2, bl2),
                        unsafe_allow_html=True)
        with mc3:
            isaret = "+" if fark_val > 0 else ""
            c3  = "#dc2626" if fark_val>0 else ("#16a34a" if fark_val<0 else "#9AACC5")
            bg3 = "#fef2f2" if fark_val>0 else ("#f0fdf4" if fark_val<0 else "#F0F3F8")
            ok  = "▲" if fark_val>0 else ("▼" if fark_val<0 else "—")
            st.markdown(_mcard("Fark", f"{ok} {isaret}{fark_val:.1f}", c3, bg3, c3),
                        unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='font-size:13px;color:#1B2A4A;font-weight:600;margin-bottom:8px;"
            f"font-family:DM Sans,Inter,sans-serif'>Yeni Talep — Kat.{sec_i} "
            f"({'+'.join(sonuc['kod_i'][sec_i])})</div>",
            unsafe_allow_html=True)
        inp_col, btn_col, rst_col = st.columns([2.35, 1.45, 1.45], gap="small", vertical_alignment="bottom")
        with inp_col:
            yeni_val = st.number_input(
                "Yeni talep",
                min_value=0.0, max_value=9999.0, value=gecerli_val, step=0.5,
                key=f"ui_input_{sec_i}",
                label_visibility="collapsed")
        with btn_col:
            if st.button("💾 KAYDET", key="ui_kaydet", use_container_width=True):
                st.session_state["U_i_override"][sec_i] = yeni_val
                st.toast(f"Kat.{sec_i}: {excel_val:.1f} → {yeni_val:.1f}", icon="💾")
                st.rerun()
        with rst_col:
            if st.button("↩️ SIFIRLA", key="ui_sifirla_tek", use_container_width=True):
                st.session_state["U_i_override"].pop(sec_i, None)
                st.rerun()

        # Değişiklikler özeti
        degisen = {i: v for i, v in st.session_state["U_i_override"].items()
                   if abs(v - U_i_excel.get(i, v)) > 0.001}
        if degisen:
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            for di, dv in degisen.items():
                ov = U_i_excel.get(di, dv); fv = dv - ov
                fr = "#dc2626" if fv > 0 else "#16a34a"
                dr = KAT_RENK[(di-1) % len(KAT_RENK)]
                isaret_i = "+" if fv > 0 else ""
                st.markdown(
                    f"<div style='display:flex;align-items:center;gap:10px;padding:8px 12px;"
                    f"background:#FFFFFF;border-left:3px solid {dr};border-radius:6px;"
                    f"border:1px solid #D8E2EE;font-size:13px;margin-bottom:4px'>"
                    f"<span style='color:#1B2A4A;flex:1;font-weight:600'>"
                    f"Kat.{di} — {'+'.join(sonuc['kod_i'][di])}</span>"
                    f"<span style='color:#9AACC5'>{ov:.1f}</span>"
                    f"<span style='color:#CBD5E1'>→</span>"
                    f"<span style='color:{fr};font-weight:700'>{dv:.1f}</span>"
                    f"<span style='color:{fr};font-size:11px'>({isaret_i}{fv:.1f})</span>"
                    f"</div>", unsafe_allow_html=True)
            if st.button("↩️ Tümünü Sıfırla", key="reset_ui_all",
                         use_container_width=True):
                st.session_state["U_i_override"] = {}
                st.rerun()

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # ── 3. SENARYO PARAMETRELERİ & ÇALIŞTIR ─────────────────────────────
        st.markdown(_slabel("🚀 Senaryo Parametreleri & Çalıştır"), unsafe_allow_html=True)

        sc1, sc2 = st.columns(2)
        with sc1: sb = st.slider("B_MAX (maks. blok/kategori)", 2, 15, b_max, key="sb")
        with sc2: sk = st.slider("MAX_KOR (maks. koridor)", 1, 4, max_kor, key="sk")

        dosya_adi = yuklenen.name if yuklenen else "bilinmiyor"
        prefix = dosya_adi.replace(".xlsx", "")
        if degisen: prefix += f"_Ui{len(degisen)}deg"
        if st.session_state["yeni_altgruplar"]:
            prefix += f"_+{len(st.session_state['yeni_altgruplar'])}yeni"
        _default_ad = f"{prefix}__B{sb}_K{sk}"
        # Varsayılan değer değişince input'u sıfırla
        if st.session_state.get("_sen_ad_default") != _default_ad:
            st.session_state["_sen_ad_default"] = _default_ad
            st.session_state["sen_ad_input"] = _default_ad
        sen_ad = st.text_input("Senaryo adı", key="sen_ad_input")

        run_col2, save_col2 = st.columns([1.35, 1.35])
        with save_col2:
            if st.button("💾 KAYDET", key="save_current", use_container_width=True):
                _senaryo_kaydet(sen_ad, sonuc, blok_ozet, I, K)
                st.success(f"✅ '{sen_ad}' kaydedildi!")
                st.rerun()

        with run_col2:
            calistir_senaryo = st.button(
                "🚀 ÇALIŞTIR", key="run_and_save",
                use_container_width=True, type="primary")

        # ── Kaydedilen Senaryolar ──────────────────────────────────────────
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        st.markdown(_slabel("📋 Kaydedilen Senaryolar"), unsafe_allow_html=True)
        if st.session_state["senaryolar"]:
            for _si, _sc in enumerate(st.session_state["senaryolar"]):
                _m = _sc["_meta"]
                _dur = _m.get("Durum", "")
                _dur_c = "#16a34a" if _dur == "OPTIMAL" else "#d97706"
                _dur_bg = "#f0fdf4" if _dur == "OPTIMAL" else "#fffbeb"
                _dur_bc = "#86efac" if _dur == "OPTIMAL" else "#fde047"
                _col_a, _col_b, _col_c, _col_d = st.columns([3, 2, 2, 1])
                with _col_a:
                    st.markdown(
                        f"<div style='background:#FFFFFF;border:1px solid #E0E8F0;"
                        f"border-left:3px solid #1B2A4A;border-radius:8px;"
                        f"padding:10px 14px;'>"
                        f"<div style='font-size:13px;font-weight:600;color:#1B2A4A;"
                        f"font-family:DM Sans,Inter,sans-serif'>{_m.get('Ad','')[:32]}</div>"
                        f"<div style='font-size:10px;color:#7B90AA;margin-top:2px;"
                        f"font-family:JetBrains Mono'>B_MAX={_m.get('B_MAX')} · KOR={_m.get('MAX_KOR')}"
                        f" · {_m.get('Süre(s)',0):.1f}s</div>"
                        f"</div>", unsafe_allow_html=True)
                with _col_b:
                    st.markdown(
                        f"<div style='background:#FFFFFF;border:1px solid #E0E8F0;"
                        f"border-radius:8px;padding:10px 14px;text-align:center'>"
                        f"<div style='font-size:9px;color:#7B90AA;font-family:JetBrains Mono;"
                        f"letter-spacing:.1em'>F×D MESAFE</div>"
                        f"<div style='font-size:16px;font-weight:500;color:#E85C1A;"
                        f"font-family:DM Mono,monospace;margin-top:3px'>"
                        f"{_m.get('Amaç',0):,.0f}</div>"
                        f"</div>", unsafe_allow_html=True)
                with _col_c:
                    st.markdown(
                        f"<div style='background:{_dur_bg};border:1px solid {_dur_bc};"
                        f"border-radius:8px;padding:10px 14px;text-align:center'>"
                        f"<div style='font-size:9px;color:#7B90AA;font-family:JetBrains Mono;"
                        f"letter-spacing:.1em'>DURUM</div>"
                        f"<div style='font-size:13px;font-weight:600;color:{_dur_c};"
                        f"font-family:DM Sans,Inter,sans-serif;margin-top:3px'>{_dur}</div>"
                        f"<div style='font-size:10px;color:#9AACC5;font-family:JetBrains Mono;"
                        f"margin-top:1px'>GAP {_m.get('Gap(%)',0):.2f}%</div>"
                        f"</div>", unsafe_allow_html=True)
                with _col_d:
                    st.markdown("<div style='padding-top:6px'>", unsafe_allow_html=True)
                    if st.button("🗑️", key=f"del_sen_{_si}", use_container_width=True):
                        st.session_state["senaryolar"].pop(_si)
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            if st.button("🗑️ Senaryoları Temizle", key="temizle_sen", use_container_width=True):
                st.session_state["senaryolar"] = []
                st.rerun()
        else:
            st.markdown(
                "<div style='background:#F8FAFC;border:1px dashed #D0DAE8;"
                "border-radius:10px;padding:20px;text-align:center'>"
                "<div style='font-size:24px;margin-bottom:8px'>📭</div>"
                "<div style='font-size:13px;color:#4A6280;font-family:DM Sans,Inter,sans-serif'>"
                "Henüz senaryo kaydedilmedi.</div>"
                "<div style='font-size:11px;color:#9AACC5;margin-top:4px'>"
                "Parametreleri ayarlayıp Modeli Çalıştır'a bas veya mevcut sonucu kaydet.</div>"
                "</div>", unsafe_allow_html=True)

    # ════════════════════════════ SAĞ: HARİTA ══════════════════════════════════
    with right_col:
        st.markdown(_slabel("🏭 Depo Haritası"), unsafe_allow_html=True)

        # Her iki butonu da dinle
        _calistir = calistir_senaryo or calistir_yeni_ag
        if _calistir:
            _db2 = st.session_state.get("_dosya_bytes")
            if not _db2:
                st.error("Excel dosyası bulunamadı.")
            else:
                with st.spinner("🔄 Gurobi çözüyor..."):
                    try:
                        # _mod zaten global scope'ta yüklenmiş — tekrar diskten okumaya gerek yok
                        _mod2 = _mod
                        veri_ov = _mod2.excel_oku(_db2)

                        # Mevcut U_i override
                        for oi, ov2 in st.session_state["U_i_override"].items():
                            if oi in veri_ov["U_i"]: veri_ov["U_i"][oi] = ov2

                        # Yeni alt grupları modele enjekte et
                        _yeni_aglar = st.session_state.get("yeni_altgruplar", {})
                        if _yeni_aglar:
                            _max_i = max(veri_ov["I"]) if veri_ov["I"] else 0
                            _hat2alan = {}
                            for _ei in list(veri_ov["I"]):
                                _eh = veri_ov.get("hat_i", {}).get(_ei)
                                _ea = veri_ov.get("alan_i", {}).get(_ei)
                                if _eh is not None and _ea is not None:
                                    _hat2alan[_eh] = _ea
                            for _ag_kod, _ag_bilgi in _yeni_aglar.items():
                                _new_i    = _max_i + 1
                                _max_i    = _new_i
                                _ag_hat   = _ag_bilgi["hat"]
                                _ag_alan  = _hat2alan.get(_ag_hat, "A")
                                _ag_talep = float(_ag_bilgi["talep"])
                                veri_ov["I"].append(_new_i)
                                veri_ov["U_i"][_new_i] = _ag_talep
                                _hat_cats = [_fi for _fi in veri_ov["I"]
                                             if veri_ov.get("hat_i",{}).get(_fi)==_ag_hat
                                             and _fi != _new_i]
                                _f_avg = (sum(veri_ov["F_i"].get(_fi,1.0) for _fi in _hat_cats)
                                          / len(_hat_cats)) if _hat_cats else 1.0
                                veri_ov["F_i"][_new_i] = _f_avg
                                if "hat_i"  in veri_ov: veri_ov["hat_i"][_new_i]  = _ag_hat
                                if "alan_i" in veri_ov: veri_ov["alan_i"][_new_i] = _ag_alan
                                if "kod_i"  in veri_ov: veri_ov["kod_i"][_new_i]  = [_ag_kod]
                                if "ad_i"   in veri_ov: veri_ov["ad_i"][_new_i]   = [_ag_kod]
                                _ref_cats = [_fi for _fi in veri_ov["I"]
                                             if veri_ov.get("hat_i",{}).get(_fi)==_ag_hat
                                             and _fi != _new_i]
                                if not _ref_cats:
                                    _ref_cats = [_fi for _fi in veri_ov["I"]
                                                 if veri_ov.get("alan_i",{}).get(_fi)==_ag_alan
                                                 and _fi != _new_i]
                                if _ref_cats:
                                    for (_ri, _rk), _rd in list(veri_ov["D_ik"].items()):
                                        if _ri == _ref_cats[0]:
                                            veri_ov["D_ik"][(_new_i, _rk)] = _rd
                            st.info(f"ℹ️ {len(_yeni_aglar)} yeni grup eklendi: "
                                    + ", ".join(_yeni_aglar.keys()))

                        _orig_oku = _mod2.excel_oku
                        _mod2.excel_oku = lambda _d, _v=veri_ov: _v
                        sonuc_ov = _mod2.model_calistir(
                            _db2, b_max=sb, max_kor=sk,
                            t_limit=t_limit, mip_gap=mip_gap/100.0)
                        _mod2.excel_oku = _orig_oku
                        st.session_state["sonuc"]         = sonuc_ov
                        st.session_state["_D_ik"]         = veri_ov["D_ik"]
                        st.session_state["_F_i"]          = veri_ov["F_i"]
                        st.session_state["_U_i_excel"]    = dict(U_i_excel)
                        st.session_state["manuel_atama"]  = {
                            ii: list(sonuc_ov["sonuc_kat"][ii]["bloklar"])
                            for ii in sonuc_ov["I"]}
                        # Yeni alt grupların gittiği blokları kaydet — haritada vurgulansın
                        _yeni_i_listesi = [_ni for _ni in sonuc_ov["I"]
                                           if _ni not in sonuc["I"]]
                        _vurgula = tuple(sorted({
                            _k for _ni in _yeni_i_listesi
                            for _k in sonuc_ov["sonuc_kat"][_ni]["bloklar"]
                        }))
                        st.session_state["_vurgula_bloklar"] = _vurgula
                        _senaryo_kaydet(sen_ad, sonuc_ov,
                                        sonuc_ov["blok_ozet"], sonuc_ov["I"], sonuc_ov["K"])
                        st.success(f"✅ {sonuc_ov['durum']} — {sonuc_ov['obj_val']:,.0f} | '{sen_ad}' kaydedildi")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Hata: {e}")

        # Haritayı cache'le — metin yazarken yeniden çizimi engelle
        _harita_sonuc = st.session_state.get("sonuc", sonuc)
        _vurgula_bloklar = st.session_state.get("_vurgula_bloklar", ())
        _sonuc_id = id(_harita_sonuc)
        if st.session_state.get("_tab4_harita_id") != (_sonuc_id, _vurgula_bloklar):
            _harita_kr = {i: KAT_RENK[idx % len(KAT_RENK)]
                          for idx, i in enumerate(_harita_sonuc["I"])}
            st.session_state["_tab4_fig_canli"] = harita_ciz(
                _harita_sonuc["sonuc_kat"], _harita_sonuc["blok_ozet"],
                _harita_sonuc["I"], _harita_sonuc["K"], _harita_kr, "tab4_live",
                vurgula_bloklar=_vurgula_bloklar)
            st.session_state["_tab4_harita_id"] = (_sonuc_id, _vurgula_bloklar)
        st.plotly_chart(
            st.session_state["_tab4_fig_canli"],
            use_container_width=True, key="tab4_harita_canli", config=FAST_PLOTLY_CONFIG)

        # ── Yeni alt grup atama kartları (mobil/tablet için harita altında göze çarpan özet) ──
        _yeni_aglar_listesi = st.session_state.get("yeni_altgruplar", {})
        _vb = st.session_state.get("_vurgula_bloklar", ())
        if _vb and _yeni_aglar_listesi:
            st.markdown(
                "<div style='background:linear-gradient(135deg,#1a0a00,#2d1200);"
                "border:2px solid #E85C1A;border-radius:12px;padding:12px 16px;margin:10px 0 6px'>"
                "<div style='font-family:JetBrains Mono;font-size:11px;font-weight:700;"
                "color:#FF7A3D;text-transform:uppercase;letter-spacing:.18em;margin-bottom:10px'>"
                "🆕 Yeni Alt Grup → Blok Ataması</div>",
                unsafe_allow_html=True)
            for _ag_kod in _yeni_aglar_listesi:
                # Bu koda ait kategori indexini bul
                _ag_i = next((
                    _ii for _ii in _harita_sonuc["I"]
                    if _ag_kod in (_harita_sonuc["sonuc_kat"][_ii].get("kodlar", []))
                ), None)
                if _ag_i is None:
                    continue
                _ag_s   = _harita_sonuc["sonuc_kat"][_ag_i]
                _ag_blk = _ag_s["bloklar"]
                _ag_alan = _ag_s.get("alan", "?")
                _ag_renk = KAT_RENK[(_ag_i - 1) % len(KAT_RENK)]
                _blok_str = "  ".join(
                    f"<span style='background:#E85C1A;color:#fff;border-radius:5px;"
                    f"padding:3px 8px;font-weight:800;font-size:14px'>B{_bk}</span>"
                    for _bk in _ag_blk
                )
                _kap_toplam = sum(_harita_sonuc["blok_ozet"][_bk]["kapasite"] for _bk in _ag_blk)
                _yuk_toplam = sum(_ag_s["u"].get(_bk, 0) for _bk in _ag_blk)
                _dol = _yuk_toplam / _kap_toplam * 100 if _kap_toplam else 0
                st.markdown(
                    f"<div style='background:rgba(255,255,255,0.06);border-left:4px solid {_ag_renk};"
                    f"border-radius:8px;padding:10px 14px;margin-bottom:8px'>"
                    f"<div style='display:flex;align-items:center;gap:10px;flex-wrap:wrap'>"
                    f"<span style='font-family:JetBrains Mono;font-size:16px;font-weight:800;"
                    f"color:#FFFFFF'>{_ag_kod}</span>"
                    f"<span style='color:#9AACC5;font-size:12px'>→ Alan {_ag_alan}</span>"
                    f"<span style='margin-left:auto;color:#9AACC5;font-size:11px'>"
                    f"{_yuk_toplam:.0f}/{_kap_toplam:.0f} raf · %{_dol:.0f}</span>"
                    f"</div>"
                    f"<div style='margin-top:8px;display:flex;gap:6px;flex-wrap:wrap'>{_blok_str}</div>"
                    f"</div>",
                    unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Haritanın okunabilirliğini artırmak için blok atamalarını ayrıca kompakt tabloda göster.
        # Model çıktısı değiştirilmez; yalnızca aynı sonuç kullanıcıya daha okunur sunulur.
        _atama_rows = []
        for _i in _harita_sonuc["I"]:
            _s = _harita_sonuc["sonuc_kat"][_i]
            for _k in _s["bloklar"]:
                _kap = _harita_sonuc["blok_ozet"][_k]["kapasite"]
                _yuk = _s["u"].get(_k, 0)
                _atama_rows.append({
                    "Blok": f"B{_k}",
                    "Alan": _harita_sonuc["blok_ozet"][_k].get("alan", "-"),
                    "Kategori": f"Kat.{_i}",
                    "Alt Grup": "+".join(_s.get("kodlar", [])),
                    "Yüklenen": round(_yuk, 1),
                    "Kapasite": round(_kap, 1),
                    "Doluluk": f"{(_yuk/_kap*100 if _kap else 0):.1f}%",
                    "Birincil": "✓" if _k == _s.get("birincil") else ""
                })
        _df_atama_canli = pd.DataFrame(_atama_rows)
        if not _df_atama_canli.empty:
            _df_atama_canli["_blok_no"] = _df_atama_canli["Blok"].str.replace("B", "", regex=False).astype(int)
            _df_atama_canli = _df_atama_canli.sort_values(["Alan", "_blok_no", "Kategori"]).drop(columns=["_blok_no"])
            with st.expander("📋 Blok Atama Özeti — haritadaki renkli blokların tablo karşılığı", expanded=True):
                st.dataframe(_df_atama_canli, hide_index=True, use_container_width=True)

        # Özet metrikler
        _t_kap = sum(_harita_sonuc["blok_ozet"][k]["kapasite"] for k in _harita_sonuc["K"])
        _t_yuk = sum(_harita_sonuc["blok_ozet"][k]["yuklu"]    for k in _harita_sonuc["K"])
        _dol   = _t_yuk/_t_kap*100 if _t_kap > 0 else 0
        _dur   = _harita_sonuc["durum"]
        _dur_renk = "#16a34a" if _dur=="OPTIMAL" else "#d97706"

        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(
                f"<div style='background:#FFFFFF;border:1px solid #D8E2EE;"
                f"border-top:3px solid {_dur_renk};border-radius:8px;padding:12px;text-align:center'>"
                f"<div style='font-size:9px;font-family:JetBrains Mono;color:#7B90AA;"
                f"text-transform:uppercase;letter-spacing:.14em'>Durum</div>"
                f"<div style='font-size:16px;font-weight:800;color:{_dur_renk};margin-top:4px'>{_dur}</div>"
                f"</div>", unsafe_allow_html=True)
        with m2:
            st.markdown(
                f"<div style='background:#FFFFFF;border:1px solid #D8E2EE;"
                f"border-top:3px solid #1B2A4A;border-radius:8px;padding:12px;text-align:center'>"
                f"<div style='font-size:9px;font-family:JetBrains Mono;color:#7B90AA;"
                f"text-transform:uppercase;letter-spacing:.14em'>Doluluk</div>"
                f"<div style='font-size:22px;font-weight:800;color:#1B2A4A;margin-top:4px'>{_dol:.1f}%</div>"
                f"</div>", unsafe_allow_html=True)
        with m3:
            st.markdown(
                f"<div style='background:#FFFFFF;border:1px solid #D8E2EE;"
                f"border-top:3px solid #E85C1A;border-radius:8px;padding:12px;text-align:center'>"
                f"<div style='font-size:9px;font-family:JetBrains Mono;color:#7B90AA;"
                f"text-transform:uppercase;letter-spacing:.14em'>F×D Mesafe</div>"
                f"<div style='font-size:22px;font-weight:800;color:#E85C1A;margin-top:4px'>"
                f"{_harita_sonuc['obj_val']:,.0f}</div>"
                f"</div>", unsafe_allow_html=True)

with tab5:
    st.markdown("### 📈 Senaryo Analizi — Karşılaştırma")
    if not st.session_state.get("senaryolar"):
        st.info("Henüz senaryo yok. 🔬 Senaryolar sekmesinden senaryo kaydedip buradan karşılaştırın.")
    else:
        df_s = pd.DataFrame([sc["_meta"] for sc in st.session_state["senaryolar"]])
        st.dataframe(df_s, hide_index=True, use_container_width=True)

        fig_cmp = px.bar(df_s, x="Ad", y="Amaç", color="Durum",
                         color_discrete_map={"OPTIMAL":"#4ade80","UYGUN":"#fbbf24"},
                         title="Senaryo Karşılaştırması — F×D Mesafe")
        fig_cmp.update_layout(paper_bgcolor="#F2F4F7", plot_bgcolor="#EEF2F8",
                              font=dict(color="#1B2A4A", family="JetBrains Mono"))
        st.plotly_chart(fig_cmp, use_container_width=True, config=FAST_PLOTLY_CONFIG)

        st.markdown("---")
        sen_adlar = [sc["_meta"]["Ad"] for sc in st.session_state["senaryolar"]]
        goruntuleme = st.radio("Mod", ["Tek senaryo", "İki senaryoyu karşılaştır"], horizontal=True)

        if goruntuleme == "Tek senaryo":
            secili = st.selectbox("Senaryo", sen_adlar, key="sen_tek")
            sc = next(s for s in st.session_state["senaryolar"] if s["_meta"]["Ad"]==secili)
            m  = sc["_meta"]
            bc = "b-opt" if m["Durum"]=="OPTIMAL" else "b-uyg"
            vc = "#4ade80" if m["Durum"]=="OPTIMAL" else "#fbbf24"
            st.markdown(f"""
            <div style='background:#FFFFFF;border:1px solid #DDE3ED;border-radius:10px;
                 padding:14px 18px;margin-bottom:12px;font-family:JetBrains Mono'>
              <span class='badge {bc}'>● {m["Durum"]}</span>
              <span style='color:#1B2A4A;font-size:18px;font-weight:600;margin-left:12px'>{m["Ad"]}</span>
              <div style='display:flex;gap:16px;margin-top:10px;font-size:12px'>
                <span style='color:#E85C1A'>F×D Mesafe: {m["Amaç"]:,}</span>
                <span style='color:#888'>Gap: {m["Gap(%)"]}%</span>
                <span style='color:#888'>Doluluk: {m["Doluluk(%)"]}%</span>
                <span style='color:#888'>B={m["B_MAX"]} K={m["MAX_KOR"]}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)
            if sc["_fig_harita"]: st.plotly_chart(sc["_fig_harita"], use_container_width=True, key=f"h_{secili}", config=FAST_PLOTLY_CONFIG)
            if sc["_fig_doluluk"]: st.plotly_chart(sc["_fig_doluluk"], use_container_width=True, key=f"d_{secili}", config=FAST_PLOTLY_CONFIG)
            st.dataframe(sc["_df_atama"], hide_index=True, use_container_width=True, height=400)
            st.download_button("📥 CSV", sc["_df_atama"].to_csv(index=False).encode(), f"{secili}.csv", "text/csv")

        else:
            ca,cb = st.columns(2)
            with ca: sec_a = st.selectbox("Sol", sen_adlar, key="sen_a")
            with cb: sec_b = st.selectbox("Sağ", sen_adlar, index=min(1,len(sen_adlar)-1), key="sen_b")
            sc_a = next(s for s in st.session_state["senaryolar"] if s["_meta"]["Ad"]==sec_a)
            sc_b = next(s for s in st.session_state["senaryolar"] if s["_meta"]["Ad"]==sec_b)

            def meta_kart(m):
                bc = "b-opt" if m["Durum"]=="OPTIMAL" else "b-uyg"
                vc = "#4ade80" if m["Durum"]=="OPTIMAL" else "#fbbf24"
                return f"""<div style='background:#FFFFFF;border:1px solid #DDE3ED;border-radius:10px;
                  padding:12px 14px;font-family:JetBrains Mono'>
                  <span class='badge {bc}'>● {m["Durum"]}</span>
                  <div style='font-size:16px;font-weight:600;color:#1B2A4A;margin:6px 0 2px'>{m["Ad"]}</div>
                  <div style='font-size:22px;font-weight:700;color:{vc}'>{m["Amaç"]:,}</div>
                  <div style='font-size:10px;color:#6B7E9E;margin-top:2px'>
                    Gap {m["Gap(%)"]}% | Doluluk {m["Doluluk(%)"]}% | B={m["B_MAX"]} K={m["MAX_KOR"]}
                  </div>
                </div>"""

            ca2,cb2 = st.columns(2)
            with ca2: st.markdown(meta_kart(sc_a["_meta"]), unsafe_allow_html=True)
            with cb2: st.markdown(meta_kart(sc_b["_meta"]), unsafe_allow_html=True)

            st.markdown("**🏭 Depo Haritaları**")
            ca3,cb3 = st.columns(2)
            with ca3:
                st.caption(sec_a)
                if sc_a["_fig_harita"]: st.plotly_chart(sc_a["_fig_harita"], use_container_width=True, key=f"ha_{sec_a}", config=FAST_PLOTLY_CONFIG)
            with cb3:
                st.caption(sec_b)
                if sc_b["_fig_harita"]: st.plotly_chart(sc_b["_fig_harita"], use_container_width=True, key=f"hb_{sec_b}", config=FAST_PLOTLY_CONFIG)

            if sc_a["_fig_doluluk"] or sc_b["_fig_doluluk"]:
                st.markdown("**📊 Blok Doluluk**")
                ca4,cb4 = st.columns(2)
                with ca4:
                    if sc_a["_fig_doluluk"]: st.plotly_chart(sc_a["_fig_doluluk"], use_container_width=True, key=f"da_{sec_a}", config=FAST_PLOTLY_CONFIG)
                with cb4:
                    if sc_b["_fig_doluluk"]: st.plotly_chart(sc_b["_fig_doluluk"], use_container_width=True, key=f"db_{sec_b}", config=FAST_PLOTLY_CONFIG)

            st.markdown("**📋 Atama Tabloları**")
            ca5,cb5 = st.columns(2)
            with ca5:
                st.dataframe(sc_a["_df_atama"], hide_index=True, use_container_width=True, height=350)
                st.download_button(f"📥 {sec_a}", sc_a["_df_atama"].to_csv(index=False).encode(), f"{sec_a}.csv", key=f"dl_a_{sec_a}")
            with cb5:
                st.dataframe(sc_b["_df_atama"], hide_index=True, use_container_width=True, height=350)
                st.download_button(f"📥 {sec_b}", sc_b["_df_atama"].to_csv(index=False).encode(), f"{sec_b}.csv", key=f"dl_b_{sec_b}")
# Çalıştırma örneği:
# cd "C:/Users/nuryi/OneDrive - gazi.edu.tr/Masaüstü/gurobiçözüm/kit_atama_ui" :streamlit run ui.py
# cd C:\Users\nuryi\Downloads
#.\cloudflared-windows-amd64.exe tunnel --url http://localhost:8501
