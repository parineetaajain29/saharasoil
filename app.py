import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd

from model_engine import compute_model, DEFAULTS, QUARTER_LABELS

# ----------------------------------------------------------------------------
# PAGE CONFIG & THEME
# ----------------------------------------------------------------------------
st.set_page_config(page_title="Saharasoil — 360 Investor Dashboard", page_icon="🌱",
                    layout="wide", initial_sidebar_state="expanded")

BIOCHAR = "#1a1510"
BIOCHAR_2 = "#241d16"
SIENNA = "#a0472a"
SIENNA_DARK = "#7c3720"
GREEN = "#5b7247"
GREEN_DARK = "#3e4e32"
SAND = "#e7d9bd"
SAND_2 = "#ddccab"
BONE = "#faf6ec"
INK = "#241c14"
INK_SOFT = "#584b3a"
LINE = "rgba(36,28,20,0.14)"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"]  {{ font-family: 'Inter', sans-serif; }}
h1, h2, h3 {{ font-family: 'Fraunces', serif !important; font-weight: 600; letter-spacing: -0.01em; color: {BIOCHAR}; }}

.mono-tag {{
    font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; text-transform: uppercase;
    letter-spacing: 0.08em; color: {SIENNA_DARK}; display: flex; align-items: center; gap: 8px; margin-bottom: 6px;
}}
.mono-tag::before {{ content: ""; width: 20px; height: 1px; background: {SIENNA_DARK}; }}

.stApp {{ background-color: {SAND}; }}

/* --- MAIN CONTENT: force dark text so nothing is white-on-light regardless of Streamlit theme --- */
section[data-testid="stMain"] {{ color: {INK}; }}
section[data-testid="stMain"] p,
section[data-testid="stMain"] li,
section[data-testid="stMain"] span,
section[data-testid="stMain"] label,
section[data-testid="stMain"] td,
section[data-testid="stMain"] th,
section[data-testid="stMain"] div[data-testid="stMarkdownContainer"],
section[data-testid="stMain"] div[data-testid="stMarkdownContainer"] * {{ color: {INK} !important; }}
section[data-testid="stMain"] h1,
section[data-testid="stMain"] h2,
section[data-testid="stMain"] h3,
section[data-testid="stMain"] h4 {{ color: {BIOCHAR} !important; font-family: 'Fraunces', serif !important; }}
/* tab labels — mono tracked caps, like the site's nav links */
button[data-testid="stTab"] p, div[data-testid="stTabs"] button p {{
    color: {INK_SOFT} !important; font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.76rem !important; text-transform: uppercase; letter-spacing: 0.06em;
}}
div[data-testid="stTabs"] button[aria-selected="true"] p {{ color: {SIENNA_DARK} !important; font-weight: 600 !important; }}
/* metric-card / callout inner text keeps its own colours (set below) */
.metric-card .value {{ color: {BIOCHAR} !important; }}
.metric-card .label, .metric-card .sub {{ color: {INK_SOFT} !important; }}

/* --- SIDEBAR: biochar-dark background with sand text --- */
section[data-testid="stSidebar"] {{ background-color: {BIOCHAR}; }}
section[data-testid="stSidebar"] * {{ color: {SAND} !important; }}
section[data-testid="stSidebar"] .stSlider label, section[data-testid="stSidebar"] label {{
    color: {SAND_2} !important; font-weight: 500; font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.74rem !important; text-transform: uppercase; letter-spacing: 0.04em;
}}
section[data-testid="stSidebar"] h2 {{ color: {BONE} !important; font-family: 'Fraunces', serif !important; }}
section[data-testid="stSidebar"] hr {{ border-color: rgba(250,246,236,0.18) !important; }}

.hero {{
    background: linear-gradient(135deg, {BIOCHAR} 0%, {BIOCHAR_2} 100%);
    padding: 2.4rem 2.6rem; border-radius: 6px; color: white; margin-bottom: 1.2rem;
    border: 1px solid rgba(250,246,236,0.1);
}}
/* High-specificity overrides: the generic "force dark text" rule above targets
   `section[data-testid="stMain"] div[data-testid="stMarkdownContainer"] *`, which is specific
   enough to beat a plain `.hero *` rule even with !important. These match that same prefix
   chain plus the .hero class, so they win instead. */
section[data-testid="stMain"] div[data-testid="stMarkdownContainer"] .hero,
section[data-testid="stMain"] div[data-testid="stMarkdownContainer"] .hero * {{ color: {BONE} !important; }}
section[data-testid="stMain"] div[data-testid="stMarkdownContainer"] .hero h1 {{
    color: {BONE} !important; font-size: 2.7rem; margin-bottom: 0.2rem; font-family: 'Fraunces', serif !important; }}
