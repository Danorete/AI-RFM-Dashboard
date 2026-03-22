import os
from pathlib import Path

import anthropic
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

_DIR = Path(__file__).resolve().parent
load_dotenv(_DIR / ".env")

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

st.set_page_config(page_title="RFM AI Dashboard", layout="wide")
st.title("Customer Segment AI Insights")
st.markdown("Powered by RFM Analysis + Claude AI")

@st.cache_data
def load_rfm():
    return pd.read_csv(_DIR / "rfm_results.csv")

df = load_rfm()

st.subheader("RFM Segment Overview")
st.dataframe(df.head(20))

st.subheader("Segment Distribution")
if "Segment" in df.columns:
    segment_counts = df["Segment"].value_counts()
    st.bar_chart(segment_counts)

st.subheader("AI-Generated Insights")

if st.button("Generate Insights with Claude"):
    segment_summary = df["Segment"].value_counts().to_string() if "Segment" in df.columns else df.describe().to_string()
    
    with st.spinner("Claude is analyzing your customer segments..."):
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": f"""You are a senior data analyst. Analyze these customer segments from an RFM analysis and provide actionable business insights:

{segment_summary}

For each segment provide:
1. What this segment means for the business
2. Risk level (churn risk, growth potential)
3. Specific marketing recommendations
4. Priority level

Keep it concise and actionable."""
                }
            ]
        )
        
        st.markdown(message.content[0].text)

st.subheader("Key Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Customers", len(df))
if "Segment" in df.columns:
    col2.metric("Total Segments", df["Segment"].nunique())
if "Monetary" in df.columns:
    col3.metric("Avg Monetary Value", f"${df['Monetary'].mean():.2f}")