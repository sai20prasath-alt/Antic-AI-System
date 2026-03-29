"""
Streamlit Chat Interface for Resume Matching Agent

Provides an interactive web interface for:
- Uploading job descriptions
- Conversational candidate search
- Viewing and comparing candidates
- Multi-round screening workflow
"""

import streamlit as st
import json
from datetime import datetime
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from matching_agent import ResumeMatchingAgent, AgentConfig, create_agent
from agent_state import ScreeningRound


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Resume Matching Agent",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================

def init_session_state():
    """Initialize session state variables"""
    if "agent" not in st.session_state:
        st.session_state.agent = create_agent()
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "job_description" not in st.session_state:
        st.session_state.job_description = ""
    
    if "matching_started" not in st.session_state:
        st.session_state.matching_started = False
    
    if "current_results" not in st.session_state:
        st.session_state.current_results = None


init_session_state()


# =============================================================================
# SIDEBAR
# =============================================================================

def render_sidebar():
    """Render the sidebar with configuration and status"""
    with st.sidebar:
        st.title("⚙️ Configuration")
        
        # Status indicator
        if st.session_state.matching_started:
            st.success("✓ Matching Active")
            
            # Show current round
            if st.session_state.current_results:
                round_name = st.session_state.current_results.get("current_round", "initial")
                st.info(f"📍 Current Round: {round_name.upper()}")
        else:
            st.warning("○ No matching in progress")
        
        st.divider()
        
        # Job Description Input
        st.subheader("📋 Job Description")
        
        jd_input_method = st.radio(
            "Input Method",
            ["Text Input", "Upload File"],
            horizontal=True
        )
        
        if jd_input_method == "Text Input":
            job_desc = st.text_area(
                "Enter Job Description",
                value=st.session_state.job_description,
                height=200,
                placeholder="Paste job description here..."
            )
            
            if st.button("Start Matching", type="primary", use_container_width=True):
                if job_desc.strip():
                    st.session_state.job_description = job_desc
                    start_matching(job_desc)
                else:
                    st.error("Please enter a job description")
        
        else:
            uploaded_file = st.file_uploader(
                "Upload JD File",
                type=["txt", "md", "json"]
            )
            
            if uploaded_file:
                job_desc = uploaded_file.read().decode("utf-8")
                st.text_area("Preview", job_desc[:500] + "...", height=150, disabled=True)
                
                if st.button("Start Matching", type="primary", use_container_width=True):
                    st.session_state.job_description = job_desc
                    start_matching(job_desc)
        
        st.divider()
        
        # Quick Actions
        st.subheader("⚡ Quick Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Reset", use_container_width=True):
                reset_session()
        
        with col2:
            if st.button("📊 Report", use_container_width=True):
                show_report()
        
        # Screening Round Controls
        if st.session_state.matching_started:
            st.divider()
            st.subheader("🎯 Screening Rounds")
            
            current_round = "initial"
            if st.session_state.current_results:
                current_round = st.session_state.current_results.get("current_round", "initial")
            
            round_progress = {
                "initial": 1,
                "second": 2,
                "final": 3
            }
            
            st.progress(round_progress.get(current_round, 1) / 3)
            st.caption(f"Round {round_progress.get(current_round, 1)} of 3")
            
            if current_round != "final":
                if st.button("➡️ Next Round", use_container_width=True):
                    process_next_round()


def start_matching(job_description: str):
    """Start the matching process"""
    with st.spinner("Analyzing job description and searching candidates..."):
        results = st.session_state.agent.start_matching(job_description)
        st.session_state.matching_started = True
        st.session_state.current_results = results
        
        # Add system message
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"I've analyzed the job description and found **{len(results.get('shortlist', []))}** matching candidates. "
                      f"You can ask me to:\n"
                      f"- Compare candidates\n"
                      f"- Explain rankings\n"
                      f"- Adjust requirements\n"
                      f"- Proceed to the next screening round"
        })
    
    st.rerun()


def reset_session():
    """Reset the session state"""
    st.session_state.agent = create_agent()
    st.session_state.messages = []
    st.session_state.job_description = ""
    st.session_state.matching_started = False
    st.session_state.current_results = None
    st.rerun()


def show_report():
    """Show the current report"""
    if st.session_state.matching_started:
        report = st.session_state.agent.get_report()
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"```\n{report}\n```"
        })
        st.rerun()


def process_next_round():
    """Process to the next screening round"""
    with st.spinner("Moving to next screening round..."):
        result = st.session_state.agent.process_query("proceed to next round")
        st.session_state.current_results = st.session_state.agent._get_results()
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": result.get("response", "Moved to next round")
        })
    
    st.rerun()


# =============================================================================
# MAIN CONTENT
# =============================================================================

def render_main_content():
    """Render the main chat interface"""
    st.title("👥 Resume Matching Agent")
    st.caption("AI-powered candidate screening and ranking")
    
    # Show candidate cards if matching has started
    if st.session_state.matching_started and st.session_state.current_results:
        render_candidate_cards()
    
    st.divider()
    
    # Chat interface
    render_chat_interface()


