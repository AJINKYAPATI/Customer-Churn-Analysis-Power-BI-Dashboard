"""
Customer Churn & Risk Analysis Dashboard
Streamlit recreation of Power BI dashboards.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import io

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Customer Churn Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# THEME CONSTANTS
# ─────────────────────────────────────────────
GREEN = "#00C49A"
GREEN_DARK = "#00A87E"
GREEN_LIGHT = "#E6FFF9"
ORANGE = "#F4A020"
PURPLE = "#6B3FA0"
PINK = "#E91E8C"
BLUE = "#1E90FF"
RED = "#E53935"
TEAL = "#00BCD4"
BG_CARD = "#FFFFFF"
TEXT_DARK = "#1A1A2E"
TEXT_MUTED = "#6B7280"
BORDER = "#E5E7EB"

# ─────────────────────────────────────────────
# CSS STYLING
# ─────────────────────────────────────────────
def inject_css(dark_mode: bool) -> None:
    bg_main = "#0F172A" if dark_mode else "#F0F4F8"
    bg_card = "#1E293B" if dark_mode else "#FFFFFF"
    text_main = "#F1F5F9" if dark_mode else TEXT_DARK
    text_sub = "#94A3B8" if dark_mode else TEXT_MUTED
    border_col = "#334155" if dark_mode else BORDER
    sidebar_bg = "#0F172A" if dark_mode else "#FFFFFF"

    st.markdown(f"""
    <style>
    /* ── Global ── */
    .stApp {{ background-color: {bg_main}; font-family: 'Segoe UI', sans-serif; }}
    .block-container {{ padding: 1rem 2rem 2rem 2rem; }}

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {{
        background-color: {sidebar_bg};
        border-right: 1px solid {border_col};
    }}
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stMultiSelect label,
    [data-testid="stSidebar"] .stSlider label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {{
        color: {text_main} !important;
    }}

    /* ── Header banner ── */
    .dashboard-header {{
        background: linear-gradient(135deg, {GREEN} 0%, {GREEN_DARK} 100%);
        color: white;
        padding: 14px 24px;
        border-radius: 12px;
        margin-bottom: 20px;
        font-size: 22px;
        font-weight: 700;
        letter-spacing: 1px;
        box-shadow: 0 4px 15px rgba(0,196,154,0.3);
    }}

    /* ── KPI card ── */
    .kpi-card {{
        background: {bg_card};
        border-radius: 12px;
        padding: 18px 20px;
        border: 1px solid {border_col};
        box-shadow: 0 2px 10px rgba(0,0,0,0.07);
        text-align: center;
        transition: transform .2s, box-shadow .2s;
        height: 110px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }}
    .kpi-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.13);
    }}
    .kpi-value {{
        font-size: 28px;
        font-weight: 700;
        margin: 0;
        line-height: 1.2;
    }}
    .kpi-label {{
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
        color: {text_sub};
        margin-top: 4px;
    }}

    /* ── Section card ── */
    .section-card {{
        background: {bg_card};
        border-radius: 12px;
        padding: 16px 18px;
        border: 1px solid {border_col};
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 16px;
    }}
    .section-title {{
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        color: {GREEN};
        border-bottom: 2px solid {GREEN};
        padding-bottom: 8px;
        margin-bottom: 12px;
    }}

    /* ── Plotly charts transparent bg ── */
    .js-plotly-plot .plotly {{ background: transparent !important; }}

    /* ── Sidebar filter label ── */
    .filter-label {{
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        color: {GREEN};
        margin-bottom: 4px;
    }}

    /* ── Insight box ── */
    .insight-box {{
        background: {GREEN_LIGHT if not dark_mode else "#0D2B24"};
        border-left: 4px solid {GREEN};
        border-radius: 6px;
        padding: 10px 14px;
        margin-top: 8px;
        font-size: 13px;
        color: {text_main};
    }}

    /* ── Toggle label ── */
    .toggle-row {{
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 14px;
    }}
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# DATA LOADING & PROCESSING
# ─────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    df = pd.read_excel("02_Customer_Churn-Dataset.xlsx")
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce").fillna(0)
    df["SeniorCitizen"] = df["SeniorCitizen"].map({0: "No", 1: "Yes"})
    df["ChurnBinary"] = (df["Churn"] == "Yes").astype(int)
    df["TenureGroup"] = pd.cut(
        df["tenure"],
        bins=[0, 12, 24, 36, 48, 60, 72],
        labels=["<1 Year", "<2 Year", "<3 Year", "<4 Year", "<5 Year", "<6 Year"],
    )
    return df


