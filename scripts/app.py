import streamlit as st
import pandas as pd
import json
import plotly.express as px
import os
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="AI Trading Monitor", layout="wide", page_icon="🚀")

st.title("🚀 AI News Sentiment Dashboard")
st.write("Real-time Monitoring: Strategy based on Impact & Confidence Score")

def load_data():
    """Loads news from the processed JSON file and calculates Priority."""
    path = "data/processed_news.json"
    if not os.path.exists(path):
        return pd.DataFrame()
        
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f) 
            
        rows = []
        for entry in data:
            # FIX FOR TICKER (LIST -> STRING)
            ticker_raw = entry.get("ticker", "N/A")
            if isinstance(ticker_raw, list):
                ticker_clean = ", ".join(ticker_raw) # Transform ["V", "MA"] în "V, MA"
            else:
                ticker_clean = str(ticker_raw)

            # Extract scores and calculate Priority
            impact = float(entry.get("impact_score", 0))
            conf = float(entry.get("confidence", 0))
            
            # Priority Formula: (Impact * Confidence) / 100
            priority = round((impact * conf) / 100, 2)
            
            try:
                # Parse the analysis timestamp for display
                ts = datetime.strptime(entry["analyzed_at"], "%Y-%m-%d %H:%M:%S")
                clean_time = ts.strftime("%b %d, %H:%M")
            except:
                clean_time = "Recent"

            rows.append({
                "Time": clean_time,
                "Ticker": ticker_clean,
                "Sector": entry.get("sector", "N/A"),
                "Title": entry.get("title", "No Title"),
                "Sentiment": entry.get("price_impact", "Neutral"),
                "Impact": impact,
                "Conf %": conf,
                "Priority": priority,
                "Logic": entry.get("logic", ""),
            })
            
        df = pd.DataFrame(rows)
        if not df.empty:
            # High-priority signals and recent news move to the top
            df = df.sort_values(by=["Priority", "Time"], ascending=[False, False])
        return df
    except Exception as e:
        st.error(f"Error reading data: {e}")
        return pd.DataFrame()

# --- MAIN DASHBOARD LOGIC ---
try:
    df = load_data()

    if df.empty:
        st.warning("No data found yet. Please run the AI News Bot first!")
    else:
        # --- TOP METRICS ---
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total News processed", len(df))
        with col2:
            critical = len(df[df['Priority'] >= 7])
            st.metric("Golden Signals (Prio > 7)", critical)
        with col3:
            top_ticker = df['Ticker'].mode()[0] if not df.empty else "N/A"
            st.metric("Hottest Ticker", top_ticker)
        with col4:
            avg_conf = f"{int(df['Conf %'].mean())}%"
            st.metric("Avg AI Confidence", avg_conf)

        # --- OPPORTUNITIES TABLE ---
        st.subheader("🔥 Top Trading Opportunities (Sorted by Priority)")
        
        # UI Styling: Highlights high-priority signals and color-codes sentiment
        def style_rows(row):
            styles = [''] * len(row)
            if row['Priority'] >= 7:
                return ['background-color: #1e4620; color: white'] * len(row) # High priority highlight
            if row['Sentiment'] == 'Bearish':
                return ['color: #ff4b4b'] * len(row) # Red text
            if row['Sentiment'] == 'Bullish':
                return ['color: #00ff00'] * len(row) # Green text
            return styles

        st.dataframe(
            df.style.apply(style_rows, axis=1)
            .format({
                "Impact": "{:.1f}", 
                "Conf %": "{:.0f}%", 
                "Priority": "{:.2f}"
            }), 
            width='stretch',
            height=500,
            hide_index=True
        )

        # --- VISUAL ANALYSIS ---
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("Sector Distribution")
            fig_sector = px.pie(
                df, names='Sector', hole=0.4, 
                color_discrete_sequence=px.colors.sequential.RdBu,
                template="plotly_dark"
            )
            st.plotly_chart(fig_sector, width='stretch')

        with col_right:
            st.subheader("Priority vs Time Analysis")
            # Scatter plot to identify "clusters" of high-impact news over time
            fig_scatter = px.scatter(
                df, x="Time", y="Priority", 
                size="Impact", color="Sentiment",
                hover_data=["Ticker", "Title"],
                color_discrete_map={"Bullish": "#00ff00", "Bearish": "#ff4b4b", "Neutral": "#808080"},
                template="plotly_dark"
            )
            st.plotly_chart(fig_scatter, width='stretch')

except Exception as e:
    st.error(f"Dashboard Load Error: {e}")