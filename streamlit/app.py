import sys
from pathlib import Path

# Add the src directory to the path so ai_analytics_agent is importable
sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "ai_analytics_agent" / "src")
)


import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import streamlit.components.v1 as components
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from ai_analytics_agent.crew import AiAnalyticsAgent  # type: ignore

# ─────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Agent Analytics",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# Dark Theme Styles — Sans-serif throughout
# ─────────────────────────────────────────────
st.markdown(
    """
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap');

  :root {
    --bg:      #0d0f14;
    --surface: #161a23;
    --border:  #252a36;
    --accent:  #4f8ef7;
    --accent2: #a78bfa;
    --text:    #e2e8f0;
    --muted:   #64748b;
    --success: #34d399;
    --warning: #fbbf24;
  }

  html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
  }

  /* Hide sidebar toggle */
  [data-testid="collapsedControl"] { display: none !important; }
  section[data-testid="stSidebar"] { display: none !important; }

  h1, h2, h3, h4, h5, h6 {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    color: var(--text) !important;
  }

  p, li, span, div {
    font-family: 'DM Sans', sans-serif !important;
  }

  .stTabs [data-baseweb="tab-list"] {
    background-color: var(--surface);
    border-bottom: 1px solid var(--border);
    gap: 0;
  }

  .stTabs [data-baseweb="tab"] {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem;
    font-weight: 500;
    color: var(--muted) !important;
    padding: 0.75rem 1.5rem;
    border-bottom: 2px solid transparent;
  }

  .stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
    background: transparent !important;
  }

  .stTextInput input, .stSelectbox select {
    background-color: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 6px;
    font-family: 'DM Sans', sans-serif !important;
  }

  .stButton button {
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    color: white !important;
    border: none !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    padding: 0.6rem 2rem !important;
    border-radius: 6px !important;
    transition: opacity 0.2s;
  }

  .stButton button:hover { opacity: 0.85; }

  .metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.2rem;
    text-align: center;
  }

  .metric-val {
    font-family: 'DM Sans', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--accent);
  }

  .metric-label {
    font-size: 0.8rem;
    color: var(--muted);
    margin-top: 0.25rem;
  }

  .insight-box {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent2);
    border-radius: 8px;
    padding: 1.4rem 1.6rem;
    margin-top: 1rem;
  }

  .insight-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
  }

  .stDataFrame { background: var(--surface) !important; }

  div[data-testid="stMarkdownContainer"] p {
    color: var(--text);
    font-family: 'DM Sans', sans-serif !important;
  }

  /* SQL code block — keep monospace only here */
  .sql-block {
    background: #0a0c10;
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 6px;
    padding: 1rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.78rem;
    color: #7dd3fc;
    white-space: pre-wrap;
    margin-top: 0.5rem;
  }
</style>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# Global Color Palette
# ─────────────────────────────────────────────
CHART_COLOR = "#4f8ef7"
COLORWAY = [CHART_COLOR, "#a78bfa", "#34d399", "#fbbf24", "#f87171"]
PLOT_BGCOLOR = "#0d0f14"
PAPER_BGCOLOR = "#161a23"
FONT_COLOR = "#e2e8f0"
GRID_COLOR = "#252a36"

# ─────────────────────────────────────────────
# Preloaded Questions
# ─────────────────────────────────────────────
PRELOADED_QUESTIONS = {
    "── Sales & Revenue ──": None,
    "What are total sales by month?": "What are total sales by month?",
    "Which product categories generate the most revenue?": "Which product categories generate the most revenue?",
    "What is the average order value by state?": "What is the average order value by state?",
    "What is the total freight value vs product value by category?": "What is the total freight value vs product value by category?",
    "Which payment types are most commonly used?": "Which payment types are most commonly used?",
    "── Orders & Volume ──": None,
    "How many orders were placed per month?": "How many orders were placed per month?",
    "What is the order status breakdown?": "What is the order status breakdown?",
    "Which states have the most orders?": "Which states have the most orders?",
    "How many unique customers placed orders in each state?": "How many unique customers placed orders?",
    "── Products & Categories ──": None,
    "Which product categories have the highest average review score?": "Which product categories have the highest average review score?",
    "What are the top 10 selling product categories by volume?": "What are the top 10 selling product categories by volume?",
    "Which categories have the highest freight cost relative to price?": "Which categories have the highest freight cost relative to price?",
    "── Sellers ──": None,
    "Which sellers have the highest total sales?": "Which sellers have the highest total sales?",
    "Which sellers have the best average review scores?": "Which sellers have the best average review scores?",
    "How many unique sellers are there per state?": "How many unique sellers are there per state?",
    "── Delivery & Experience ──": None,
    "What is the average delivery time by state?": "What is the average delivery time by state?",
    "Which states have the longest delivery times?": "Which states have the longest delivery times?",
    "Is there a correlation between delivery days and review score?": "Is there a correlation between delivery days and review score?",
    "Which product categories have the slowest delivery?": "Which product categories have the slowest delivery?",
    "── Payments ──": None,
    "What is the average payment value by payment type?": "What is the average payment value by payment type?",
    "How does payment type vary by state?": "How does payment type vary by state?",
}

# ─────────────────────────────────────────────
# Session State Initialization
# ─────────────────────────────────────────────
if "result" not in st.session_state:
    st.session_state.result = None
if "sql_query" not in st.session_state:
    st.session_state.sql_query = None
if "running_question" not in st.session_state:
    st.session_state.running_question = None

# ─────────────────────────────────────────────
# Tabs
# ─────────────────────────────────────────────
tab1, tab2 = st.tabs(["📊  Overview", "🔍  Ask a Question"])

# ─────────────────────────────────────────────
# TAB 1 — Overview
# ─────────────────────────────────────────────
with tab1:
    st.markdown("## Agent Analytics")
    st.markdown(
        "<p style='color:#64748b;font-size:1rem;'>An AI-powered BI system built on the Olist Brazilian e-commerce dataset.</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    col1, col2, col3, col4 = st.columns(4)
    for col, val, label in zip(
        [col1, col2, col3, col4],
        ["99k+", "96k+", "3k+", "73"],
        ["Orders", "Customers", "Sellers", "Product Categories"],
    ):
        with col:
            st.markdown(
                f'<div class="metric-card"><div class="metric-val">{val}</div><div class="metric-label">{label}</div></div>',
                unsafe_allow_html=True,
            )

    st.divider()

    st.markdown("### Data Model — analytics_orders view")
    st.markdown(
        "<p style='color:#64748b;'>A denormalized analytics view joining all core Olist tables into a single queryable surface.</p>",
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("**Core Dimensions**")
        dims = {
            "🧑 Customer": ["customer_id", "customer_state"],
            "📦 Product": ["product_id", "product_category_name_english"],
            "🏪 Seller": ["seller_id"],
            "💳 Payment": ["payment_type", "payment_value"],
        }
        for dim, cols in dims.items():
            st.markdown(f"**{dim}**")
            for c in cols:
                st.markdown(
                    f"<code style='color:#4f8ef7;background:transparent;'>{c}</code>",
                    unsafe_allow_html=True,
                )

    with col_right:
        st.markdown("**Facts & Metrics**")
        facts = {
            "🛒 Order": [
                "order_id",
                "order_status",
                "order_purchase_timestamp",
                "purchase_month",
            ],
            "💰 Financials": ["price", "freight_value", "order_item_value"],
            "⭐ Experience": ["review_score", "delivery_days"],
        }
        for fact, cols in facts.items():
            st.markdown(f"**{fact}**")
            for c in cols:
                st.markdown(
                    f"<code style='color:#a78bfa;background:transparent;'>{c}</code>",
                    unsafe_allow_html=True,
                )

    st.divider()

    st.markdown("### How It Works")
    col1, col2, col3, col4 = st.columns(4)
    steps = [
        (
            "1",
            "Manager",
            "Interprets your question and creates a structured query plan",
        ),
        ("2", "SQL Generator", "Writes a DuckDB SQL query from the plan"),
        ("3", "Visualizer", "Selects the best chart type and prepares metadata"),
        ("4", "Insight Analyst", "Generates a plain English summary and key takeaway"),
    ]
    for col, (num, title, desc) in zip([col1, col2, col3, col4], steps):
        with col:
            st.markdown(
                f"""
            <div class="metric-card" style="text-align:left;padding:1rem;">
                <div style="color:#4f8ef7;font-size:0.72rem;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:0.4rem;">Step {num}</div>
                <div style="font-weight:600;font-size:1rem;margin-bottom:0.4rem;">{title}</div>
                <div style="color:#64748b;font-size:0.85rem;">{desc}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

# ─────────────────────────────────────────────
# TAB 2 — Ask a Question
# ─────────────────────────────────────────────
with tab2:
    st.markdown("## Ask a Question")
    st.markdown(
        "<p style='color:#64748b;'>Type your own question or select one from the dropdown below.</p>",
        unsafe_allow_html=True,
    )

    # Initialize current question in session state
    if "current_question" not in st.session_state:
        st.session_state.current_question = ""

    selected = st.selectbox(
        "Choose a preloaded question or type your own below",
        options=list(PRELOADED_QUESTIONS.keys()),
        label_visibility="visible",
    )

    if selected and PRELOADED_QUESTIONS.get(selected):
        st.session_state.current_question = PRELOADED_QUESTIONS[selected]

    user_question = st.text_input(
        "Or type your own question",
        value=st.session_state.current_question,
        placeholder="e.g. Which product categories generate the most revenue?",
    )

    analyze_clicked = st.button("⚡  Analyze")

    st.divider()

    # ── Trigger Analysis ──
    if analyze_clicked and user_question and not user_question.startswith("──"):
        st.session_state.result = None
        st.session_state.sql_query = None
        st.session_state.running_question = user_question

    # ── Run Analysis ──
    if st.session_state.running_question:
        question = st.session_state.running_question

        with st.status("Running analysis...", expanded=True) as status:
            try:
                st.write("🧠 Manager interpreting question...")
                crew = AiAnalyticsAgent()

                st.write("⚙️ SQL Generator writing query...")
                result = crew.run_ai_analytics(question=question)

                st.write("📊 Visualizer preparing chart...")
                st.write("💡 Insight Analyst generating summary...")

                st.session_state.sql_query = result["sql_query"]
                st.session_state.result = result
                st.session_state.running_question = None

                status.update(label="Analysis complete!", state="complete")

            except Exception as e:
                st.session_state.running_question = None
                status.update(label="Analysis failed", state="error")
                st.error(f"Analysis failed: {e}")

    # ── SQL Inspector ──
    if st.session_state.sql_query:
        with st.expander("🔍 SQL Inspector", expanded=False):
            st.markdown(
                f'<div class="sql-block">{st.session_state.sql_query}</div>',
                unsafe_allow_html=True,
            )

    # ── Display Results ──

    if st.session_state.result:
        result = st.session_state.result
        df = result["dataframe"]
        df = df.replace("None", np.nan).dropna(subset=[df.columns[0]])
        for col in df.columns[1:]:
            converted = pd.to_numeric(df[col], errors="coerce")
            if converted.notna().all():
                df[col] = converted

        chart_meta = result["chart_metadata"]
        insight = result["insight"]

        # Safety check — fall back to actual column names if fields don't match
        if chart_meta.x_field not in df.columns or chart_meta.y_field not in df.columns:
            cols = df.columns.tolist()
            chart_meta = chart_meta.model_copy(
                update={
                    "x_field": cols[0],
                    "y_field": cols[1] if len(cols) > 1 else cols[0],
                }
            )
            st.warning(f"Chart fields adjusted to match data columns: {cols}")

        st.markdown("### Results")

        chart_fn = {
            "bar": px.bar,
            "line": px.line,
            "pie": px.pie,
            "scatter": px.scatter,
            "histogram": px.histogram,
            "box": px.box,
            "area": px.area,
        }

        df = df.reset_index(drop=True)

        fn = chart_fn.get(chart_meta.chart_type, px.bar)
        if chart_meta.chart_type == "pie":
            fig = fn(
                df,
                names=chart_meta.x_field,
                values=chart_meta.y_field,
                title=chart_meta.title,
            )
        else:
            fig = fn(
                df,
                x=chart_meta.x_field,
                y=chart_meta.y_field,
                title=chart_meta.title,
                color_discrete_sequence=COLORWAY,
            )

        fig.update_layout(
            paper_bgcolor=PAPER_BGCOLOR,
            plot_bgcolor=PLOT_BGCOLOR,
            font_color=FONT_COLOR,
            font_family="DM Sans",
            title_font_size=15,
            # colorway=COLORWAY,
        )
        fig.update_xaxes(gridcolor=GRID_COLOR)
        fig.update_yaxes(gridcolor=GRID_COLOR)

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("**Data Table**")
        st.dataframe(df, use_container_width=True, hide_index=True)

        anomaly_html = ""
        if insight.anomalies:
            anomaly_html = f"""
            <div style="margin-top:0.75rem;padding-top:0.75rem;border-top:1px solid #252a36;">
                <div style="font-size:0.72rem;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;color:#fbbf24;margin-bottom:0.4rem;">⚠ Anomaly</div>
                <p style="color:#fbbf24;margin:0;font-family:'DM Sans',sans-serif;font-size:0.95rem;">{insight.anomalies}</p>
            </div>"""

        insight_html = f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&display=swap');
        * {{ font-family: 'DM Sans', sans-serif; box-sizing: border-box; }}
        </style>
        <div style="background:#161a23;border:1px solid #252a36;border-left:3px solid #a78bfa;border-radius:8px;padding:1.4rem 1.6rem;">
            <div style="font-size:0.72rem;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;color:#a78bfa;margin-bottom:0.4rem;">AI Insight</div>
            <p style="color:#e2e8f0;margin-bottom:0.75rem;font-size:0.95rem;">{insight.summary}</p>
            <div style="font-size:0.72rem;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;color:#64748b;margin-bottom:0.4rem;">Key Takeaway</div>
            <p style="color:#4f8ef7;font-weight:500;margin:0;font-size:0.95rem;">{insight.key_takeaway}</p>
            <br>
            {anomaly_html}
        </div>"""

        components.html(insight_html, height=350)

        # anomaly_html = ""
        # if insight.anomalies:
        #     anomaly_html = f"""
        #     <div style="margin-top:0.75rem;padding-top:0.75rem;border-top:1px solid #252a36;">
        #         <div class="insight-label" style="color:#fbbf24;">⚠ Anomaly</div>
        #         <p style="color:#fbbf24;margin:0;">{insight.anomalies}</p>
        #     </div>"""

        # st.markdown(
        #     f"""
        # <div class="insight-box">
        #     <div class="insight-label" style="color:#a78bfa;">AI Insight</div>
        #     <p style="margin-bottom:0.75rem;">{insight.summary}</p>
        #     <div class="insight-label" style="color:#64748b;">Key Takeaway</div>
        #     <p style="color:#4f8ef7;font-weight:500;margin:0;">{insight.key_takeaway}</p>
        #     {anomaly_html}
        # </div>
        # """,
        #     unsafe_allow_html=True,
        # )
