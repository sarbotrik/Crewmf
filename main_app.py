import streamlit as st
import requests
import json
from datetime import datetime
import time
import re

# Page configuration
st.set_page_config(
    page_title="Mutual Fund Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .report-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #1f77b4;
    }
    
    .metric-container {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
    }
    
    .loading-message {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #ffeaa7;
    }
    
    .stButton > button {
        background-color: #1f77b4;
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 5px;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #155a8a;
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# Configuration
API_BASE_URL = "https://web-production-f508e.up.railway.app"  # Replace with your actual Railway URL

def call_analysis_api(fund_name: str):
    """Call the FastAPI analysis endpoint"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/analyze",
            json={"mutual_fund_name": fund_name},
            timeout=300  # 5 minutes timeout
        )
        
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"API Error: {response.status_code} - {response.text}"
            
    except requests.exceptions.ConnectionError:
        return None, f"Connection Error: Unable to connect to the API server at {API_BASE_URL}. Please ensure the FastAPI server is running."
    except requests.exceptions.Timeout:
        return None, "Timeout Error: The analysis is taking longer than expected. Please try again."
    except Exception as e:
        return None, f"Unexpected Error: {str(e)}"

def format_markdown_content(content: str) -> str:
    """Clean and format markdown content for better display"""
    if not content:
        return "No data available"
    
    # Clean up extra whitespace and line breaks
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content.strip())
    
    # Ensure proper spacing around headers
    content = re.sub(r'(#{1,6})\s*(.+)', r'\1 \2', content)
    
    return content

def display_analysis_section(title: str, content: str, icon: str = "📊"):
    """Display a formatted analysis section"""
    with st.container():
        st.markdown(f"### {icon} {title}")
        
        if content and content.strip():
            # Format and display the content
            formatted_content = format_markdown_content(content)
            
            # Display in an expander for better organization
            with st.expander(f"View {title}", expanded=True):
                st.markdown(formatted_content)
        else:
            st.warning(f"No {title.lower()} data available")

def display_final_report(report_content: str):
    """Display the final report with special formatting"""
    if not report_content or not report_content.strip():
        st.error("No final report generated")
        return
    
    st.markdown("## 📋 Comprehensive Investment Research Report")
    
    # Split the report into sections for better display
    sections = report_content.split('\n## ')
    
    if len(sections) > 1:
        # Display executive summary first if available
        if sections[0].strip():
            st.markdown(sections[0])
        
        # Display other sections in tabs
        section_titles = []
        section_contents = []
        
        for section in sections[1:]:
            if section.strip():
                lines = section.split('\n', 1)
                if len(lines) >= 2:
                    title = lines[0].strip()
                    content = lines[1].strip()
                    section_titles.append(title)
                    section_contents.append(content)
        
        if section_titles:
            tabs = st.tabs(section_titles)
            for tab, content in zip(tabs, section_contents):
                with tab:
                    st.markdown(content)
    else:
        # Display the whole report if no clear sections
        formatted_report = format_markdown_content(report_content)
        st.markdown(formatted_report)

def main():
    # Header
    st.markdown('<h1 class="main-header">📈 Mutual Fund Analysis Platform</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem; color: #666;">
        Get comprehensive analysis of Indian mutual funds with AI-powered insights covering 
        fund performance, market sentiment, and macroeconomic factors.
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        api_url = st.text_input("API Base URL", value=API_BASE_URL)
        st.info("Make sure your FastAPI server is running on the specified URL.")
        
        st.header("📖 How to Use")
        st.markdown("""
        1. Enter the complete mutual fund name
        2. Click 'Analyze Fund' button
        3. Wait for the comprehensive analysis
        4. Review the detailed report sections
        """)
        
        # Popular fund examples
        st.header("💡 Popular Funds")
        example_funds = [
            "HDFC Mid-Cap Opportunities Fund - Growth Option - Direct Plan",
            "SBI Small Cap Fund - Direct Plan - Growth",
            "Axis Bluechip Fund - Direct Plan - Growth",
            "Mirae Asset Large Cap Fund - Direct Plan - Growth",
            "Parag Parikh Long Term Equity Fund - Direct Plan - Growth"
        ]
        
        for fund in example_funds:
            if st.button(f"📊 {fund.split('-')[0].strip()}", key=fund):
                st.session_state['fund_name'] = fund
    
    # Main input section
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        st.markdown("### 🎯 Enter Mutual Fund Details")
        
        # Initialize session state
        if 'fund_name' not in st.session_state:
            st.session_state['fund_name'] = ""
        
        # Input field
        fund_name = st.text_input(
            "Mutual Fund Name",
            value=st.session_state.get('fund_name', ''),
            placeholder="e.g., HDFC Mid-Cap Opportunities Fund - Growth Option - Direct Plan",
            help="Enter the complete name of the mutual fund scheme"
        )
        
        # Update session state
        st.session_state['fund_name'] = fund_name
        
        # Submit button
        analyze_button = st.button(
            "🔍 Analyze Fund",
            use_container_width=True,
            disabled=not fund_name.strip()
        )
    
    # Analysis section
    if analyze_button and fund_name.strip():
        st.markdown("---")
        
        # Show loading message
        with st.container():
            st.markdown('<div class="loading-message">🔄 Analyzing your mutual fund... This may take 2-3 minutes.</div>', unsafe_allow_html=True)
            
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Simulate progress updates
            for i in range(100):
                progress_bar.progress(i + 1)
                if i < 25:
                    status_text.text("🔍 Gathering fund information...")
                elif i < 50:
                    status_text.text("📰 Analyzing market sentiment...")
                elif i < 75:
                    status_text.text("🏛️ Evaluating macroeconomic factors...")
                else:
                    status_text.text("📊 Compiling final report...")
                time.sleep(0.05)  # Small delay for visual effect
            
        # Call the API
        result, error = call_analysis_api(fund_name)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        if error:
            st.markdown(f'<div class="error-message">❌ {error}</div>', unsafe_allow_html=True)
            
            # Troubleshooting tips
            with st.expander("🛠️ Troubleshooting Tips"):
                st.markdown("""
                **Common Issues and Solutions:**
                
                1. **Connection Error**: Make sure your FastAPI server is running:
                   ```bash
                   uvicorn main:app --reload
                   ```
                
                2. **Timeout Error**: The analysis takes time. Try with a shorter fund name or check your internet connection.
                
                3. **API Error**: Verify the API endpoint is working by visiting: http://127.0.0.1:8000/docs
                
                4. **Fund Name**: Ensure you're using the complete official fund name.
                """)
        
        elif result and result.get('status') == 'success':
            # Success message
            st.markdown('<div class="success-message">✅ Analysis completed successfully!</div>', unsafe_allow_html=True)
            
            # Display fund name and timestamp
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📊 Fund Analyzed", result['fund_name'])
            with col2:
                analysis_time = datetime.fromisoformat(result['timestamp'].replace('Z', '+00:00'))
                st.metric("🕐 Analysis Time", analysis_time.strftime("%Y-%m-%d %H:%M:%S"))
            
            st.markdown("---")
            
            # Get analysis data
            analysis = result.get('analysis', {})
            
            # Display analysis sections
            if analysis:
                # Create tabs for different analysis sections
                tab1, tab2, tab3, tab4 = st.tabs([
                    "📊 Fund Analysis",
                    "📰 Sentiment Analysis", 
                    "🏛️ Macroeconomic Analysis",
                    "📋 Final Report"
                ])
                
                with tab1:
                    display_analysis_section(
                        "Fund Performance & Details",
                        analysis.get('fund_analysis', ''),
                        "📊"
                    )
                
                with tab2:
                    display_analysis_section(
                        "Market Sentiment & News",
                        analysis.get('sentiment_analysis', ''),
                        "📰"
                    )
                
                with tab3:
                    display_analysis_section(
                        "Economic Environment",
                        analysis.get('macroeconomic_analysis', ''),
                        "🏛️"
                    )
                
                with tab4:
                    display_final_report(analysis.get('final_report', ''))
                
                # Download option
                st.markdown("---")
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    # Prepare download data
                    download_data = f"""
# Mutual Fund Analysis Report
**Fund:** {result['fund_name']}
**Analysis Date:** {result['timestamp']}

## Fund Analysis
{analysis.get('fund_analysis', 'No data available')}

## Sentiment Analysis  
{analysis.get('sentiment_analysis', 'No data available')}

## Macroeconomic Analysis
{analysis.get('macroeconomic_analysis', 'No data available')}

## Final Investment Report
{analysis.get('final_report', 'No data available')}
                    """
                    
                    st.download_button(
                        label="📥 Download Full Report",
                        data=download_data,
                        file_name=f"MF_Analysis_{fund_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
            else:
                st.error("No analysis data received from the API")
        
        else:
            st.error("Unexpected response from the API. Please try again.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        🚀 Powered by AI | 📊 Real-time Analysis | 💡 Investment Intelligence
        <br>
        <small>This tool provides analysis for informational purposes only. Please consult with a financial advisor before making investment decisions.</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