section[data-testid="stMain"] div[data-testid="stMarkdownContainer"] .hero p {{
    color: #d69a6e !important; font-size: 1.1rem; font-style: italic; margin: 0; }}

.metric-card {{
    background: {BONE}; border-radius: 3px; padding: 1.1rem 1.3rem; border: 1px solid {LINE};
    border-left: 3px solid {SIENNA}; height: 100%;
}}
.metric-card .label {{ color: {INK_SOFT}; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em;
    font-weight: 600; font-family: 'IBM Plex Mono', monospace; }}
.metric-card .value {{ color: {BIOCHAR}; font-size: 1.7rem; font-weight: 600; font-family: 'Fraunces', serif; }}
.metric-card .sub {{ color: {INK_SOFT}; font-size: 0.82rem; }}

.callout {{
    background: {BONE}; border: 1px solid {LINE}; border-left: 3px solid {SIENNA_DARK};
    border-radius: 3px; padding: 1rem 1.3rem; margin: 0.8rem 0;
}}
.callout.green {{ border-left-color: {GREEN}; }}
.callout.sand {{ border-left-color: {SIENNA}; }}
.callout b {{ color: {BIOCHAR}; }}

.section-title {{ color: {BIOCHAR}; border-bottom: none; padding-bottom: 0; margin-top: 0.2rem;
    font-family: 'Fraunces', serif !important; }}


.pill {{ display:inline-block; background:{BIOCHAR}; padding: 0.15rem 0.7rem; border-radius: 2px;
         font-family: 'IBM Plex Mono', monospace; font-size: 0.68rem; font-weight: 600; letter-spacing: 0.06em;
         text-transform: uppercase; margin-bottom: 0.4rem;}}
section[data-testid="stMain"] div[data-testid="stMarkdownContainer"] .pill,
section[data-testid="stMain"] div[data-testid="stMarkdownContainer"] .pill * {{ color: {BONE} !important; }}

.process-card {{ background: {BONE}; border-radius: 3px; padding: 1.2rem; text-align: center;
                  border: 1px solid {LINE}; border-top: 3px solid {SIENNA}; height: 100%;}}
.process-card .icon {{ font-size: 2.2rem; }}
.process-card h4 {{ color: {BIOCHAR}; margin: 0.4rem 0 0.3rem 0; font-family: 'Fraunces', serif;}}
.process-card p {{ color: {INK_SOFT}; font-size: 0.85rem; }}

/* Streamlit's own buttons, in the mono-tracked CTA style */
.stButton button {{ font-family: 'IBM Plex Mono', monospace !important; font-size: 0.76rem !important;
    text-transform: uppercase; letter-spacing: 0.05em; border-radius: 2px !important; }}

/* Native alert boxes (fallback, in case any st.info/warning/success slip through) */
div[data-testid="stAlert"] {{ background-color: {BONE} !important; border-left: 3px solid {SIENNA_DARK} !important;
    border-radius: 3px !important; color: {INK} !important; }}
div[data-testid="stAlert"] * {{ color: {INK} !important; }}

/* Slider handle — the track fill/background now comes correctly from
   .streamlit/config.toml's primaryColor, so we only need to tint the handle. */
div[data-testid="stSlider"] div[role="slider"] {{ background-color: {SIENNA} !important;
    border-color: {SIENNA} !important; }}

/* Dataframe header */
div[data-testid="stDataFrame"] {{ border: 1px solid {LINE}; border-radius: 3px; }}

footer, #MainMenu {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)

PLOTLY_TEMPLATE = dict(
    layout=go.Layout(
        font=dict(family="Inter, sans-serif", color=INK, size=13),
        title=dict(font=dict(family="Fraunces, serif", color=BIOCHAR, size=16)),
        plot_bgcolor=BONE, paper_bgcolor=SAND,
        colorway=[BIOCHAR, SIENNA, SIENNA_DARK, GREEN, SAND_2],
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
)

def section_head(tag_text, title_text):
    st.markdown(f'<div class="mono-tag">{tag_text}</div><h3 class="section-title">{title_text}</h3>',
                unsafe_allow_html=True)

def sub_head(text):
    st.markdown(f'<h4 style="color:{BIOCHAR};font-family:\'Fraunces\',serif;margin-top:0.6rem;">{text}</h4>',
                unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# SIDEBAR — LIVE MODEL CONTROLS
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## SAHARASOIL")
    st.caption("360° Investor Dashboard · Group 10 · SP Jain SGM")
    st.markdown("---")
    st.markdown("### Live Model Controls")
    st.caption("Every chart on this dashboard recalculates from these levers — exactly like the underlying Excel model, live.")

    if "reset_nonce" not in st.session_state:
        st.session_state.reset_nonce = 0
    nz = st.session_state.reset_nonce  # suffix baked into every slider key below

    price = st.slider("Bulk price (AED/tonne)", 600, 1300, int(DEFAULTS["price"]), 10, key=f"price_{nz}")
    tonnes_pc = st.slider("Tonnes per contractor / quarter", 2.0, 14.0, DEFAULTS["tonnes_per_contractor"], 0.5,
                           key=f"tonnes_pc_{nz}",
                           help="Flagged in the model as THE swing variable — unvalidated, moves the outcome more than price or cost.")
    churn = st.slider("Quarterly contractor churn", 0.02, 0.30, DEFAULTS["churn"], 0.01, format="%.2f", key=f"churn_{nz}")
    signings_mult = st.slider("Signings-pace multiplier", 0.5, 2.0, 1.0, 0.1, key=f"signings_mult_{nz}",
                               help="Scales the whole contractor-signing ramp up or down, keeping its shape.")
    deposit_pct = st.slider("Upfront deposit on signing (share)", 0.0, 0.6, DEFAULTS["deposit_pct"], 0.05,
                             format="%.2f", key=f"deposit_pct_{nz}")
    funding_ask = st.slider("Funding ask (AED)", 200000, 900000, int(DEFAULTS["funding_ask"]), 10000, key=f"funding_ask_{nz}")

    with st.expander("Advanced: cost structure"):
        feedstock_cost = st.slider("Feedstock cost (AED/t)", 0, 400, int(DEFAULTS["feedstock_cost"]), 10, key=f"feedstock_cost_{nz}")
        biochar_cost = st.slider("Biochar sourcing (AED/t)", 100, 700, int(DEFAULTS["biochar_cost"]), 10, key=f"biochar_cost_{nz}")
        blending_cost = st.slider("Blending & packaging (AED/t)", 0, 300, int(DEFAULTS["blending_cost"]), 10, key=f"blending_cost_{nz}")
        opex_y3 = st.slider("Year 3 fixed opex (AED/qtr)", 40000, 150000, int(DEFAULTS["opex_y3"]), 1000, key=f"opex_y3_{nz}")

    if st.button("↺ Reset to validated defaults", use_container_width=True):
        st.session_state.reset_nonce += 1
        st.rerun()

    st.markdown("---")
    st.caption("Source model: Saharasoil_B2B_Model_Reanchored.xlsx — re-anchored, 3-year, deposit + collection-lag cash mechanics.")

assumptions = dict(DEFAULTS)
assumptions.update(dict(
    price=float(price), tonnes_per_contractor=float(tonnes_pc), churn=float(churn),
    signings_multiplier=float(signings_mult), deposit_pct=float(deposit_pct), funding_ask=float(funding_ask),
    feedstock_cost=float(feedstock_cost), biochar_cost=float(biochar_cost), blending_cost=float(blending_cost),
    opex_y3=float(opex_y3),
))
m = compute_model(assumptions)
is_default = all(abs(assumptions[k] - DEFAULTS[k]) < 1e-9 for k in
                  ["price","tonnes_per_contractor","churn","signings_multiplier","deposit_pct","funding_ask",
                   "feedstock_cost","biochar_cost","blending_cost","opex_y3"])

# ----------------------------------------------------------------------------
# HERO
# ----------------------------------------------------------------------------
st.markdown(f"""
<div class="hero">
  <h1>SAHARASOIL</h1>
  <p>Turning camel waste into the substrate behind the UAE's greenest offices</p>
</div>
""", unsafe_allow_html=True)

if not is_default:
    st.markdown("""<div class="callout sand"><b>You're viewing a live, adjusted scenario</b> — every number
    below reflects your slider changes, not the validated defaults. Use <i>Reset</i> in the sidebar to return
    to the pitch-ready baseline.</div>""", unsafe_allow_html=True)

def metric_card(col, label, value, sub="", value_color=None):
    vc = f"color:{value_color} !important;" if value_color else ""
    col.markdown(f"""<div class="metric-card"><div class="label">{label}</div>
        <div class="value" style="{vc}">{value}</div><div class="sub">{sub}</div></div>""", unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)
metric_card(c1, "3-Year Revenue", f"AED {m['year1_rev']+m['year2_rev']+m['year3_rev']:,.0f}", "Y1+Y2+Y3 modelled")
metric_card(c2, "Blended Gross Margin", f"{m['gross_margin'][-1]*100:.1f}%", "steady across the model")
metric_card(c3, "EBITDA Turns Positive", m['ebitda_positive_q'], "first profitable quarter")
metric_card(c4, "LTV : CAC (all-in)", f"{m['ltv_cac_allin']:.1f}x", "conservative, loaded CAC")
runway_label = "Covered" if m['runway_ok'] else "Short"
metric_card(c5, "Runway at Current Ask", runway_label, f"trough AED {m['trough']:,.0f}",
            value_color=GREEN if m['runway_ok'] else SIENNA_DARK)

st.markdown("<br>", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# TABS
# ----------------------------------------------------------------------------
tab_overview, tab_product, tab_market, tab_unit, tab_fin, tab_risk, tab_road, tab_ask = st.tabs(
    ["Overview", "Product 360°", "Market Sizing", "Unit Economics",
     "Financial Model", "Risk Register", "Roadmap", "The Ask"]
)

# ============================================================================
# TAB: OVERVIEW
# ============================================================================
with tab_overview:
    colA, colB = st.columns([3, 2])
    with colA:
        section_head("01 — Overview", "The Problem, In Two Facts")
        st.markdown(f"""
<div class="callout"><b>Offices are paying for greenery that dies.</b> Generic imported soil isn't formulated for Gulf heat,
saline water, or HVAC-dried air — biophilic installations decline fast, and ESG/WELL budgets fund constant replacement
instead of results.</div>
<div class="callout sand"><b>Farms are sitting on an under-used resource.</b> Camel manure has proven soil-amendment
properties for exactly these conditions — but Northern Emirates farms are paid little to nothing for it today.</div>
<div class="callout green"><b>No one has connected them.</b> There is no B2B channel linking climate-adapted circular
waste to the office-greenery supply chain — until now.</div>
""", unsafe_allow_html=True)

    with colB:
        section_head("Business Model", "Snapshot")
        st.markdown(f"""
- **Customer:** plantscaping / facility-management contractors (B2B, not B2C)
- **Product:** bulk camel-biochar soil blend + recurring top-dressing service
- **Channel:** 2–3 anchor contractors + free-zone FM associations & ESG consultancies
- **Moat:** feedstock proximity, formal offtake agreements, below industrial biochar producers' economics
- **Ask:** AED {assumptions['funding_ask']:,.0f} — MVP setup, MOCCAE registration, and working-capital runway
""")
        section_head("Methodology", "Why This Dashboard")
        st.markdown("""
Every figure here is **formula-driven**, not typed in. Move a slider in the sidebar — price, churn, tonnes per
contractor, the funding ask — and revenue, margin, cash runway, and unit economics all recompute together,
exactly like the underlying financial model.
""")

# ============================================================================
# TAB: PRODUCT 360
# ============================================================================
with tab_product:
    section_head("02 — Product", "The Product, From Every Angle")

    sub_head("The Circular Flow — Source → Process → Blend → Supply")
    steps = [("01", "Source", "Camel manure from offtake-agreement farms across the Northern Emirates"),
             ("02", "Process", "Finished biochar from an established external processor"),
             ("03", "Blend", "Finished into a Gulf-climate-formulated soil amendment"),
             ("04", "Supply", "Bulk delivery to plantscaping & facility-management contractors")]
    cols = st.columns(4)
    for col, (num, title, desc) in zip(cols, steps):
        col.markdown(f"""<div class="process-card"><div class="icon">{num}</div><h4>{title}</h4><p>{desc}</p></div>""",
                      unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    colL, colR = st.columns(2)

    with colL:
        sub_head("Competitive Positioning (illustrative — pending pilot validation)")
        categories = ["Heat Tolerance", "Salinity Tolerance", "Water Retention", "Circularity / ESG",
                      "Cost Efficiency", "Local Sourcing"]
        saharasoil_scores = [9, 8, 8, 10, 7, 10]
        generic_scores = [4, 3, 4, 2, 8, 2]
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=saharasoil_scores + [saharasoil_scores[0]],
                                       theta=categories + [categories[0]], fill='toself', name='Saharasoil',
                                       line_color=GREEN, fillcolor="rgba(63,107,79,0.25)"))
        fig.add_trace(go.Scatterpolar(r=generic_scores + [generic_scores[0]],
                                       theta=categories + [categories[0]], fill='toself', name='Generic imported soil',
                                       line_color=SIENNA_DARK, fillcolor="rgba(156,75,59,0.15)"))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
                           template=PLOTLY_TEMPLATE, height=380, showlegend=True,
                           title="Saharasoil vs. generic imported soil (1–10 scale)")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Directional scores for pitch purposes — not lab-verified. Validate with agronomic pilot testing (see Risk Register).")

    with colR:
        sub_head("Blend Composition")
        fig2 = go.Figure(data=[go.Pie(labels=["Biochar", "Compost, sand & manure carrier"], values=[27, 73],
                                       hole=0.55, marker_colors=[SIENNA, BIOCHAR], textinfo="label+percent")])
        fig2.update_layout(template=PLOTLY_TEMPLATE, height=380,
                            title="~27% biochar / ~73% compost, sand & manure by weight")
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("At ~27% blend share and ~AED 1,300/t physical biochar, the AED 350/t input cost used across this model is internally consistent.")

    sub_head("Feedstock Diversification — 5-Year View")
    years = ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]
    camel = [100, 90, 65, 45, 35]
    cow = [0, 10, 30, 35, 35]
    poultry = [0, 0, 0, 10, 15]
    palm = [0, 0, 5, 10, 15]
    fig3 = go.Figure()
    for name, vals, color in [("Camel manure", camel, BIOCHAR), ("Cow / dairy manure", cow, SIENNA),
                                ("Poultry litter", poultry, SIENNA_DARK), ("Date-palm biomass", palm, GREEN)]:
        fig3.add_trace(go.Scatter(x=years, y=vals, mode="lines", name=name, stackgroup="one",
                                   line=dict(width=0.5), fillcolor=color, line_color=color))
    fig3.update_layout(template=PLOTLY_TEMPLATE, height=340, yaxis_title="% of feedstock mix",
                        title="Camel stays the flagship story — the mix quietly de-risks supply")
    st.plotly_chart(fig3, use_container_width=True)
    st.caption("Illustrative diversification path from the 5-Year Diversification & Expansion Plan — starts Year 2, never disturbs the Year 1 pitch numbers.")

# ============================================================================
# TAB: MARKET SIZING
# ============================================================================
with tab_market:
    section_head("03 — Market Sizing", "TAM · SAM · SOM")

    colL, colR = st.columns([3, 2])
    with colL:
        fig = go.Figure(go.Funnel(
            y=["TAM<br><span style='font-size:0.8em'>UAE Landscaping Market (2024)</span>",
               "SAM<br><span style='font-size:0.8em'>Commercial softscape materials</span>",
               "SOM<br><span style='font-size:0.8em'>Realistic Year-5 capture</span>"],
            x=[1670000000, 105210000, 275000],
            textposition="inside", textinfo="value",
            marker={"color": [BIOCHAR, SIENNA, SIENNA_DARK]},
        ))
        fig.update_layout(template=PLOTLY_TEMPLATE, height=420, title="Market sizing funnel (USD)")
        st.plotly_chart(fig, use_container_width=True)

    with colR:
        sub_head("How we got there")
        st.markdown("""
| Step | Value |
|---|---|
| TAM | UAE Landscaping Market, TechSci Research (2024) |
| × Commercial share | 35% |
| × Softscape share | 60% |
| × Materials-only share | 30% |
| **= SAM** | **~$105M** |
| SOM | Bottom-up from Year-5 production ceiling, **not** a % of SAM |
""")
        st.markdown("""<div class="callout sand">We deliberately built SOM bottom-up from our own production capacity
rather than guessing a market-share percentage — a small, defensible bite beats an inflated one under Q&A.</div>""",
                     unsafe_allow_html=True)

    sub_head("UAE Landscaping Market Growth")
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=[2024, 2025, 2030], y=[1.67, 1.8, 2.84], mode="lines+markers",
                               line=dict(color=BIOCHAR, width=3), marker=dict(size=10), name="TechSci Research"))
    fig4.update_layout(template=PLOTLY_TEMPLATE, height=320, yaxis_title="USD Billions",
                        title="UAE Landscaping Market — USD 1.67B (2024) → USD 2.84B (2030F), 9.07% CAGR")
    st.plotly_chart(fig4, use_container_width=True)

