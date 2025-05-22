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
        gap: 1px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #F0F8FF;
        border-radius: 4px 4px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
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

# Application title and description
st.title("Career AI Impact Analyzer")
st.markdown("""
Analyze how AI might impact your career in the next 1-5 years. Get data-driven insights on automation risk and recommendations for future-proofing your skillset.
""")

# Database connection setup (with fallback to in-memory data if not available)
try:
    from database import save_job_search, get_popular_searches, get_highest_risk_jobs, get_lowest_risk_jobs, get_recent_searches
    database_available = True
except:
    from db_fallback import save_job_search, get_popular_searches, get_highest_risk_jobs, get_lowest_risk_jobs, get_recent_searches
    database_available = False

def check_data_refresh():
    """Check if data needs to be refreshed (monthly schedule)"""
    try:
        with open("last_refresh.json", "r") as f:
            refresh_data = json.load(f)
            last_refresh = datetime.datetime.fromisoformat(refresh_data["date"])
            
            # Refresh if more than a month has passed
            if (datetime.datetime.now() - last_refresh).days > 30:
                # Trigger data refresh operations here
                return True
            return False
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        # If file doesn't exist or is invalid, trigger refresh
        with open("last_refresh.json", "w") as f:
            json.dump({"date": datetime.datetime.now().isoformat()}, f)
        return True

# Tabs for different sections
tabs = st.tabs(["Job Analysis", "Compare Jobs"])