# ─────────────────────────────────────────────
# PLOTLY CHART HELPERS
# ─────────────────────────────────────────────
def chart_layout(fig, dark_mode: bool, height: int = 300, margin=None) -> go.Figure:
    paper_bg = "#1E293B" if dark_mode else "white"
    plot_bg = "#1E293B" if dark_mode else "white"
    font_color = "#F1F5F9" if dark_mode else TEXT_DARK
    grid_color = "#334155" if dark_mode else "#F3F4F6"

    fig.update_layout(
        paper_bgcolor=paper_bg,
        plot_bgcolor=plot_bg,
        font=dict(color=font_color, family="Segoe UI", size=11),
        height=height,
        margin=margin or dict(l=10, r=10, t=30, b=10),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=10),
        ),
        xaxis=dict(gridcolor=grid_color, showgrid=False),
        yaxis=dict(gridcolor=grid_color),
    )
    return fig


def kpi_card(value: str, label: str, color: str = TEXT_DARK) -> str:
    return f"""
    <div class="kpi-card">
        <div class="kpi-value" style="color:{color}">{value}</div>
        <div class="kpi-label">{label}</div>
    </div>
    """


# ─────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────
def sidebar_filters(df: pd.DataFrame, dark_mode: bool) -> pd.DataFrame:
    st.sidebar.markdown(
        f'<div style="text-align:center;padding:10px 0;font-size:18px;'
        f'font-weight:700;color:{GREEN}">⚙️ Filters</div>',
        unsafe_allow_html=True,
    )

    def multi(label, col, options):
        st.sidebar.markdown(f'<div class="filter-label">{label}</div>', unsafe_allow_html=True)
        sel = st.sidebar.multiselect("", options, default=options, key=label, label_visibility="collapsed")
        return sel if sel else options

    churn_opts = multi("Churn", "Churn", sorted(df["Churn"].unique()))
    internet_opts = multi("Internet Service", "InternetService", sorted(df["InternetService"].unique()))
    contract_opts = multi("Contract Type", "Contract", sorted(df["Contract"].unique()))
    payment_opts = multi("Payment Method", "PaymentMethod", sorted(df["PaymentMethod"].unique()))
    gender_opts = multi("Gender", "gender", sorted(df["gender"].unique()))
    senior_opts = multi("Senior Citizen", "SeniorCitizen", sorted(df["SeniorCitizen"].unique()))

    st.sidebar.markdown("---")
    st.sidebar.markdown(f'<div class="filter-label">Tenure (Months)</div>', unsafe_allow_html=True)
    min_t, max_t = int(df["tenure"].min()), int(df["tenure"].max())
    tenure_range = st.sidebar.slider("", min_t, max_t, (min_t, max_t), label_visibility="collapsed")

    st.sidebar.markdown("---")
    st.sidebar.markdown(f'<div class="filter-label">🔍 Search Customer ID</div>', unsafe_allow_html=True)
    search = st.sidebar.text_input("", placeholder="e.g. 7590-VHVEG", label_visibility="collapsed")

    # Apply filters
    mask = (
        df["Churn"].isin(churn_opts)
        & df["InternetService"].isin(internet_opts)
        & df["Contract"].isin(contract_opts)
        & df["PaymentMethod"].isin(payment_opts)
        & df["gender"].isin(gender_opts)
        & df["SeniorCitizen"].isin(senior_opts)
        & df["tenure"].between(tenure_range[0], tenure_range[1])
    )
    if search.strip():
        mask &= df["customerID"].str.contains(search.strip(), case=False, na=False)

    filtered = df[mask].copy()

    # Download button
    st.sidebar.markdown("---")
    csv_buf = io.StringIO()
    filtered.to_csv(csv_buf, index=False)
    st.sidebar.download_button(
        "⬇️  Download Filtered Data",
        csv_buf.getvalue(),
        "filtered_churn_data.csv",
        "text/csv",
        use_container_width=True,
    )

    st.sidebar.markdown(
        f'<div style="text-align:center;color:{TEXT_MUTED};font-size:11px;margin-top:8px">'
        f'{len(filtered):,} of {len(df):,} records</div>',
        unsafe_allow_html=True,
    )
    return filtered