# ============================================================================
# TAB: UNIT ECONOMICS
# ============================================================================
with tab_unit:
    section_head("04 — Unit Economics", "Per-Tonne & Per-Contractor Economics")

    c1, c2, c3, c4 = st.columns(4)
    metric_card(c1, "Bulk Gross Margin", f"{m['bulk_margin']*100:.1f}%", f"AED {m['bulk_gp_per_tonne']:.0f} / tonne")
    metric_card(c2, "Top-Dressing Margin", f"{m['topdress_margin']*100:.0f}%", "lighter-touch, higher margin")
    metric_card(c3, "CAC (narrow / all-in)", f"AED {m['cac_narrow']:,.0f} / {m['cac_all_in']:,.0f}", "activity-only vs. loaded")
    metric_card(c4, "CAC Payback", f"{m['cac_payback_q']:.1f} qtrs", "narrow CAC basis")

    st.markdown("<br>", unsafe_allow_html=True)
    colL, colR = st.columns(2)
    with colL:
        fig = go.Figure(data=[
            go.Bar(name="Gross margin %", x=["Bulk supply", "Top-dressing"],
                   y=[m['bulk_margin']*100, m['topdress_margin']*100],
                   marker_color=[BIOCHAR, SIENNA], text=[f"{m['bulk_margin']*100:.1f}%", f"{m['topdress_margin']*100:.0f}%"],
                   textposition="outside")
        ])
        fig.update_layout(template=PLOTLY_TEMPLATE, height=360, title="Gross margin by revenue line", yaxis_range=[0, 75])
        st.plotly_chart(fig, use_container_width=True)

    with colR:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=[c*100 for c in m['churn_grid']], y=m['ltv_cac_sensitivity'],
                                   mode="lines+markers", line=dict(color=SIENNA_DARK, width=3), marker=dict(size=9),
                                   name="LTV:CAC (all-in)"))
        fig2.add_hline(y=3, line_dash="dash", line_color=GREEN, annotation_text="3x healthy B2B threshold")
        fig2.update_layout(template=PLOTLY_TEMPLATE, height=360, xaxis_title="Quarterly churn (%)",
                            yaxis_title="LTV : CAC (all-in)", title="LTV:CAC sensitivity to churn — stress-tested, not just hoped for")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown(f"""<div class="callout green">At the current settings, LTV:CAC (all-in) is <b>{m['ltv_cac_allin']:.2f}x</b> —
even under much more conservative churn than the 5%/quarter base case, it stays near or above the 3x threshold
considered healthy for B2B. The narrow-CAC headline number ({m['ltv_cac_narrow']:.1f}x) is real, but the all-in number
is the one we'd defend under questioning.</div>""", unsafe_allow_html=True)

    with st.expander("Methodology note — a correction we made to the source workbook"):
        st.markdown("""
The uploaded workbook's `Gross profit / contractor` formula used the top-dressing **COGS%** where it should have used
the top-dressing **margin%** (i.e. `1 − COGS%`) when adding top-dressing's contribution to per-contractor gross profit.
That understated gross profit per contractor (AED 2,532 instead of the correct AED 2,748) and, downstream, understated
LTV, LTV:CAC, and overstated the break-even contractor count. This dashboard uses the corrected formula throughout —
it's more favourable than the original file, and we'd rather you hear about the fix from us than find the discrepancy yourselves.
""")

