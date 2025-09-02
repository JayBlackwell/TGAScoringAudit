#!/usr/bin/env python3
"""Streamlit web application for TGA Scoring Audit."""

import streamlit as st
import pandas as pd
import csv
from datetime import datetime, date, timedelta
from typing import List, Optional
from io import StringIO

from tga_scoring_audit.config import Config
from tga_scoring_audit.api.golf_genius import GolfGeniusAPI
from tga_scoring_audit.api import AuthenticationError
from tga_scoring_audit.models.season import Season
from tga_scoring_audit.models.event import Event
from tga_scoring_audit.models.round import Round
from tga_scoring_audit.analysis.scoring import ScoringAnalyzer
from tga_scoring_audit.utils.date_helpers import validate_date_range, is_date_in_range, format_date_for_display

# Page configuration
st.set_page_config(
    page_title="TGA Scoring Audit",
    page_icon="🏌️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for orange theme
st.markdown("""
<style>
    .main-header {
        color: #ff6633;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #ff6633;
        margin-bottom: 2rem;
    }
    .step-counter {
        background-color: #ff6633;
        color: white;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 10px;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    div[data-testid="stSelectbox"] > label {
        color: #ff6633 !important;
        font-weight: bold;
    }
    div[data-testid="stTextInput"] > label {
        color: #ff6633 !important;
        font-weight: bold;
    }
    div[data-testid="stDateInput"] > label {
        color: #ff6633 !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    """Initialize session state variables."""
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ""
    if 'api_connected' not in st.session_state:
        st.session_state.api_connected = False
    if 'seasons' not in st.session_state:
        st.session_state.seasons = []
    if 'selected_season' not in st.session_state:
        st.session_state.selected_season = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = []

def main():
    """Main Streamlit application."""
    init_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🏌️ TGA Scoring Audit</h1>', unsafe_allow_html=True)
    st.markdown("**Automated Golf Genius scoring issue detection for your golf leagues**")
    
    # Progress indicator
    progress_cols = st.columns(5)
    steps = ["API Key", "Season", "Date Range", "Analysis", "Results"]
    for i, (col, step_name) in enumerate(zip(progress_cols, steps)):
        with col:
            if i + 1 < st.session_state.step:
                st.markdown(f'<div class="step-counter">✓</div>{step_name}', unsafe_allow_html=True)
            elif i + 1 == st.session_state.step:
                st.markdown(f'<div class="step-counter">{i+1}</div>**{step_name}**', unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="color: #ccc;">⚪ {step_name}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Step routing
    if st.session_state.step == 1:
        show_api_key_step()
    elif st.session_state.step == 2:
        show_season_selection_step()
    elif st.session_state.step == 3:
        show_date_range_step()
    elif st.session_state.step == 4:
        show_analysis_step()
    elif st.session_state.step == 5:
        show_results_step()

def show_api_key_step():
    """Step 1: API Key Input and Validation."""
    st.header("🔑 Step 1: API Key Setup")
    st.write("Enter your Golf Genius API key to connect to the system.")
    
    # API Key input
    api_key = st.text_input(
        "Golf Genius API Key",
        type="password",
        value=st.session_state.api_key,
        placeholder="Enter your API key...",
        help="Your API key will be used securely and not stored permanently."
    )
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🔗 Connect & Test", type="primary"):
            if not api_key.strip():
                st.error("❌ API key is required")
                return
            
            with st.spinner("Testing API connection..."):
                try:
                    config = Config()
                    config.set_api_key(api_key)
                    api = GolfGeniusAPI(config)
                    
                    if api.test_connection():
                        st.session_state.api_key = api_key
                        st.session_state.api_connected = True
                        st.success("✅ Successfully connected to Golf Genius API!")
                        st.balloons()
                        
                        # Auto-advance to next step after a brief delay
                        st.session_state.step = 2
                        st.rerun()
                    else:
                        st.error("❌ Failed to connect. Please check your API key.")
                        
                except AuthenticationError:
                    st.error("❌ Authentication failed. Please verify your API key.")
                except Exception as e:
                    st.error(f"❌ Connection error: {str(e)}")
    
    with col2:
        if st.button("↻ Reset Application"):
            # Reset all session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Help section
    with st.expander("ℹ️ Need an API Key?"):
        st.write("""
        Contact Golf Genius support to request API access for your account. 
        You'll need administrative privileges for your golf organization.
        
        **Requirements:**
        - Valid Golf Genius account
        - Administrative access to your golf organization
        - API access enabled by Golf Genius support
        """)

def show_season_selection_step():
    """Step 2: Season Selection."""
    st.header("📅 Step 2: Select Season")
    
    # Load seasons if not already loaded
    if not st.session_state.seasons:
        with st.spinner("Loading available seasons..."):
            try:
                config = Config()
                config.set_api_key(st.session_state.api_key)
                api = GolfGeniusAPI(config)
                seasons_data = api.get_seasons()
                st.session_state.seasons = [Season.from_api_response(data) for data in seasons_data]
            except Exception as e:
                st.error(f"❌ Error loading seasons: {str(e)}")
                if st.button("← Back to API Key"):
                    st.session_state.step = 1
                    st.rerun()
                return
    
    if st.session_state.seasons:
        st.success(f"✅ Found {len(st.session_state.seasons)} available seasons")
        
        # Season selection
        season_options = [f"{season.name} (ID: {season.id})" for season in st.session_state.seasons]
        selected_index = st.selectbox(
            "Choose a season to audit:",
            range(len(season_options)),
            format_func=lambda x: season_options[x],
            help="Select the season you want to analyze for scoring issues."
        )
        
        if selected_index is not None:
            st.session_state.selected_season = st.session_state.seasons[selected_index]
            
            # Show selected season info
            season = st.session_state.selected_season
            st.markdown(f"""
            <div class="success-box">
                <h4>Selected Season: {season.name}</h4>
                <p><strong>Season ID:</strong> {season.id}</p>
                {f"<p><strong>Date Range:</strong> {season.start_date.strftime('%B %d, %Y')} - {season.end_date.strftime('%B %d, %Y')}</p>" if season.start_date and season.end_date else ""}
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("← Back to API Key"):
                    st.session_state.step = 1
                    st.rerun()
            with col2:
                if st.button("Continue to Date Range →", type="primary"):
                    st.session_state.step = 3
                    st.rerun()
    else:
        st.warning("⚠️ No seasons found. Please check your API key permissions.")
        if st.button("← Back to API Key"):
            st.session_state.step = 1
            st.rerun()

def show_date_range_step():
    """Step 3: Date Range Selection."""
    st.header("📅 Step 3: Select Date Range")
    
    if st.session_state.selected_season:
        st.info(f"**Selected Season:** {st.session_state.selected_season.name}")
        
        st.write("Choose the date range for your scoring audit. Only rounds within this range will be analyzed.")
        
        # Initialize default dates in session state if not set
        if 'preset_start_date' not in st.session_state:
            st.session_state.preset_start_date = date.today().replace(day=1)  # First day of current month
        if 'preset_end_date' not in st.session_state:
            st.session_state.preset_end_date = date.today()
        
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=st.session_state.preset_start_date,
                help="Choose the start date for analysis"
            )
        
        with col2:
            end_date = st.date_input(
                "End Date",
                value=st.session_state.preset_end_date,
                help="Choose the end date for analysis"
            )
        
        # Quick presets
        st.subheader("Quick Presets:")
        preset_cols = st.columns(5)
        
        with preset_cols[0]:
            if st.button("Last 7 Days"):
                st.session_state.preset_end_date = date.today()
                st.session_state.preset_start_date = date.today() - timedelta(days=7)
                st.rerun()
        
        with preset_cols[1]:
            if st.button("Last 30 Days"):
                st.session_state.preset_end_date = date.today()
                st.session_state.preset_start_date = date.today() - timedelta(days=30)
                st.rerun()
        
        with preset_cols[2]:
            if st.button("This Month"):
                st.session_state.preset_end_date = date.today()
                st.session_state.preset_start_date = date.today().replace(day=1)
                st.rerun()
        
        with preset_cols[3]:
            if st.button("Last Month"):
                today = date.today()
                st.session_state.preset_end_date = today.replace(day=1) - timedelta(days=1)
                st.session_state.preset_start_date = st.session_state.preset_end_date.replace(day=1)
                st.rerun()
        
        with preset_cols[4]:
            if st.button("Yesterday"):
                yesterday = date.today() - timedelta(days=1)
                st.session_state.preset_start_date = yesterday
                st.session_state.preset_end_date = yesterday
                st.rerun()
        
        # Update session state with current input values
        st.session_state.preset_start_date = start_date
        st.session_state.preset_end_date = end_date
        
        # Validate and store dates
        if start_date and end_date:
            if start_date <= end_date:
                st.session_state.start_date = start_date
                st.session_state.end_date = end_date
                
                st.success(f"✅ Date range: {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}")
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("← Back to Season Selection"):
                        st.session_state.step = 2
                        st.rerun()
                with col2:
                    if st.button("Start Analysis →", type="primary"):
                        st.session_state.step = 4
                        st.rerun()
            else:
                st.error("❌ End date must be after start date")

def show_analysis_step():
    """Step 4: Run Analysis."""
    st.header("⚙️ Step 4: Running Analysis")
    
    # Show analysis parameters
    st.markdown(f"""
    <div class="success-box">
        <h4>Analysis Parameters</h4>
        <p><strong>Season:</strong> {st.session_state.selected_season.name}</p>
        <p><strong>Date Range:</strong> {st.session_state.start_date.strftime('%B %d, %Y')} to {st.session_state.end_date.strftime('%B %d, %Y')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 Start Analysis", type="primary"):
        run_analysis()
    
    # Navigation
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("← Back to Date Range"):
            st.session_state.step = 3
            st.rerun()

def run_analysis():
    """Execute the scoring analysis."""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Setup API
        config = Config()
        config.set_api_key(st.session_state.api_key)
        api = GolfGeniusAPI(config)
        analyzer = ScoringAnalyzer()
        
        # Step 1: Fetch events
        status_text.text("📋 Fetching events for selected season...")
        progress_bar.progress(20)
        
        events_data = api.get_all_events(st.session_state.selected_season.id)
        events = [Event.from_api_response(data) for data in events_data]
        
        st.info(f"✅ Found {len(events)} events")
        
        # Step 2: Collect rounds
        status_text.text("🔄 Collecting rounds from all events...")
        progress_bar.progress(40)
        
        all_rounds = []
        for i, event in enumerate(events):
            try:
                rounds_data = api.get_rounds(event.id)
                rounds = [Round.from_api_response(data, event.id) for data in rounds_data]
                all_rounds.extend(rounds)
                
                # Update progress
                progress = 40 + (i + 1) / len(events) * 30
                progress_bar.progress(int(progress))
                
            except Exception as e:
                st.warning(f"⚠️ Failed to fetch rounds for event {event.name}: {e}")
                continue
        
        # Step 3: Filter by date range
        status_text.text("📅 Filtering rounds by date range...")
        progress_bar.progress(70)
        
        start_dt = datetime.combine(st.session_state.start_date, datetime.min.time())
        end_dt = datetime.combine(st.session_state.end_date, datetime.max.time())
        
        filtered_rounds = [r for r in all_rounds if is_date_in_range(r.date, start_dt, end_dt)]
        
        st.info(f"✅ Found {len(filtered_rounds)} rounds in date range")
        
        # Step 4: Analyze scoring
        status_text.text("🔍 Analyzing scoring data...")
        progress_bar.progress(80)
        
        flagged_rounds = []
        for i, round_obj in enumerate(filtered_rounds):
            try:
                tee_sheet_data = api.get_tee_sheet(round_obj.event_id, round_obj.id)
                is_flagged, reason = analyzer.analyze_round_scoring(tee_sheet_data)
                
                if is_flagged:
                    round_obj.flag(reason)
                    flagged_rounds.append(round_obj)
                
                # Update progress
                progress = 80 + (i + 1) / len(filtered_rounds) * 20
                progress_bar.progress(int(progress))
                
            except Exception as e:
                round_obj.flag(f"Unable to retrieve scoring data: {str(e)}")
                flagged_rounds.append(round_obj)
                continue
        
        # Complete
        status_text.text("✅ Analysis complete!")
        progress_bar.progress(100)
        
        # Store results
        results_data = []
        for round_obj in flagged_rounds:
            results_data.append({
                'Event ID': round_obj.event_id,
                'Round ID': round_obj.id,
                'Date': format_date_for_display(round_obj.date),
                'Round Name': round_obj.name,
                'Issue': round_obj.flag_reason,
                'Scorecard URL': f"https://www.golfgenius.com/leagues/{round_obj.event_id}/rounds/{round_obj.id}/scorecards"
            })
        
        st.session_state.analysis_results = results_data
        
        # Show summary
        st.success(f"""
        🎉 **Analysis Complete!**
        
        - **Total rounds analyzed:** {len(filtered_rounds)}
        - **Flagged rounds:** {len(flagged_rounds)}
        - **Clean rounds:** {len(filtered_rounds) - len(flagged_rounds)}
        """)
        
        if st.button("View Results →", type="primary"):
            st.session_state.step = 5
            st.rerun()
            
    except Exception as e:
        st.error(f"❌ Analysis failed: {str(e)}")
        progress_bar.progress(0)
        status_text.text("❌ Analysis failed")

def show_results_step():
    """Step 5: Display Results."""
    st.header("📊 Step 5: Analysis Results")
    
    results = st.session_state.analysis_results
    
    # Summary
    st.markdown(f"""
    <div class="success-box">
        <h4>📋 Analysis Summary</h4>
        <p><strong>Season:</strong> {st.session_state.selected_season.name}</p>
        <p><strong>Date Range:</strong> {st.session_state.start_date.strftime('%B %d, %Y')} to {st.session_state.end_date.strftime('%B %d, %Y')}</p>
        <p><strong>Flagged Rounds:</strong> {len(results)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if results:
        st.subheader(f"⚠️ Flagged Rounds ({len(results)})")
        
        # Convert to DataFrame for better display
        df = pd.DataFrame(results)
        
        # Display as interactive table
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Scorecard URL": st.column_config.LinkColumn("Scorecard URL")
            }
        )
        
        # CSV download
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tga_scoring_audit_{timestamp}.csv"
        
        st.download_button(
            label="📥 Download CSV Report",
            data=csv_data,
            file_name=filename,
            mime="text/csv",
            type="primary"
        )
        
        # Issue explanations
        with st.expander("ℹ️ Understanding the Issues"):
            st.markdown("""
            **Common Issue Types:**
            
            - **Incomplete front 9**: Missing scores for holes 1-9
            - **Incomplete back 9**: Missing scores for holes 10-18  
            - **No scoring data**: No scores found for any holes
            - **Data retrieval error**: Unable to access scoring data
            
            **Next Steps:**
            1. Click the "Scorecard URL" links to review rounds in Golf Genius
            2. Check if scores need to be entered or updated
            3. Contact players if score entry is incomplete
            4. Re-run analysis after corrections are made
            """)
    
    else:
        st.success("""
        🎉 **No Scoring Issues Found!**
        
        All rounds in the specified date range appear to have complete scoring data.
        Your golf leagues are in good shape for the analyzed period.
        """)
    
    # Navigation
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("← Back to Analysis"):
            st.session_state.step = 4
            st.rerun()
    with col2:
        if st.button("🔄 New Analysis"):
            # Reset session state for new analysis
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()