import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import time
import os
import datetime

# Import our API integration
import job_api_integration

# Setup for data refresh
if 'last_data_refresh' not in st.session_state:
    # Initialize with current date for first run
    st.session_state.last_data_refresh = datetime.datetime.now().strftime("%Y-%m-%d")
    
# Function to handle monthly data refresh
def check_data_refresh():
    """Check if data needs to be refreshed (monthly schedule)"""
    if 'last_data_refresh' not in st.session_state:
        return False
        
    last_refresh = datetime.datetime.strptime(st.session_state.last_data_refresh, "%Y-%m-%d")
    current_date = datetime.datetime.now()
    
    # Calculate if it's been a month since the last refresh
    if (current_date.year > last_refresh.year or 
        (current_date.year == last_refresh.year and current_date.month > last_refresh.month)):
        # Clear the job cache to force fresh API calls
        job_api_integration._job_cache = {}
        # Update the refresh date
        st.session_state.last_data_refresh = current_date.strftime("%Y-%m-%d")
        return True
    
    return False
    
# Check for refresh on app startup
refresh_happened = check_data_refresh()

# Set page config first - this must be the first Streamlit command
st.set_page_config(
    page_title="iThriveAI Job Risk Analyzer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"  # Start with sidebar collapsed for faster load
)