# ============================================================================
# TAB: FINANCIAL MODEL
# ============================================================================
with tab_fin:
    section_head("05 — Financial Model", "3-Year Quarterly Model")

    c1, c2, c3, c4 = st.columns(4)
    metric_card(c1, "Year 1 Revenue", f"AED {m['year1_rev']:,.0f}")
    metric_card(c2, "Year 2 Revenue", f"AED {m['year2_rev']:,.0f}")
    metric_card(c3, "Year 3 Revenue", f"AED {m['year3_rev']:,.0f}")
    metric_card(c4, "EBITDA-Positive Quarter", m['ebitda_positive_q'])

    fig = go.Figure()
    fig.add_trace(go.Bar(x=m['quarters'], y=m['bulk_rev'], name="Bulk revenue", marker_color=BIOCHAR))
    fig.add_trace(go.Bar(x=m['quarters'], y=m['topdress_rev'], name="Top-dressing revenue", marker_color=SIENNA))
    fig.update_layout(barmode="stack", template=PLOTLY_TEMPLATE, height=380, title="Quarterly revenue build")
    st.plotly_chart(fig, use_container_width=True)

    colL, colR = st.columns(2)
    with colL:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=m['quarters'], y=m['ebitda'], mode="lines+markers", name="EBITDA",
                                   line=dict(color=SIENNA_DARK, width=3)))
        fig2.add_hline(y=0, line_dash="dot", line_color=INK_SOFT)
        fig2.update_layout(template=PLOTLY_TEMPLATE, height=360, title="EBITDA by quarter")
        st.plotly_chart(fig2, use_container_width=True)
    with colR:
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=m['quarters'], y=m['cum_cash_incl'], mode="lines+markers", name="Cumulative cash",
                                   line=dict(color=BIOCHAR, width=3), fill="tozeroy", fillcolor="rgba(31,59,77,0.12)"))
        fig3.add_hline(y=0, line_dash="dash", line_color=SIENNA_DARK, annotation_text="cash-out line")
        fig3.update_layout(template=PLOTLY_TEMPLATE, height=360,
                            title=f"Cumulative cash incl. ask of AED {assumptions['funding_ask']:,.0f}")
        st.plotly_chart(fig3, use_container_width=True)

    status_color = GREEN if m['runway_ok'] else SIENNA_DARK
    status_text = "Ask covers the modelled runway" if m['runway_ok'] else "Cash goes negative — raise the ask or pull a lever"
    st.markdown(f"""<div class="callout" style="border-left-color:{status_color}">
    <b>Runway status: {status_text}</b><br>
    Deepest modelled cash trough: <b>AED {m['trough']:,.0f}</b> · Model-derived recommended ask (trough × 1.10 buffer):
    <b>AED {m['recommended_ask']:,.0f}</b> · Current ask: <b>AED {assumptions['funding_ask']:,.0f}</b>
    </div>""", unsafe_allow_html=True)

    with st.expander("Full quarterly table"):
        df = pd.DataFrame({
            "Quarter": m['quarters'], "Active contractors": np.round(m['active'], 1),
            "Total revenue": np.round(m['total_rev']), "Total COGS": np.round(m['total_cogs']),
            "Opex": np.round(m['opex']), "EBITDA": np.round(m['ebitda']),
            "Cumulative cash (incl. ask)": np.round(m['cum_cash_incl']),
        })
        st.dataframe(df, use_container_width=True, hide_index=True)