# ─────────────────────────────────────────────
# PAGE 1 — CUSTOMER CHURN DASHBOARD
# ─────────────────────────────────────────────
def page_churn(df: pd.DataFrame, dark_mode: bool) -> None:
    churned = df[df["Churn"] == "Yes"]

    # ── KPI Row ──────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(kpi_card(f"{len(churned):,}", "Customers at Risk", RED), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card(f"{int(churned['numTechTickets'].sum()):,}", "# of Tech Tickets", PURPLE), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card(f"{int(churned['numAdminTickets'].sum()):,}", "# Admin Tickets", ORANGE), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_card(f"${churned['TotalCharges'].sum()/1e6:.2f}M", "Yearly Charges", GREEN_DARK), unsafe_allow_html=True)
    with c5:
        st.markdown(kpi_card(f"{churned['MonthlyCharges'].sum()/1e3:.2f}K", "Monthly Charges", BLUE), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 2: Demographics | Subscribed Services ──
    left, right = st.columns([5, 5])

    with left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Demographics by Gender</div>', unsafe_allow_html=True)

        dl, dm, dr = st.columns([4, 3, 3])

        # Donut – churned by gender
        with dl:
            gender_counts = churned["gender"].value_counts()
            fig = go.Figure(go.Pie(
                labels=gender_counts.index,
                values=gender_counts.values,
                hole=0.55,
                marker_colors=[ORANGE, GREEN],
                textinfo="percent+label",
                textfont_size=10,
            ))
            fig.update_layout(
                showlegend=True,
                title=dict(text="Churned by Gender", font=dict(size=11)),
                height=200, margin=dict(l=0, r=0, t=30, b=0),
                paper_bgcolor="#1E293B" if dark_mode else "white",
                font=dict(color="#F1F5F9" if dark_mode else TEXT_DARK),
                legend=dict(orientation="h", yanchor="bottom", y=-0.15, bgcolor="rgba(0,0,0,0)"),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # Demographics metrics
        with dm:
            pct_senior = round(df["SeniorCitizen"].eq("Yes").mean() * 100)
            pct_partner = round(df["Partner"].eq("Yes").mean() * 100)
            pct_dep = round(df["Dependents"].eq("Yes").mean() * 100)
            st.markdown(f"""
            <div style="padding:10px 0">
                <div style="font-size:28px;font-weight:700;color:{GREEN}">{pct_senior}%</div>
                <div style="font-size:11px;color:{TEXT_MUTED}">Senior Citizen</div>
                <br>
                <div style="font-size:28px;font-weight:700;color:{ORANGE}">{pct_partner}%</div>
                <div style="font-size:11px;color:{TEXT_MUTED}">Partner</div>
                <br>
                <div style="font-size:28px;font-weight:700;color:{PURPLE}">{pct_dep}%</div>
                <div style="font-size:11px;color:{TEXT_MUTED}">Dependents</div>
            </div>
            """, unsafe_allow_html=True)

        # Subscription time horizontal bar
        with dr:
            tg = (churned["TenureGroup"].value_counts(normalize=True) * 100).sort_index()
            fig2 = go.Figure(go.Bar(
                x=tg.values,
                y=tg.index.astype(str),
                orientation="h",
                marker_color=GREEN,
                text=[f"{v:.2f}%" for v in tg.values],
                textposition="outside",
                textfont=dict(size=9),
            ))
            fig2.update_layout(
                title=dict(text="Subscription Time", font=dict(size=11)),
                height=200, margin=dict(l=10, r=40, t=30, b=10),
                xaxis=dict(showticklabels=False, showgrid=False),
                yaxis=dict(showgrid=False),
                paper_bgcolor="#1E293B" if dark_mode else "white",
                plot_bgcolor="#1E293B" if dark_mode else "white",
                font=dict(color="#F1F5F9" if dark_mode else TEXT_DARK, size=10),
            )
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Subscribed Services</div>', unsafe_allow_html=True)

        # Service subscription %
        services = {
            "Tech Support": df["TechSupport"].eq("Yes").mean(),
            "Streaming TV": df["StreamingTV"].eq("Yes").mean(),
            "Streaming Movies": df["StreamingMovies"].eq("Yes").mean(),
            "Device Protection": df["DeviceProtection"].eq("Yes").mean(),
            "Online Backup": df["OnlineBackup"].eq("Yes").mean(),
            "Online Security": df["OnlineSecurity"].eq("Yes").mean(),
        }
        svc_colors = [TEAL, ORANGE, ORANGE, GREEN, GREEN_DARK, PURPLE]

        r1 = st.columns(3)
        r2 = st.columns(3)

        for i, (svc, pct) in enumerate(services.items()):
            row = r1 if i < 3 else r2
            col = row[i % 3]
            border_color = svc_colors[i]
            with col:
                st.markdown(
                    f'<div style="border:2px solid {border_color};border-radius:8px;'
                    f'padding:10px;text-align:center;margin-bottom:6px">'
                    f'<div style="font-size:22px;font-weight:700;color:{border_color}">{pct*100:.0f}%</div>'
                    f'<div style="font-size:10px;color:{TEXT_MUTED}">{svc}</div></div>',
                    unsafe_allow_html=True,
                )

        # Phone service + multiple lines
        phone_pct = df["PhoneService"].eq("Yes").mean() * 100
        ml_yes = df["MultipleLines"].eq("Yes").mean() * 100
        ml_no = 100 - ml_yes
        st.markdown(
            f'<div style="display:flex;gap:10px;align-items:center;margin-top:4px">'
            f'<div style="border:2px solid {GREEN};border-radius:8px;padding:8px 12px;text-align:center;flex:1">'
            f'<div style="font-size:22px;font-weight:700;color:{GREEN}">{phone_pct:.0f}%</div>'
            f'<div style="font-size:10px;color:{TEXT_MUTED}">Phone Service</div></div>'
            f'<div style="font-size:18px">→</div>'
            f'<div style="font-size:12px;font-weight:600;color:{ORANGE}">Multiple Lines<br>'
            f'<span style="color:{ORANGE}">{ml_yes:.2f}% Yes</span> &nbsp; '
            f'<span style="color:{PURPLE}">{ml_no:.2f}% No</span></div></div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 3: Customer Account | Internet Service Users ──
    left2, right2 = st.columns([5, 5])

    with left2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Customer Account Information</div>', unsafe_allow_html=True)

        ac1, ac2, ac3 = st.columns(3)

        # Payment method bar
        with ac1:
            pm = churned["PaymentMethod"].value_counts()
            pm_pct = (pm / pm.sum() * 100)
            pm_short = pm_pct.index.str.replace(r"\s*\(.*\)", "", regex=True).str[:10]
            fig_pm = go.Figure(go.Bar(
                x=pm_pct.values,
                y=pm_short,
                orientation="h",
                marker_color=[PURPLE, BLUE, ORANGE, RED],
                text=[f"{v:.2f}%" for v in pm_pct.values],
                textposition="outside",
                textfont=dict(size=9),
            ))
            fig_pm.update_layout(
                title=dict(text="Payment Method", font=dict(size=11)),
                height=200, margin=dict(l=0, r=40, t=30, b=0),
                xaxis=dict(showticklabels=False, showgrid=False),
                yaxis=dict(showgrid=False, tickfont=dict(size=9)),
                paper_bgcolor="#1E293B" if dark_mode else "white",
                plot_bgcolor="#1E293B" if dark_mode else "white",
                font=dict(color="#F1F5F9" if dark_mode else TEXT_DARK),
            )
            st.plotly_chart(fig_pm, use_container_width=True, config={"displayModeBar": False})

        # Paperless billing donut
        with ac2:
            pb = churned["PaperlessBilling"].value_counts()
            fig_pb = go.Figure(go.Pie(
                labels=pb.index,
                values=pb.values,
                hole=0.6,
                marker_colors=[GREEN, ORANGE],
                textinfo="percent",
                textfont_size=10,
            ))
            avg_monthly = churned["MonthlyCharges"].mean()
            avg_total = churned["TotalCharges"].mean()
            fig_pb.update_layout(
                title=dict(text="Paperless Billing", font=dict(size=11)),
                height=200, margin=dict(l=0, r=0, t=30, b=0),
                showlegend=True,
                legend=dict(orientation="h", y=-0.1, bgcolor="rgba(0,0,0,0)", font=dict(size=9)),
                paper_bgcolor="#1E293B" if dark_mode else "white",
                font=dict(color="#F1F5F9" if dark_mode else TEXT_DARK),
                annotations=[dict(text=f"", showarrow=False)],
            )
            st.plotly_chart(fig_pb, use_container_width=True, config={"displayModeBar": False})
            st.markdown(
                f'<div style="text-align:center;font-size:11px;margin-top:-10px">'
                f'<b>Avg Charges</b><br>'
                f'<span style="color:{GREEN}">${avg_monthly:.2f}</span> Monthly<br>'
                f'<span style="color:{ORANGE}">${avg_total:,.0f}</span> Total</div>',
                unsafe_allow_html=True,
            )

        # Contract type bar
        with ac3:
            ct = churned["Contract"].value_counts()
            ct_pct = ct / ct.sum() * 100
            ct_short = ct_pct.index.str.replace("-to-", "-", regex=False)
            fig_ct = go.Figure(go.Bar(
                x=ct_pct.values,
                y=ct_short,
                orientation="h",
                marker_color=[PINK, BLUE, ORANGE],
                text=[f"{v:.2f}%" for v in ct_pct.values],
                textposition="outside",
                textfont=dict(size=9),
            ))
            fig_ct.update_layout(
                title=dict(text="Type of Contracts", font=dict(size=11)),
                height=200, margin=dict(l=0, r=50, t=30, b=0),
                xaxis=dict(showticklabels=False, showgrid=False),
                yaxis=dict(showgrid=False, tickfont=dict(size=9)),
                paper_bgcolor="#1E293B" if dark_mode else "white",
                plot_bgcolor="#1E293B" if dark_mode else "white",
                font=dict(color="#F1F5F9" if dark_mode else TEXT_DARK),
            )
            st.plotly_chart(fig_ct, use_container_width=True, config={"displayModeBar": False})

        st.markdown('</div>', unsafe_allow_html=True)

    with right2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Internet Service Users</div>', unsafe_allow_html=True)

        is_counts = churned["InternetService"].value_counts()
        is_pct = is_counts / is_counts.sum() * 100
        is_colors = {"Fiber optic": RED, "DSL": ORANGE, "No": BLUE}
        colors_list = [is_colors.get(i, GREEN) for i in is_pct.index]

        fig_is = go.Figure(go.Bar(
            x=is_pct.values,
            y=is_pct.index,
            orientation="h",
            marker_color=colors_list,
            text=[f"{v:.2f}%" for v in is_pct.values],
            textposition="outside",
            textfont=dict(size=11),
        ))
        fig_is.update_layout(
            height=250, margin=dict(l=10, r=60, t=10, b=10),
            xaxis=dict(showticklabels=False, showgrid=False, range=[0, 90]),
            yaxis=dict(showgrid=False, tickfont=dict(size=12)),
            paper_bgcolor="#1E293B" if dark_mode else "white",
            plot_bgcolor="#1E293B" if dark_mode else "white",
            font=dict(color="#F1F5F9" if dark_mode else TEXT_DARK),
        )
        st.plotly_chart(fig_is, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Insight box ──
    top_churn_contract = df.groupby("Contract")["ChurnBinary"].mean().idxmax()
    top_churn_is = df.groupby("InternetService")["ChurnBinary"].mean().idxmax()
    st.markdown(
        f'<div class="insight-box">💡 <b>Key Insight:</b> '
        f'{len(churned):,} customers have churned ({len(churned)/len(df)*100:.1f}%). '
        f'<b>{top_churn_contract}</b> contracts and <b>{top_churn_is}</b> internet '
        f'service users show the highest churn rates.</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# PAGE 2 — CUSTOMER RISK ANALYSIS DASHBOARD
# ─────────────────────────────────────────────
def page_risk(df: pd.DataFrame, dark_mode: bool) -> None:
    total = len(df)
    churn_rate = df["ChurnBinary"].mean() * 100
    yearly = df["TotalCharges"].sum()
    admin_t = int(df["numAdminTickets"].sum())
    tech_t = int(df["numTechTickets"].sum())

    # ── KPI Row ──────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(kpi_card(f"{total:,}", "Total Customers", ORANGE), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card(f"{churn_rate:.2f}%", "Churn Rate", RED), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card(f"${yearly/1e6:.2f}M", "Yearly Charges", GREEN_DARK), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_card(f"{admin_t:,}", "Admin Tickets", PURPLE), unsafe_allow_html=True)
    with c5:
        st.markdown(kpi_card(f"{tech_t:,}", "Tech Tickets", BLUE), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 2: three charts ──────────────────
    r2a, r2b, r2c = st.columns(3)

    with r2a:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        is_churn = df.groupby("InternetService")["ChurnBinary"].mean() * 100
        fig = go.Figure(go.Bar(
            x=is_churn.index,
            y=is_churn.values,
            marker_color=[ORANGE, RED, GREEN],
            text=[f"{v:.2f}%" for v in is_churn.values],
            textposition="outside",
        ))
        fig = chart_layout(fig, dark_mode, height=250)
        fig.update_layout(title=dict(text="Churn Rate by Internet Service", font=dict(size=12)))
        fig.update_xaxis(title_text="Internet Service")
        fig.update_yaxis(title_text="Churn Rate %", range=[0, 55])
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with r2b:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        is_counts = df["InternetService"].value_counts()
        fig2 = go.Figure(go.Pie(
            labels=is_counts.index,
            values=is_counts.values,
            marker_colors=[ORANGE, GREEN, BLUE],
            textinfo="label+percent",
            textfont_size=10,
        ))
        fig2.update_layout(
            title=dict(text="# Customers by Internet Service", font=dict(size=12)),
            height=250, margin=dict(l=10, r=10, t=40, b=10),
            showlegend=False,
            paper_bgcolor="#1E293B" if dark_mode else "white",
            font=dict(color="#F1F5F9" if dark_mode else TEXT_DARK),
        )
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with r2c:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        mc_by_is = df.groupby("InternetService")["MonthlyCharges"].sum() / 1e3
        fig3 = go.Figure(go.Pie(
            labels=mc_by_is.index,
            values=mc_by_is.values,
            marker_colors=[ORANGE, GREEN, BLUE],
            textinfo="label+value",
            texttemplate="%{label}<br>%{value:.1f}K",
            textfont_size=10,
        ))
        fig3.update_layout(
            title=dict(text="Sum of Monthly Charges", font=dict(size=12)),
            height=250, margin=dict(l=10, r=10, t=40, b=10),
            showlegend=False,
            paper_bgcolor="#1E293B" if dark_mode else "white",
            font=dict(color="#F1F5F9" if dark_mode else TEXT_DARK),
        )
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Row 3: three more charts ──────────────
    r3a, r3b, r3c = st.columns(3)

    with r3a:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        ct_churn = df.groupby("Contract")["ChurnBinary"].mean() * 100
        ct_count = df.groupby("Contract").size()
        ct_short = [c.replace("-to-", "-") for c in ct_churn.index]

        fig4 = make_subplots(specs=[[{"secondary_y": True}]])
        fig4.add_trace(go.Bar(
            x=ct_short, y=ct_count.values,
            name="Customers", marker_color=[PURPLE, ORANGE, TEAL],
            text=[f"{v:,}" for v in ct_count.values], textposition="inside",
        ), secondary_y=False)
        fig4.add_trace(go.Scatter(
            x=ct_short, y=ct_churn.values,
            name="Churn Rate", mode="lines+markers+text",
            line=dict(color=BLUE, width=2),
            marker=dict(size=8, color=BLUE),
            text=[f"{v:.2f}%" for v in ct_churn.values],
            textposition="top center", textfont=dict(size=9),
        ), secondary_y=True)

        fig4 = chart_layout(fig4, dark_mode, height=270)
        fig4.update_layout(
            title=dict(text="Type of Contract", font=dict(size=12)),
            legend=dict(orientation="h", y=-0.2),
        )
        fig4.update_yaxes(title_text="Customers", secondary_y=False, showgrid=False)
        fig4.update_yaxes(title_text="Churn %", secondary_y=True, showgrid=False)
        st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with r3b:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        tg_churn = df.groupby("TenureGroup", observed=False)["ChurnBinary"].mean() * 100
        tg_mc = df.groupby("TenureGroup", observed=False)["MonthlyCharges"].sum() / 1e3

        bar_colors = [PINK, "#FFD700", GREEN, BLUE, ORANGE, TEAL]
        fig5 = make_subplots(specs=[[{"secondary_y": True}]])
        fig5.add_trace(go.Bar(
            x=tg_churn.index.astype(str), y=tg_mc.values,
            name="Monthly Charges (K)", marker_color=bar_colors,
            text=[f"${v:.2f}M" if v > 100 else f"${v:.0f}K" for v in tg_mc.values],
            textposition="inside", textfont=dict(size=8),
        ), secondary_y=False)
        fig5.add_trace(go.Scatter(
            x=tg_churn.index.astype(str), y=tg_churn.values,
            name="Churn Rate", mode="lines+markers+text",
            line=dict(color=BLUE, width=2),
            marker=dict(size=7, color=BLUE),
            text=[f"{v:.2f}%" for v in tg_churn.values],
            textposition="top center", textfont=dict(size=8),
        ), secondary_y=True)

        fig5 = chart_layout(fig5, dark_mode, height=270)
        fig5.update_layout(
            title=dict(text="Years of Contract", font=dict(size=12)),
            legend=dict(orientation="h", y=-0.2),
        )
        fig5.update_yaxes(title_text="Monthly Charges (K)", secondary_y=False, showgrid=False)
        fig5.update_yaxes(title_text="Churn %", secondary_y=True, showgrid=False)
        st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with r3c:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        pm_churn = df.groupby("PaymentMethod")["ChurnBinary"].mean() * 100
        pm_mc = df.groupby("PaymentMethod")["MonthlyCharges"].sum() / 1e6
        pm_short = pm_churn.index.str.replace(r"\s*\(.*\)", "", regex=True).str.strip()

        pm_colors = [PURPLE, PINK, ORANGE, TEAL]
        fig6 = make_subplots(specs=[[{"secondary_y": True}]])
        fig6.add_trace(go.Bar(
            x=pm_short, y=pm_mc.values,
            name="Monthly Charges (M)", marker_color=pm_colors,
            text=[f"${v:.2f}M" for v in pm_mc.values],
            textposition="inside", textfont=dict(size=8),
        ), secondary_y=False)
        fig6.add_trace(go.Scatter(
            x=pm_short, y=pm_churn.values,
            name="Churn Rate", mode="lines+markers+text",
            line=dict(color=PURPLE, width=2),
            marker=dict(size=7, color=PURPLE),
            text=[f"{v:.2f}%" for v in pm_churn.values],
            textposition="top center", textfont=dict(size=8),
        ), secondary_y=True)

        fig6 = chart_layout(fig6, dark_mode, height=270)
        fig6.update_layout(
            title=dict(text="Churn by Payment Method", font=dict(size=12)),
            legend=dict(orientation="h", y=-0.2),
        )
        fig6.update_xaxis(tickfont=dict(size=9))
        fig6.update_yaxes(title_text="Monthly Charges (M)", secondary_y=False, showgrid=False)
        fig6.update_yaxes(title_text="Churn %", secondary_y=True, showgrid=False)
        st.plotly_chart(fig6, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Insight ──
    worst_pm = df.groupby("PaymentMethod")["ChurnBinary"].mean().idxmax()
    worst_is = df.groupby("InternetService")["ChurnBinary"].mean().idxmax()
    st.markdown(
        f'<div class="insight-box">📊 <b>Risk Insight:</b> '
        f'Overall churn rate is <b>{churn_rate:.1f}%</b>. '
        f'<b>{worst_pm}</b> payment users and <b>{worst_is}</b> internet users '
        f'are highest risk segments. Month-to-month contracts churn at <b>'
        f'{df[df["Contract"]=="Month-to-month"]["ChurnBinary"].mean()*100:.1f}%</b>.</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# PAGE 3 — DATA EXPLORER
# ─────────────────────────────────────────────
def page_explorer(df: pd.DataFrame, dark_mode: bool) -> None:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📋 Raw Data Explorer</div>', unsafe_allow_html=True)

    cols_to_show = st.multiselect(
        "Select columns to display",
        df.columns.tolist(),
        default=["customerID", "gender", "SeniorCitizen", "Contract",
                 "InternetService", "MonthlyCharges", "TotalCharges", "Churn"],
    )
    st.dataframe(
    df[cols_to_show],
    use_container_width=True
)
        ),
        use_container_width=True,
        height=400,
    )
    st.markdown(
        f'<div style="font-size:12px;color:{TEXT_MUTED};margin-top:6px">'
        f'Showing {len(df):,} records</div>',
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # Summary stats
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📈 Summary Statistics</div>', unsafe_allow_html=True)
    num_cols = df.select_dtypes(include="number").columns.tolist()
    st.dataframe(df[num_cols].describe().round(2), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main() -> None:
    # Dark mode toggle in sidebar
    st.sidebar.markdown("---")
    dark_mode = st.sidebar.toggle("🌙  Dark Mode", value=False)

    inject_css(dark_mode)

    df_raw = load_data()

    # Navigation
    st.sidebar.markdown(
        f'<div style="font-size:11px;font-weight:700;letter-spacing:1px;'
        f'color:{GREEN};text-transform:uppercase;margin-bottom:6px">Navigation</div>',
        unsafe_allow_html=True,
    )
    page = st.sidebar.radio(
        "",
        ["📊 Churn Dashboard", "⚠️ Risk Analysis", "🔍 Data Explorer"],
        label_visibility="collapsed",
    )
    st.sidebar.markdown("---")

    # Apply filters
    df_filtered = sidebar_filters(df_raw, dark_mode)

    # Header
    title_map = {
        "📊 Churn Dashboard": "CUSTOMER CHURN DASHBOARD",
        "⚠️ Risk Analysis": "CUSTOMER RISK ANALYSIS DASHBOARD",
        "🔍 Data Explorer": "DATA EXPLORER",
    }
    st.markdown(f'<div class="dashboard-header">📊 {title_map[page]}</div>', unsafe_allow_html=True)

    if page == "📊 Churn Dashboard":
        page_churn(df_filtered, dark_mode)
    elif page == "⚠️ Risk Analysis":
        page_risk(df_filtered, dark_mode)
    else:
        page_explorer(df_filtered, dark_mode)


if __name__ == "__main__":
    main()