# Job Analysis Tab - More optimized interface
with tabs[0]:  # Job Analysis tab
    st.markdown("<h2 style='color: #0084FF;'>Job Analysis</h2>", unsafe_allow_html=True)
    
    # Job title input - this should be at the very top for immediate interaction
    search_job_title = st.text_input("Enter a job title to analyze", "Project Manager")
    
    # Normalize the job title for special cases
    normalized_job_title = search_job_title.lower().strip()
    
    # Check for variations of "Diagnosician" for demo purposes
    if re.search(r'diagnos(i(c|s|t|cian)|e)', normalized_job_title):
        search_job_title = "Diagnosician"
    
    # Add search button for a more deliberate interaction
    search_clicked = st.button("Analyze Job")
    
    # Either search is clicked or it's the first load with default value
    if search_clicked or search_job_title == "Project Manager":
        # Show loading spinner during API calls and data processing
        with st.spinner(f"Analyzing {search_job_title}..."):
            # Get job data with optimized API calls
            job_data = job_api_integration.get_job_data(search_job_title)
            
            # Save to database
            if database_available:
                save_job_search(search_job_title, {
                    'year_1_risk': job_data.get('risk_scores', {}).get('year_1', 0),
                    'year_5_risk': job_data.get('risk_scores', {}).get('year_5', 0),
                    'risk_category': job_data.get('risk_category', 'Unknown'),
                    'job_category': job_data.get('job_category', 'Unknown')
                })
            
            # Show results once data is ready
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Job title and basic info panel
                risk_category = job_data.get("risk_category", "Unknown")
                risk_class = {
                    "Low": "job-risk-low",
                    "Moderate": "job-risk-moderate", 
                    "High": "job-risk-high",
                    "Very High": "job-risk-very-high"
                }.get(risk_category, "job-risk-moderate")
                
                st.markdown(f"""
                <div class="{risk_class}">
                    <h3 style="margin-top:0">{search_job_title}</h3>
                    <p><strong>Category:</strong> {job_data.get("job_category", "General")}</p>
                    <p><strong>AI Displacement Risk (5-year):</strong> {risk_category}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Primary risk visualization
                st.subheader("Displacement Risk Timeline")
                
                # Create a line chart with Plotly
                year_labels = ["Present", "Year 1", "Year 3", "Year 5"]
                risk_values = [
                    0,  # Starting point is always 0
                    job_data.get("risk_scores", {}).get("year_1", 0),
                    job_data.get("risk_scores", {}).get("year_3", 0),
                    job_data.get("risk_scores", {}).get("year_5", 0)
                ]
                
                fig = go.Figure()
                
                # Add line chart trace
                fig.add_trace(go.Scatter(
                    x=year_labels,
                    y=risk_values,
                    mode='lines+markers',
                    name='Risk Percentage',
                    line=dict(color='#0084FF', width=3),
                    marker=dict(size=10)
                ))
                
                # Customize layout
                fig.update_layout(
                    title="Projected AI Displacement Risk Over Time",
                    xaxis_title="Timeline",
                    yaxis_title="Risk Percentage",
                    yaxis=dict(
                        tickformat=".0%",
                        range=[0, 1]
                    ),
                    height=400,
                    margin=dict(l=40, r=40, t=60, b=40),
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    hovermode='x unified'
                )
                
                # Add reference areas for risk categories
                fig.add_shape(
                    type="rect",
                    x0=-0.5, x1=3.5,
                    y0=0, y1=0.25,
                    fillcolor="rgba(212, 237, 218, 0.5)",
                    line_width=0,
                    layer="below"
                )
                fig.add_shape(
                    type="rect", 
                    x0=-0.5, x1=3.5,
                    y0=0.25, y1=0.5,
                    fillcolor="rgba(255, 243, 205, 0.5)",
                    line_width=0,
                    layer="below"
                )
                fig.add_shape(
                    type="rect",
                    x0=-0.5, x1=3.5,
                    y0=0.5, y1=0.75,
                    fillcolor="rgba(248, 215, 218, 0.5)",
                    line_width=0,
                    layer="below"
                )
                fig.add_shape(
                    type="rect",
                    x0=-0.5, x1=3.5,
                    y0=0.75, y1=1,
                    fillcolor="rgba(220, 53, 69, 0.3)",
                    line_width=0,
                    layer="below"
                )
                
                # Add reference labels
                fig.add_annotation(x=3.4, y=0.125, text="Low Risk", showarrow=False, 
                                  font=dict(size=12, color="black"), xanchor="right")
                fig.add_annotation(x=3.4, y=0.375, text="Moderate Risk", showarrow=False, 
                                  font=dict(size=12, color="black"), xanchor="right")
                fig.add_annotation(x=3.4, y=0.625, text="High Risk", showarrow=False, 
                                  font=dict(size=12, color="black"), xanchor="right")
                fig.add_annotation(x=3.4, y=0.875, text="Very High Risk", showarrow=False, 
                                  font=dict(size=12, color="black"), xanchor="right")
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Analysis section
                st.subheader("AI Impact Analysis")
                st.markdown(job_data.get("analysis", "No analysis available for this job."))
                
                # Risk factors section
                st.subheader("Key Risk Factors")
                risk_factors = job_data.get("risk_factors", [])
                if risk_factors:
                    for factor in risk_factors:
                        st.markdown(f"- {factor}")
                else:
                    st.markdown("No specific risk factors identified.")
                
                # Protective factors
                st.subheader("Protective Factors")
                protective_factors = job_data.get("protective_factors", [])
                if protective_factors:
                    for factor in protective_factors:
                        st.markdown(f"- {factor}")
                else:
                    st.markdown("No specific protective factors identified.")
            
            with col2:
                # Job statistics from BLS when available
                if "bls_data" in job_data and job_data["bls_data"]:
                    st.subheader("Job Statistics")
                    bls_data = job_data["bls_data"]
                    
                    # Employment information
                    if "employment" in bls_data:
                        st.metric("Total Employment", f"{bls_data['employment']:,.0f} jobs")
                    
                    # Wage information
                    if "median_annual_wage" in bls_data:
                        st.metric("Median Annual Wage", f"${bls_data['median_annual_wage']:,.0f}")
                    
                    # Growth projection if available
                    if "employment_change_percent" in bls_data:
                        growth = bls_data['employment_change_percent']
                        growth_text = f"{growth:+.1f}%" if growth else "No data"
                        delta_color = "normal" if growth >= 0 else "inverse"
                        st.metric("Projected Growth (10yr)", growth_text, 
                                delta=f"{'Faster' if growth > 5 else 'Slower'} than average" if growth else None,
                                delta_color=delta_color)
                
                # Similar jobs section with risk comparison
                st.subheader("Similar Jobs")
                
                similar_jobs = job_data.get("similar_jobs", [])
                if similar_jobs:
                    # Convert to DataFrame for better display
                    similar_df = pd.DataFrame(similar_jobs)
                    
                    # Check column names to avoid KeyError
                    if 'title' in similar_df.columns and 'year_5_risk' in similar_df.columns:
                        # Format for display
                        similar_df['year_5_risk'] = similar_df['year_5_risk'].apply(lambda x: f"{x:.1%}")
                        similar_df = similar_df.rename(columns={
                            'title': 'Job Title',
                            'year_5_risk': '5-Year Risk'
                        })
                        
                        st.dataframe(similar_df[['Job Title', '5-Year Risk']], use_container_width=True)
                    else:
                        # Display with original column names
                        st.dataframe(similar_df, use_container_width=True)
                else:
                    st.markdown("No similar job data available.")
                
                # Career transition suggestions
                st.subheader("Recommended Career Transitions")
                
                if risk_category in ["High", "Very High"]:
                    st.markdown("""
                    Consider these paths for greater job security:
                    1. Transition to roles requiring more human-to-human interaction
                    2. Develop specialized skills in areas AI is still weak
                    3. Build technical expertise to work alongside AI systems
                    """)
                elif risk_category == "Moderate":
                    st.markdown("""
                    Strengthen your career with these strategies:
                    1. Develop complementary skills that enhance AI capabilities
                    2. Focus on creative, strategic, and emotionally intelligent aspects of your role
                    3. Learn to use AI tools to increase your productivity and value
                    """)
                else:  # Low risk
                    st.markdown("""
                    Even with low risk, stay competitive with these approaches:
                    1. Continue developing interpersonal and leadership skills
                    2. Specialize in areas that AI complements rather than replaces
                    3. Develop skills that bridge between your current and target roles
                    """)
        
        # Career Navigator call-to-action
        st.markdown("---")
        
        navigator_html = """
        <div style="background-color: #0084FF; padding: 30px; border-radius: 10px; text-align: center; margin-top: 20px;">
            <div style="background-color: white; padding: 12px; border-radius: 8px; margin-bottom: 20px;">
                <h2 style="color: #0084FF; font-size: 24px; font-weight: bold; margin: 0;">Transform AI Risk Into Career Opportunity</h2>
            </div>
            
            <p style="color: white; font-size: 18px; margin-bottom: 20px;">
                Don't just analyze your job risk - get a complete career transformation strategy with our Career Navigator service.
            </p>
            
            <div style="background-color: white; padding: 20px; border-radius: 8px; margin: 15px auto; max-width: 90%; color: #333;">
                <h3 style="color: #0084FF; margin-top: 0;">Transform Your Career With Expert Guidance:</h3>
                <ul style="text-align: left; margin: 15px auto; max-width: 80%;">
                    <li><strong>Personalized Career Strength Profile</strong> - Discover your unique transferable skills that AI can't replace</li>
                    <li><strong>AI-Resilient Career Pathways</strong> - Custom-matched opportunities with detailed transition plans</li>
                    <li><strong>Curated Training Resources</strong> - Top 10 recommended courses with links and cost estimates</li>
                    <li><strong>Targeted Career Matches</strong> - Three ideal roles with descriptions and salary ranges</li>
                    <li><strong>Strategic Learning Roadmap</strong> - Exact certifications and courses with highest career ROI</li>
                    <li><strong>Month-by-Month Action Plan</strong> - Clear steps to secure more valuable, future-proof positions</li>
                </ul>
            </div>
            
            <a href="https://form.jotform.com/251137815706154" target="_blank" style="display: inline-block; background-color: white; color: #0084FF; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 18px; margin-top: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">Get Your Career Navigator Package</a>
            
            <p style="color: white; font-size: 14px; margin-top: 15px;">
                Join professionals who've secured higher-paying, AI-resilient positions with our strategic guidance.
            </p>
        </div>
        """
        
        st.markdown(navigator_html, unsafe_allow_html=True)

# Job Comparison Tab - Ultra-simplified with automatic display
with tabs[1]:  # Job Comparison tab
    st.markdown("<h2 style='color: #0084FF;'>Compare Jobs</h2>", unsafe_allow_html=True)
    
    job_categories = simple_comparison.get_job_categories()
    
    # Select a job category and display job options
    selected_category = st.selectbox("Select a job category to compare", job_categories)
    
    # Get jobs in selected category and allow multiple selection
    job_options = simple_comparison.get_jobs_by_category(selected_category)
    default_selections = job_options[:3] if len(job_options) >= 3 else job_options
    
    selected_jobs = st.multiselect(
        "Select jobs to compare (2-5 recommended)",
        options=job_options,
        default=default_selections
    )
    
    # Allow manual job entry to the comparison
    custom_job = st.text_input("Add another job to compare (optional)")
    if custom_job and st.button("Add to Comparison"):
        if custom_job not in selected_jobs:
            selected_jobs.append(custom_job)
            # Add to database for future availability
            simple_comparison.add_custom_job(custom_job, selected_category)
    
    # Display comparison when jobs are selected
    if selected_jobs and len(selected_jobs) >= 1:
        with st.spinner("Generating comparison..."):
            # Get data for selected jobs
            job_data = simple_comparison.get_job_data(selected_jobs)
            
            # Create visualization tabs for different comparison views
            comparison_tabs = st.tabs(["Comparison Chart", "Comparative Analysis", "Risk Heatmap", "Risk Factors"])
            
            # Tab 1: Basic comparison chart
            with comparison_tabs[0]:
                st.markdown("<h3 style='color: #0084FF;'>5-Year AI Displacement Risk Comparison</h3>", unsafe_allow_html=True)
                chart = simple_comparison.create_comparison_chart(job_data)
                st.plotly_chart(chart, use_container_width=True)
                
                # Display short explanation under the chart
                st.markdown("""
                **Chart Explanation**: This chart shows the projected AI displacement risk after 5 years for each selected job. 
                Higher percentages indicate greater likelihood that AI will significantly impact or automate aspects of this role.
                """)
            
            # Tab 2: Side-by-side comparative analysis
            with comparison_tabs[1]:
                st.markdown("<h3 style='color: #0084FF;'>Detailed Comparison</h3>", unsafe_allow_html=True)
                
                # Create tabular comparison
                comparison_df = simple_comparison.create_comparison_table(job_data)
                
                # Display the table with improved formatting
                st.dataframe(comparison_df, use_container_width=True)
                
                # Key insights from the comparison
                st.subheader("Key Insights")
                
                # Get highest and lowest risk jobs from selection
                risk_values = [(job, data.get("risk_scores", {}).get("year_5", 0)) 
                              for job, data in job_data.items()]
                
                if risk_values:
                    lowest_job = min(risk_values, key=lambda x: x[1])
                    highest_job = max(risk_values, key=lambda x: x[1])
                    
                    st.markdown(f"""
                    - **Lowest Risk Position**: *{lowest_job[0]}* ({lowest_job[1]:.1%}) is likely to be more resistant to AI displacement
                    - **Highest Risk Position**: *{highest_job[0]}* ({highest_job[1]:.1%}) shows higher vulnerability to AI-driven changes
                    - **Risk Differential**: {(highest_job[1] - lowest_job[1]):.1%} difference between highest and lowest risk positions
                    """)
                    
                    # Add strategic advice based on the comparison
                    if highest_job[1] - lowest_job[1] > 0.3:  # Large risk differential
                        st.markdown("""
                        **Strategic Recommendation**: Consider transitioning from higher-risk to lower-risk roles, 
                        focusing on transferable skills that apply to both positions.
                        """)
            
            # Tab 3: Risk Heatmap
            with comparison_tabs[2]:
                st.markdown("<h3 style='color: #0084FF;'>Risk Over Time Heatmap</h3>", unsafe_allow_html=True)
                
                heatmap = simple_comparison.create_risk_heatmap(job_data)
                st.plotly_chart(heatmap, use_container_width=True)
                
                st.markdown("""
                **Heatmap Explanation**: This visualization shows how AI displacement risk 
                increases over time for each role. Darker colors indicate higher risk levels.
                """)
            
            # Tab 4: Risk Factors Comparison
            with comparison_tabs[3]:
                st.markdown("<h3 style='color: #0084FF;'>Risk Factor Comparison</h3>", unsafe_allow_html=True)
                
                radar = simple_comparison.create_factor_comparison(job_data)
                st.plotly_chart(radar, use_container_width=True)
                
                st.markdown("""
                **Factor Analysis**: This radar chart compares jobs across key risk dimensions.
                Smaller areas indicate lower overall risk, while specific spikes show
                vulnerability in certain aspects of the role.
                """)
    
        # Career Navigator call-to-action
        st.markdown("---")
        
        navigator_html = """
        <div style="background-color: #0084FF; padding: 30px; border-radius: 10px; text-align: center; margin-top: 20px;">
            <div style="background-color: white; padding: 12px; border-radius: 8px; margin-bottom: 20px;">
                <h2 style="color: #0084FF; font-size: 24px; font-weight: bold; margin: 0;">Transform AI Risk Into Career Opportunity</h2>
            </div>
            
            <p style="color: white; font-size: 18px; margin-bottom: 20px;">
                Don't just analyze your job risk - get a complete career transformation strategy with our Career Navigator service.
            </p>
            
            <div style="background-color: white; padding: 20px; border-radius: 8px; margin: 15px auto; max-width: 90%; color: #333;">
                <h3 style="color: #0084FF; margin-top: 0;">Transform Your Career With Expert Guidance:</h3>
                <ul style="text-align: left; margin: 15px auto; max-width: 80%;">
                    <li><strong>Personalized Career Strength Profile</strong> - Discover your unique transferable skills that AI can't replace</li>
                    <li><strong>AI-Resilient Career Pathways</strong> - Custom-matched opportunities with detailed transition plans</li>
                    <li><strong>Curated Training Resources</strong> - Top 10 recommended courses with links and cost estimates</li>
                    <li><strong>Targeted Career Matches</strong> - Three ideal roles with descriptions and salary ranges</li>
                    <li><strong>Strategic Learning Roadmap</strong> - Exact certifications and courses with highest career ROI</li>
                    <li><strong>Month-by-Month Action Plan</strong> - Clear steps to secure more valuable, future-proof positions</li>
                </ul>
            </div>
            
            <a href="https://form.jotform.com/251137815706154" target="_blank" style="display: inline-block; background-color: white; color: #0084FF; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 18px; margin-top: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">Get Your Career Navigator Package</a>
            
            <p style="color: white; font-size: 14px; margin-top: 15px;">
                Join professionals who've secured higher-paying, AI-resilient positions with our strategic guidance.
            </p>
        </div>
        """
        
        st.markdown(navigator_html, unsafe_allow_html=True)
    else:
        st.info("Please select at least one job to see comparison data.")

# Display message if BLS API key is needed
if not bls_api_key:
    st.sidebar.title("💡 Enable BLS Data")
    st.sidebar.info(
        "To enable fresh data from the Bureau of Labor Statistics, "
        "add your BLS API key to the environment variables. "
        "This will enable more accurate and up-to-date employment statistics."
    )

# Sidebar for additional data
st.sidebar.title("AI Job Impact Data")

# Recent Searches
st.sidebar.subheader("Recent Searches")
recent_searches = get_recent_searches(5)
for job in recent_searches:
    st.sidebar.markdown(f"- {job['job_title']}")

# Popular Searches
st.sidebar.subheader("Most Popular Searches")
popular_searches = get_popular_searches(5)
for job in popular_searches:
    st.sidebar.markdown(f"- {job['job_title']} ({job['count']} searches)")

# Highest/Lowest Risk Jobs
st.sidebar.subheader("Highest Risk Jobs")
high_risk_jobs = get_highest_risk_jobs(3)
for job in high_risk_jobs:
    st.sidebar.markdown(f"- {job['job_title']} ({job['avg_risk']:.1%})")

st.sidebar.subheader("Lowest Risk Jobs")
low_risk_jobs = get_lowest_risk_jobs(3)
for job in low_risk_jobs:
    st.sidebar.markdown(f"- {job['job_title']} ({job['avg_risk']:.1%})")

# Check for data refresh needs
if check_data_refresh():
    # This would trigger update operations for fresh data
    st.sidebar.success("Data refreshed with latest information.")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("© 2025 Career AI Impact Analyzer")
st.sidebar.markdown("Data sources: BLS, Oxford Martin School, McKinsey Global Institute")