# ============================================================================
# TAB: RISK REGISTER
# ============================================================================
with tab_risk:
    section_head("06 — Risk Register", "Demand-Side Risk — Read This First")
    st.markdown(f"""<div class="callout">
    <b>The cost side of this model is anchored to real market data. The demand side is the exposed assumption —
    and we're saying so ourselves.</b><br><br>
    Revenue is driven almost entirely by <b>tonnes per active contractor per quarter</b> — currently set to
    <b>{assumptions['tonnes_per_contractor']:.1f}</b> in the sidebar. No contractor has confirmed this number yet.
    It moves the outcome more than price or cost do.
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""<div class="callout sand">
    <b>Much of UAE office "greenery" buys no soil at all.</b> A large share of green walls sold in the UAE are
    artificial/faux panels — marketed as lasting 7–10 years, maintenance-free — that buy zero substrate. Real living
    walls typically use modular felt-pocket or hydroponic systems with minimal bulk soil. Real soil demand concentrates
    in potted plants, planters, and landscaped beds — a narrower slice than "all biophilic office greenery" implies.
    </div>""", unsafe_allow_html=True)

    sub_head("How sensitive the model is to this one number")
    df_sens = pd.DataFrame(m['tonnes_sensitivity'])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_sens['tonnes'], y=df_sens['breakeven_contractors'], mode="lines+markers",
                              line=dict(color=SIENNA_DARK, width=3), marker=dict(size=10)))
    fig.add_vline(x=assumptions['tonnes_per_contractor'], line_dash="dash", line_color=BIOCHAR,
                  annotation_text="current setting")
    fig.update_layout(template=PLOTLY_TEMPLATE, height=340, xaxis_title="Tonnes / contractor / quarter",
                       yaxis_title="Contractors needed to break even (Year 3 opex)",
                       title="A small, unvalidated number swings break-even by a year or more")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df_sens.rename(columns={
        "tonnes": "Tonnes/contractor/qtr", "rev_per_contractor_q": "Revenue/contractor/qtr",
        "gp_per_contractor_q": "GP/contractor/qtr", "breakeven_contractors": "Break-even contractors",
        "rev_per_contractor_yr": "Revenue/contractor/yr"}).round(0), use_container_width=True, hide_index=True)

    st.markdown("""<div class="callout green"><b>Mitigation (also the fastest way to de-risk this pitch):</b>
    validate with 3+ interviews of UAE plantscaping/FM contractors — (a) tonnes of soil/substrate per site per year,
    (b) share of their work that's live-soil vs. artificial vs. hydroponic, (c) appetite for a recurring top-dressing
    contract. Three calls confirm or correct the single most load-bearing assumption in this model.</div>""",
                unsafe_allow_html=True)

    section_head("06 — Risk Register", "Business Risk Register")
    risks = [
        ("Feedstock competition", "Industrial buyers (e.g. cement-plant fuel use) compete for camel manure",
         "Sourcing targets farms outside existing industrial buyers' radius; pay a higher-value-add price than commodity fuel use"),
        ("Supplier = competitor", "Camelicious/Viqa are both our biochar supplier and our biggest incumbent threat",
         "Formal supply agreement now; second independent biochar source qualified by Phase 2"),
        ("Channel concentration", "2–3 anchor contractors as the sole go-to-market channel",
         "Secondary FM-association & ESG-consultancy channel added from Phase 1, not later"),
        ("Recurring revenue vs. product success", "A product that works too well could shrink its own reorder cycle",
         "Top-dressing contract decouples recurring revenue from plant mortality"),
    ]
    cols = st.columns(2)
    for i, (title, risk, mitig) in enumerate(risks):
        with cols[i % 2]:
            st.markdown(f"""<div class="metric-card" style="margin-bottom:1rem;">
                <div class="pill">Risk</div><br><b>{title}</b>
                <p style="color:{INK_SOFT};font-size:0.85rem;margin:0.4rem 0;">{risk}</p>
                <div class="pill" style="background:{GREEN};">Mitigation</div>
                <p style="color:{INK};font-size:0.85rem;">{mitig}</p>
                </div>""", unsafe_allow_html=True)