# Custom CSS for light theme matching the deployed version
st.markdown("""
<style>
    /* Main app background */
    .stApp {
        background-color: #FFFFFF;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #0084FF !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #F8FBFF;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #F0F7FF;
        border-radius: 4px 4px 0 0;
        color: #333333;
        padding: 10px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #4CACE5 !important;
        color: white !important;
    }
    
    /* Make input fields and dropdowns more visible */
    .stTextInput input, .stSelectbox > div > div {
        border: 1px solid #CCCCCC !important;
        background-color: #FFFFFF !important;
        border-radius: 4px !important;
        padding: 8px 12px !important;
    }
    
    .stTextInput input:focus, .stSelectbox > div > div:focus {
        border-color: #4CACE5 !important;
        box-shadow: 0 0 0 1px #4CACE5 !important;
    }
    
    /* Style buttons */
    .stButton button {
        background-color: #4CACE5 !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        transition: all 0.2s !important;
    }
    
    .stButton button:hover {
        background-color: #3d8bc9 !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
    }
    
    /* Remove white space after Analyze a Job */
    [data-testid="stVerticalBlock"] {
        gap: 0 !important;
    }
    
    .element-container:empty {
        display: none !important;
    }
    
    /* General spacing */
    .css-1y0tads, .css-1544g2n {
        padding: 0rem 1rem 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Display logo and header matching your deployed version
st.image("https://img1.wsimg.com/isteam/ip/70686f32-22d2-489c-a383-6fcd793644be/blob-3712e2e.png/:/rs=h:197,cg:true,m/qt=q:95", width=250)
st.markdown("<h1 style='text-align: center; color: #0084FF;'>Is your job at risk with AI innovation?</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #4CACE5; font-size: 24px; font-weight: 600;'>AI Job Displacement Risk Analyzer</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666666; font-weight: bold; font-size: 16px;'>Discover how AI might impact your career in the next 5 years and get personalized recommendations.</p>", unsafe_allow_html=True)

# Create tabs for single job analysis and comparison - matching your deployed version
tabs = st.tabs(["Single Job Analysis", "Job Comparison"])

# Check if BLS API key is set
bls_api_key = os.environ.get('BLS_API_KEY')
if not bls_api_key and 'api_keys' in st.secrets and 'BLS_API_KEY' in st.secrets['api_keys']:
    bls_api_key = st.secrets['api_keys']['BLS_API_KEY']
    os.environ['BLS_API_KEY'] = bls_api_key  # Set it as environment variable for our connector

with tabs[0]:  # Single Job Analysis tab
    st.markdown("<h2 style='color: #0084FF;'>Analyze a Job</h2>", unsafe_allow_html=True)
    
    # Display API source information
    if bls_api_key:
        st.info("📊 Using real-time data from the Bureau of Labor Statistics API")
    
    # Single column layout for job entry
    st.subheader("Enter any job title to analyze")
    
    # Custom job input - now centralized and prominent
    custom_job = st.text_input(
        "Enter your job title",
        placeholder="e.g. Software Developer, Nurse, Marketing Manager",
        key="job_input"
    )
    
    # Analyze button aligned to the left
    analyze_button = st.button("Analyze Job Risk", key="analyze_job", type="primary")
    
    # Determine which job to analyze
    job_to_analyze = None
    if analyze_button and custom_job:
        job_to_analyze = custom_job
    
    # Add space
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Clear button centered on separate line
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Clear Entry", type="secondary"):
            st.session_state.clear()
            st.rerun()
    
    # Process when a job is selected for analysis
    if job_to_analyze:
        # Add a spinner during API call
        with st.spinner(f"Analyzing '{job_to_analyze}' - retrieving latest data..."):
            # Get job data from the API integration
            job_data = job_api_integration.get_job_data(job_to_analyze)
            
            # For testing/demo purposes
            time.sleep(0.5)  # Simulate API delay
        
        # Display the results
        st.markdown("---")
        
        # Show standardized job title (may be different from user input)
        standardized_title = job_data.get("job_title", job_to_analyze)
        
        st.markdown(f"<h2 style='color: #0084FF;'>AI Displacement Risk Analysis: {standardized_title}</h2>", unsafe_allow_html=True)
        
        # Create layout for results
        left_col, center_col, right_col = st.columns([1, 1.2, 1])
        
        # Left column - Job details
        with left_col:
            st.subheader("Job Information")
            
            # Display job category and SOC code if available
            job_category = "General"  # Default
            if "occupation_code" in job_data:
                st.write(f"**Occupation Code:** {job_data['occupation_code']}")
                job_category = job_data['occupation_code'].split('-')[0]  # Major group
                
                # Map SOC major groups to user-friendly categories
                soc_categories = {
                    "11": "Management",
                    "13": "Business & Financial",
                    "15": "Computer & Mathematics",
                    "17": "Architecture & Engineering",
                    "19": "Science",
                    "21": "Community & Social Service",
                    "23": "Legal",
                    "25": "Education",
                    "27": "Arts & Media",
                    "29": "Healthcare Practitioners",
                    "31": "Healthcare Support",
                    "33": "Protective Service",
                    "35": "Food Preparation & Service",
                    "37": "Building & Grounds",
                    "39": "Personal Care & Service",
                    "41": "Sales",
                    "43": "Administrative Support",
                    "45": "Farming, Fishing & Forestry",
                    "47": "Construction & Extraction",
                    "49": "Installation & Maintenance",
                    "51": "Production",
                    "53": "Transportation & Material Moving"
                }
                
                if job_category in soc_categories:
                    st.write(f"**Job Category:** {soc_categories[job_category]}")
                else:
                    st.write(f"**Job Category:** {job_category}")
            
            # Employment information if available
            if "latest_employment" in job_data and job_data["latest_employment"]:
                employment_num = int(float(job_data["latest_employment"]))
                st.write(f"**Current Employment:** {employment_num:,} jobs")
            
            # Employment projections if available
            if "projections" in job_data and job_data["projections"]:
                projections = job_data["projections"]
                if "percent_change" in projections:
                    change = projections["percent_change"]
                    color = "#4CAF50" if change > 0 else "#F44336"
                    st.markdown(f"**BLS Projected Growth:** <span style='color:{color};'>{change}%</span>", unsafe_allow_html=True)
                
                if "annual_job_openings" in projections:
                    st.write(f"**Annual Job Openings:** {projections['annual_job_openings']:,}")
            
            # Add new statistics section
            st.subheader("Career Outlook Statistics")
            
            # Automation probability
            if "risk_analysis" in job_data and "automation_probability" in job_data["risk_analysis"]:
                auto_prob = job_data["risk_analysis"]["automation_probability"]
                auto_prob_pct = auto_prob * 100
                
                # Color code based on probability
                if auto_prob < 0.3:
                    auto_color = "#4CAF50"  # Green
                elif auto_prob < 0.5:
                    auto_color = "#FFC107"  # Amber
                else:
                    auto_color = "#F44336"  # Red
                
                st.markdown(f"**Task Automation Probability:** <span style='color:{auto_color};'>{auto_prob_pct:.1f}%</span> of job tasks could be automated", unsafe_allow_html=True)
            
            # Wage trend
            if "risk_analysis" in job_data and "wage_trend" in job_data["risk_analysis"]:
                wage_trend = job_data["risk_analysis"]["wage_trend"]
                
                # Color code based on trend
                if "increasing" in wage_trend.lower():
                    wage_color = "#4CAF50"  # Green
                elif "stable" in wage_trend.lower():
                    wage_color = "#FFC107"  # Amber
                else:
                    wage_color = "#F44336"  # Red
                    
                st.markdown(f"**Wage Trend:** <span style='color:{wage_color};'>{wage_trend}</span>", unsafe_allow_html=True)
            
            # Growth projection
            if "risk_analysis" in job_data and "projected_growth" in job_data["risk_analysis"]:
                growth_data = job_data["risk_analysis"]["projected_growth"]
                growth_analysis = growth_data.get("analysis", "Data not available")
                
                # Color code based on growth
                if "strong" in growth_analysis.lower() or "increase" in growth_analysis.lower():
                    growth_color = "#4CAF50"  # Green
                elif "slight" in growth_analysis.lower() or "stable" in growth_analysis.lower():
                    growth_color = "#FFC107"  # Amber
                else:
                    growth_color = "#F44336"  # Red
                    
                st.markdown(f"**Employment Growth:** <span style='color:{growth_color};'>{growth_analysis}</span>", unsafe_allow_html=True)
        
        # Center column - Risk gauge
        with center_col:
            # Extract risk values
            risk_analysis = job_data.get("risk_analysis", {})
            year_1_risk = risk_analysis.get("year_1_risk", 50.0)
            year_5_risk = risk_analysis.get("year_5_risk", 70.0)
            
            # Determine overall risk category
            risk_level = "Low"
            if year_5_risk >= 80:
                risk_level = "Very High"
            elif year_5_risk >= 60:
                risk_level = "High"
            elif year_5_risk >= 30:
                risk_level = "Moderate"
            
            # Create gauge chart for overall risk
            fig = go.Figure(go.Indicator(
                domain={'x': [0, 1], 'y': [0, 1]},
                value=year_5_risk,
                mode="gauge+number",
                title={'text': f"Overall AI Displacement Risk: {risk_level}"},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar': {'color': "rgba(50,50,50,0.1)"},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 20], 'color': '#4CAF50'},  # Green
                        {'range': [20, 40], 'color': '#8BC34A'},  # Light Green
                        {'range': [40, 60], 'color': '#FFC107'},  # Amber
                        {'range': [60, 80], 'color': '#FF9800'},  # Orange
                        {'range': [80, 100], 'color': '#F44336'}  # Red
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': year_5_risk
                    }
                }
            ))
            
            fig.update_layout(
                height=250,
                margin=dict(l=20, r=20, t=50, b=20),
                font=dict(family="Arial", size=12)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display 1-year and 5-year risk percentages
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"<h3 style='text-align: center; color: #0084FF;'>1-Year Risk</h3>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center; font-size: 24px;'>{year_1_risk:.1f}%</p>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<h3 style='text-align: center; color: #0084FF;'>5-Year Risk</h3>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center; font-size: 24px;'>{year_5_risk:.1f}%</p>", unsafe_allow_html=True)
        
        # Right column - Risk factors
        with right_col:
            st.subheader("Risk Factors")
            
            # Risk factors
            if "risk_factors" in risk_analysis and risk_analysis["risk_factors"]:
                for factor in risk_analysis["risk_factors"]:
                    st.markdown(f"❌ {factor}")
            
            st.subheader("Protective Factors")
            
            # Protective factors
            if "protective_factors" in risk_analysis and risk_analysis["protective_factors"]:
                for factor in risk_analysis["protective_factors"]:
                    st.markdown(f"✅ {factor}")
        
        # Full-width sections
        st.markdown("---")
        
        # Analysis text
        if "analysis" in risk_analysis:
            st.subheader("Analysis")
            st.write(risk_analysis["analysis"])
        
        # Employment trend
        st.subheader("Employment Trend")
        with st.spinner("Loading employment trend data..."):
            # First check if job_data already contains trend_data (for custom jobs like Project Manager)
            if "trend_data" in job_data and "years" in job_data["trend_data"] and "employment" in job_data["trend_data"]:
                years = job_data["trend_data"]["years"]
                employment = job_data["trend_data"]["employment"]
                
                df = pd.DataFrame({
                    "Year": years,
                    "Employment": employment
                })
                
                fig = px.line(
                    df, 
                    x="Year", 
                    y="Employment",
                    title=f"Employment Trend for {standardized_title}",
                    markers=True
                )
                
                fig.update_layout(
                    height=400,
                    xaxis_title="Year",
                    yaxis_title="Employment",
                    font=dict(family="Arial", size=12)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                # Try to get trend data from the API
                trend_data = job_api_integration.get_employment_trend(job_to_analyze)
                
                # Create trend chart if data is available
                if "years" in trend_data and "employment" in trend_data:
                    years = trend_data["years"]
                    employment = trend_data["employment"]
                    
                    df = pd.DataFrame({
                        "Year": years,
                        "Employment": employment
                    })
                    
                    fig = px.line(
                        df, 
                        x="Year", 
                        y="Employment",
                        title=f"Employment Trend for {standardized_title}",
                        markers=True
                    )
                    
                    fig.update_layout(
                        height=400,
                        xaxis_title="Year",
                        yaxis_title="Employment",
                        font=dict(family="Arial", size=12)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    # Fallback for when trend data isn't available
                    st.info(f"Official employment trend data for {standardized_title} is not currently available. However, you can still analyze the risk factors and skills needed to stay competitive in this field.")
        
        # Similar jobs
        st.subheader("Similar Jobs")
        with st.spinner("Finding similar jobs..."):
            # First check if job_data already contains similar_jobs (for custom jobs like Project Manager)
            if "similar_jobs" in job_data and job_data["similar_jobs"]:
                similar_jobs = job_data["similar_jobs"]
            else:
                # Try to find similar jobs through the API
                similar_jobs = job_api_integration.search_similar_jobs(job_to_analyze)
            
            if similar_jobs:
                # Create DataFrame for similar jobs
                similar_df = pd.DataFrame(similar_jobs)
                
                # Create bar chart for similar jobs
                fig = px.bar(
                    similar_df,
                    x="job_title",
                    y="year_5_risk",
                    labels={"job_title": "Job Title", "year_5_risk": "5-Year Risk (%)"},
                    title="AI Displacement Risk for Similar Jobs",
                    color="year_5_risk",
                    color_continuous_scale=["green", "yellow", "orange", "red"],
                    range_color=[0, 100]
                )
                
                fig.update_layout(
                    height=400,
                    xaxis_title="Job Title",
                    yaxis_title="5-Year Risk (%)",
                    font=dict(family="Arial", size=12)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Display similar jobs in a table
                st.write("Compare risk levels of similar occupations:")
                
                # Format the DataFrame for display
                display_df = similar_df.copy()
                display_df.columns = ["Job Title", "Occupation Code", "1-Year Risk (%)", "5-Year Risk (%)", "Risk Category"]
                
                # Format percentage columns
                display_df["1-Year Risk (%)"] = display_df["1-Year Risk (%)"].apply(lambda x: f"{x:.1f}%")
                display_df["5-Year Risk (%)"] = display_df["5-Year Risk (%)"].apply(lambda x: f"{x:.1f}%")
                
                # Drop the occupation code column for cleaner display
                display_df = display_df.drop(columns=["Occupation Code"])
                
                st.dataframe(display_df, use_container_width=True)
            else:
                st.info(f"We couldn't find similar jobs for {standardized_title} in our database. Try searching for a related job title to see comparison data.")
        
        # Store skill data in session state for potential API retrieval (but don't display)
        # This will allow integration with n8n later for PDF reports
        if "risk_analysis" in job_data and "skill_areas" in job_data["risk_analysis"]:
            skill_areas = job_data["risk_analysis"]["skill_areas"]
            
            # Store skill data in session state for potential API retrieval
            if "job_skills" not in st.session_state:
                st.session_state.job_skills = {}
            
            # Save skills with job title as key for easy extraction via API
            st.session_state.job_skills[job_to_analyze] = {
                "technical_skills": skill_areas.get("technical_skills", []),
                "soft_skills": skill_areas.get("soft_skills", []),
                "transferable_skills": skill_areas.get("transferable_skills", [])
            }
        
        # Similar storage for regular evolving skills if detailed areas not available
        elif "risk_analysis" in job_data and "evolving_skills" in job_data["risk_analysis"]:
            evolving_skills = job_data["risk_analysis"]["evolving_skills"]
            
            # Store for potential API retrieval
            if "job_skills" not in st.session_state:
                st.session_state.job_skills = {}
            
            # Save in simplified format
            st.session_state.job_skills[job_to_analyze] = {
                "evolving_skills": evolving_skills
            }
        
        # Career transition summary without specific skill steps
        st.markdown("---")
        st.subheader("Risk Assessment Summary")
        
        # Define risk summaries based on risk level
        if year_5_risk >= 80:
            st.markdown("""
            ### 🚨 High Displacement Risk Alert
            
            Your job has a very high risk of being impacted by AI and automation in the next 5 years. 
            Jobs with this risk level typically see significant transformation or reduction due to technological advancements.
            
            Get a personalized career transition plan with our Career Navigator service.
            """)
        elif year_5_risk >= 60:
            st.markdown("""
            ### ⚠️ Significant Displacement Risk
            
            Your job has a high risk of partial automation in the next 5 years. 
            While the role may not disappear completely, substantial portions may be automated, changing skill requirements.
            
            Get a personalized career transition plan with our Career Navigator service.
            """)
        elif year_5_risk >= 30:
            st.markdown("""
            ### 🔔 Moderate Displacement Risk
            
            Your job may experience partial automation in the next 5 years.
            Certain aspects of your role could be automated, but the core functions will likely remain human-centered.
            
            Get a personalized career transition plan with our Career Navigator service.
            """)
        else:
            st.markdown("""
            ### ✅ Low Displacement Risk
            
            Your job appears relatively safe from automation in the next 5 years.
            These roles typically involve complex human interactions, creativity, or expertise that AI cannot easily replicate.
            
            Even with low risk, get a personalized career advancement plan with our Career Navigator service.
            """)
        
        # Career Navigator call-to-action - simplified with explicit HTML
        st.markdown("---")
        
        cta_html = """
        <div style="background-color: #0084FF; padding: 30px; border-radius: 10px; text-align: center; margin-top: 20px;">
            <div style="background-color: white; padding: 10px; border-radius: 8px; margin-bottom: 15px;">
                <h2 style="color: #0084FF; font-size: 26px; font-weight: bold; margin: 0;">Transform AI Risk Into Career Opportunity</h2>
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
            <a href="https://form.jotform.com/251137815706154" target="_blank" style="
                display: inline-block;
                background-color: white;
                color: #0084FF;
                padding: 15px 30px;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 18px;
                margin-top: 20px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                Get Your Career Navigator Package</a>
            <p style="color: white; font-size: 14px; margin-top: 15px;">
                Join professionals who've secured higher-paying, AI-resilient positions with our strategic guidance.
            </p>
        </div>
        """
        
        st.markdown(cta_html, unsafe_allow_html=True)

# Job Comparison Tab - Ultra-simplified with automatic display
with tabs[1]:  # Job Comparison tab
    st.markdown("<h2 style='color: #0084FF;'>Compare Jobs</h2>", unsafe_allow_html=True)
    
    st.markdown("<p>Compare the AI displacement risk for multiple jobs side by side to explore transition opportunities. Add up to 5 jobs.</p>", unsafe_allow_html=True)
    
    # Initialize session state for job comparison
    if 'comparison_jobs' not in st.session_state:
        st.session_state.comparison_jobs = []
    
    # Main job input
    if len(st.session_state.comparison_jobs) < 5:  # Limit to 5 jobs
        new_job = st.text_input(
            "Enter a job title and press Enter to add to comparison",
            placeholder="e.g. Software Developer, Nurse, Marketing Manager",
            key="compare_job_input"
        )
        
        # Add job directly when Enter is pressed
        if new_job and new_job not in st.session_state.comparison_jobs:
            st.session_state.comparison_jobs.append(new_job)
            # We can't clear the field directly, but we can use rerun
            st.rerun()
    else:
        st.warning("Maximum of 5 jobs reached. Remove a job to add another.")
    
    # Display current jobs in comparison with remove option
    if st.session_state.comparison_jobs:
        # Create a container for job chips
        st.markdown("### Current Comparison:")
        job_container = st.container()
        
        # Display each job as a removable chip in a horizontal layout
        cols = job_container.columns(min(5, len(st.session_state.comparison_jobs)))
        
        for i, job in enumerate(st.session_state.comparison_jobs):
            col_index = i % len(cols)
            with cols[col_index]:
                # Create a container for each job with a remove button
                st.markdown(f"""
                <div style="
                    background-color: #e6f2ff; 
                    padding: 8px 12px; 
                    border-radius: 20px; 
                    margin: 5px 0;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                ">
                    <span>{job}</span>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"❌", key=f"remove_{i}", help=f"Remove {job} from comparison"):
                    st.session_state.comparison_jobs.remove(job)
                    st.rerun()
    
    # Add some space before the clear button
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Clear selections button centered
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Clear All Jobs", type="secondary"):
            st.session_state.comparison_jobs = []
            st.rerun()
    
    # Set jobs to compare for analysis section
    jobs_to_compare = st.session_state.comparison_jobs
    
    # Display comparison when at least 1 job is selected
    if jobs_to_compare and len(jobs_to_compare) >= 1:
        st.markdown("---")
        st.markdown(f"<h2 style='color: #0084FF;'>Analyzing {len(jobs_to_compare)} Jobs</h2>", unsafe_allow_html=True)
        
        # Get data for all selected jobs
        comparison_data = {}
        progress_bar = st.progress(0)
        
        for i, job in enumerate(jobs_to_compare):
            with st.spinner(f"Analyzing {job}..."):
                # Get job data using enhanced API
                job_data = job_api_integration.get_job_data(job)
                
                # Extract risk analysis
                risk_analysis = job_data.get("risk_analysis", {})
                
                # Store comprehensive data for comparison
                comparison_data[job] = {
                    "job_title": job_data.get("job_title", job),
                    "occupation_code": job_data.get("occupation_code", "N/A"),
                    "year_1_risk": risk_analysis.get("year_1_risk", 0),
                    "year_5_risk": risk_analysis.get("year_5_risk", 0),
                    "risk_category": risk_analysis.get("risk_category", "Unknown"),
                    "automation_probability": risk_analysis.get("automation_probability", 0.5) * 100,
                    "wage_trend": risk_analysis.get("wage_trend", "Unknown"),
                    "skill_areas": risk_analysis.get("skill_areas", {}),
                    "risk_factors": risk_analysis.get("risk_factors", []),
                    "protective_factors": risk_analysis.get("protective_factors", [])
                }
                
                # Update progress
                progress_bar.progress((i + 1) / len(jobs_to_compare))
        
        # Create visual comparison section
        st.subheader("Career Risk Comparison")
        
        # Convert to DataFrame for visualization
        df = pd.DataFrame.from_dict(comparison_data, orient='index')
        
        # Create bar chart for 5-year risk comparison
        fig = px.bar(
            df,
            x=df.index,
            y="year_5_risk",
            labels={"year_5_risk": "5-Year AI Displacement Risk (%)", "index": "Job Title"},
            title="AI Displacement Risk Comparison (5-Year Projection)",
            color="year_5_risk",
            color_continuous_scale=["green", "yellow", "orange", "red"],
            range_color=[0, 100],
            text="year_5_risk"
        )
        
        fig.update_layout(
            height=400,
            xaxis_title="Job Title",
            yaxis_title="Risk (%)",
            font=dict(family="Arial", size=12),
        )
        
        # Format text labels
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='inside')
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Create multi-factor comparison
        if len(jobs_to_compare) >= 2:
            st.subheader("Multi-factor Comparison")
            
            # Create radar chart for comprehensive comparison
            categories = ['5-Year Risk', 'Automation Probability', '1-Year Risk']
            
            fig = go.Figure()
            
            for job in df.index:
                fig.add_trace(go.Scatterpolar(
                    r=[df.loc[job, 'year_5_risk'], 
                       df.loc[job, 'automation_probability'],
                       df.loc[job, 'year_1_risk']],
                    theta=categories,
                    fill='toself',
                    name=job
                ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )
                ),
                showlegend=True,
                height=500,
                title="Multi-factor Risk Comparison"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Comprehensive comparison table
        st.subheader("Detailed Job Comparison")
        
        # Create formatted table
        comparison_table = []
        for job_title, data in comparison_data.items():
            comparison_table.append({
                "Job Title": data["job_title"],
                "5-Year Risk": f"{data['year_5_risk']:.1f}%",
                "Risk Category": data["risk_category"],
                "Automation": f"{data['automation_probability']:.1f}%",
                "Wage Trend": data["wage_trend"]
            })
        
        comparison_df = pd.DataFrame(comparison_table)
        st.dataframe(comparison_df, use_container_width=True)
        
        # Career transition insights
        st.markdown("---")
        st.subheader("Career Transition Insights")
        
        # Sort jobs by risk level
        sorted_jobs = sorted(comparison_data.items(), key=lambda x: x[1]["year_5_risk"])
        
        # Create columns for insights and visualization
        if len(jobs_to_compare) >= 2:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Identify lowest and highest risk jobs
                lowest_risk_job = sorted_jobs[0]
                highest_risk_job = sorted_jobs[-1]
                
                st.markdown(f"""
                ### Key Insights:
                
                - **Lowest Risk Job:** {lowest_risk_job[1]['job_title']} ({lowest_risk_job[1]['year_5_risk']:.1f}% risk)
                - **Highest Risk Job:** {highest_risk_job[1]['job_title']} ({highest_risk_job[1]['year_5_risk']:.1f}% risk)
                - **Risk Difference:** {(highest_risk_job[1]['year_5_risk'] - lowest_risk_job[1]['year_5_risk']):.1f}%
                
                The substantial difference in risk levels highlights the value of strategic career planning and skill development.
                """)
            
            with col2:
                # Create transition recommendation callout
                st.markdown("""
                ### Transition Recommendation:
                
                If you're currently in a higher-risk role, consider developing transferable skills that would enable you to:
                
                1. Move to adjacent lower-risk roles
                2. Specialize in areas that AI complements rather than replaces
                3. Develop skills that bridge between your current and target roles
                """)
        
        # Career Navigator service - Updated with more compelling benefits
        st.markdown("---")
        
        comparison_cta_html = """
        <div style="background-color: #0084FF; padding: 30px; border-radius: 10px; text-align: center; margin-top: 20px;">
            <div style="background-color: white; padding: 10px; border-radius: 8px; margin-bottom: 15px;">
                <h2 style="color: #0084FF; font-size: 26px; font-weight: bold; margin: 0;">Transform AI Risk Into Career Opportunity</h2>
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
            <a href="https://form.jotform.com/251137815706154" target="_blank" style="
                display: inline-block;
                background-color: white;
                color: #0084FF;
                padding: 15px 30px;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 18px;
                margin-top: 20px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                Get Your Career Navigator Package</a>
            <p style="color: white; font-size: 14px; margin-top: 15px;">
                Join professionals who've secured higher-paying, AI-resilient positions with our strategic guidance.
            </p>
        </div>
        """
        
        st.markdown(comparison_cta_html, unsafe_allow_html=True)

# Display message if BLS API key is needed
if not bls_api_key:
    st.sidebar.title("💡 Enable BLS Data")
    st.sidebar.info(
        "To use real-time Bureau of Labor Statistics data, you'll need to register for a free API key at "
        "[data.bls.gov/registrationEngine](https://data.bls.gov/registrationEngine/) and add it as an environment variable."
    )
    st.sidebar.code("BLS_API_KEY=your_api_key_here")
    st.sidebar.markdown("**Benefits of using BLS data:**")
    st.sidebar.markdown("• Up-to-date employment statistics")
    st.sidebar.markdown("• Official government data sources")
    st.sidebar.markdown("• Comprehensive coverage of occupations")
    st.sidebar.markdown("• Enhanced accuracy of risk analysis")