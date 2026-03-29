"""
Agent State Design for Resume Matching Agent

This module defines the state schema for tracking:
- Conversation history
- Job requirements understanding
- Candidate shortlist and reasoning
"""

from typing import TypedDict, List, Dict, Optional, Annotated, Any
from pydantic import BaseModel, Field
from enum import Enum
import operator


class ScreeningRound(str, Enum):
    """Screening round stages"""
    INITIAL = "initial"      # Initial screen: top 10 from 100 resumes
    SECOND = "second"        # Deep analysis of top 10
    FINAL = "final"          # Final hire/no-hire recommendation


class RequirementType(str, Enum):
    """Types of job requirements"""
    MUST_HAVE = "must_have"
    NICE_TO_HAVE = "nice_to_have"


class JobRequirement(BaseModel):
    """Individual job requirement"""
    description: str
    type: RequirementType
    category: str  # e.g., "skills", "experience", "education", "certifications"
    weight: float = Field(default=1.0, ge=0.0, le=1.0)


class CandidateMatch(BaseModel):
    """Candidate match information"""
    candidate_id: str
    name: str
    score: float = Field(ge=0.0, le=100.0)
    strengths: List[str] = Field(default_factory=list)
    gaps: List[str] = Field(default_factory=list)
    improvement_suggestions: List[str] = Field(default_factory=list)
    must_have_match: Dict[str, bool] = Field(default_factory=dict)
    nice_to_have_match: Dict[str, bool] = Field(default_factory=dict)
    ranking_explanation: str = ""
    recommendation: Optional[str] = None  # "hire", "no_hire", "maybe"


class ParsedJobDescription(BaseModel):
    """Parsed job description structure"""
    title: str = ""
    company: str = ""
    summary: str = ""
    must_have_requirements: List[JobRequirement] = Field(default_factory=list)
    nice_to_have_requirements: List[JobRequirement] = Field(default_factory=list)
    experience_years: Optional[int] = None
    education_level: Optional[str] = None
    raw_text: str = ""


class ConversationMessage(BaseModel):
    """Single conversation message"""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: Optional[str] = None


class MatchReport(BaseModel):
    """Detailed match report for a candidate"""
    candidate_id: str
    candidate_name: str
    overall_score: float
    category_scores: Dict[str, float] = Field(default_factory=dict)
    detailed_analysis: str = ""
    interview_questions: List[str] = Field(default_factory=list)
    comparison_notes: str = ""


# Helper function for message accumulation
def add_messages(left: List[ConversationMessage], right: List[ConversationMessage]) -> List[ConversationMessage]:
    """Accumulate messages in conversation history"""
    return left + right


class AgentState(TypedDict):
    """
    Main agent state for the Resume Matching Agent
    
    This state tracks:
    1. Conversation history - All user and agent messages
    2. Job requirements understanding - Parsed JD with must-have/nice-to-have
    3. Candidate shortlist and reasoning - Ranked candidates with explanations
    """
    
    # Conversation tracking
    messages: Annotated[List[ConversationMessage], add_messages]
    current_query: str
    
    # Job description understanding
    job_description_raw: str
    parsed_job_description: Optional[ParsedJobDescription]
    requirements_extracted: bool
    
    # Candidate management
    all_candidates: List[Dict[str, Any]]
    candidate_shortlist: List[CandidateMatch]
    current_screening_round: ScreeningRound
    
    # Search and ranking
    search_results: List[Dict[str, Any]]
    ranking_criteria: Dict[str, float]
    
    # Reports and outputs
    match_reports: List[MatchReport]
    final_report: str
    
    # Human feedback
    human_feedback: Optional[str]
    awaiting_feedback: bool
    
    # Workflow control
    current_node: str
    error_message: Optional[str]
    is_complete: bool


def create_initial_state() -> AgentState:
    """Create initial empty state"""
    return AgentState(
        messages=[],
        current_query="",
        job_description_raw="",
        parsed_job_description=None,
        requirements_extracted=False,
        all_candidates=[],
        candidate_shortlist=[],
        current_screening_round=ScreeningRound.INITIAL,
        search_results=[],
        ranking_criteria={
            "must_have_match": 0.5,
            "nice_to_have_match": 0.2,
            "experience_match": 0.2,
            "education_match": 0.1
        },
        match_reports=[],
        final_report="",
        human_feedback=None,
        awaiting_feedback=False,
        current_node="start",
        error_message=None,
        is_complete=False
    )


def update_state_with_message(state: AgentState, role: str, content: str) -> AgentState:
    """Helper to add a message to state"""
    from datetime import datetime
    new_message = ConversationMessage(
        role=role,
        content=content,
        timestamp=datetime.now().isoformat()
    )
    state["messages"] = state["messages"] + [new_message]
    return state
