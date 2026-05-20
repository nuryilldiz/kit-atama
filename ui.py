import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import importlib.util, sys, os, copy, time

st.set_page_config(
    page_title="Kit Atama Opt. — TürkTraktör",
    page_icon="🏭", layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&family=Barlow+Condensed:wght@400;600;700;800&family=Barlow:wght@400;500;600;700;800&display=swap');

* { box-sizing: border-box; }

/* ══ ANA UYGULAMA ══ */
.stApp {
    background: #F0F3F8;
    color: #1B2A4A;
    font-family: 'Barlow', 'Inter', sans-serif;
}

/* Üst toolbar gizle */
header[data-testid="stHeader"] { background: transparent !important; }

/* ══ SIDEBAR ══ */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F1E38 0%, #1B2A4A 40%, #162239 100%) !important;
    border-right: 3px solid #E85C1A !important;
    min-width: 280px !important;
    overflow: hidden !important;
    position: relative !important;
}
/* Streamlit'in iç scrollable container — tüm versiyonlar */
section[data-testid="stSidebar"] > div:first-child {
    overflow-y: auto !important;
    overflow-x: hidden !important;
    height: 100vh !important;
    padding-bottom: 80px !important;
    scrollbar-width: thin !important;
    scrollbar-color: #E85C1A #1B2A4A !important;
}
section[data-testid="stSidebar"] > div:first-child::-webkit-scrollbar { width: 5px; }
section[data-testid="stSidebar"] > div:first-child::-webkit-scrollbar-track { background: #1B2A4A; }
section[data-testid="stSidebar"] > div:first-child::-webkit-scrollbar-thumb { background: #E85C1A; border-radius: 3px; }
/* Streamlit 1.28+ stSidebarContent hedefi */
div[data-testid="stSidebarContent"] {
    overflow-y: auto !important;
    height: 100vh !important;
    padding-bottom: 80px !important;
}
/* İç dikey blokların overflow'unu serbest bırak */
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"],
section[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
    overflow: visible !important;
}
section[data-testid="stSidebar"] * { color: #C8D8EA !important; }
section[data-testid="stSidebar"] label { color: #8FAECB !important; font-size:11px !important; font-family:'JetBrains Mono',monospace !important; letter-spacing:.06em !important; }
section[data-testid="stSidebar"] .stSlider > div > div { background: rgba(232,92,26,0.2) !important; }
section[data-testid="stSidebar"] .stSlider > div > div > div { background: #E85C1A !important; border: 2px solid #FF8A5C !important; }
section[data-testid="stSidebar"] input { background: #243554 !important; color: #FFFFFF !important; border: 1px solid #3A5070 !important; border-radius: 6px !important; }
section[data-testid="stSidebar"] .stNumberInput input { color: #FFFFFF !important; }

/* ══ KPI KARTLARI ══ */
.kpi {
    flex: 1;
    background: #FFFFFF;
    border: 1px solid #D8E2EE;
    border-top: 4px solid #CBD8E8;
    border-radius: 12px;
    padding: 14px 18px;
    box-shadow: 0 2px 12px rgba(27,42,74,.07);
    transition: transform .15s, box-shadow .15s;
}
.kpi:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(27,42,74,.12); }
.kpi .lbl {
    font-size: 10px;
    color: #7B90AA;
    text-transform: uppercase;
    letter-spacing: .14em;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    margin-bottom: 6px;
}
.kpi .val {
    font-size: 24px;
    font-weight: 800;
    color: #1B2A4A;
    font-family: 'Barlow Condensed', 'JetBrains Mono', monospace;
    line-height: 1;
}
.kpi.green  { border-top-color: #22c55e; }  .kpi.green .val  { color: #16a34a; }
.kpi.yellow { border-top-color: #f59e0b; }  .kpi.yellow .val { color: #d97706; }
.kpi.red    { border-top-color: #ef4444; }  .kpi.red .val    { color: #dc2626; }
.kpi.orange { border-top-color: #E85C1A; }  .kpi.orange .val { color: #E85C1A; }
.kpi.blue   { border-top-color: #1B2A4A; }  .kpi.blue .val   { color: #1B2A4A; }

/* ══ BÖLÜM BAŞLIĞI ══ */
.slabel {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    font-weight: 700;
    color: #E85C1A;
    text-transform: uppercase;
    letter-spacing: .22em;
    padding-bottom: 7px;
    border-bottom: 2px solid #E85C1A;
    margin-bottom: 12px;
}
section[data-testid="stSidebar"] .slabel { color: #E85C1A !important; border-bottom-color: rgba(232,92,26,.5) !important; }

/* ══ BADGE ══ */
.badge { display:inline-flex; align-items:center; gap:5px; padding:4px 12px; border-radius:20px; font-size:11px; font-family:'JetBrains Mono',monospace; font-weight:700; letter-spacing:.04em; }
.b-opt { background:#dcfce7; color:#15803d; border:1px solid #86efac; }
.b-uyg { background:#fef9c3; color:#a16207; border:1px solid #fde047; }
.b-err { background:#fee2e2; color:#dc2626; border:1px solid #fca5a5; }

/* ══ BUTONLAR ══ */
.stButton > button {
    background: linear-gradient(135deg, #E85C1A 0%, #FF7A3D 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Barlow', sans-serif !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    letter-spacing: .06em !important;
    text-transform: uppercase !important;
    transition: all .2s ease !important;
    box-shadow: 0 3px 12px rgba(232,92,26,.4) !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #FF7A3D 0%, #FFB08A 100%) !important;
    box-shadow: 0 6px 20px rgba(232,92,26,.6) !important;
    transform: translateY(-2px) !important;
}
.run-btn > .stButton > button {
    background: linear-gradient(135deg, #0F1E38 0%, #1B2A4A 50%, #243554 100%) !important;
    box-shadow: 0 3px 12px rgba(15,30,56,.5) !important;
    font-size: 15px !important;
    padding: 14px 20px !important;
    border-top: 2px solid #E85C1A !important;
    letter-spacing: .1em !important;
}
.run-btn > .stButton > button:hover {
    background: linear-gradient(135deg, #1B2A4A 0%, #2A4170 100%) !important;
    box-shadow: 0 6px 22px rgba(15,30,56,.65) !important;
    border-top-color: #FF8A5C !important;
}

/* ══ SEKMELER ══ */
div[data-testid="stTabs"] { border-bottom: 2px solid #D8E2EE !important; }
div[data-testid="stTabs"] button {
    font-family: 'Barlow', sans-serif !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    color: #7B90AA !important;
    letter-spacing: .04em !important;
    text-transform: uppercase !important;
    padding: 10px 20px !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #E85C1A !important;
    border-bottom: 3px solid #E85C1A !important;
}
div[data-testid="stTabs"] button:hover { color: #1B2A4A !important; }

/* ══ INPUT ETİKETLERİ ══ */
div[data-testid="stSlider"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] label {
    font-size: 11px !important;
    color: #4A6280 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: .08em !important;
}

/* ══ METRİK KARTLARI (üç sütunlu) ══ */
.metric-card {
    background: #FFFFFF;
    border: 1px solid #D8E2EE;
    border-radius: 10px;
    padding: 16px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(27,42,74,.06);
}
.metric-card .mc-label {
    font-size: 9px;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    color: #7B90AA;
    text-transform: uppercase;
    letter-spacing: .16em;
    margin-bottom: 8px;
}
.metric-card .mc-value {
    font-size: 30px;
    font-weight: 800;
    font-family: 'Barlow Condensed', monospace;
    color: #1B2A4A;
    line-height: 1;
}
.metric-card .mc-unit {
    font-size: 10px;
    color: #9AACC5;
    margin-top: 5px;
    font-family: 'Inter', sans-serif;
}

/* ══ BAŞLIKLAR ══ */
h1, h2, h3 { font-family: 'Barlow Condensed', sans-serif !important; color: #1B2A4A !important; font-weight: 700 !important; letter-spacing: .02em !important; }
h3 { font-size: 20px !important; }
p, li { color: #2C3E55; }

/* ══ TABLO ══ */
.stDataFrame { border-radius: 10px; overflow: hidden; border: 1px solid #D8E2EE; box-shadow: 0 2px 8px rgba(27,42,74,.05); }
.stDataFrame thead th { background: #1B2A4A !important; color: #FFFFFF !important; font-family: 'Barlow', sans-serif !important; font-weight: 700 !important; font-size: 12px !important; }

/* ══ RADIO / TOGGLE ══ */
div[data-testid="stRadio"] label { font-size: 13px !important; color: #1B2A4A !important; font-weight: 600 !important; font-family: 'Barlow', sans-serif !important; }

/* ══ SUCCESS / ERROR MESAJLARI ══ */
.stSuccess { background: #f0fdf4 !important; border-left: 4px solid #22c55e !important; border-radius: 8px !important; }
.stError   { background: #fef2f2 !important; border-left: 4px solid #ef4444 !important; border-radius: 8px !important; }
.stWarning { background: #fffbeb !important; border-left: 4px solid #f59e0b !important; border-radius: 8px !important; }
.stInfo    { background: #eff6ff !important; border-left: 4px solid #3b82f6 !important; border-radius: 8px !important; }

/* ══ DIVIDER ══ */
.tt-divider { height: 1px; background: linear-gradient(90deg, transparent, #E85C1A 30%, #E85C1A 70%, transparent); margin: 14px 0; opacity: .5; }

/* == RESPONSIVE LAYOUT - sidebar kapaninca icerik genislesin == */
section[data-testid="stSidebar"][aria-expanded="false"] {
    min-width: 0 !important;
    width: 0 !important;
    overflow: hidden !important;
    border-right: none !important;
}

/* Ana icerik her zaman kalan alani doldursun */
.main .block-container,
div[data-testid="stMainBlockContainer"],
div.block-container {
    max-width: 100% !important;
    width: 100% !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    transition: padding 0.3s ease !important;
}

/* AppView flex container */
div[data-testid="stAppViewContainer"] {
    display: flex !important;
    flex-direction: row !important;
    align-items: flex-start !important;
}
div[data-testid="stAppViewContainer"] > section[data-testid="stMain"],
div[data-testid="stAppViewContainer"] > div.main {
    flex: 1 1 0% !important;
    min-width: 0 !important;
    overflow: hidden !important;
}

/* Mobil uyum */
@media (max-width: 768px) {
    .main .block-container,
    div[data-testid="stMainBlockContainer"] {
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
    }
    .kpi { padding: 10px 12px !important; }
    .kpi .val { font-size: 18px !important; }
    section[data-testid="stSidebar"] { min-width: 240px !important; }
}
</style>
""", unsafe_allow_html=True)

# ── SABITLER ─────────────────────────────────────────────────────────────────
ALAN_RENK  = {"A":"#06b6d4","B":"#a855f7","C":"#22c55e","D":"#eab308"}
ALAN_RGBA  = {"A":"rgba(6,182,212,.08)","B":"rgba(168,85,247,.08)","C":"rgba(34,197,94,.08)","D":"rgba(234,179,8,.08)"}
KAT_RENK   = ["#ef4444","#f97316","#eab308","#22c55e","#06b6d4","#3b82f6","#8b5cf6",
               "#ec4899","#14b8a6","#f59e0b","#84cc16","#6366f1","#e11d48","#0891b2",
               "#d946ef","#0ea5e9","#a3e635"]

W, H = 35, 150
BLOK_LAYOUT = {
    8: {"x":20,"y":30,"w":W,"h":H,"alan":"B"}, 9: {"x":65,"y":30,"w":W,"h":H,"alan":"B"},
    4: {"x":20,"y":210,"w":W,"h":H,"alan":"A"}, 5: {"x":65,"y":210,"w":W,"h":H,"alan":"A"},
    6: {"x":110,"y":210,"w":W,"h":H,"alan":"A"}, 7: {"x":180,"y":210,"w":W,"h":H,"alan":"A"},
    1: {"x":20,"y":370,"w":W,"h":H,"alan":"A"}, 2: {"x":65,"y":370,"w":W,"h":H,"alan":"A"},
    3: {"x":110,"y":370,"w":W,"h":H,"alan":"A"},
    15:{"x":230,"y":30,"w":W,"h":H,"alan":"C"}, 16:{"x":275,"y":30,"w":W,"h":H,"alan":"C"},
    17:{"x":320,"y":30,"w":W,"h":H,"alan":"C"}, 18:{"x":365,"y":30,"w":W,"h":H,"alan":"C"},
    19:{"x":410,"y":30,"w":W,"h":H,"alan":"C"}, 20:{"x":455,"y":30,"w":W,"h":H,"alan":"C"},
    21:{"x":500,"y":30,"w":W,"h":H,"alan":"C"},
    10:{"x":230,"y":190,"w":W,"h":H,"alan":"C"}, 11:{"x":275,"y":190,"w":W,"h":H,"alan":"C"},
    12:{"x":320,"y":190,"w":W,"h":H,"alan":"C"}, 13:{"x":365,"y":190,"w":W,"h":H,"alan":"C"},
    14:{"x":410,"y":190,"w":W,"h":H,"alan":"C"},
    22:{"x":545,"y":110,"w":W,"h":H,"alan":"C"}, 23:{"x":590,"y":110,"w":W,"h":H,"alan":"C"},
    24:{"x":635,"y":110,"w":W,"h":H,"alan":"C"}, 25:{"x":680,"y":110,"w":W,"h":H,"alan":"C"},
    26:{"x":720,"y":220,"w":70,"h":35,"alan":"D"}, 29:{"x":800,"y":220,"w":70,"h":35,"alan":"D"},
    27:{"x":720,"y":265,"w":70,"h":35,"alan":"D"}, 30:{"x":800,"y":265,"w":70,"h":35,"alan":"D"},
    28:{"x":720,"y":310,"w":70,"h":35,"alan":"D"}, 31:{"x":800,"y":310,"w":70,"h":35,"alan":"D"},
}
ALAN_BOUNDS = {"B":(10,115,15,195),"A":(10,230,195,535),"C":(220,730,15,355),"D":(735,915,205,360)}

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
def harita_ciz(sonuc_kat, blok_ozet, I, K, kat_renk, key_suffix=""):
    blok_katlar = {}
    for i in I:
        for k in sonuc_kat[i]["bloklar"]:
            blok_katlar.setdefault(k, [])
            if sonuc_kat[i]["birincil"] == k:
                blok_katlar[k].insert(0, i)
            else:
                blok_katlar[k].append(i)

    fig = go.Figure()

    for alan, (x0,x1,y0,y1) in ALAN_BOUNDS.items():
        r = ALAN_RENK[alan]
        fig.add_shape(type="rect",x0=x0,y0=y0,x1=x1,y1=y1,
                      fillcolor=ALAN_RGBA[alan],line=dict(color=r,width=1.5,dash="dot"),layer="below")
        fig.add_annotation(x=(x0+x1)/2,y=y1+10,text=f"<b>Alan {alan}</b>",
                           font=dict(color=r,size=14,family="JetBrains Mono,Barlow"),showarrow=False)

    for blok_no, lo in BLOK_LAYOUT.items():
        bx,by,bw,bh = lo["x"],lo["y"],lo["w"],lo["h"]
        ozet = blok_ozet.get(blok_no,{})
        kap  = ozet.get("kapasite",1)
        tip  = ozet.get("tip","Mevcut")
        dash = "dash" if tip=="Aday" else "solid"
        katlar = blok_katlar.get(blok_no,[])

        if not katlar:
            fig.add_shape(type="rect",x0=bx,y0=by,x1=bx+bw,y1=by+bh,
                          fillcolor="#243554",line=dict(color="#3A5070",width=1,dash=dash))
            fig.add_annotation(x=bx+bw/2,y=by+bh/2,text=f"<b>{blok_no}</b>",
                               font=dict(color="#A8BDD6",size=11,family="JetBrains Mono"),showarrow=False)
        elif len(katlar)==1:
            i0 = katlar[0]; fill = kat_renk[i0]
            kodlar = "+".join(sonuc_kat[i0]["kodlar"])
            yuklu  = sonuc_kat[i0]["u"].get(blok_no,0)
            dol    = yuklu/kap*100 if kap>0 else 0
            fig.add_shape(type="rect",x0=bx,y0=by,x1=bx+bw,y1=by+bh,
                          fillcolor=fill,line=dict(color=fill,width=1.5,dash=dash))
            fig.add_annotation(x=bx+bw/2,y=by+bh/2-12,text=f"<b>{blok_no}</b>",
                               font=dict(color="white",size=11,family="JetBrains Mono"),showarrow=False)
            fig.add_annotation(x=bx+bw/2,y=by+bh/2+8,text=kodlar[:8],
                               font=dict(color="white",size=9,family="JetBrains Mono"),showarrow=False)
            fig.add_annotation(x=bx+bw/2,y=by+bh/2+22,text=f"{dol:.0f}%",
                               font=dict(color="rgba(255,255,255,0.85)",size=8,family="JetBrains Mono"),showarrow=False)
        else:
            n = len(katlar); dw = bw/n
            for idx,i0 in enumerate(katlar):
                dx0=bx+idx*dw; dx1=bx+(idx+1)*dw
                fill=kat_renk[i0]; kodlar="+".join(sonuc_kat[i0]["kodlar"])
                fig.add_shape(type="rect",x0=dx0,y0=by,x1=dx1,y1=by+bh,
                              fillcolor=fill,line=dict(color="white",width=0.8,dash=dash))
                fig.add_annotation(x=(dx0+dx1)/2,y=by+bh/2+4,text=kodlar[:6],
                                   font=dict(color="white",size=6,family="JetBrains Mono"),showarrow=False)
            fig.add_annotation(x=bx+bw/2,y=by+8,text=f"<b>{blok_no}</b>",
                               font=dict(color="white",size=8,family="JetBrains Mono"),showarrow=False)

        kull = "<br>".join(f"Kat.{ki}: {uv:.0f}/{kap:.0f} ({uv/kap*100:.0f}%)"
                           for ki,uv in ozet.get("kullananlar",[]))
        fig.add_trace(go.Scatter(x=[bx+bw/2],y=[by+bh/2],mode="markers",
            marker=dict(size=max(bw,bh)*0.8,opacity=0),showlegend=False,
            hovertemplate=f"<b>Blok {blok_no}</b><br>Doluluk: {ozet.get('doluluk',0):.1f}%<br>{kull}<extra></extra>"))

    for i in I:
        s = sonuc_kat[i]
        fig.add_trace(go.Scatter(x=[None],y=[None],mode="markers",
            marker=dict(size=10,color=kat_renk[i],symbol="square"),
            name=f"Kat.{i} — {'+'.join(s['adlar'])[:28]}",showlegend=True))

    fig.update_layout(
        height=700,margin=dict(l=5,r=5,t=30,b=10),
        paper_bgcolor="#F2F4F7",plot_bgcolor="#1B2A4A",
        xaxis=dict(showgrid=False,showticklabels=False,zeroline=False,range=[-10,920]),
        yaxis=dict(showgrid=False,showticklabels=False,zeroline=False,range=[0,560],autorange="reversed"),
        legend=dict(bgcolor="#FFFFFF",bordercolor="#DDE3ED",borderwidth=1,
                    font=dict(color="#1B2A4A",size=11,family="JetBrains Mono"),x=1.01,y=1),
        font=dict(family="JetBrains Mono",color="#D8E4F0"),
    )
    return fig

# ── SAYFA BAŞLIĞI ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='display:flex;align-items:center;justify-content:space-between;
     background:linear-gradient(135deg,#0F1E38 0%,#1B2A4A 60%,#243554 100%);
     border-radius:14px;padding:20px 28px;margin-bottom:20px;
     box-shadow:0 4px 24px rgba(15,30,56,.25);
     border-left:5px solid #E85C1A;'>
  <div style='display:flex;align-items:center;gap:20px'>
  <img src='data:image/png;base64,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'
       style='height:54px;object-fit:contain' onerror="this.style.display='none'">
  <div>
    <div>
      <div style='font-family:Barlow Condensed,Barlow,sans-serif;font-size:26px;font-weight:800;color:#FFFFFF;letter-spacing:.04em;text-transform:uppercase'>
        Kit Atama Optimizasyon Sistemi
      </div>
      <div style='font-size:12px;color:#8FAECB;margin-top:4px;font-family:Inter;letter-spacing:.02em'>
        🏭 TürkTraktör Fabrikası &nbsp;·&nbsp; Depo Yerleşim Optimizasyonu &nbsp;·&nbsp; Gazi Üniversitesi
      </div>
    </div>
  </div>
    </div>
  <div style='text-align:right'>
    <div style='font-family:JetBrains Mono,monospace;font-size:9px;color:#8FAECB;text-transform:uppercase;letter-spacing:.16em;margin-bottom:4px'>Sistem</div>
    <div style='display:inline-flex;align-items:center;gap:6px;background:rgba(34,197,94,.15);border:1px solid rgba(34,197,94,.3);border-radius:20px;padding:4px 12px'>
      <div style='width:7px;height:7px;background:#22c55e;border-radius:50%;box-shadow:0 0 6px #22c55e'></div>
      <span style='font-family:JetBrains Mono,monospace;font-size:10px;color:#86efac;font-weight:700;letter-spacing:.08em'>AKTİF</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:14px 4px 8px'>
      <div style='display:flex;align-items:center;gap:12px'>
        <img src='data:image/png;base64,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'
             style='height:36px;object-fit:contain' onerror="this.style.display='none'">
        <div>
          <div style='font-family:Barlow Condensed,Barlow,sans-serif;font-size:16px;font-weight:800;color:#FFFFFF;letter-spacing:.06em;text-transform:uppercase'>Kit Atama</div>
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
    <div style='background:#243554;border:1px solid #3A5070;border-left:3px solid #E85C1A;border-radius:8px;padding:10px 13px;margin:10px 0;font-family:JetBrains Mono;font-size:11px;line-height:2'>
      <span style='color:#A8BDD6'>B_MAX</span><span style='color:#FFFFFF;float:right;font-weight:600'>{b_max}</span><br>
      <span style='color:#A8BDD6'>MAX_KOR</span><span style='color:#FFFFFF;float:right;font-weight:600'>{max_kor}</span><br>
      <span style='color:#A8BDD6'>T_LIMIT</span><span style='color:#FFFFFF;float:right;font-weight:600'>{t_limit} sn</span><br>
      <span style='color:#A8BDD6'>MIP_GAP</span><span style='color:#FFFFFF;float:right;font-weight:600'>{mip_gap}%</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:1px;background:linear-gradient(90deg,transparent,#E85C1A,transparent);margin:10px 0'></div>", unsafe_allow_html=True)

    st.markdown('<div class="run-btn">', unsafe_allow_html=True)
    calistir = st.button("🚀  MODELİ ÇALIŞTIR", use_container_width=True)
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
          <div style='font-family:JetBrains Mono;font-size:26px;font-weight:600;color:{vc};margin:8px 0 2px'>{s.get("obj_val",0):,.0f}</div>
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
        <div style='font-family:Barlow Condensed,Barlow,sans-serif;font-size:30px;font-weight:800;
             color:#1B2A4A;text-align:center;text-transform:uppercase;letter-spacing:.06em'>
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
          <div style='font-size:22px;font-weight:800;color:#E85C1A;font-family:Barlow Condensed,sans-serif'>MIP</div>
          <div style='font-size:9px;color:#7B90AA;font-family:JetBrains Mono;text-transform:uppercase;letter-spacing:.1em;margin-top:3px'>Optimizasyon</div>
        </div>
        <div style='background:#FFFFFF;border:1px solid #D8E2EE;border-top:3px solid #1B2A4A;
             border-radius:10px;padding:14px 20px;text-align:center;min-width:120px;
             box-shadow:0 2px 10px rgba(27,42,74,.08)'>
          <div style='font-size:22px;font-weight:800;color:#1B2A4A;font-family:Barlow Condensed,sans-serif'>GUROBI</div>
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
tab1, tab4, tab5, tab3, tab2 = st.tabs([
    "🏭 Depo Haritası",
    "📈 Senaryo Analizi",
    "🔬 Senaryolar",
    "📊 Blok Doluluk",
    "📦 Kategori Atama",
])

# ══ TAB 1: DEPO HARİTASI ════════════════════════════════════════════════════
with tab1:
    mod = st.radio("", ["🤖 Optimal Çözüm","⚖️ Optimal vs Manuel Karşılaştırma"],
                   horizontal=True, label_visibility="collapsed")

    fig_opt = harita_ciz(sonuc_kat, blok_ozet, I, K, kat_renk)
    st.session_state["_harita_fig"] = fig_opt

    if mod == "🤖 Optimal Çözüm":
        st.plotly_chart(fig_opt, use_container_width=True, key="harita_opt")

    else:
        # Manuel karşılaştırma
        D_ik = st.session_state.get("_D_ik")
        F_i  = st.session_state.get("_F_i")
        if D_ik is None:
            st.info("Manuel karşılaştırma için modeli bir kez çalıştırın.")
            st.plotly_chart(fig_opt, use_container_width=True, key="harita_opt2")
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
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            with ctrl4:
                st.markdown("<div style='margin-top:26px'>", unsafe_allow_html=True)
                if st.button("🔄 Sıfırla", key="man_sifirla", use_container_width=True):
                    st.session_state["manuel_atama"] = {i: list(sonuc_kat[i]["bloklar"]) for i in I}
                    st.session_state.pop("manuel_dogrula_sonuc", None)
                    st.rerun()
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
                    _fig_m = harita_ciz(man_sonuc_kat_k, man_blok_ozet_k, I, K, _kat_renk_m, str(int(_t.time()*1000)))
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
                if st.button("🔬 Manuel Atamayı Modelle Doğrula", use_container_width=True, key="dogrula_btn"):
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
                st.plotly_chart(fig_opt, use_container_width=True, key="harita_opt_cmp")
            with col_man:
                st.markdown("<div style='font-size:12px;color:#fbbf24;font-family:JetBrains Mono;margin-bottom:4px;text-align:center'>✋ MANUEL</div>", unsafe_allow_html=True)
                st.plotly_chart(fig_man, use_container_width=True, key="harita_man")


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
        st.plotly_chart(fig3, use_container_width=True)

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
                          _kat_renk_s, str(int(_time.time()*1000)))
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
    left_col, right_col = st.columns([1, 1], gap="large")

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

        yeni_kod = st.text_input(
            "Alt grup adı / kodu",
            key="yeni_ag_kod",
            placeholder="örn: UTRDK, MOTOR, SANZIMAN")

        yeni_talep = st.number_input(
            "Miktar (raf birimi)",
            min_value=1.0, max_value=9999.0,
            value=10.0, step=1.0, key="yeni_ag_talep")

        hat_sec_idx = st.selectbox(
            "Montaj Hattı",
            range(len(mevcut_hatlar)),
            format_func=lambda x: hat_label(mevcut_hatlar[x]),
            key="yeni_ag_hat_idx")
        yeni_hat = mevcut_hatlar[hat_sec_idx]

        ag_ekle_col, ag_sil_col = st.columns(2)
        with ag_ekle_col:
            if st.button("✅ Listeye Ekle", key="yeni_ag_ekle", use_container_width=True):
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
        with ag_sil_col:
            if st.button("🗑️ Tümünü Sil", key="yeni_ag_hepsini_sil", use_container_width=True):
                st.session_state["yeni_altgruplar"] = {}
                st.rerun()

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

            # ── Hemen altında "Modeli Çalıştır" butonu ──────────────────────
            st.markdown(
                "<div style='background:linear-gradient(135deg,#FFF7F4,#FFF0E8);"
                "border:1px solid rgba(232,92,26,.25);border-radius:10px;"
                "padding:12px 16px;margin:10px 0 6px'>"
                "<div style='font-size:12px;color:#7B2D00;font-weight:600'>"
                "✅ Gruplar hazır — modeli çalıştırarak depo atamasını görebilirsin.</div>"
                "</div>", unsafe_allow_html=True)
            calistir_yeni_ag = st.button(
                "🚀  YENİ GRUPLARLA MODELİ ÇALIŞTIR",
                key="run_yeni_ag_hizli", use_container_width=True, type="primary")
        else:
            calistir_yeni_ag = False

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
                    f"font-family:Barlow Condensed,sans-serif;line-height:1'>{val}</div>"
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
        inp_col, btn_col, rst_col = st.columns([3, 1, 1])
        with inp_col:
            yeni_val = st.number_input(
                f"Yeni talep — Kat.{sec_i} ({'+'.join(sonuc['kod_i'][sec_i])})",
                min_value=0.0, max_value=9999.0, value=gecerli_val, step=0.5,
                key=f"ui_input_{sec_i}")
        with btn_col:
            st.markdown("<div style='margin-top:28px'>", unsafe_allow_html=True)
            if st.button("💾 Kaydet", key="ui_kaydet", use_container_width=True):
                st.session_state["U_i_override"][sec_i] = yeni_val
                st.toast(f"Kat.{sec_i}: {excel_val:.1f} → {yeni_val:.1f}", icon="💾")
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        with rst_col:
            st.markdown("<div style='margin-top:28px'>", unsafe_allow_html=True)
            if st.button("↩️ Sıfırla", key="ui_sifirla_tek", use_container_width=True):
                st.session_state["U_i_override"].pop(sec_i, None)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

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
            if st.button("↩️ Tüm değişiklikleri sıfırla", key="reset_ui_all",
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
        sen_ad = st.text_input("Senaryo adı", f"{prefix}__B{sb}_K{sk}", key="sen_ad_input")

        run_col2, save_col2 = st.columns(2)
        with save_col2:
            if st.button("💾 Mevcut sonucu kaydet", key="save_current", use_container_width=True):
                _senaryo_kaydet(sen_ad, sonuc, blok_ozet, I, K)
                st.success(f"✅ '{sen_ad}' kaydedildi!")
                st.rerun()

        with run_col2:
            calistir_senaryo = st.button(
                "🚀  MODELİ ÇALIŞTIR", key="run_and_save",
                use_container_width=True, type="primary")

        # Senaryo listesi özet
        if st.session_state["senaryolar"]:
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            st.markdown(_slabel("📋 Kaydedilen Senaryolar"), unsafe_allow_html=True)
            df_sen = pd.DataFrame([sc["_meta"] for sc in st.session_state["senaryolar"]])
            st.dataframe(df_sen, hide_index=True, use_container_width=True)
            if st.button("🗑️ Tüm senaryoları temizle", key="temizle_sen"):
                st.session_state["senaryolar"] = []
                st.rerun()
        else:
            st.info("Henüz senaryo yok. Parametreleri ayarlayıp çalıştırın veya mevcut sonucu kaydedin.")

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
                        _spec2 = importlib.util.spec_from_file_location("_kit2", _dosya_adi)
                        _mod2  = importlib.util.module_from_spec(_spec2)
                        _spec2.loader.exec_module(_mod2)
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
                        _senaryo_kaydet(sen_ad, sonuc_ov,
                                        sonuc_ov["blok_ozet"], sonuc_ov["I"], sonuc_ov["K"])
                        st.success(f"✅ {sonuc_ov['durum']} — {sonuc_ov['obj_val']:,.0f} | '{sen_ad}' kaydedildi")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Hata: {e}")

        # Haritayı her zaman göster — mevcut çözüm
        _harita_sonuc = st.session_state.get("sonuc", sonuc)
        _harita_kr = {i: KAT_RENK[idx % len(KAT_RENK)]
                      for idx, i in enumerate(_harita_sonuc["I"])}
        _fig_canli = harita_ciz(
            _harita_sonuc["sonuc_kat"], _harita_sonuc["blok_ozet"],
            _harita_sonuc["I"], _harita_sonuc["K"], _harita_kr, "tab4_live")
        st.plotly_chart(_fig_canli, use_container_width=True, key="tab4_harita_canli")

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
        st.plotly_chart(fig_cmp, use_container_width=True)

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
            if sc["_fig_harita"]: st.plotly_chart(sc["_fig_harita"], use_container_width=True, key=f"h_{secili}")
            if sc["_fig_doluluk"]: st.plotly_chart(sc["_fig_doluluk"], use_container_width=True, key=f"d_{secili}")
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
                if sc_a["_fig_harita"]: st.plotly_chart(sc_a["_fig_harita"], use_container_width=True, key=f"ha_{sec_a}")
            with cb3:
                st.caption(sec_b)
                if sc_b["_fig_harita"]: st.plotly_chart(sc_b["_fig_harita"], use_container_width=True, key=f"hb_{sec_b}")

            if sc_a["_fig_doluluk"] or sc_b["_fig_doluluk"]:
                st.markdown("**📊 Blok Doluluk**")
                ca4,cb4 = st.columns(2)
                with ca4:
                    if sc_a["_fig_doluluk"]: st.plotly_chart(sc_a["_fig_doluluk"], use_container_width=True, key=f"da_{sec_a}")
                with cb4:
                    if sc_b["_fig_doluluk"]: st.plotly_chart(sc_b["_fig_doluluk"], use_container_width=True, key=f"db_{sec_b}")

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