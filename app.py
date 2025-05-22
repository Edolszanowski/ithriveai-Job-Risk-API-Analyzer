import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import datetime
import os
import sys
import simple_comparison
import job_api_integration
import ai_job_displacement
import time
import re
import career_navigator
from sqlalchemy import create_engine, text

# Import the enhanced autocomplete functionality
from job_title_autocomplete_v2 import job_title_autocomplete, load_job_titles_from_db

# Check if BLS API key is set
bls_api_key = os.environ.get('BLS_API_KEY')

# Page configuration
st.set_page_config(
    page_title="Career AI Impact Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
<style>
    .main {
        background-color: #FFFFFF;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        width: 250px;
        white-space: pre-wrap;
        background-color: #F0F8FF;
        border-radius: 4px 4px 0 0;
        gap: 10px;
        padding-top: 15px;
        padding-bottom: 15px;
        font-size: 18px;
        font-weight: 600;
        text-align: center;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0084FF;
        color: white;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #0084FF;
    }
    .job-risk-low {
        background-color: #d4edda;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .job-risk-moderate {
        background-color: #fff3cd;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .job-risk-high {
        background-color: #f8d7da;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .job-risk-very-high {
        background-color: #f8d7da;
        border-color: #f5c6cb;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
        border-width: 2px;
        border-style: solid;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .st-eb {
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Very simple health check endpoint for reliable monitoring
if 'health' in st.query_params:
    st.write("OK")  # Just return a simple OK response
    st.stop()

# Detailed health check endpoint for troubleshooting
if 'health_check' in st.query_params:
    st.title("iThriveAI Job Analyzer - Health Check")
    
    # Always show application is running
    st.success("✅ Application status: Running")
    
    # Check database connection
    try:
        # Try to connect to the database
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            engine = create_engine(database_url)
            with engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                if result.fetchone():
                    st.success("✅ Database connection: OK")
        else:
            st.warning("⚠️ Database connection: Not configured")
    except Exception as e:
        st.warning("⚠️ Database connection: Using fallback data")
        st.info("ℹ️ The application is running in fallback mode with built-in sample data")
    
    # Check BLS API key
    if bls_api_key:
        st.success("✅ BLS API key: Available")
    else:
        st.warning("⚠️ BLS API key: Not configured")
        
    st.info("ℹ️ This endpoint is used for application monitoring")
    st.stop()  # Stop further execution

# Application title and description
st.image("https://img1.wsimg.com/isteam/ip/70686f32-22d2-489c-a383-6fcd793644be/blob-3712e2e.png/:/rs=h:197,cg:true,m/qt=q:95", width=250)
st.markdown("<h1 style='text-align: center; color: #0084FF;'>Is your job at risk with AI innovation?</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #4CACE5; font-size: 24px; font-weight: 600;'>AI Job Displacement Risk Analyzer</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666666; font-weight: bold; font-size: 16px;'>Discover how AI might impact your career in the next 5 years and get personalized recommendations.</p>", unsafe_allow_html=True)

# Database connection setup (with fallback to in-memory data if not available)
try:
    from database import save_job_search, get_popular_searches, get_highest_risk_jobs, get_lowest_risk_jobs, get_recent_searches
    database_available = True
except:
    from db_fallback import save_job_search, get_popular_searches, get_highest_risk_jobs, get_lowest_risk_jobs, get_recent_searches
    database_available = False

def check_data_refresh():
    """Check if data needs to be refreshed (daily schedule to keep database active)"""
    try:
        with open("last_refresh.json", "r") as f:
            refresh_data = json.load(f)
            last_refresh = datetime.datetime.fromisoformat(refresh_data["date"])
            
            # Refresh if more than a day has passed
            days_since_refresh = (datetime.datetime.now() - last_refresh).days
            
            if days_since_refresh >= 1:
                # Run the daily refresh to keep database active
                try:
                    import db_refresh
                    st.info("Refreshing BLS data and performing database activity...")
                    # Run a sample job update to keep database active
                    sample_job = "Software Developer"
                    db_refresh.update_job_data(sample_job)
                    db_refresh.perform_database_queries()
                    db_refresh.check_and_update_refresh_timestamp()
                    st.success(f"Database activity performed successfully. Updated {sample_job} data.")
                except Exception as e:
                    st.warning(f"Database refresh attempted but encountered an issue: {str(e)}")
                return True
            return False
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        # If file doesn't exist or is invalid, trigger refresh
        with open("last_refresh.json", "w") as f:
            json.dump({"date": datetime.datetime.now().isoformat()}, f)
        return True

# Get cached job data to improve performance
@st.cache_data(ttl=3600)
def get_cached_job_data(job_title):
    """Cache job data to improve performance"""
    try:
        job_data = job_api_integration.get_job_data(job_title)
        return job_data
    except Exception as e:
        st.error(f"Error fetching job data: {str(e)}")
        return None

# Tabs for different sections - use original tab names from screenshots
tabs = st.tabs(["Single Job Analysis", "Job Comparison"])

# Single Job Analysis Tab - Matching original layout
with tabs[0]:  # Single Job Analysis tab
    st.markdown("<h2 style='color: #0084FF;'>Analyze a Job</h2>", unsafe_allow_html=True)
    
    # Display API source information
    if bls_api_key:
        st.info("📊 Using real-time data from the Bureau of Labor Statistics API")
    
    # Job title input with enhanced autocomplete functionality
    st.markdown("Enter any job title to analyze")
    search_job_title = job_title_autocomplete(
        label="Enter your job title",
        key="job_title_search",
        placeholder="Start typing to see suggestions...",
        help="Type a job title and select from matching suggestions"
    )
    
    # Normalize the job title for special cases
    normalized_job_title = search_job_title.lower().strip() if search_job_title else ""
    
    # Check for variations of "Diagnosician" for demo purposes
    if re.search(r'diagnos(i(c|s|t|cian)|e)', normalized_job_title):
        search_job_title = "Diagnosician"
    
    # Add search button and clear button
    col1, col2 = st.columns([1, 4])
    search_clicked = col1.button("Analyze Job Risk")
    clear_search = col2.button("Clear Entry")
    
    # Clear the search when clear button is clicked
    if clear_search:
        st.session_state.job_title_search = ""
        st.rerun()
    
    # Only search when button is clicked and there's a job title
    # Check for data refresh when the app starts
    check_data_refresh()
    
    if search_clicked and search_job_title:
        # Show loading spinner during API calls and data processing
        with st.spinner(f"Analyzing {search_job_title}..."):
            try:
                # Get job data with optimized API calls and caching
                job_data = get_cached_job_data(search_job_title)
                if not job_data:
                    # Fallback to direct API call if caching fails
                    job_data = job_api_integration.get_job_data(search_job_title)
            except ValueError as e:
                if "BLS_API_KEY" in str(e):
                    st.error("The Bureau of Labor Statistics (BLS) API key is needed to fetch real-time data. Using pre-loaded job data instead.")
                    # Use our internal job data instead of BLS data
                    from job_api_integration import get_internal_job_data
                    job_data = get_internal_job_data(search_job_title)
                else:
                    st.error(f"Error: {str(e)}")
                    st.stop()
            
            # Save to database
            if database_available:
                save_job_search(search_job_title, {
                    'year_1_risk': job_data.get('risk_scores', {}).get('year_1', 0),
                    'year_5_risk': job_data.get('risk_scores', {}).get('year_5', 0),
                    'risk_category': job_data.get('risk_category', 'Unknown'),
                    'job_category': job_data.get('job_category', 'Unknown')
                })
            
            # Show results once data is ready
            # Display header with job title and risk assessment
            st.subheader(f"AI Displacement Risk Analysis: {search_job_title}")
            
            # Use columns to create layout matching the screenshots
            job_info_col, risk_gauge_col, risk_factors_col = st.columns([1, 1, 1])
            
            with job_info_col:
                # Job Information section - left column
                st.markdown("<h3 style='color: #0084FF; font-size: 20px;'>Job Information</h3>", unsafe_allow_html=True)
                
                bls_data = job_data.get("bls_data", {})
                if "occupation_code" in job_data:
                    st.markdown(f"**Occupation Code:** {job_data['occupation_code']}")
                elif "occ_code" in bls_data:
                    st.markdown(f"**Occupation Code:** {bls_data['occ_code']}")
                
                st.markdown(f"**Job Category:** {job_data.get('job_category', 'General')}")
                
                if "employment" in bls_data:
                    st.markdown(f"**Current Employment:** {bls_data['employment']:,.0f} jobs")
                
                if "employment_change_percent" in bls_data:
                    growth = bls_data['employment_change_percent']
                    growth_text = f"{growth:+.1f}%" if growth else "No data"
                    st.markdown(f"**BLS Projected Growth:** {growth_text}")
                
                if "annual_job_openings" in bls_data:
                    st.markdown(f"**Annual Job Openings:** {bls_data['annual_job_openings']:,.0f}")
                
                # Career Outlook section
                st.markdown("<h3 style='color: #0084FF; font-size: 20px; margin-top: 20px;'>Career Outlook</h3>", unsafe_allow_html=True)
                st.markdown("<h4 style='color: #0084FF; font-size: 16px;'>Statistics</h4>", unsafe_allow_html=True)
                
                automation_prob = job_data.get("automation_probability", 45.0)
                st.markdown(f"**Task Automation Probability:** {automation_prob:.1f}% of job tasks could be automated")
                
                # Wage trend
                st.markdown("**Wage Trend:** Stable to increasing for specialized roles")
                
                # Employment growth
                st.markdown("**Employment Growth:** Moderate growth projected")
            
            with risk_gauge_col:
                # Overall risk and gauge - center column
                risk_category = job_data.get("risk_category", "High")
                year_1_risk = job_data.get("risk_scores", {}).get("year_1", 35.0)
                year_5_risk = job_data.get("risk_scores", {}).get("year_5", 60.0)
                
                st.markdown(f"<h3 style='text-align: center; margin-bottom: 10px;'>Overall AI Displacement Risk: {risk_category}</h3>", unsafe_allow_html=True)
                
                # Create gauge chart for the risk - ensure it matches the Task Automation Probability
                automation_prob = job_data.get("automation_probability", 45.0)
                
                # Make sure we have valid values for the gauge
                if year_5_risk is None:
                    year_5_risk = 0.6  # Default to 60% if value is None

                # Ensure values are in decimal format (0-1) before converting to percentage
                if year_5_risk > 1:
                    gauge_value = year_5_risk  # Already a percentage
                else:
                    gauge_value = year_5_risk * 100  # Convert to percentage
                
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = gauge_value,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': ""},
                    number = {'suffix': '%', 'font': {'size': 28}},
                    gauge = {
                        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                        'bar': {'color': "#0084FF"},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "gray",
                        'steps': [
                            {'range': [0, 25], 'color': "rgba(0, 255, 0, 0.5)"},
                            {'range': [25, 50], 'color': "rgba(255, 255, 0, 0.5)"},
                            {'range': [50, 75], 'color': "rgba(255, 165, 0, 0.5)"},
                            {'range': [75, 100], 'color': "rgba(255, 0, 0, 0.5)"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': gauge_value
                        }
                    }
                ))
                
                fig.update_layout(
                    height=250,
                    margin=dict(l=20, r=20, t=30, b=20)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Year risks as text
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("<div style='text-align: center;'><h4 style='color: #0084FF; font-size: 18px;'>1-Year Risk</h4></div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center; font-size: 20px; font-weight: bold;'>{year_1_risk:.1f}%</div>", unsafe_allow_html=True)
                with col2:
                    st.markdown("<div style='text-align: center;'><h4 style='color: #0084FF; font-size: 18px;'>5-Year Risk</h4></div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align: center; font-size: 20px; font-weight: bold;'>{year_5_risk:.1f}%</div>", unsafe_allow_html=True)
            
            with risk_factors_col:
                # Risk Factors section - right column
                st.markdown("<h3 style='color: #0084FF; font-size: 20px;'>Key Risk Factors</h3>", unsafe_allow_html=True)
                
                # Get risk factors from job data or provide job-specific defaults based on searched job title
                default_risk_factors = [
                    "Task automation increasingly handles routine work",
                    "AI tools can perform basic analysis and reporting",
                    "Software solutions automate administrative tasks",
                    "Digital platforms reduce need for human oversight"
                ]
                
                # Display risk factors
                risk_factors = job_data.get("risk_factors", default_risk_factors)
                for factor in risk_factors:
                    st.markdown(f"• {factor}")
                
                # Display protective factors
                st.markdown("<h3 style='color: #0084FF; font-size: 20px; margin-top: 20px;'>Protective Factors</h3>", unsafe_allow_html=True)
                
                # Get protective factors or provide job-specific defaults
                default_protective_factors = [
                    "Complex problem-solving requiring human judgment",
                    "Interpersonal skills and relationship building",
                    "Creative thinking and innovation capabilities",
                    "Adaptability to changing situations and requirements"
                ]
                
                # Display protective factors
                protective_factors = job_data.get("protective_factors", default_protective_factors)
                for factor in protective_factors:
                    st.markdown(f"• {factor}")
            
            # Add a divider
            st.markdown("---")
            
            # Add analysis and recommendation sections - full width
            st.markdown("<h3 style='color: #0084FF; font-size: 22px;'>Analysis</h3>", unsafe_allow_html=True)
            
            # Get analysis or provide job-specific default
            default_analysis = f"""
            The {search_job_title} role faces {risk_category.lower()} displacement risk from AI over the next 5 years. 
            While AI and automation tools increasingly handle routine aspects of the job, human professionals who excel 
            at complex problem-solving, creativity, and stakeholder management will remain valuable.
            
            The most significant impacts will be seen in the automation of repetitive tasks, allowing professionals 
            to focus on higher-value activities that require human judgment and creativity.
            """
            
            analysis = job_data.get("analysis", default_analysis)
            st.markdown(f"{analysis}")
            
            # Display Career Navigator button
            st.markdown("<h3 style='color: #0084FF; font-size: 22px;'>Career Navigator</h3>", unsafe_allow_html=True)
            st.markdown("Get personalized skill recommendations and career transition guidance.")
            
            # Career navigator with HTML element
            if st.button("Launch Career Navigator"):
                with st.spinner("Loading Career Navigator..."):
                    time.sleep(1)  # Simulate loading
                    # Use iframe to display career navigator content
                    career_html = career_navigator.get_html()
                    st.markdown(career_html, unsafe_allow_html=True)

# Job Comparison Tab
with tabs[1]:  # Job Comparison tab
    st.markdown("<h2 style='color: #0084FF;'>Compare Jobs</h2>", unsafe_allow_html=True)
    st.write("Compare AI displacement risk between multiple jobs to help with career planning.")
    
    # Two-column layout for job selection
    col1, col2 = st.columns(2)
    
    with col1:
        # First job selection with enhanced autocomplete
        job1 = job_title_autocomplete(
            label="First Job Title",
            key="job1_search",
            placeholder="Start typing to see suggestions...",
            help="Enter the first job to compare"
        )
    
    with col2:
        # Second job selection with enhanced autocomplete
        job2 = job_title_autocomplete(
            label="Second Job Title",
            key="job2_search",
            placeholder="Start typing to see suggestions...",
            help="Enter the second job to compare"
        )
    
    # Compare button
    if st.button("Compare Jobs"):
        if not job1 or not job2:
            st.error("Please enter both job titles to compare.")
        elif job1 == job2:
            st.error("Please select different jobs to compare.")
        else:
            # Show loading spinner
            with st.spinner(f"Comparing {job1} and {job2}..."):
                # Get data for both jobs
                try:
                    # Get job data with caching
                    job1_data = get_cached_job_data(job1)
                    job2_data = get_cached_job_data(job2)
                    
                    if not job1_data or not job2_data:
                        # Fallback to direct API calls if caching fails
                        job1_data = job_api_integration.get_job_data(job1)
                        job2_data = job_api_integration.get_job_data(job2)
                    
                    # Display comparison
                    st.subheader(f"Comparing: {job1} vs {job2}")
                    
                    # Create three columns for comparison
                    metric_col, job1_col, job2_col = st.columns([1, 1, 1])
                    
                    with metric_col:
                        st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
                        st.markdown("<h4>Metric</h4>", unsafe_allow_html=True)
                        st.markdown("<p>Job Category</p>", unsafe_allow_html=True)
                        st.markdown("<p>1-Year Risk</p>", unsafe_allow_html=True)
                        st.markdown("<p>5-Year Risk</p>", unsafe_allow_html=True)
                        st.markdown("<p>Risk Category</p>", unsafe_allow_html=True)
                        st.markdown("<p>Current Employment</p>", unsafe_allow_html=True)
                        st.markdown("<p>Projected Growth</p>", unsafe_allow_html=True)
                        st.markdown("<p>Annual Job Openings</p>", unsafe_allow_html=True)
                    
                    with job1_col:
                        st.markdown(f"<h4>{job1}</h4>", unsafe_allow_html=True)
                        st.markdown(f"<p>{job1_data.get('job_category', 'Unknown')}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p>{job1_data.get('risk_scores', {}).get('year_1', 0):.1f}%</p>", unsafe_allow_html=True)
                        st.markdown(f"<p>{job1_data.get('risk_scores', {}).get('year_5', 0):.1f}%</p>", unsafe_allow_html=True)
                        st.markdown(f"<p>{job1_data.get('risk_category', 'Unknown')}</p>", unsafe_allow_html=True)
                        
                        bls_data1 = job1_data.get("bls_data", {})
                        employment1 = bls_data1.get("employment", "Unknown")
                        if isinstance(employment1, (int, float)):
                            employment1 = f"{employment1:,.0f}"
                        st.markdown(f"<p>{employment1}</p>", unsafe_allow_html=True)
                        
                        growth1 = bls_data1.get("employment_change_percent", "Unknown")
                        if isinstance(growth1, (int, float)):
                            growth1 = f"{growth1:+.1f}%"
                        st.markdown(f"<p>{growth1}</p>", unsafe_allow_html=True)
                        
                        openings1 = bls_data1.get("annual_job_openings", "Unknown")
                        if isinstance(openings1, (int, float)):
                            openings1 = f"{openings1:,.0f}"
                        st.markdown(f"<p>{openings1}</p>", unsafe_allow_html=True)
                    
                    with job2_col:
                        st.markdown(f"<h4>{job2}</h4>", unsafe_allow_html=True)
                        st.markdown(f"<p>{job2_data.get('job_category', 'Unknown')}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p>{job2_data.get('risk_scores', {}).get('year_1', 0):.1f}%</p>", unsafe_allow_html=True)
                        st.markdown(f"<p>{job2_data.get('risk_scores', {}).get('year_5', 0):.1f}%</p>", unsafe_allow_html=True)
                        st.markdown(f"<p>{job2_data.get('risk_category', 'Unknown')}</p>", unsafe_allow_html=True)
                        
                        bls_data2 = job2_data.get("bls_data", {})
                        employment2 = bls_data2.get("employment", "Unknown")
                        if isinstance(employment2, (int, float)):
                            employment2 = f"{employment2:,.0f}"
                        st.markdown(f"<p>{employment2}</p>", unsafe_allow_html=True)
                        
                        growth2 = bls_data2.get("employment_change_percent", "Unknown")
                        if isinstance(growth2, (int, float)):
                            growth2 = f"{growth2:+.1f}%"
                        st.markdown(f"<p>{growth2}</p>", unsafe_allow_html=True)
                        
                        openings2 = bls_data2.get("annual_job_openings", "Unknown")
                        if isinstance(openings2, (int, float)):
                            openings2 = f"{openings2:,.0f}"
                        st.markdown(f"<p>{openings2}</p>", unsafe_allow_html=True)
                    
                    # Divider
                    st.markdown("---")
                    
                    # Comparison Chart - Bar chart comparing 5-year risk
                    st.subheader("5-Year Risk Comparison")
                    
                    # Prepare chart data
                    chart_data = pd.DataFrame({
                        'Job': [job1, job2],
                        'Risk': [
                            job1_data.get('risk_scores', {}).get('year_5', 0),
                            job2_data.get('risk_scores', {}).get('year_5', 0)
                        ]
                    })
                    
                    # Create a bar chart
                    fig = go.Figure()
                    
                    # Add bars with different colors based on risk level
                    for job, risk in zip(chart_data['Job'], chart_data['Risk']):
                        if risk < 25:
                            color = "rgba(0, 255, 0, 0.7)"  # Green for low risk
                        elif risk < 50:
                            color = "rgba(255, 255, 0, 0.7)"  # Yellow for moderate risk
                        elif risk < 75:
                            color = "rgba(255, 165, 0, 0.7)"  # Orange for high risk
                        else:
                            color = "rgba(255, 0, 0, 0.7)"  # Red for very high risk
                        
                        fig.add_trace(go.Bar(
                            x=[job],
                            y=[risk],
                            name=job,
                            marker_color=color,
                            text=[f"{risk:.1f}%"],
                            textposition='auto'
                        ))
                    
                    # Update layout
                    fig.update_layout(
                        title="5-Year AI Displacement Risk",
                        yaxis=dict(
                            title="Risk Percentage",
                            ticksuffix="%",
                            range=[0, 100]  # Fixed range for better comparison
                        ),
                        barmode='group',
                        height=400
                    )
                    
                    # Display the chart
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Comparative Analysis
                    st.subheader("Comparative Analysis")
                    
                    # Determine which job has lower risk
                    job1_risk = job1_data.get('risk_scores', {}).get('year_5', 0)
                    job2_risk = job2_data.get('risk_scores', {}).get('year_5', 0)
                    
                    if job1_risk < job2_risk:
                        lower_risk_job = job1
                        higher_risk_job = job2
                        risk_difference = job2_risk - job1_risk
                    else:
                        lower_risk_job = job2
                        higher_risk_job = job1
                        risk_difference = job1_risk - job2_risk
                    
                    # Create analysis text
                    if risk_difference < 5:
                        analysis_text = f"**{job1}** and **{job2}** have similar AI displacement risk levels (difference of {risk_difference:.1f}%). Both roles face comparable challenges from automation in the next 5 years."
                    else:
                        analysis_text = f"**{lower_risk_job}** has {risk_difference:.1f}% lower AI displacement risk than **{higher_risk_job}**. This suggests that {lower_risk_job} may offer more job security over the next 5 years."
                    
                    st.markdown(analysis_text)
                    
                    # Add career recommendation based on the comparison
                    st.subheader("Career Recommendation")
                    
                    if risk_difference < 5:
                        recommendation = "Since both roles have similar risk profiles, consider which job better aligns with your skills, interests, and long-term career goals. Focus on developing complementary skills that enhance your value in either role."
                    elif job1_risk < job2_risk:
                        recommendation = f"Based on AI displacement risk alone, {job1} offers more job security. However, also consider factors like job satisfaction, salary potential, and alignment with your skills and interests before making a career decision."
                    else:
                        recommendation = f"Based on AI displacement risk alone, {job2} offers more job security. However, also consider factors like job satisfaction, salary potential, and alignment with your skills and interests before making a career decision."
                    
                    st.markdown(recommendation)
                    
                    # Career transition button
                    if st.button("Career Transition Plan"):
                        with st.spinner("Loading Career Navigator..."):
                            time.sleep(1)  # Simulate loading
                            career_html = career_navigator.get_html()
                            st.markdown(career_html, unsafe_allow_html=True)
                
                except Exception as e:
                    st.error(f"Error comparing jobs: {str(e)}")

# Sidebar with recent searches and statistics
with st.sidebar:
    st.markdown("<h3 style='color: #0084FF;'>Job Search Insights</h3>", unsafe_allow_html=True)
    
    # Recent searches
    st.markdown("<h4 style='color: #0084FF;'>Recent Searches</h4>", unsafe_allow_html=True)
    recent_searches = get_recent_searches(limit=5)
    for job in recent_searches:
        job_title = job.get("job_title", "Unknown")
        risk = job.get("year_5_risk", 0)
        risk_text = f"{risk:.1f}%" if isinstance(risk, (int, float)) else "Unknown"
        risk_class = "job-risk-low"
        if risk >= 75:
            risk_class = "job-risk-very-high"
        elif risk >= 50:
            risk_class = "job-risk-high"
        elif risk >= 25:
            risk_class = "job-risk-moderate"
        
        st.markdown(f"""
        <div class="{risk_class}">
            <strong>{job_title}</strong><br>
            5-Year Risk: {risk_text}
        </div>
        """, unsafe_allow_html=True)
    
    # Most popular searches
    st.markdown("<h4 style='color: #0084FF;'>Popular Searches</h4>", unsafe_allow_html=True)
    popular_searches = get_popular_searches(limit=5)
    for job in popular_searches:
        st.markdown(f"• {job.get('job_title', 'Unknown')}")
    
    # High and Low Risk Jobs
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h4 style='color: #0084FF; font-size: 14px;'>Highest Risk</h4>", unsafe_allow_html=True)
        highest_risk = get_highest_risk_jobs(limit=5)
        for job in highest_risk:
            st.markdown(f"• {job.get('job_title', 'Unknown')}")
    
    with col2:
        st.markdown("<h4 style='color: #0084FF; font-size: 14px;'>Lowest Risk</h4>", unsafe_allow_html=True)
        lowest_risk = get_lowest_risk_jobs(limit=5)
        for job in lowest_risk:
            st.markdown(f"• {job.get('job_title', 'Unknown')}")
    
    # Database status
    st.markdown("---")
    if database_available:
        st.success("✅ Using connected database")
    else:
        st.info("ℹ️ Using local storage (database not connected)")
    
    # Version info
    st.markdown("<div style='font-size: 12px; color: #999;'>iThriveAI Job Risk Analyzer v2.5 - Enhanced Autocomplete</div>", unsafe_allow_html=True)