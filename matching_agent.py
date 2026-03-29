"""
Resume Matching Agent using LangGraph

This module implements a sophisticated resume matching agent with:
- Multi-node workflow graph
- Human-in-the-loop feedback
- Multi-round screening
- Explainable recommendations

Workflow:
START → Parse JD → Extract Requirements → Search Resumes → 
Rank Candidates → Generate Report → Human Feedback Loop → END
"""

import os
import json
from typing import Dict, Any, List, Optional, Literal
from datetime import datetime

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI

# Try to import from langchain based on version
try:
    from langchain_core.prompts import ChatPromptTemplate
except ImportError:
    from langchain.prompts import ChatPromptTemplate

from agent_state import (
    AgentState, 
    create_initial_state,
    update_state_with_message,
    ParsedJobDescription,
    JobRequirement,
    RequirementType,
    CandidateMatch,
    ScreeningRound,
    MatchReport,
    ConversationMessage
)

from tools import (
    ALL_TOOLS,
    extract_requirements,
    compare_candidates,
    generate_interview_questions,
    score_candidate,
    rank_candidates,
    generate_match_report,
    rag_search_resumes,
    read_resume_file,
    list_resume_directory
)


# =============================================================================
# CONFIGURATION
# =============================================================================

class AgentConfig:
    """Configuration for the matching agent"""
    
    def __init__(
        self,
        model_name: str = "gpt-4",
        temperature: float = 0.1,
        max_candidates_initial: int = 100,
        top_n_initial: int = 10,
        top_n_second: int = 5,
        top_n_final: int = 3,
        resume_directory: str = "./resumes",
        reports_directory: str = "./reports"
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.max_candidates_initial = max_candidates_initial
        self.top_n_initial = top_n_initial
        self.top_n_second = top_n_second
        self.top_n_final = top_n_final
        self.resume_directory = resume_directory
        self.reports_directory = reports_directory


# Global config
config = AgentConfig()


# =============================================================================
# LLM INITIALIZATION
# =============================================================================

def get_llm(config: AgentConfig = None) -> ChatOpenAI:
    """Initialize the LLM with configuration"""
    cfg = config or AgentConfig()
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY", "")
    
    if not api_key:
        # Return a mock LLM for testing without API key
        print("Warning: OPENAI_API_KEY not set. Using mock responses.")
        return None
    
    return ChatOpenAI(
        model=cfg.model_name,
        temperature=cfg.temperature,
        api_key=api_key
    )


# =============================================================================
# NODE FUNCTIONS
# =============================================================================

def parse_jd_node(state: AgentState) -> AgentState:
    """
    Node: Parse Job Description
    
    Takes raw job description and creates structured representation.
    """
    state["current_node"] = "parse_jd"
    
    jd_raw = state.get("job_description_raw", "")
    
    if not jd_raw:
        state["error_message"] = "No job description provided"
        return state
    
    # Extract basic structure from JD
    lines = jd_raw.strip().split('\n')
    title = lines[0] if lines else "Unknown Position"
    
    # Create parsed JD object
    parsed = ParsedJobDescription(
        title=title.strip(),
        raw_text=jd_raw,
        summary=jd_raw[:500] + "..." if len(jd_raw) > 500 else jd_raw
    )
    
    state["parsed_job_description"] = parsed
    
    # Add message to conversation
    state = update_state_with_message(
        state, 
        "assistant", 
        f"Parsed job description for: {title}"
    )
    
    return state


def extract_requirements_node(state: AgentState) -> AgentState:
    """
    Node: Extract Requirements
    
    Analyzes JD to identify must-have vs nice-to-have requirements.
    """
    state["current_node"] = "extract_requirements"
    
    jd_raw = state.get("job_description_raw", "")
    
    if not jd_raw:
        state["error_message"] = "No job description to extract requirements from"
        return state
    
    # Use the extract_requirements tool
    requirements = extract_requirements.invoke({"jd": jd_raw})
    
    # Update parsed JD with requirements
    parsed = state.get("parsed_job_description") or ParsedJobDescription()
    
    # Convert to JobRequirement objects
    must_have = []
    for req in requirements.get("must_have", []):
        must_have.append(JobRequirement(
            description=req,
            type=RequirementType.MUST_HAVE,
            category="general",
            weight=1.0
        ))
    
    nice_to_have = []
    for req in requirements.get("nice_to_have", []):
        nice_to_have.append(JobRequirement(
            description=req,
            type=RequirementType.NICE_TO_HAVE,
            category="general",
            weight=0.5
        ))
    
    # Add skills as requirements
    for skill in requirements.get("skills", {}).get("technical", []):
        must_have.append(JobRequirement(
            description=skill,
            type=RequirementType.MUST_HAVE,
            category="skills",
            weight=0.8
        ))
    
    parsed.must_have_requirements = must_have
    parsed.nice_to_have_requirements = nice_to_have
    parsed.experience_years = requirements.get("experience_years")
    parsed.education_level = requirements.get("education")
    
    state["parsed_job_description"] = parsed
    state["requirements_extracted"] = True
    
    # Store requirements in a format suitable for ranking
    state["ranking_criteria"] = {
        "must_have": requirements.get("must_have", []),
        "nice_to_have": requirements.get("nice_to_have", []),
        "skills": requirements.get("skills", {}),
        "experience_years": requirements.get("experience_years"),
        "education": requirements.get("education")
    }
    
    state = update_state_with_message(
        state,
        "assistant",
        f"Extracted {len(must_have)} must-have and {len(nice_to_have)} nice-to-have requirements"
    )
    
    return state


def search_resumes_node(state: AgentState) -> AgentState:
    """
    Node: Search Resumes
    
    Uses RAG to find relevant candidates from the resume database.
    """
    state["current_node"] = "search_resumes"
    
    parsed_jd = state.get("parsed_job_description")
    if not parsed_jd:
        state["error_message"] = "No parsed job description available"
        return state
    
    # Build search query from requirements
    search_terms = []
    
    if parsed_jd.title:
        search_terms.append(parsed_jd.title)
    
    for req in parsed_jd.must_have_requirements[:5]:
        search_terms.append(req.description)
    
    query = " ".join(search_terms)
    
    # Determine number of results based on screening round
    round_to_limit = {
        ScreeningRound.INITIAL: config.max_candidates_initial,
        ScreeningRound.SECOND: config.top_n_initial,
        ScreeningRound.FINAL: config.top_n_second
    }
    num_results = round_to_limit.get(state.get("current_screening_round", ScreeningRound.INITIAL), 100)
    
    # Search using RAG
    results = rag_search_resumes.invoke({
        "query": query,
        "num_results": num_results
    })
    
    state["search_results"] = results if results else []
    
    # Also load candidates from directory if available
    if os.path.exists(config.resume_directory):
        files = list_resume_directory.invoke({"directory_path": config.resume_directory})
        if isinstance(files, list) and files and not files[0].startswith("Error"):
            loaded_candidates = []
            for file_path in files:
                content = read_resume_file.invoke({"file_path": file_path})
                if not content.startswith("Error"):
                    # Try to parse as JSON, otherwise treat as text
                    try:
                        candidate_data = json.loads(content)
                    except json.JSONDecodeError:
                        candidate_data = {
                            "id": os.path.basename(file_path).replace('.txt', '').replace('.json', ''),
                            "name": os.path.basename(file_path).replace('.txt', '').replace('.json', ''),
                            "raw_content": content
                        }
                    loaded_candidates.append(candidate_data)
            
            state["all_candidates"] = loaded_candidates
    
    state = update_state_with_message(
        state,
        "assistant",
        f"Found {len(state.get('search_results', []))} candidates from search, "
        f"{len(state.get('all_candidates', []))} from directory"
    )
    
    return state


def rank_candidates_node(state: AgentState) -> AgentState:
    """
    Node: Rank Candidates
    
    Scores and ranks candidates based on job requirements.
    """
    state["current_node"] = "rank_candidates"
    
    candidates = state.get("all_candidates", []) or state.get("search_results", [])
    
    if not candidates:
        state["error_message"] = "No candidates to rank"
        return state
    
    requirements = state.get("ranking_criteria", {})
    
    # Determine how many to select based on round
    round_to_top_n = {
        ScreeningRound.INITIAL: config.top_n_initial,
        ScreeningRound.SECOND: config.top_n_second,
        ScreeningRound.FINAL: config.top_n_final
    }
    top_n = round_to_top_n.get(state.get("current_screening_round", ScreeningRound.INITIAL), 10)
    
    # Rank candidates
    ranked = rank_candidates.invoke({
        "candidates": candidates,
        "job_requirements": requirements,
        "top_n": top_n
    })
    
    # Convert to CandidateMatch objects
    shortlist = []
    for candidate in ranked:
        match = CandidateMatch(
            candidate_id=candidate.get("id", candidate.get("candidate_id", "unknown")),
            name=candidate.get("name", "Unknown"),
            score=candidate.get("score", 0),
            strengths=candidate.get("strengths", []),
            gaps=candidate.get("gaps", []),
            must_have_match=candidate.get("must_have_breakdown", {}),
            nice_to_have_match=candidate.get("nice_to_have_breakdown", {}),
            ranking_explanation=f"Score: {candidate.get('score', 0):.1f}/100"
        )
        
        # Add recommendation based on score
        if match.score >= 80:
            match.recommendation = "hire"
        elif match.score >= 60:
            match.recommendation = "maybe"
        else:
            match.recommendation = "no_hire"
        
        shortlist.append(match)
    
    state["candidate_shortlist"] = shortlist
    
    state = update_state_with_message(
        state,
        "assistant",
        f"Ranked candidates. Top {len(shortlist)} shortlisted for {state.get('current_screening_round', 'initial')} round"
    )
    
    return state


def generate_report_node(state: AgentState) -> AgentState:
    """
    Node: Generate Report
    
    Creates detailed match reports for shortlisted candidates.
    """
    state["current_node"] = "generate_report"
    
    shortlist = state.get("candidate_shortlist", [])
    requirements = state.get("ranking_criteria", {})
    
    if not shortlist:
        state["error_message"] = "No candidates in shortlist"
        return state
    
    reports = []
    final_report_parts = []
    
    final_report_parts.append("=" * 70)
    final_report_parts.append("RESUME MATCHING AGENT - FINAL REPORT")
    final_report_parts.append("=" * 70)
    final_report_parts.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    final_report_parts.append(f"Screening Round: {state.get('current_screening_round', 'Initial')}")
    final_report_parts.append(f"Candidates Evaluated: {len(shortlist)}")
    final_report_parts.append("")
    
    # Summary section
    final_report_parts.append("-" * 50)
    final_report_parts.append("EXECUTIVE SUMMARY")
    final_report_parts.append("-" * 50)
    
    hire_count = sum(1 for c in shortlist if c.recommendation == "hire")
    maybe_count = sum(1 for c in shortlist if c.recommendation == "maybe")
    no_hire_count = sum(1 for c in shortlist if c.recommendation == "no_hire")
    
    final_report_parts.append(f"  Recommended for Hire: {hire_count}")
    final_report_parts.append(f"  Need Further Evaluation: {maybe_count}")
    final_report_parts.append(f"  Not Recommended: {no_hire_count}")
    final_report_parts.append("")
    
    # Ranking table
    final_report_parts.append("-" * 50)
    final_report_parts.append("CANDIDATE RANKINGS")
    final_report_parts.append("-" * 50)
    final_report_parts.append(f"{'Rank':<6}{'Name':<25}{'Score':<10}{'Recommendation':<15}")
    final_report_parts.append("-" * 50)
    
    for i, candidate in enumerate(shortlist, 1):
        rec_symbol = "★" if candidate.recommendation == "hire" else ("◐" if candidate.recommendation == "maybe" else "✗")
        final_report_parts.append(
            f"{i:<6}{candidate.name[:24]:<25}{candidate.score:<10.1f}{rec_symbol} {candidate.recommendation:<15}"
        )
    
    final_report_parts.append("")
    
    # Detailed reports for each candidate
    final_report_parts.append("-" * 50)
    final_report_parts.append("DETAILED CANDIDATE REPORTS")
    final_report_parts.append("-" * 50)
    
    for candidate in shortlist:
        # Convert CandidateMatch to dict for report generation
        candidate_dict = {
            "id": candidate.candidate_id,
            "candidate_id": candidate.candidate_id,
            "name": candidate.name,
            "score": candidate.score,
            "strengths": candidate.strengths,
            "gaps": candidate.gaps,
            "category_scores": {},  # Would be populated with actual data
            "must_have_breakdown": candidate.must_have_match,
            "nice_to_have_breakdown": candidate.nice_to_have_match
        }
        
        report_text = generate_match_report.invoke({
            "candidate": candidate_dict,
            "job_requirements": requirements,
            "include_interview_questions": True
        })
        
        final_report_parts.append(report_text)
        final_report_parts.append("")
        
        # Create MatchReport object
        reports.append(MatchReport(
            candidate_id=candidate.candidate_id,
            candidate_name=candidate.name,
            overall_score=candidate.score,
            detailed_analysis=report_text
        ))
    
    state["match_reports"] = reports
    state["final_report"] = "\n".join(final_report_parts)
    
    state = update_state_with_message(
        state,
        "assistant",
        f"Generated detailed reports for {len(reports)} candidates"
    )
    
    return state


def human_feedback_node(state: AgentState) -> AgentState:
    """
    Node: Human Feedback Loop
    
    Waits for and processes human feedback.
    """
    state["current_node"] = "human_feedback"
    state["awaiting_feedback"] = True
    
    return state


def process_feedback_node(state: AgentState) -> AgentState:
    """
    Node: Process Feedback
    
    Processes human feedback and determines next action.
    """
    state["current_node"] = "process_feedback"
    
    feedback = state.get("human_feedback", "")
    
    if not feedback:
        return state
    
    feedback_lower = feedback.lower()
    
    # Check if user wants to adjust requirements
    if any(word in feedback_lower for word in ["adjust", "change", "modify", "add", "remove", "update"]):
        # Reset to extract requirements with new criteria
        state["requirements_extracted"] = False
        state = update_state_with_message(
            state,
            "assistant",
            "Adjusting requirements based on feedback. Will re-rank candidates."
        )
    
    # Check if user wants to compare specific candidates
    elif any(word in feedback_lower for word in ["compare", "versus", "vs", "side by side"]):
        state = update_state_with_message(
            state,
            "assistant",
            "I'll create a detailed comparison of the requested candidates."
        )
    
    # Check if user wants to proceed to next round
    elif any(word in feedback_lower for word in ["next", "proceed", "continue", "deeper"]):
        current_round = state.get("current_screening_round", ScreeningRound.INITIAL)
        if current_round == ScreeningRound.INITIAL:
            state["current_screening_round"] = ScreeningRound.SECOND
        elif current_round == ScreeningRound.SECOND:
            state["current_screening_round"] = ScreeningRound.FINAL
        
        state = update_state_with_message(
            state,
            "assistant",
            f"Moving to {state['current_screening_round'].value} screening round."
        )
    
    # Check if user approves/finalizes
    elif any(word in feedback_lower for word in ["approve", "accept", "finalize", "done", "complete"]):
        state["is_complete"] = True
        state = update_state_with_message(
            state,
            "assistant",
            "Screening process completed. Final report is ready."
        )
    
    state["awaiting_feedback"] = False
    state["human_feedback"] = None
    
    return state


def end_node(state: AgentState) -> AgentState:
    """
    Node: End
    
    Final node that marks completion.
    """
    state["current_node"] = "end"
    state["is_complete"] = True
    
    state = update_state_with_message(
        state,
        "assistant",
        "Resume matching process complete. Thank you for using the Resume Matching Agent."
    )
    
    return state


# =============================================================================
# ROUTING FUNCTIONS
# =============================================================================

def route_after_feedback(state: AgentState) -> str:
    """Determine next node after processing feedback"""
    
    if state.get("is_complete"):
        return "end"
    
    if not state.get("requirements_extracted"):
        return "extract_requirements"
    
    current_round = state.get("current_screening_round", ScreeningRound.INITIAL)
    
    if current_round == ScreeningRound.FINAL:
        # In final round, generate final report and end
        return "generate_report"
    
    # Otherwise continue with ranking
    return "rank_candidates"


def should_continue_to_feedback(state: AgentState) -> str:
    """Determine if we should go to feedback or continue"""
    
    if state.get("error_message"):
        return "end"
    
    current_round = state.get("current_screening_round", ScreeningRound.INITIAL)
    
    # Always go to feedback after initial and second rounds
    if current_round in [ScreeningRound.INITIAL, ScreeningRound.SECOND]:
        return "human_feedback"
    
    # Final round goes directly to end
    return "end"


# =============================================================================
# GRAPH CONSTRUCTION
# =============================================================================

def create_matching_agent_graph() -> StateGraph:
    """
    Create the LangGraph workflow for the Resume Matching Agent.
    
    Workflow:
    START → Parse JD → Extract Requirements → Search Resumes → 
    Rank Candidates → Generate Report → Human Feedback Loop → END
    """
    
    # Create the graph
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("parse_jd", parse_jd_node)
    graph.add_node("extract_requirements", extract_requirements_node)
    graph.add_node("search_resumes", search_resumes_node)
    graph.add_node("rank_candidates", rank_candidates_node)
    graph.add_node("generate_report", generate_report_node)
    graph.add_node("human_feedback", human_feedback_node)
    graph.add_node("process_feedback", process_feedback_node)
    graph.add_node("end", end_node)
    
    # Set entry point
    graph.set_entry_point("parse_jd")
    
    # Add edges
    graph.add_edge("parse_jd", "extract_requirements")
    graph.add_edge("extract_requirements", "search_resumes")
    graph.add_edge("search_resumes", "rank_candidates")
    graph.add_edge("rank_candidates", "generate_report")
    
    # Conditional edge after report generation
    graph.add_conditional_edges(
        "generate_report",
        should_continue_to_feedback,
        {
            "human_feedback": "human_feedback",
            "end": "end"
        }
    )
    
    # Edge from feedback to process
    graph.add_edge("human_feedback", "process_feedback")
    
    # Conditional edge after processing feedback
    graph.add_conditional_edges(
        "process_feedback",
        route_after_feedback,
        {
            "extract_requirements": "extract_requirements",
            "rank_candidates": "rank_candidates",
            "generate_report": "generate_report",
            "end": "end"
        }
    )
    
    # Set finish point
    graph.set_finish_point("end")
    
    return graph


# =============================================================================
# MAIN AGENT CLASS
# =============================================================================

class ResumeMatchingAgent:
    """
    Main class for the Resume Matching Agent.
    
    Provides a high-level interface for:
    - Processing job descriptions
    - Searching and ranking candidates
    - Interactive conversation
    - Multi-round screening
    """
    
    def __init__(self, config: AgentConfig = None):
        self.config = config or AgentConfig()
        self.graph = create_matching_agent_graph()
        self.compiled_graph = self.graph.compile()
        self.state = create_initial_state()
        self.llm = get_llm(self.config)
    
    def start_matching(self, job_description: str) -> Dict[str, Any]:
        """
        Start a new matching session with a job description.
        
        Args:
            job_description: Raw job description text
            
        Returns:
            Initial results with shortlisted candidates
        """
        # Reset state
        self.state = create_initial_state()
        self.state["job_description_raw"] = job_description
        
        # Run until we hit human feedback node
        for step in self.compiled_graph.stream(self.state):
            node_name = list(step.keys())[0]
            self.state = step[node_name]
            
            if self.state.get("awaiting_feedback") or self.state.get("is_complete"):
                break
        
        return self._get_results()
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language query.
        
        Supports queries like:
        - "Find me candidates with React and 3+ years experience"
        - "Compare the top 3 matches side by side"
        - "Why did John rank higher than Jane?"
        
        Args:
            query: Natural language query
            
        Returns:
            Response with relevant information
        """
        query_lower = query.lower()
        
        # Add query to state
        self.state["current_query"] = query
        self.state = update_state_with_message(self.state, "user", query)
        
        # Determine query type and handle
        if any(word in query_lower for word in ["find", "search", "candidates with", "looking for"]):
            return self._handle_search_query(query)
        
        elif any(word in query_lower for word in ["compare", "versus", "vs", "side by side"]):
            return self._handle_compare_query(query)
        
        elif any(word in query_lower for word in ["why", "explain", "reason", "how come"]):
            return self._handle_explain_query(query)
        
        elif any(word in query_lower for word in ["adjust", "change", "modify", "new criteria"]):
            return self._handle_adjust_query(query)
        
        elif any(word in query_lower for word in ["next round", "deeper analysis", "proceed"]):
            return self._handle_next_round_query()
        
        else:
            return self._handle_general_query(query)
    
    def _handle_search_query(self, query: str) -> Dict[str, Any]:
        """Handle search-type queries"""
        # Update job requirements based on query
        requirements = extract_requirements.invoke({"jd": query})
        
        # Merge with existing requirements
        existing = self.state.get("ranking_criteria", {})
        existing.update(requirements)
        self.state["ranking_criteria"] = existing
        
        # Re-rank candidates
        self.state = rank_candidates_node(self.state)
        
        response = f"Found candidates matching: {query}\n\n"
        response += self._format_shortlist()
        
        self.state = update_state_with_message(self.state, "assistant", response)
        
        return {"response": response, "shortlist": self.state.get("candidate_shortlist", [])}
    
    def _handle_compare_query(self, query: str) -> Dict[str, Any]:
        """Handle comparison queries"""
        shortlist = self.state.get("candidate_shortlist", [])
        
        if not shortlist:
            response = "No candidates available for comparison. Please run a search first."
            self.state = update_state_with_message(self.state, "assistant", response)
            return {"response": response}
        
        # Extract candidate names/IDs from query or use top 3
        candidate_ids = [c.candidate_id for c in shortlist[:3]]
        candidate_data = [
            {
                "id": c.candidate_id,
                "name": c.name,
                "score": c.score,
                "strengths": c.strengths,
                "gaps": c.gaps
            }
            for c in shortlist[:3]
        ]
        
        comparison = compare_candidates.invoke({
            "candidate_ids": candidate_ids,
            "candidates_data": candidate_data
        })
        
        response = self._format_comparison(comparison)
        self.state = update_state_with_message(self.state, "assistant", response)
        
        return {"response": response, "comparison": comparison}
    
    def _handle_explain_query(self, query: str) -> Dict[str, Any]:
        """Handle explanation queries"""
        shortlist = self.state.get("candidate_shortlist", [])
        
        # Try to identify candidates mentioned in query
        mentioned = []
        for candidate in shortlist:
            if candidate.name.lower() in query.lower() or candidate.candidate_id.lower() in query.lower():
                mentioned.append(candidate)
        
        if len(mentioned) >= 2:
            # Compare two mentioned candidates
            response = f"Comparing {mentioned[0].name} and {mentioned[1].name}:\n\n"
            
            response += f"{mentioned[0].name} (Score: {mentioned[0].score:.1f}):\n"
            response += f"  Strengths: {', '.join(mentioned[0].strengths[:3])}\n"
            response += f"  Gaps: {', '.join(mentioned[0].gaps[:3])}\n\n"
            
            response += f"{mentioned[1].name} (Score: {mentioned[1].score:.1f}):\n"
            response += f"  Strengths: {', '.join(mentioned[1].strengths[:3])}\n"
            response += f"  Gaps: {', '.join(mentioned[1].gaps[:3])}\n\n"
            
            score_diff = mentioned[0].score - mentioned[1].score
            if score_diff > 0:
                response += f"{mentioned[0].name} ranks higher due to +{score_diff:.1f} point difference, "
                response += f"primarily because of: {', '.join(mentioned[0].strengths[:2])}"
            else:
                response += f"{mentioned[1].name} ranks higher due to +{-score_diff:.1f} point difference, "
                response += f"primarily because of: {', '.join(mentioned[1].strengths[:2])}"
        
        elif shortlist:
            # General explanation of rankings
            response = "Here's why candidates are ranked this way:\n\n"
            for i, c in enumerate(shortlist[:5], 1):
                response += f"{i}. {c.name} ({c.score:.1f} pts): {c.ranking_explanation}\n"
                response += f"   Key differentiator: {c.strengths[0] if c.strengths else 'N/A'}\n"
        
        else:
            response = "No ranking data available. Please run a search first."
        
        self.state = update_state_with_message(self.state, "assistant", response)
        return {"response": response}
    
    def _handle_adjust_query(self, query: str) -> Dict[str, Any]:
        """Handle requirement adjustment queries"""
        # Extract new requirements from query
        new_requirements = extract_requirements.invoke({"jd": query})
        
        # Update existing requirements
        existing = self.state.get("ranking_criteria", {})
        
        # Merge lists
        for key in ["must_have", "nice_to_have"]:
            if key in new_requirements:
                existing_list = existing.get(key, [])
                existing[key] = list(set(existing_list + new_requirements[key]))
        
        # Update skills
        if "skills" in new_requirements:
            existing_skills = existing.get("skills", {"technical": [], "soft": []})
            for skill_type in ["technical", "soft"]:
                existing_skills[skill_type] = list(set(
                    existing_skills.get(skill_type, []) + 
                    new_requirements.get("skills", {}).get(skill_type, [])
                ))
            existing["skills"] = existing_skills
        
        self.state["ranking_criteria"] = existing
        
        # Re-rank
        self.state = rank_candidates_node(self.state)
        
        response = f"Adjusted requirements and re-ranked candidates.\n\n"
        response += "Updated criteria:\n"
        response += f"  Must-have: {len(existing.get('must_have', []))} requirements\n"
        response += f"  Nice-to-have: {len(existing.get('nice_to_have', []))} requirements\n\n"
        response += self._format_shortlist()
        
        self.state = update_state_with_message(self.state, "assistant", response)
        
        return {"response": response, "shortlist": self.state.get("candidate_shortlist", [])}
    
    def _handle_next_round_query(self) -> Dict[str, Any]:
        """Handle requests to proceed to next screening round"""
        current_round = self.state.get("current_screening_round", ScreeningRound.INITIAL)
        
        if current_round == ScreeningRound.INITIAL:
            self.state["current_screening_round"] = ScreeningRound.SECOND
            response = "Moving to SECOND round screening (deep analysis of top candidates)...\n\n"
        elif current_round == ScreeningRound.SECOND:
            self.state["current_screening_round"] = ScreeningRound.FINAL
            response = "Moving to FINAL round (hire/no-hire recommendations)...\n\n"
        else:
            response = "Already at final screening round.\n\n"
            self.state = update_state_with_message(self.state, "assistant", response)
            return {"response": response}
        
        # Run ranking for new round
        self.state = rank_candidates_node(self.state)
        self.state = generate_report_node(self.state)
        
        response += self._format_shortlist()
        self.state = update_state_with_message(self.state, "assistant", response)
        
        return {
            "response": response, 
            "shortlist": self.state.get("candidate_shortlist", []),
            "report": self.state.get("final_report", "")
        }
    
    def _handle_general_query(self, query: str) -> Dict[str, Any]:
        """Handle general queries using LLM if available"""
        if self.llm:
            # Use LLM to generate response based on current state
            context = self._build_context()
            prompt = f"""You are a resume matching assistant. Based on the current matching context:

{context}

User Query: {query}

Provide a helpful, concise response."""
            
            try:
                response = self.llm.invoke(prompt).content
            except Exception as e:
                response = f"I understand you're asking: '{query}'. How can I help you with the candidate matching process?"
        else:
            response = f"I understand you're asking: '{query}'. I can help you with:\n"
            response += "- Finding candidates (e.g., 'Find React developers')\n"
            response += "- Comparing candidates (e.g., 'Compare top 3')\n"
            response += "- Explaining rankings (e.g., 'Why does John rank higher?')\n"
            response += "- Adjusting criteria (e.g., 'Add Python as a requirement')\n"
            response += "- Moving to next round (e.g., 'Proceed to final round')"
        
        self.state = update_state_with_message(self.state, "assistant", response)
        return {"response": response}
    
    def submit_feedback(self, feedback: str) -> Dict[str, Any]:
        """
        Submit human feedback to influence the matching process.
        
        Args:
            feedback: User feedback text
            
        Returns:
            Updated results
        """
        self.state["human_feedback"] = feedback
        self.state = process_feedback_node(self.state)
        
        # Continue graph execution if not complete
        if not self.state.get("is_complete"):
            for step in self.compiled_graph.stream(self.state):
                node_name = list(step.keys())[0]
                self.state = step[node_name]
                
                if self.state.get("awaiting_feedback") or self.state.get("is_complete"):
                    break
        
        return self._get_results()
    
    def get_report(self) -> str:
        """Get the current final report"""
        return self.state.get("final_report", "No report generated yet.")
    
    def get_interview_questions(self, candidate_id: str) -> Dict[str, Any]:
        """
        Generate interview questions for a specific candidate.
        
        Args:
            candidate_id: ID of the candidate
            
        Returns:
            Interview questions
        """
        shortlist = self.state.get("candidate_shortlist", [])
        candidate = next((c for c in shortlist if c.candidate_id == candidate_id), None)
        
        if not candidate:
            return {"error": f"Candidate {candidate_id} not found in shortlist"}
        
        candidate_data = {
            "id": candidate.candidate_id,
            "name": candidate.name,
            "skills": [],
            "experience": [],
            "gaps": candidate.gaps,
            "strengths": candidate.strengths
        }
        
        questions = generate_interview_questions.invoke({
            "candidate_id": candidate_id,
            "candidate_data": candidate_data,
            "job_requirements": self.state.get("ranking_criteria", {})
        })
        
        return questions
    
    def _get_results(self) -> Dict[str, Any]:
        """Get current results from state"""
        return {
            "shortlist": [
                {
                    "id": c.candidate_id,
                    "name": c.name,
                    "score": c.score,
                    "recommendation": c.recommendation,
                    "strengths": c.strengths[:3],
                    "gaps": c.gaps[:3]
                }
                for c in self.state.get("candidate_shortlist", [])
            ],
            "current_round": self.state.get("current_screening_round", ScreeningRound.INITIAL).value,
            "awaiting_feedback": self.state.get("awaiting_feedback", False),
            "is_complete": self.state.get("is_complete", False),
            "report_available": bool(self.state.get("final_report")),
            "conversation_history": [
                {"role": m.role, "content": m.content}
                for m in self.state.get("messages", [])[-10:]
            ]
        }
    
    def _format_shortlist(self) -> str:
        """Format shortlist for display"""
        shortlist = self.state.get("candidate_shortlist", [])
        if not shortlist:
            return "No candidates in shortlist."
        
        lines = ["Top Candidates:"]
        lines.append("-" * 50)
        
        for i, c in enumerate(shortlist, 1):
            rec = "★ HIRE" if c.recommendation == "hire" else ("◐ MAYBE" if c.recommendation == "maybe" else "✗ NO")
            lines.append(f"{i}. {c.name} - Score: {c.score:.1f}/100 [{rec}]")
            if c.strengths:
                lines.append(f"   Strengths: {', '.join(c.strengths[:2])}")
        
        return "\n".join(lines)
    
    def _format_comparison(self, comparison: Dict[str, Any]) -> str:
        """Format comparison for display"""
        lines = ["Candidate Comparison:"]
        lines.append("=" * 50)
        
        for rank_info in comparison.get("ranking", []):
            lines.append(f"#{rank_info['rank']}: {rank_info['name']} (Score: {rank_info['score']:.1f})")
        
        lines.append("")
        lines.append("Key Differentiators:")
        lines.append("-" * 50)
        
        for cid, diff in comparison.get("key_differentiators", {}).items():
            lines.append(f"\n{cid}:")
            lines.append(f"  Strengths: {', '.join(diff.get('strengths', []))}")
            lines.append(f"  Gaps: {', '.join(diff.get('gaps', []))}")
        
        if comparison.get("recommendation"):
            lines.append("")
            lines.append("-" * 50)
            rec = comparison["recommendation"]
            lines.append(f"Recommendation: {rec['candidate_name']} ({rec['score']:.1f})")
            lines.append(f"Reasoning: {rec.get('reasoning', 'N/A')}")
        
        return "\n".join(lines)
    
    def _build_context(self) -> str:
        """Build context string for LLM"""
        context_parts = []
        
        if self.state.get("parsed_job_description"):
            jd = self.state["parsed_job_description"]
            context_parts.append(f"Job Title: {jd.title}")
        
        shortlist = self.state.get("candidate_shortlist", [])
        if shortlist:
            context_parts.append(f"Candidates in shortlist: {len(shortlist)}")
            context_parts.append("Top candidates: " + ", ".join(c.name for c in shortlist[:3]))
        
        context_parts.append(f"Current round: {self.state.get('current_screening_round', 'initial')}")
        
        return "\n".join(context_parts)


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def create_agent(config: AgentConfig = None) -> ResumeMatchingAgent:
    """Create and return a ResumeMatchingAgent instance"""
    return ResumeMatchingAgent(config)


if __name__ == "__main__":
    # Simple test
    print("Resume Matching Agent - LangGraph Implementation")
    print("=" * 50)
    
    # Create agent
    agent = create_agent()
    
    # Test with sample JD
    sample_jd = """
    Senior Software Engineer
    
    Requirements:
    - 5+ years of experience in software development
    - Strong proficiency in Python and JavaScript
    - Experience with React and Node.js
    - Bachelor's degree in Computer Science
    
    Nice to have:
    - Experience with AWS or cloud platforms
    - Knowledge of machine learning
    - Leadership experience
    """
    
    print("\nStarting matching for sample job description...")
    results = agent.start_matching(sample_jd)
    
    print(f"\nResults:")
    print(f"  Current round: {results['current_round']}")
    print(f"  Candidates found: {len(results['shortlist'])}")
    print(f"  Awaiting feedback: {results['awaiting_feedback']}")