def render_candidate_cards():
    """Render candidate shortlist as cards"""
    results = st.session_state.current_results
    shortlist = results.get("shortlist", [])
    
    if not shortlist:
        st.info("No candidates found yet. Try adjusting the job description.")
        return
    
    st.subheader(f"🏆 Top {len(shortlist)} Candidates")
    
    # Create columns for candidate cards
    cols = st.columns(min(len(shortlist), 4))
    
    for i, candidate in enumerate(shortlist[:4]):
        with cols[i]:
            render_candidate_card(candidate, i + 1)
    
    # Show remaining candidates in expander
    if len(shortlist) > 4:
        with st.expander(f"View {len(shortlist) - 4} more candidates"):
            for i, candidate in enumerate(shortlist[4:], 5):
                render_candidate_row(candidate, i)


def render_candidate_card(candidate: dict, rank: int):
    """Render a single candidate card"""
    score = candidate.get("score", 0)
    recommendation = candidate.get("recommendation", "unknown")
    
    # Determine card color based on recommendation
    if recommendation == "hire":
        border_color = "green"
        rec_emoji = "✅"
    elif recommendation == "maybe":
        border_color = "orange"
        rec_emoji = "🟡"
    else:
        border_color = "red"
        rec_emoji = "❌"
    
    with st.container():
        st.markdown(f"""
        <div style="
            border: 2px solid {border_color};
            border-radius: 10px;
            padding: 15px;
            margin: 5px 0;
        ">
            <h4>#{rank} {candidate.get('name', 'Unknown')}</h4>
            <p><strong>Score:</strong> {score:.1f}/100 {rec_emoji}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Strengths
        strengths = candidate.get("strengths", [])[:2]
        if strengths:
            st.caption("**Strengths:**")
            for s in strengths:
                st.caption(f"• {s[:30]}...")
        
        # Gaps
        gaps = candidate.get("gaps", [])[:2]
        if gaps:
            st.caption("**Gaps:**")
            for g in gaps:
                st.caption(f"• {g[:30]}...")


def render_candidate_row(candidate: dict, rank: int):
    """Render a candidate as a row"""
    col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
    
    with col1:
        st.write(f"**#{rank}**")
    
    with col2:
        st.write(candidate.get("name", "Unknown"))
    
    with col3:
        score = candidate.get("score", 0)
        st.progress(score / 100)
        st.caption(f"{score:.1f}/100")
    
    with col4:
        rec = candidate.get("recommendation", "unknown")
        if rec == "hire":
            st.success("HIRE")
        elif rec == "maybe":
            st.warning("MAYBE")
        else:
            st.error("NO")


def render_chat_interface():
    """Render the chat interface"""
    st.subheader("💬 Chat with the Agent")
    
    # Display chat messages
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about candidates... (e.g., 'Compare top 3' or 'Why does John rank higher?')"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get agent response
        with st.spinner("Thinking..."):
            result = st.session_state.agent.process_query(prompt)
            response = result.get("response", "I couldn't process that request.")
            
            # Update results if changed
            st.session_state.current_results = st.session_state.agent._get_results()
        
        # Add assistant response
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        st.rerun()
    
    # Quick query buttons
    st.caption("Quick queries:")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Compare top 3"):
            quick_query("Compare the top 3 candidates side by side")
    
    with col2:
        if st.button("Explain rankings"):
            quick_query("Why are the candidates ranked this way?")
    
    with col3:
        if st.button("Find React devs"):
            quick_query("Find candidates with React experience")
    
    with col4:
        if st.button("Get interview Qs"):
            quick_query("Generate interview questions for the top candidate")


def quick_query(query: str):
    """Process a quick query"""
    st.session_state.messages.append({"role": "user", "content": query})
    
    with st.spinner("Processing..."):
        result = st.session_state.agent.process_query(query)
        response = result.get("response", "I couldn't process that request.")
        st.session_state.current_results = st.session_state.agent._get_results()
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()


# =============================================================================
# SAMPLE DATA
# =============================================================================

def load_sample_data():
    """Load sample job description and resumes for demo"""
    sample_jd = """
Senior Full-Stack Developer

Company: TechCorp Inc.
Location: San Francisco, CA (Remote OK)

About the Role:
We're looking for a Senior Full-Stack Developer to join our growing team. 
You'll be building next-generation web applications using modern technologies.

Requirements:
- 5+ years of software development experience
- Strong proficiency in React.js and Node.js
- Experience with Python and Django/Flask
- PostgreSQL and MongoDB database experience
- AWS or cloud platform experience
- Bachelor's degree in Computer Science or related field

Nice to Have:
- Experience with TypeScript
- Knowledge of Docker and Kubernetes
- GraphQL experience
- Leadership or mentoring experience
- Open source contributions

Responsibilities:
- Design and implement scalable web applications
- Mentor junior developers
- Participate in code reviews
- Collaborate with product and design teams
    """
    
    return sample_jd


# =============================================================================
# MAIN APP
# =============================================================================

def main():
    """Main application entry point"""
    # Render sidebar
    render_sidebar()
    
    # Render main content
    render_main_content()
    
    # Footer
    st.divider()
    st.caption("Resume Matching Agent v1.0 | Built with LangGraph & Streamlit")
    
    # Sample data loader (in sidebar)
    with st.sidebar:
        st.divider()
        if st.button("📝 Load Sample JD", use_container_width=True):
            sample_jd = load_sample_data()
            st.session_state.job_description = sample_jd
            st.rerun()


if __name__ == "__main__":
    main()