# ============================================================================
# TAB: ROADMAP
# ============================================================================
with tab_road:
    section_head("07 — Roadmap", "5-Year Roadmap — Geography, Feedstock & Segments")

    roadmap = [
        dict(Year="Year 1", Phase="Launch", Start=0, Duration=1,
             Detail="100% camel manure · Home-base free zones · Corporate office greenery"),
        dict(Year="Year 2", Phase="Near Expansion", Start=1, Duration=1,
             Detail="Camel primary, dairy-farm relationships open · Ajman & UAQ · Blend R&D begins"),
        dict(Year="Year 3", Phase="Blend Launch + New Segment", Start=2, Duration=1,
             Detail="50/50 camel-cow blend live · East coast · First government/developer pilot"),
        dict(Year="Year 4", Phase="Second Hub + Commercial", Start=3, Duration=1,
             Detail="Feedstock-agnostic 2nd hub · Government + developers commercial"),
        dict(Year="Year 5", Phase="Full Diversification", Start=4, Duration=1,
             Detail="Camel+cow+poultry+palm biomass · CEA pilot · GCC exploration"),
    ]
    colors = [BIOCHAR, SIENNA, SIENNA_DARK, GREEN, BIOCHAR_2]
    fig = go.Figure()
    for i, r in enumerate(roadmap):
        fig.add_trace(go.Bar(y=[r["Phase"]], x=[r["Duration"]], base=[r["Start"]], orientation="h",
                              marker_color=colors[i], name=r["Year"],
                              hovertext=r["Detail"], hoverinfo="text",
                              text=r["Year"], textposition="inside"))
    fig.update_layout(template=PLOTLY_TEMPLATE, height=340, showlegend=False, barmode="stack",
                       xaxis=dict(title="Year", tickvals=list(range(6))),
                       title="Hover each bar for what actually happens that year")
    st.plotly_chart(fig, use_container_width=True)

    cols = st.columns(5)
    for col, r in zip(cols, roadmap):
        col.markdown(f"""<div class="metric-card"><div class="label">{r['Year']}</div>
            <div style="color:{BIOCHAR};font-weight:700;font-size:1rem;margin:0.3rem 0;">{r['Phase']}</div>
            <div class="sub">{r['Detail']}</div></div>""", unsafe_allow_html=True)

