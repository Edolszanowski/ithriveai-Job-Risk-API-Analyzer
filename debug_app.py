import streamlit as st
import os
import sys

# Basic page setup
st.set_page_config(
    page_title="Debug App",
    page_icon="🔧",
    layout="wide"
)

st.title("iThriveAI Job Risk Analyzer - Debug Mode")

# Display environment info
st.subheader("Environment Information")
st.write(f"Python version: {sys.version}")
st.write(f"Working directory: {os.getcwd()}")
st.write(f"Directory contents: {os.listdir()}")

# Try to import each module and report success/failure
st.subheader("Module Import Test")

modules_to_test = [
    "pandas", "plotly", "sqlalchemy", "json", "datetime", 
    "simple_comparison", "job_api_integration", "ai_job_displacement", 
    "career_navigator", "data_processor", "database", 
    "db_fallback", "db_refresh", "historical_trends", "bls_connector",
    "bls_employment_data"
]

for module in modules_to_test:
    try:
        __import__(module)
        st.success(f"✅ Successfully imported {module}")
    except Exception as e:
        st.error(f"❌ Failed to import {module}: {str(e)}")

# Check for secrets
st.subheader("Secret Configuration")
try:
    if st.secrets.get("BLS_API_KEY"):
        st.success("✅ BLS_API_KEY is configured")
    else:
        st.warning("⚠️ BLS_API_KEY is not configured")
        
    if st.secrets.get("DATABASE_URL"):
        st.success("✅ DATABASE_URL is configured")
    else:
        st.warning("⚠️ DATABASE_URL is not configured")
except Exception as e:
    st.error(f"❌ Error checking secrets: {str(e)}")
