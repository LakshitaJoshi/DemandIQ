import os
import json
import shutil
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="DemandIQ — Manufacturing Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────
# CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&family=Syne:wght@700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0c0e14 !important;
    color: #e2e6f0 !important;
}
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #13151e; }
::-webkit-scrollbar-thumb { background: #2a2e40; border-radius: 8px; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 3rem !important; max-width: 100% !important; }
[data-testid="stSidebar"] { background: #0e1018 !important; border-right: 1px solid #1e2130; }
[data-testid="stSidebar"] * { color: #c8cede !important; }

.brand-bar { display:flex;align-items:baseline;gap:10px;padding:0 0 1.4rem 0;border-bottom:1px solid #1e2130;margin-bottom:1.4rem; }
.brand-name { font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;background:linear-gradient(120deg,#00f5c4 0%,#0ea5e9 60%,#a855f7 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:-0.5px;line-height:1; }
.brand-tag { font-size:.7rem;font-weight:500;letter-spacing:2px;color:#4a5270;text-transform:uppercase;margin-bottom:2px; }
.brand-subtitle { font-size:.82rem;color:#4a5270;font-family:'IBM Plex Mono',monospace;margin-left:auto; }

.kpi-grid { display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin-bottom:1.5rem; }
.kpi-card { background:#12141f;border:1px solid #1e2130;border-radius:12px;padding:1.1rem 1.2rem;position:relative;overflow:hidden;transition:border-color .2s,transform .15s; }
.kpi-card:hover { border-color:#2e3450;transform:translateY(-2px); }
.kpi-card::before { content:'';position:absolute;top:0;left:0;right:0;height:2px; }
.kpi-card.c1::before{background:linear-gradient(90deg,#00f5c4,#0ea5e9);}
.kpi-card.c2::before{background:linear-gradient(90deg,#0ea5e9,#a855f7);}
.kpi-card.c3::before{background:linear-gradient(90deg,#a855f7,#f97316);}
.kpi-card.c4::before{background:linear-gradient(90deg,#f97316,#ef4444);}
.kpi-card.c5::before{background:linear-gradient(90deg,#22c55e,#00f5c4);}
.kpi-card.c6::before{background:linear-gradient(90deg,#f59e0b,#f97316);}
.kpi-label { font-size:.7rem;letter-spacing:1.5px;text-transform:uppercase;color:#4a5270;font-weight:500;margin-bottom:6px; }
.kpi-value { font-family:'IBM Plex Mono',monospace;font-size:1.55rem;font-weight:500;color:#f0f4ff;line-height:1.1; }
.kpi-sub   { font-size:.72rem;color:#4a5270;margin-top:5px; }

.panel { background:#12141f;border:1px solid #1e2130;border-radius:16px;padding:1.2rem 1.4rem;margin-bottom:1.2rem; }
.panel-title { font-size:.72rem;letter-spacing:2px;text-transform:uppercase;color:#4a5270;font-weight:600;margin-bottom:1rem;display:flex;align-items:center;gap:8px; }
.panel-title::before { content:'';display:inline-block;width:6px;height:6px;border-radius:50%;background:#00f5c4; }

.insight-card { background:linear-gradient(135deg,rgba(0,245,196,.06),rgba(14,165,233,.06));border:1px solid rgba(0,245,196,.18);border-radius:14px;padding:1.3rem 1.4rem; }
.insight-card h3 { font-family:'Syne',sans-serif;font-size:.65rem;letter-spacing:2px;text-transform:uppercase;color:#00f5c4;margin-bottom:12px;font-weight:700; }
.mrow { display:flex;align-items:center;justify-content:space-between;margin-bottom:8px; }
.mkey { font-size:.78rem;color:#6b7494; }
.mval { font-family:'IBM Plex Mono',monospace;font-size:.85rem;color:#e2e6f0;font-weight:500; }

.tag { display:inline-block;padding:3px 10px;border-radius:20px;font-size:.68rem;font-weight:600;letter-spacing:.5px; }
.tag-high     { background:rgba(34,197,94,.15);color:#4ade80;border:1px solid rgba(74,222,128,.25); }
.tag-moderate { background:rgba(251,191,36,.12);color:#fbbf24;border:1px solid rgba(251,191,36,.25); }
.tag-low      { background:rgba(239,68,68,.12);color:#f87171;border:1px solid rgba(248,113,113,.25); }

.alert-strip { background:rgba(0,245,196,.05);border-left:3px solid #00f5c4;border-radius:0 10px 10px 0;padding:10px 16px;margin-bottom:8px;font-size:.83rem;color:#b8c1de; }
.alert-strip strong { color:#00f5c4; }

.priority-card { background:#181b28;border:1px solid #1e2130;border-radius:12px;padding:1rem 1.2rem;margin-bottom:10px; }
.pc-name { font-weight:600;font-size:.9rem;color:#e2e6f0;margin-bottom:6px; }
.pc-meta { display:flex;flex-wrap:wrap;gap:8px;font-family:'IBM Plex Mono',monospace;font-size:.72rem;color:#6b7494; }

.metric-pair { display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px; }
.metric-box { background:#181b28;border-radius:10px;padding:.8rem 1rem;border:1px solid #1e2130; }
.mb-label { font-size:.68rem;color:#4a5270;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:4px; }
.mb-val   { font-family:'IBM Plex Mono',monospace;font-size:1rem;font-weight:500;color:#e2e6f0; }
.mb-accent { color:#00f5c4 !important; }
.mb-warn   { color:#f59e0b !important; }
.mb-danger { color:#ef4444 !important; }

.run-card        { background:#12141f;border:1px solid #1e2130;border-radius:12px;padding:1rem 1.2rem;margin-bottom:10px; }
.run-card-latest { background:rgba(0,245,196,.04);border:1px solid rgba(0,245,196,.35);border-radius:12px;padding:1rem 1.2rem;margin-bottom:10px; }
.run-id   { font-family:'IBM Plex Mono',monospace;font-size:.72rem;color:#4a5270; }
.run-time { font-size:.78rem;color:#8891b2;margin-bottom:6px; }
.run-meta-row { display:flex;flex-wrap:wrap;gap:14px;font-size:.78rem;color:#6b7494;font-family:'IBM Plex Mono',monospace; }
.run-notes { font-size:.75rem;color:#6b7494;margin-top:6px;border-top:1px solid #1e2130;padding-top:6px; }
.sbadge         { display:inline-block;padding:2px 8px;border-radius:6px;font-size:.65rem;font-weight:600;letter-spacing:.5px;text-transform:uppercase; }
.sbadge-success { background:rgba(34,197,94,.12);color:#4ade80;border:1px solid rgba(74,222,128,.2); }
.sbadge-latest  { background:rgba(0,245,196,.1);color:#00f5c4;border:1px solid rgba(0,245,196,.25); }

.driver-row { margin-bottom:10px; }
.driver-label { font-size:.78rem;color:#8891b2;margin-bottom:4px; }
.driver-bar-bg { height:6px;border-radius:4px;background:#1e2130;overflow:hidden; }
.driver-bar-fill { height:100%;border-radius:4px;background:linear-gradient(90deg,#00f5c4,#0ea5e9); }
.driver-val { font-family:'IBM Plex Mono',monospace;font-size:.7rem;color:#4a5270;text-align:right;margin-top:2px; }

.sidebar-section { font-size:.65rem;letter-spacing:2px;text-transform:uppercase;color:#4a5270;font-weight:700;margin:1.2rem 0 .5rem; }

[data-testid="stTabs"] [role="tab"] { font-size:.78rem !important;letter-spacing:1px;text-transform:uppercase !important;font-weight:600 !important;color:#4a5270 !important;padding:8px 18px !important;border-radius:8px 8px 0 0 !important; }
[data-testid="stTabs"] [role="tab"][aria-selected="true"] { color:#00f5c4 !important;background:rgba(0,245,196,.07) !important;border-bottom:2px solid #00f5c4 !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# CONSTANTS & HELPERS
# ─────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", size=12, color="#8891b2"),
    margin=dict(l=8, r=8, t=36, b=8),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
    xaxis=dict(gridcolor="#1a1d2a", linecolor="#1e2130", tickfont=dict(size=11, color="#4a5270"), zeroline=False),
    yaxis=dict(gridcolor="#1a1d2a", linecolor="#1e2130", tickfont=dict(size=11, color="#4a5270"), zeroline=False)
)
ACCENT  = "#00f5c4"
ACCENT2 = "#0ea5e9"
ACCENT3 = "#a855f7"
WARN    = "#f59e0b"
DANGER  = "#ef4444"
PALETTE = [ACCENT, ACCENT2, ACCENT3, WARN, DANGER, "#f97316", "#22c55e", "#ec4899"]

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
RUNS_DIR   = os.path.join(BASE_DIR, "runs")
RUN_LOG    = os.path.join(RUNS_DIR, "run_log.json")


def sf(fig, h=340):
    fig.update_layout(height=h, **PLOTLY_LAYOUT)
    return fig

def dtag(level):
    cls = {"High":"tag-high","Moderate":"tag-moderate","Low":"tag-low"}.get(level,"tag-low")
    return f'<span class="tag {cls}">{level}</span>'

def kc(label, value, sub, cc):
    return f'<div class="kpi-card {cc}"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-sub">{sub}</div></div>'

def panel_open(title):
    return f'<div class="panel"><div class="panel-title">{title}</div>'

PANEL_CLOSE = '</div>'

def gradbar(n):
    return [f"rgba(0,245,196,{0.3+0.7*(i/max(n-1,1))})" for i in range(n)]

def dorder(v):
    return {"High":0,"Moderate":1,"Low":2}.get(v,99)


# ─────────────────────────────────────────
# RUN LOG
# ─────────────────────────────────────────
def load_run_log():
    if os.path.exists(RUN_LOG):
        with open(RUN_LOG) as f:
            return json.load(f)
    return []


# ─────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────
@st.cache_data
def load_outputs():
    files = {
        "metrics":  "model_metrics.csv",
        "forecast": "forecast_results.csv",
        "future":   "future_forecasts.csv",
        "summary":  "product_summary.csv",
        "drivers":  "feature_importance.csv",
        "report":   "final_business_report.csv",
    }
    out = {}
    for key, fname in files.items():
        path = os.path.join(OUTPUT_DIR, fname)
        if os.path.exists(path):
            df = pd.read_csv(path)
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"])
            out[key] = df
        else:
            out[key] = pd.DataFrame()
    return out

data        = load_outputs()
metrics_df  = data["metrics"]
forecast_df = data["forecast"]
future_df   = data["future"]
summary_df  = data["summary"]
driver_df   = data["drivers"]
report_df   = data["report"]

if summary_df.empty:
    st.error("No output files found. Run `python src/pipeline.py` first.")
    st.stop()


# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="font-family:'Syne',sans-serif;font-size:1.3rem;font-weight:800;
         background:linear-gradient(120deg,#00f5c4,#0ea5e9);
         -webkit-background-clip:text;-webkit-text-fill-color:transparent;
         margin-bottom:4px;">DemandIQ</div>
    <div style="font-size:.65rem;color:#4a5270;letter-spacing:2px;
         text-transform:uppercase;margin-bottom:1.5rem;">Manufacturing Intelligence</div>
    """, unsafe_allow_html=True)

    all_cats   = sorted(summary_df["Category"].dropna().unique().tolist())
    all_demand = [x for x in ["High","Moderate","Low"] if x in summary_df["Demand_Level"].dropna().unique()]
    all_models = sorted(summary_df["Final_Model"].dropna().unique().tolist())

    # FIX 1: non-empty label strings, hidden with label_visibility="hidden"
    st.markdown('<div class="sidebar-section">Category</div>', unsafe_allow_html=True)
    cat_filter = st.multiselect("Category", all_cats, default=all_cats, label_visibility="hidden")

    st.markdown('<div class="sidebar-section">Demand Level</div>', unsafe_allow_html=True)
    dem_filter = st.multiselect("Demand Level", all_demand, default=all_demand, label_visibility="hidden")

    st.markdown('<div class="sidebar-section">Forecast Model</div>', unsafe_allow_html=True)
    mod_filter = st.multiselect("Forecast Model", all_models, default=all_models, label_visibility="hidden")

    st.divider()
    st.markdown('<div class="sidebar-section">Export Data</div>', unsafe_allow_html=True)
    for lbl, fname in [("Business Report","final_business_report.csv"),
                       ("Product Summary","product_summary.csv"),
                       ("Future Forecast","future_forecasts.csv")]:
        path = os.path.join(OUTPUT_DIR, fname)
        if os.path.exists(path):
            with open(path, "rb") as f:
                st.download_button(f"⬇ {lbl}", f, file_name=fname, mime="text/csv", use_container_width=True)


# ─────────────────────────────────────────
# FILTER
# ─────────────────────────────────────────
filtered = summary_df[
    summary_df["Category"].isin(cat_filter) &
    summary_df["Demand_Level"].isin(dem_filter) &
    summary_df["Final_Model"].isin(mod_filter)
].copy()

if filtered.empty:
    st.error("No products match current filters. Adjust sidebar selections.")
    st.stop()

filtered["Demand_Order"] = filtered["Demand_Level"].apply(dorder)
fps = filtered["Product_Name"].tolist()

mdf  = metrics_df[metrics_df["Product_Name"].isin(fps)].copy()
fcdf = forecast_df[forecast_df["Product_Name"].isin(fps)].copy()
fudf = future_df[future_df["Product_Name"].isin(fps)].copy()
ddf  = driver_df[driver_df["Product_Name"].isin(fps)].copy() if not driver_df.empty and "Product_Name" in driver_df.columns else pd.DataFrame()
rdf  = report_df[report_df["Product_Name"].isin(fps)].copy() if not report_df.empty and "Product_Name" in report_df.columns else pd.DataFrame()

sel = st.sidebar.selectbox("Product Deep-Dive", fps, key="prod_sel")


# ─────────────────────────────────────────
# KPIs
# ─────────────────────────────────────────
n_prod  = filtered["Product_Name"].nunique()
avg_mpe = round(filtered["Final_MAPE"].mean(), 2)
tot_dem = int(round(fudf["Forecast_Sales"].sum(), 0))
n_high  = int((filtered["Demand_Level"] == "High").sum())
avg_grw = round(filtered["Forecast_Growth_Percent"].mean(), 2)
tot_mgn = round(rdf["Expected_Gross_Margin"].sum(), 2) if not rdf.empty and "Expected_Gross_Margin" in rdf.columns else 0

run_log  = load_run_log()
last     = run_log[-1] if run_log else None
last_str = f"Last run: {last['timestamp'][:16].replace('T',' ')}  ·  MAPE {last['avg_mape']}%" if last else "No runs yet"

# ─────────────────────────────────────────
# BRAND BAR
# ─────────────────────────────────────────
st.markdown(f"""
<div class="brand-bar">
  <div>
    <div class="brand-tag">Manufacturing Intelligence Platform</div>
    <div class="brand-name">DemandIQ</div>
  </div>
  <div class="brand-subtitle">{last_str}</div>
</div>""", unsafe_allow_html=True)

st.markdown(f"""
<div class="kpi-grid">
  {kc("Products Tracked", str(n_prod),       "Filtered portfolio",    "c1")}
  {kc("Avg MAPE",         f"{avg_mpe}%",      "Forecast accuracy",     "c2")}
  {kc("12-Mo Demand",     f"{tot_dem:,}",     "Units forecasted",      "c3")}
  {kc("Annual Margin",    f"&#8377;{tot_mgn:,.0f}", "Expected gross margin", "c4")}
  {kc("High Priority",    str(n_high),         "High-demand SKUs",      "c5")}
  {kc("Avg Growth",       f"{avg_grw:+.1f}%", "vs historical avg",     "c6")}
</div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# TABS
# ─────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Overview", "Product Deep-Dive", "Portfolio",
    "Decision Support", "Profitability", "Run History"
])


# ═══════════════════════════════════════════
# TAB 1 — OVERVIEW
# ═══════════════════════════════════════════
with tab1:
    tg  = filtered.sort_values("Forecast_Growth_Percent", ascending=False).iloc[0]
    act = tg.get("Recommendation","Prioritize production capacity.") if "Recommendation" in filtered.columns else "Prioritize production capacity."

    cl, cr = st.columns([1, 2.4])
    with cl:
        st.markdown(f"""
        <div class="insight-card" style="min-height:320px;">
          <h3>Top Growth Signal</h3>
          <div style="font-size:1.05rem;font-weight:600;color:#e2e6f0;margin-bottom:14px;">{tg['Product_Name']}</div>
          <div class="mrow"><span class="mkey">Category</span><span class="mval">{tg['Category']}</span></div>
          <div class="mrow"><span class="mkey">Growth</span><span class="mval" style="color:#00f5c4;">{tg['Forecast_Growth_Percent']:+.1f}%</span></div>
          <div class="mrow"><span class="mkey">Demand</span><span class="mval">{dtag(tg['Demand_Level'])}</span></div>
          <div class="mrow"><span class="mkey">MAPE</span><span class="mval">{tg['Final_MAPE']}%</span></div>
          <div style="border-top:1px solid rgba(0,245,196,.12);padding-top:12px;margin-top:12px;">
            <div style="font-size:.68rem;color:#4a5270;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;">Action</div>
            <div style="font-size:.81rem;color:#a0aabb;line-height:1.5;">{act}</div>
          </div>
        </div>""", unsafe_allow_html=True)

    with cr:
        st.markdown(panel_open("Portfolio Demand Trend — Next 12 Months"), unsafe_allow_html=True)
        ov  = fudf.groupby("Date", as_index=False)["Forecast_Sales"].sum()
        fig = px.area(ov, x="Date", y="Forecast_Sales", color_discrete_sequence=[ACCENT])
        fig.update_traces(line=dict(width=2.5), fillcolor="rgba(0,245,196,0.07)")
        st.plotly_chart(sf(fig, 310), use_container_width=True)
        st.markdown(PANEL_CLOSE, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(panel_open("Top Products by Forecast Demand"), unsafe_allow_html=True)
        tp = fudf.groupby("Product_Name", as_index=False)["Forecast_Sales"].sum().sort_values("Forecast_Sales")
        fig = go.Figure(go.Bar(x=tp["Forecast_Sales"], y=tp["Product_Name"], orientation="h",
            marker=dict(color=gradbar(len(tp)), line=dict(width=0)),
            text=tp["Forecast_Sales"].apply(lambda v: f"{v:,.0f}"),
            textposition="outside", textfont=dict(size=10, color="#4a5270")))
        st.plotly_chart(sf(fig, 340), use_container_width=True)
        st.markdown(PANEL_CLOSE, unsafe_allow_html=True)

    with c2:
        st.markdown(panel_open("Demand Share by Category"), unsafe_allow_html=True)
        cs  = fudf.groupby("Category", as_index=False)["Forecast_Sales"].sum()
        fig = go.Figure(go.Pie(labels=cs["Category"], values=cs["Forecast_Sales"], hole=0.62,
            marker=dict(colors=PALETTE, line=dict(color="#0c0e14", width=3)),
            textinfo="label+percent", textfont=dict(size=11)))
        fig.update_layout(height=340, margin=dict(l=8,r=8,t=36,b=8),
            paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#8891b2"),
            legend=dict(font=dict(size=10, color="#6b7494"), bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(PANEL_CLOSE, unsafe_allow_html=True)

    with c3:
        st.markdown(panel_open("Model Distribution"), unsafe_allow_html=True)
        mc  = filtered["Final_Model"].value_counts().reset_index()
        mc.columns = ["Final_Model","Count"]
        fig = go.Figure(go.Bar(x=mc["Final_Model"], y=mc["Count"],
            marker=dict(color=PALETTE[:len(mc)], line=dict(width=0)),
            text=mc["Count"], textposition="outside", textfont=dict(size=11, color="#4a5270")))
        st.plotly_chart(sf(fig, 340), use_container_width=True)
        st.markdown(PANEL_CLOSE, unsafe_allow_html=True)


# ═══════════════════════════════════════════
# TAB 2 — PRODUCT DEEP-DIVE
# ═══════════════════════════════════════════
with tab2:
    hp = fcdf[fcdf["Product_Name"] == sel][["Date","Actual_Sales","Forecast_Sales"]].copy()
    fp = fudf[fudf["Product_Name"] == sel].copy()
    pi = filtered[filtered["Product_Name"] == sel].iloc[0]
    def sv(k): return pi[k] if k in pi.index else "—"

    ll, rl = st.columns([1.8, 1])
    with ll:
        st.markdown(panel_open("Sales History · Test Forecast · Future Projection"), unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hp["Date"], y=hp["Actual_Sales"], mode="lines+markers",
            name="Actual", line=dict(color=ACCENT2, width=2.5), marker=dict(size=5)))
        fig.add_trace(go.Scatter(x=hp["Date"], y=hp["Forecast_Sales"], mode="lines+markers",
            name="Test Forecast", line=dict(color=ACCENT3, width=2.5, dash="dot"), marker=dict(size=5)))
        fig.add_trace(go.Scatter(x=fp["Date"], y=fp["Forecast_Sales"], mode="lines+markers",
            name="Future", line=dict(color=ACCENT, width=3, dash="dash"), marker=dict(size=6),
            fill="tozeroy", fillcolor="rgba(0,245,196,0.05)"))
        st.plotly_chart(sf(fig, 400), use_container_width=True)
        st.markdown(PANEL_CLOSE, unsafe_allow_html=True)

        st.markdown(panel_open("Monthly Future Forecast"), unsafe_allow_html=True)
        fig = go.Figure(go.Bar(x=fp["Date"], y=fp["Forecast_Sales"],
            marker=dict(color=[f"rgba(14,165,233,{0.4+0.6*(i/max(len(fp)-1,1))})" for i in range(len(fp))], line=dict(width=0)),
            text=fp["Forecast_Sales"].apply(lambda v: f"{v:,.0f}"),
            textposition="outside", textfont=dict(size=10, color="#4a5270")))
        st.plotly_chart(sf(fig, 260), use_container_width=True)
        st.markdown(PANEL_CLOSE, unsafe_allow_html=True)

    with rl:
        g   = pi["Forecast_Growth_Percent"]
        gcl = "mb-accent" if g >= 0 else "mb-danger"
        mcl = "mb-accent" if pi["Final_MAPE"] < 10 else ("mb-warn" if pi["Final_MAPE"] < 20 else "mb-danger")
        st.markdown(f"""
        <div class="panel">
          <div class="panel-title">{sel}</div>
          <div class="metric-pair">
            <div class="metric-box"><div class="mb-label">Model</div><div class="mb-val">{pi['Final_Model']}</div></div>
            <div class="metric-box"><div class="mb-label">MAPE</div><div class="mb-val {mcl}">{pi['Final_MAPE']}%</div></div>
          </div>
          <div class="metric-pair">
            <div class="metric-box"><div class="mb-label">Demand</div><div class="mb-val">{dtag(pi['Demand_Level'])}</div></div>
            <div class="metric-box"><div class="mb-label">Growth</div><div class="mb-val {gcl}">{g:+.1f}%</div></div>
          </div>
          <div class="metric-pair">
            <div class="metric-box"><div class="mb-label">Avg Historical</div><div class="mb-val">{pi['Avg_Historical_Sales']:.1f}</div></div>
            <div class="metric-box"><div class="mb-label">Avg Forecast</div><div class="mb-val mb-accent">{pi['Avg_Forecast_Sales']:.1f}</div></div>
          </div>
          <div style="border-top:1px solid #1e2130;padding-top:12px;margin-top:4px;display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:.78rem;">
            <div><span style="color:#4a5270;">Category</span><br><span style="color:#b8c1de;">{pi['Category']}</span></div>
            <div><span style="color:#4a5270;">Risk Level</span><br><span style="color:#b8c1de;">{sv('Risk_Level')}</span></div>
            <div><span style="color:#4a5270;">Safety Stock</span><br><span style="font-family:'IBM Plex Mono';color:#b8c1de;">{sv('Safety_Stock')}</span></div>
            <div><span style="color:#4a5270;">Reorder Point</span><br><span style="font-family:'IBM Plex Mono';color:#b8c1de;">{sv('Reorder_Point')}</span></div>
            <div><span style="color:#4a5270;">Margin Band</span><br><span style="color:#b8c1de;">{sv('Margin_Band')}</span></div>
            <div><span style="color:#4a5270;">Action</span><br><span style="color:#b8c1de;">{sv('Inventory_Action')}</span></div>
          </div>
        </div>""", unsafe_allow_html=True)

        rec = sv("Recommendation")
        if rec and rec != "—":
            st.markdown(f"""
            <div style="background:rgba(0,245,196,.05);border:1px solid rgba(0,245,196,.15);
                        border-radius:10px;padding:12px 14px;margin-bottom:10px;">
              <div style="font-size:.65rem;color:#00f5c4;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:6px;font-weight:600;">Recommendation</div>
              <div style="font-size:.82rem;color:#a0aabb;line-height:1.55;">{rec}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown(panel_open("Model Accuracy Comparison"), unsafe_allow_html=True)
        pm = mdf[mdf["Product_Name"] == sel]
        if not pm.empty:
            vals = [pm["Baseline_MAPE"].iloc[0], pm["Exogenous_MAPE"].iloc[0], pm["Final_MAPE"].iloc[0]]
            fig = go.Figure(go.Bar(x=["Baseline","Exogenous","Final"], y=vals,
                marker=dict(color=[DANGER, WARN, ACCENT], line=dict(width=0)),
                text=[f"{v:.1f}%" for v in vals], textposition="outside",
                textfont=dict(size=11, color="#4a5270")))
            st.plotly_chart(sf(fig, 210), use_container_width=True)
        st.markdown(PANEL_CLOSE, unsafe_allow_html=True)


# ═══════════════════════════════════════════
# TAB 3 — PORTFOLIO
# ═══════════════════════════════════════════
with tab3:
    qa, qb = st.columns(2)
    with qa:
        st.markdown(panel_open("Efficiency Quadrant — Sales vs Growth vs MAPE"), unsafe_allow_html=True)
        fig = px.scatter(filtered, x="Avg_Historical_Sales", y="Forecast_Growth_Percent",
            size="Final_MAPE", color="Category", hover_name="Product_Name",
            color_discrete_sequence=PALETTE)
        fig.add_hline(y=0, line_color="#2a2e40", line_dash="dot")
        st.plotly_chart(sf(fig, 370), use_container_width=True)
        st.markdown(PANEL_CLOSE, unsafe_allow_html=True)

    with qb:
        st.markdown(panel_open("MAPE Heatmap — Product x Category"), unsafe_allow_html=True)
        hm  = filtered.pivot_table(values="Final_MAPE", index="Product_Name", columns="Category", aggfunc="mean")
        fig = px.imshow(hm, text_auto=".1f",
            color_continuous_scale=[[0,ACCENT],[0.5,WARN],[1,DANGER]], aspect="auto")
        st.plotly_chart(sf(fig, 370), use_container_width=True)
        st.markdown(PANEL_CLOSE, unsafe_allow_html=True)

    qc, qd = st.columns([1.3, 0.9])
    with qc:
        st.markdown(panel_open("Category Demand Trend — Stacked Area"), unsafe_allow_html=True)
        mc2 = fudf.groupby(["Date","Category"], as_index=False)["Forecast_Sales"].sum()
        fig = px.area(mc2, x="Date", y="Forecast_Sales", color="Category", color_discrete_sequence=PALETTE)
        st.plotly_chart(sf(fig, 310), use_container_width=True)
        st.markdown(PANEL_CLOSE, unsafe_allow_html=True)

    with qd:
        st.markdown(panel_open("Demand Level Distribution"), unsafe_allow_html=True)
        dd   = filtered["Demand_Level"].value_counts().reindex(["High","Moderate","Low"], fill_value=0).reset_index()
        dd.columns = ["Demand_Level","Count"]
        dclr = [{"High":ACCENT,"Moderate":WARN,"Low":DANGER}[d] for d in dd["Demand_Level"]]
        fig  = go.Figure(go.Bar(x=dd["Demand_Level"], y=dd["Count"],
            marker=dict(color=dclr, line=dict(width=0)),
            text=dd["Count"], textposition="outside", textfont=dict(size=12, color="#4a5270")))
        st.plotly_chart(sf(fig, 310), use_container_width=True)
        st.markdown(PANEL_CLOSE, unsafe_allow_html=True)

    st.markdown(panel_open("Model Comparison — Baseline vs Exogenous vs Final MAPE"), unsafe_allow_html=True)
    cl2 = mdf.melt(id_vars=["Product_Name"],
        value_vars=["Baseline_MAPE","Exogenous_MAPE","Final_MAPE"],
        var_name="Model_Type", value_name="MAPE")
    fig = px.bar(cl2, x="Product_Name", y="MAPE", color="Model_Type", barmode="group",
        color_discrete_map={"Baseline_MAPE":DANGER,"Exogenous_MAPE":WARN,"Final_MAPE":ACCENT})
    st.plotly_chart(sf(fig, 320), use_container_width=True)
    st.markdown(PANEL_CLOSE, unsafe_allow_html=True)


# ═══════════════════════════════════════════
# TAB 4 — DECISION SUPPORT
# ═══════════════════════════════════════════
with tab4:
    if "Forecast_Growth_Percent" in filtered.columns and "Inventory_Action" in filtered.columns:
        alts = filtered[filtered["Forecast_Growth_Percent"] >= 8].sort_values("Forecast_Growth_Percent", ascending=False)
        if not alts.empty:
            st.markdown(panel_open("High-Growth Alerts"), unsafe_allow_html=True)
            for _, row in alts.iterrows():
                st.markdown(f"""
                <div class="alert-strip">
                  <strong>{row['Product_Name']}</strong> — growth
                  <strong style="color:#00f5c4;">{row['Forecast_Growth_Percent']:+.1f}%</strong>
                  &nbsp;&middot;&nbsp; Action: <strong>{row.get('Inventory_Action','—')}</strong>
                </div>""", unsafe_allow_html=True)
            st.markdown(PANEL_CLOSE, unsafe_allow_html=True)

    d1, d2 = st.columns([1, 1.6])
    with d1:
        st.markdown(panel_open("Top 5 Priority Products"), unsafe_allow_html=True)
        prio = filtered.sort_values(["Demand_Order","Forecast_Growth_Percent","Final_MAPE"],
            ascending=[True,False,True]).head(5)
        for _, row in prio.iterrows():
            inv = row.get("Inventory_Action","Review") if "Inventory_Action" in row.index else "Review"
            st.markdown(f"""
            <div class="priority-card">
              <div class="pc-name">{row['Product_Name']}</div>
              <div class="pc-meta">
                <span>{dtag(row['Demand_Level'])}</span>
                <span>{row['Forecast_Growth_Percent']:+.1f}%</span>
                <span>MAPE {row['Final_MAPE']}%</span>
                <span style="color:#4a5270;">{row['Category']}</span>
              </div>
              <div style="font-size:.73rem;color:#4a5270;margin-top:6px;">{inv}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown(PANEL_CLOSE, unsafe_allow_html=True)

    with d2:
        rk = filtered.copy()
        if "Priority_Score" not in rk.columns:
            rk["Priority_Score"] = rk["Avg_Forecast_Sales"]*0.5 + rk["Forecast_Growth_Percent"]*10 - rk["Final_MAPE"]*5
        rk = rk.sort_values("Priority_Score", ascending=False)

        st.markdown(panel_open("Production Priority Score Ranking"), unsafe_allow_html=True)
        n   = len(rk)
        fig = go.Figure(go.Bar(x=rk["Priority_Score"], y=rk["Product_Name"], orientation="h",
            marker=dict(color=[f"rgba(0,245,196,{0.25+0.75*(1-i/max(n-1,1))})" for i in range(n)], line=dict(width=0)),
            text=rk["Priority_Score"].apply(lambda v: f"{v:.0f}"),
            textposition="outside", textfont=dict(size=10, color="#4a5270")))
        fig.update_layout(yaxis={"categoryorder":"total ascending"})
        st.plotly_chart(sf(fig, 330), use_container_width=True)
        st.markdown(PANEL_CLOSE, unsafe_allow_html=True)

        best = rk.iloc[0]
        low  = filtered.sort_values("Avg_Forecast_Sales").iloc[0]
        st.markdown(f"""
        <div class="insight-card">
          <h3>Strategic Recommendation</h3>
          <div style="margin-bottom:10px;">
            <div style="font-size:.72rem;color:#4a5270;margin-bottom:3px;">INCREASE FOCUS ON</div>
            <div style="font-size:.92rem;font-weight:600;color:#00f5c4;">{best['Product_Name']}</div>
            <div style="font-size:.79rem;color:#6b7494;margin-top:3px;">Highest priority score — strong demand, growth, and margin.</div>
          </div>
          <div style="margin-bottom:10px;">
            <div style="font-size:.72rem;color:#4a5270;margin-bottom:3px;">MONITOR CAREFULLY</div>
            <div style="font-size:.92rem;font-weight:600;color:#f59e0b;">{low['Product_Name']}</div>
            <div style="font-size:.79rem;color:#6b7494;margin-top:3px;">Lowest forecast demand in filtered portfolio.</div>
          </div>
          <div style="border-top:1px solid rgba(0,245,196,.12);padding-top:10px;font-size:.79rem;color:#6b7494;line-height:1.5;">
            High-demand &#8594; aggressive scheduling &nbsp;&middot;&nbsp; Moderate &#8594; stable planning &nbsp;&middot;&nbsp; Low &#8594; controlled inventory
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown(panel_open("Portfolio Decision Matrix"), unsafe_allow_html=True)
    bc  = ["Product_Name","Category","Final_Model","Final_MAPE","Avg_Historical_Sales","Avg_Forecast_Sales","Forecast_Growth_Percent","Demand_Level"]
    ec  = ["Margin_Band","Risk_Level","Inventory_Action","Priority_Score","Safety_Stock","Reorder_Point"]
    fc2 = [c for c in bc + ec if c in filtered.columns]
    st.dataframe(filtered.sort_values(["Demand_Order","Final_MAPE"])[fc2], use_container_width=True, hide_index=True)
    st.markdown(PANEL_CLOSE, unsafe_allow_html=True)


# ═══════════════════════════════════════════
# TAB 5 — PROFITABILITY
# ═══════════════════════════════════════════
with tab5:
    if rdf.empty:
        st.info("Run the pipeline to generate profitability data.")
    else:
        tr  = round(rdf["Expected_Revenue"].sum(), 0)
        tc  = round(rdf["Expected_Cost"].sum(), 0)
        tg2 = round(rdf["Expected_Gross_Margin"].sum(), 0)
        am  = round(rdf["Expected_Margin_Percentage"].mean(), 2)
        st.markdown(f"""
        <div class="kpi-grid" style="grid-template-columns:repeat(4,1fr);">
          {kc("Expected Revenue", f"&#8377;{tr:,.0f}", "Forecast period total",  "c1")}
          {kc("Expected Cost",    f"&#8377;{tc:,.0f}", "Forecast period total",  "c2")}
          {kc("Gross Margin",     f"&#8377;{tg2:,.0f}","Revenue minus cost",     "c3")}
          {kc("Avg Margin %",     f"{am}%",             "Across all SKUs",        "c5")}
        </div>""", unsafe_allow_html=True)

        pa, pb = st.columns(2)
        with pa:
            st.markdown(panel_open("Product-wise Gross Margin"), unsafe_allow_html=True)
            mp  = rdf.groupby("Product_Name", as_index=False)["Expected_Gross_Margin"].sum().sort_values("Expected_Gross_Margin")
            fig = go.Figure(go.Bar(x=mp["Expected_Gross_Margin"], y=mp["Product_Name"], orientation="h",
                marker=dict(color=gradbar(len(mp)), line=dict(width=0)),
                text=mp["Expected_Gross_Margin"].apply(lambda v: f"&#8377;{v:,.0f}"),
                textposition="outside", textfont=dict(size=10, color="#4a5270")))
            fig.update_layout(yaxis={"categoryorder":"total ascending"})
            st.plotly_chart(sf(fig, 350), use_container_width=True)
            st.markdown(PANEL_CLOSE, unsafe_allow_html=True)

        with pb:
            st.markdown(panel_open("Category — Revenue vs Cost vs Margin"), unsafe_allow_html=True)
            mc3 = rdf.groupby("Category", as_index=False)[["Expected_Revenue","Expected_Cost","Expected_Gross_Margin"]].sum()
            fig = go.Figure()
            for col, clr, nm in [("Expected_Revenue",ACCENT2,"Revenue"),("Expected_Cost",DANGER,"Cost"),("Expected_Gross_Margin",ACCENT,"Gross Margin")]:
                fig.add_trace(go.Bar(name=nm, x=mc3["Category"], y=mc3[col], marker_color=clr, marker_line_width=0))
            fig.update_layout(barmode="group")
            st.plotly_chart(sf(fig, 350), use_container_width=True)
            st.markdown(PANEL_CLOSE, unsafe_allow_html=True)

        if "Expected_Margin_Percentage" in rdf.columns:
            st.markdown(panel_open("Low Margin Warning — Bottom 5 Products"), unsafe_allow_html=True)
            lm = rdf.groupby("Product_Name", as_index=False)["Expected_Margin_Percentage"].mean() \
                    .sort_values("Expected_Margin_Percentage").head(5)
            st.dataframe(lm, use_container_width=True, hide_index=True)
            st.markdown(PANEL_CLOSE, unsafe_allow_html=True)

        if not ddf.empty:
            st.markdown(panel_open("Top Demand Drivers — Portfolio Average"), unsafe_allow_html=True)
            od = ddf.groupby("Feature", as_index=False)["Importance"].mean() \
                    .sort_values("Importance", ascending=False).head(12)
            mx = od["Importance"].max()
            bars = "".join([
                f'<div class="driver-row">'
                f'<div class="driver-label">{r["Feature"]}</div>'
                f'<div class="driver-bar-bg"><div class="driver-bar-fill" style="width:{r["Importance"]/mx*100:.1f}%;"></div></div>'
                f'<div class="driver-val">{r["Importance"]:.4f}</div>'
                f'</div>'
                for _, r in od.iterrows()
            ])
            st.markdown(bars, unsafe_allow_html=True)
            st.markdown(PANEL_CLOSE, unsafe_allow_html=True)


# ═══════════════════════════════════════════
# TAB 6 — RUN HISTORY
# ═══════════════════════════════════════════
with tab6:
    run_log = load_run_log()

    if not run_log:
        st.markdown("""
        <div class="panel" style="text-align:center;padding:3rem;">
          <div style="font-size:2rem;margin-bottom:1rem;">&#128203;</div>
          <div style="font-size:.9rem;color:#4a5270;">No pipeline runs logged yet.</div>
          <div style="font-size:.8rem;color:#2e3450;margin-top:6px;">Run <code>python src/pipeline.py</code> to get started.</div>
        </div>""", unsafe_allow_html=True)
    else:
        runs   = list(reversed(run_log))
        best_r = min(run_log, key=lambda r: r["avg_mape"])
        latest = runs[0]

        # Summary KPIs
        st.markdown(f"""
        <div class="kpi-grid" style="grid-template-columns:repeat(3,1fr);margin-bottom:1.2rem;">
          {kc("Total Runs",  str(len(runs)),             "Pipeline executions logged",               "c1")}
          {kc("Best MAPE",   f"{best_r['avg_mape']}%",   best_r['timestamp'][:10],                  "c5")}
          {kc("Latest MAPE", f"{latest['avg_mape']}%",   latest['timestamp'][:16].replace('T',' '), "c3")}
        </div>""", unsafe_allow_html=True)

        # MAPE trend chart (only if >1 run)
        if len(runs) > 1:
            st.markdown(panel_open("MAPE Trend Across Runs"), unsafe_allow_html=True)
            trend = pd.DataFrame([{
                "Run":   f"#{len(runs)-i}",
                "MAPE":  r["avg_mape"],
            } for i, r in enumerate(runs)])
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=trend["Run"], y=trend["MAPE"],
                mode="lines+markers",
                line=dict(color=ACCENT, width=2.5),
                marker=dict(size=8, color=ACCENT),
                hovertemplate="<b>%{x}</b><br>MAPE: %{y}%<extra></extra>"))
            fig.add_hline(y=trend["MAPE"].mean(), line_color="#2a2e40", line_dash="dot")
            st.plotly_chart(sf(fig, 220), use_container_width=True)
            st.markdown(PANEL_CLOSE, unsafe_allow_html=True)

        # Run cards
        st.markdown(panel_open("All Runs"), unsafe_allow_html=True)
        for i, run in enumerate(runs):
            is_latest   = (i == 0)
            ts          = run["timestamp"][:16].replace("T", " ")
            dur         = run.get("duration_seconds", "—")
            n_pr        = run.get("n_products", 0)
            avg_m       = run["avg_mape"]
            notes       = run.get("notes", "")
            card_class  = "run-card-latest" if is_latest else "run-card"
            model_str   = "  &middot;  ".join([f"{v}&times; {k}" for k, v in run.get("model_counts", {}).items()])
            demand_str  = "  &middot;  ".join([f"{k}: {v}" for k, v in run.get("demand_counts", {}).items()])
            notes_html  = f'<div class="run-notes">&#128221; {notes}</div>' if notes else ""
            late_badge  = '<span class="sbadge sbadge-latest">LATEST</span>' if is_latest else ""

            col_c, col_b = st.columns([5, 1])
            with col_c:
                st.markdown(f"""
                <div class="{card_class}">
                  <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;flex-wrap:wrap;">
                    <span class="run-id">{run['run_id']}</span>
                    <span class="sbadge sbadge-success">success</span>
                    {late_badge}
                  </div>
                  <div class="run-time">{ts} &nbsp;&middot;&nbsp; {dur}s &nbsp;&middot;&nbsp; {n_pr} products</div>
                  <div class="run-meta-row">
                    <span>MAPE {avg_m}%</span>
                    <span>{model_str}</span>
                    <span>{demand_str}</span>
                  </div>
                  {notes_html}
                </div>""", unsafe_allow_html=True)

            with col_b:
                run_dir = os.path.join(RUNS_DIR, run["run_id"])
                if os.path.exists(run_dir) and not is_latest:
                    if st.button("Restore", key=f"rst_{run['run_id']}"):
                        for fname in ["model_metrics.csv","product_summary.csv",
                                      "future_forecasts.csv","final_business_report.csv"]:
                            src = os.path.join(run_dir, fname)
                            dst = os.path.join(OUTPUT_DIR, fname)
                            if os.path.exists(src):
                                shutil.copy2(src, dst)
                        st.success("Restored!")
                        st.cache_data.clear()
                        st.rerun()

        st.markdown(PANEL_CLOSE, unsafe_allow_html=True)

        # Export run log
        st.markdown(panel_open("Export Run Log"), unsafe_allow_html=True)
        st.download_button(
            "&#11015; Download run_log.json",
            json.dumps(run_log, indent=2),
            "run_log.json",
            "application/json"
        )
        st.markdown(PANEL_CLOSE, unsafe_allow_html=True)