# ============================================================================
# TAB: THE ASK
# ============================================================================
with tab_ask:
    section_head("08 — The Ask", "Funding the Runway")
    c1, c2, c3 = st.columns(3)
    metric_card(c1, "Current Ask", f"AED {assumptions['funding_ask']:,.0f}")
    metric_card(c2, "Model-Recommended Ask", f"AED {m['recommended_ask']:,.0f}", "trough × 1.10 buffer")
    metric_card(c3, "Runway Status", "Covered" if m['runway_ok'] else "Short",
                value_color=GREEN if m['runway_ok'] else SIENNA_DARK)

    colL, colR = st.columns(2)
    with colL:
        fig = go.Figure(data=[go.Pie(
            labels=["Working capital / runway buffer", "Production & blending setup", "BD & contractor acquisition",
                    "MOCCAE registration & pilot testing", "Contingency"],
            values=[40, 25, 15, 10, 10], hole=0.45,
            marker_colors=[BIOCHAR, SIENNA, GREEN, SIENNA_DARK, SAND_2])])
        fig.update_layout(template=PLOTLY_TEMPLATE, height=380, title="Use of funds")
        st.plotly_chart(fig, use_container_width=True)
    with colR:
        fig2 = go.Figure(data=[
            go.Bar(x=["Current ask", "Model-recommended"], y=[assumptions['funding_ask'], m['recommended_ask']],
                   marker_color=[SIENNA, GREEN if m['runway_ok'] else SIENNA_DARK],
                   text=[f"AED {assumptions['funding_ask']:,.0f}", f"AED {m['recommended_ask']:,.0f}"],
                   textposition="outside")
        ])
        fig2.update_layout(template=PLOTLY_TEMPLATE, height=380, title="Ask vs. model-derived requirement")
        st.plotly_chart(fig2, use_container_width=True)

    if not m['runway_ok']:
        st.markdown(f"""<div class="callout"><b>Levers if short (in order of ease):</b>
        (1) raise the deposit percentage negotiated with contractors, (2) validate a higher tonnes/contractor number
        in the field, (3) phase the Year-3 opex step-up later, (4) raise nearer the modelled trough of
        AED {abs(m['trough']):,.0f}.</div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div class="callout green">At current settings, the ask covers the modelled cash trough with
        the built-in buffer. This is the scenario to present live if asked to defend the number.</div>""",
                     unsafe_allow_html=True)

st.markdown("<br><hr><center style='color:#6B6B6B;font-size:0.8rem;'>SAHARASOIL · Group 10 · SP Jain School of Global Management · Entrepreneurship & Digital Leadership</center>", unsafe_allow_html=True)
