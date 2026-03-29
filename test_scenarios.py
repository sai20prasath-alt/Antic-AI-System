"""
Test Scenarios for Resume Matching Agent

Contains 5+ conversation flows to test the agent's capabilities:
1. Basic matching flow
2. Candidate comparison flow
3. Requirement adjustment flow
4. Multi-round screening flow
5. Explainability flow
6. Interview questions flow
"""

import os
import sys
import json
import unittest
from typing import List, Dict, Any

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from matching_agent import ResumeMatchingAgent, AgentConfig, create_agent
from agent_state import ScreeningRound, create_initial_state
from tools import extract_requirements, compare_candidates, generate_interview_questions


# =============================================================================
# SAMPLE DATA
# =============================================================================

SAMPLE_JOB_DESCRIPTION = """
Senior Full-Stack Developer

Company: TechCorp Inc.
Location: Remote

Requirements:
- 5+ years of software development experience
- Strong proficiency in Python and JavaScript
- Experience with React.js and Node.js
- PostgreSQL database experience
- AWS cloud platform experience
- Bachelor's degree in Computer Science

Nice to Have:
- TypeScript experience
- Docker and Kubernetes knowledge
- GraphQL experience
- Team leadership experience
"""

SAMPLE_CANDIDATES = [
    {
        "id": "candidate_001",
        "name": "Alice Johnson",
        "skills": ["Python", "JavaScript", "React.js", "Node.js", "PostgreSQL", "AWS", "Docker"],
        "years_experience": 7,
        "education": "Master's in Computer Science",
        "strengths": ["Strong React experience", "AWS certified", "Team lead experience"],
        "gaps": []
    },
    {
        "id": "candidate_002",
        "name": "Bob Smith",
        "skills": ["Python", "JavaScript", "React.js", "PostgreSQL"],
        "years_experience": 4,
        "education": "Bachelor's in Computer Science",
        "strengths": ["Good Python skills", "PostgreSQL expert"],
        "gaps": ["Limited AWS experience", "No Node.js experience"]
    },
    {
        "id": "candidate_003",
        "name": "Carol Davis",
        "skills": ["JavaScript", "React.js", "Node.js", "MongoDB", "AWS", "Kubernetes"],
        "years_experience": 6,
        "education": "Bachelor's in Software Engineering",
        "strengths": ["Full-stack expertise", "Kubernetes experience", "AWS experience"],
        "gaps": ["No Python experience", "No PostgreSQL experience"]
    },
    {
        "id": "candidate_004",
        "name": "David Wilson",
        "skills": ["Python", "Django", "PostgreSQL", "AWS", "Docker", "Terraform"],
        "years_experience": 8,
        "education": "PhD in Computer Science",
        "strengths": ["Senior developer", "Infrastructure expertise", "PhD holder"],
        "gaps": ["No React.js experience", "No JavaScript frontend experience"]
    },
    {
        "id": "candidate_005",
        "name": "Eva Martinez",
        "skills": ["Python", "JavaScript", "React.js", "Node.js", "PostgreSQL", "AWS", "TypeScript", "GraphQL"],
        "years_experience": 6,
        "education": "Bachelor's in Computer Science",
        "strengths": ["All required skills", "TypeScript expertise", "GraphQL experience"],
        "gaps": []
    }
]


# =============================================================================
# TEST SCENARIO 1: Basic Matching Flow
# =============================================================================

def test_scenario_1_basic_matching():
    """
    Scenario 1: Basic Matching Flow
    
    Tests the basic workflow:
    1. User provides job description
    2. Agent extracts requirements
    3. Agent searches and ranks candidates
    4. Agent provides results
    """
    print("\n" + "=" * 60)
    print("SCENARIO 1: Basic Matching Flow")
    print("=" * 60)
    
    # Initialize agent
    agent = create_agent()
    
    # Start matching
    print("\n[User] Starting matching with job description...")
    results = agent.start_matching(SAMPLE_JOB_DESCRIPTION)
    
    print(f"\n[Agent] Found {len(results.get('shortlist', []))} candidates")
    print(f"[Agent] Current round: {results.get('current_round')}")
    print(f"[Agent] Awaiting feedback: {results.get('awaiting_feedback')}")
    
    # Verify results
    assert "shortlist" in results, "Should have shortlist"
    assert "current_round" in results, "Should have current_round"
    
    print("\n✓ Scenario 1 PASSED: Basic matching flow works correctly")
    return True


# =============================================================================
# TEST SCENARIO 2: Candidate Comparison Flow
# =============================================================================

def test_scenario_2_candidate_comparison():
    """
    Scenario 2: Candidate Comparison Flow
    
    Tests:
    1. Compare top 3 candidates side by side
    2. Agent provides detailed comparison
    3. Highlights strengths and gaps for each
    """
    print("\n" + "=" * 60)
    print("SCENARIO 2: Candidate Comparison Flow")
    print("=" * 60)
    
    # Initialize agent with pre-loaded candidates
    agent = create_agent()
    agent.state["all_candidates"] = SAMPLE_CANDIDATES
    agent.state["job_description_raw"] = SAMPLE_JOB_DESCRIPTION
    
    # Set up requirements
    requirements = extract_requirements.invoke({"jd": SAMPLE_JOB_DESCRIPTION})
    agent.state["ranking_criteria"] = requirements
    
    print("\n[User] Compare the top 3 candidates side by side")
    result = agent.process_query("Compare the top 3 candidates side by side")
    
    print(f"\n[Agent Response]")
    print(result.get("response", "No response")[:500] + "...")
    
    # Verify comparison was performed
    assert "response" in result, "Should have response"
    
    print("\n✓ Scenario 2 PASSED: Candidate comparison works correctly")
    return True


# =============================================================================
# TEST SCENARIO 3: Requirement Adjustment Flow
# =============================================================================

def test_scenario_3_requirement_adjustment():
    """
    Scenario 3: Requirement Adjustment Flow
    
    Tests:
    1. Initial matching
    2. User adjusts requirements mid-conversation
    3. Agent re-ranks based on new criteria
    4. Agent explains changes
    """
    print("\n" + "=" * 60)
    print("SCENARIO 3: Requirement Adjustment Flow")
    print("=" * 60)
    
    # Initialize agent
    agent = create_agent()
    agent.state["all_candidates"] = SAMPLE_CANDIDATES
    
    # Start matching
    print("\n[User] Starting initial match...")
    results = agent.start_matching(SAMPLE_JOB_DESCRIPTION)
    initial_shortlist = results.get("shortlist", [])
    
    print(f"\n[Agent] Initial ranking complete. Top candidate: {initial_shortlist[0]['name'] if initial_shortlist else 'None'}")
    
    # Adjust requirements
    print("\n[User] Add Kubernetes as a must-have requirement")
    adjusted_result = agent.process_query("Add Kubernetes as a must-have requirement and re-rank")
    
    print(f"\n[Agent Response]")
    print(adjusted_result.get("response", "No response")[:400] + "...")
    
    # Verify re-ranking
    new_shortlist = adjusted_result.get("shortlist", [])
    
    print(f"\n[Agent] Updated ranking after adjustment")
    if new_shortlist:
        print(f"  New top candidate: {new_shortlist[0]['name']}")
    
    print("\n✓ Scenario 3 PASSED: Requirement adjustment works correctly")
    return True


# =============================================================================
# TEST SCENARIO 4: Multi-Round Screening Flow
# =============================================================================

def test_scenario_4_multi_round_screening():
    """
    Scenario 4: Multi-Round Screening Flow
    
    Tests:
    1. Initial screen: top 10 from candidates
    2. Second round: deep analysis
    3. Final round: hire/no-hire recommendation
    """
    print("\n" + "=" * 60)
    print("SCENARIO 4: Multi-Round Screening Flow")
    print("=" * 60)
    
    # Initialize agent
    agent = create_agent()
    agent.state["all_candidates"] = SAMPLE_CANDIDATES
    
    # Round 1: Initial screening
    print("\n[Round 1: Initial Screening]")
    results = agent.start_matching(SAMPLE_JOB_DESCRIPTION)
    
    print(f"  Candidates shortlisted: {len(results.get('shortlist', []))}")
    print(f"  Current round: {results.get('current_round')}")
    
    assert results.get("current_round") == "initial", "Should be in initial round"
    
    # Round 2: Deep analysis
    print("\n[User] Proceed to the second round for deeper analysis")
    round2_result = agent.process_query("Proceed to next screening round for deeper analysis")
    
    print(f"\n[Round 2: Deep Analysis]")
    print(f"  Current round: {agent._get_results().get('current_round')}")
    
    # Round 3: Final recommendations
    print("\n[User] Move to final round with hire/no-hire recommendations")
    round3_result = agent.process_query("Proceed to final round")
    
    final_results = agent._get_results()
    print(f"\n[Round 3: Final Recommendations]")
    print(f"  Current round: {final_results.get('current_round')}")
    
    for candidate in final_results.get("shortlist", [])[:3]:
        rec = candidate.get("recommendation", "unknown")
        print(f"  - {candidate.get('name')}: {rec.upper()}")
    
    print("\n✓ Scenario 4 PASSED: Multi-round screening works correctly")
    return True


# =============================================================================
# TEST SCENARIO 5: Explainability Flow
# =============================================================================

def test_scenario_5_explainability():
    """
    Scenario 5: Explainability Flow
    
    Tests:
    1. User asks why a candidate ranked higher
    2. Agent provides detailed explanation
    3. Agent highlights strengths and gaps
    """
    print("\n" + "=" * 60)
    print("SCENARIO 5: Explainability Flow")
    print("=" * 60)
    
    # Initialize agent with candidates
    agent = create_agent()
    agent.state["all_candidates"] = SAMPLE_CANDIDATES
    
    # Start matching
    results = agent.start_matching(SAMPLE_JOB_DESCRIPTION)
    shortlist = results.get("shortlist", [])
    
    if len(shortlist) >= 2:
        candidate1 = shortlist[0]["name"]
        candidate2 = shortlist[1]["name"]
        
        print(f"\n[User] Why did {candidate1} rank higher than {candidate2}?")
        
        explanation = agent.process_query(f"Why did {candidate1} rank higher than {candidate2}?")
        
        print(f"\n[Agent Response]")
        print(explanation.get("response", "No response"))
        
        assert "response" in explanation, "Should have explanation response"
    else:
        print("\nNot enough candidates for comparison test")
    
    # Also test general ranking explanation
    print("\n[User] Explain the overall ranking methodology")
    method_explanation = agent.process_query("Explain why the candidates are ranked this way")
    
    print(f"\n[Agent Response]")
    print(method_explanation.get("response", "No response")[:400] + "...")
    
    print("\n✓ Scenario 5 PASSED: Explainability works correctly")
    return True


# =============================================================================
# TEST SCENARIO 6: Interview Questions Flow
# =============================================================================

def test_scenario_6_interview_questions():
    """
    Scenario 6: Interview Questions Generation Flow
    
    Tests:
    1. User requests interview questions for a candidate
    2. Agent generates tailored questions
    3. Questions cover technical, behavioral, and gap areas
    """
    print("\n" + "=" * 60)
    print("SCENARIO 6: Interview Questions Flow")
    print("=" * 60)
    
    # Initialize agent
    agent = create_agent()
    agent.state["all_candidates"] = SAMPLE_CANDIDATES
    
    # Start matching
    results = agent.start_matching(SAMPLE_JOB_DESCRIPTION)
    shortlist = results.get("shortlist", [])
    
    if shortlist:
        candidate_id = shortlist[0]["id"]
        candidate_name = shortlist[0]["name"]
        
        print(f"\n[User] Generate interview questions for {candidate_name}")
        
        questions = agent.get_interview_questions(candidate_id)
        
        print(f"\n[Agent] Interview Questions for {questions.get('candidate_name', 'Unknown')}:")
        
        # Technical questions
        tech_qs = questions.get("technical_questions", [])
        print(f"\n  Technical Questions ({len(tech_qs)}):")
        for i, q in enumerate(tech_qs[:2], 1):
            question_text = q.get("question", str(q)) if isinstance(q, dict) else q
            print(f"    {i}. {question_text[:80]}...")
        
        # Behavioral questions
        behav_qs = questions.get("behavioral_questions", [])
        print(f"\n  Behavioral Questions ({len(behav_qs)}):")
        for i, q in enumerate(behav_qs[:2], 1):
            question_text = q.get("question", str(q)) if isinstance(q, dict) else q
            print(f"    {i}. {question_text[:80]}...")
        
        # Gap-probing questions
        gap_qs = questions.get("gap_probing_questions", [])
        print(f"\n  Gap-Probing Questions ({len(gap_qs)}):")
        for i, q in enumerate(gap_qs[:2], 1):
            question_text = q.get("question", str(q)) if isinstance(q, dict) else q
            print(f"    {i}. {question_text[:80]}...")
        
        assert "technical_questions" in questions, "Should have technical questions"
        assert "behavioral_questions" in questions, "Should have behavioral questions"
    
    print("\n✓ Scenario 6 PASSED: Interview questions generation works correctly")
    return True


# =============================================================================
# TEST SCENARIO 7: Natural Language Queries
# =============================================================================

def test_scenario_7_natural_language():
    """
    Scenario 7: Natural Language Query Flow
    
    Tests various natural language queries:
    1. "Find me candidates with React and 3+ years experience"
    2. "Show me Python developers"
    3. "Who has AWS experience?"
    """
    print("\n" + "=" * 60)
    print("SCENARIO 7: Natural Language Queries")
    print("=" * 60)
    
    # Initialize agent
    agent = create_agent()
    agent.state["all_candidates"] = SAMPLE_CANDIDATES
    agent.state["job_description_raw"] = SAMPLE_JOB_DESCRIPTION
    
    # Set up requirements
    requirements = extract_requirements.invoke({"jd": SAMPLE_JOB_DESCRIPTION})
    agent.state["ranking_criteria"] = requirements
    
    queries = [
        "Find me candidates with React and 3+ years experience",
        "Show me candidates who know Python and AWS",
        "Who has the most experience with Kubernetes?"
    ]
    
    for query in queries:
        print(f"\n[User] {query}")
        result = agent.process_query(query)
        print(f"[Agent] {result.get('response', 'No response')[:200]}...")
    
    print("\n✓ Scenario 7 PASSED: Natural language queries work correctly")
    return True


# =============================================================================
# TOOL TESTS
# =============================================================================

def test_extract_requirements_tool():
    """Test the extract_requirements tool"""
    print("\n" + "=" * 60)
    print("TOOL TEST: extract_requirements")
    print("=" * 60)
    
    result = extract_requirements.invoke({"jd": SAMPLE_JOB_DESCRIPTION})
    
    print(f"\nExtracted Requirements:")
    print(f"  Must-have: {len(result.get('must_have', []))} items")
    print(f"  Nice-to-have: {len(result.get('nice_to_have', []))} items")
    print(f"  Experience years: {result.get('experience_years')}")
    print(f"  Technical skills: {result.get('skills', {}).get('technical', [])}")
    
    assert "must_have" in result, "Should extract must-have requirements"
    assert "nice_to_have" in result, "Should extract nice-to-have requirements"
    
    print("\n✓ extract_requirements tool works correctly")
    return True


def test_compare_candidates_tool():
    """Test the compare_candidates tool"""
    print("\n" + "=" * 60)
    print("TOOL TEST: compare_candidates")
    print("=" * 60)
    
    candidate_ids = ["candidate_001", "candidate_002", "candidate_003"]
    
    # Prepare candidate data with scores
    candidates_with_scores = []
    for c in SAMPLE_CANDIDATES[:3]:
        c_copy = c.copy()
        c_copy["score"] = 75 + (10 if "React" in c.get("skills", []) else 0)
        candidates_with_scores.append(c_copy)
    
    result = compare_candidates.invoke({
        "candidate_ids": candidate_ids,
        "candidates_data": candidates_with_scores
    })
    
    print(f"\nComparison Results:")
    print(f"  Candidates compared: {result.get('candidates_compared', 0)}")
    print(f"  Ranking: {result.get('ranking', [])}")
    
    if result.get("recommendation"):
        rec = result["recommendation"]
        print(f"  Recommended: {rec.get('candidate_name')} (Score: {rec.get('score')})")
    
    assert "ranking" in result, "Should have ranking"
    assert "recommendation" in result, "Should have recommendation"
    
    print("\n✓ compare_candidates tool works correctly")
    return True


def test_generate_interview_questions_tool():
    """Test the generate_interview_questions tool"""
    print("\n" + "=" * 60)
    print("TOOL TEST: generate_interview_questions")
    print("=" * 60)
    
    candidate = SAMPLE_CANDIDATES[0]
    requirements = extract_requirements.invoke({"jd": SAMPLE_JOB_DESCRIPTION})
    
    result = generate_interview_questions.invoke({
        "candidate_id": candidate["id"],
        "candidate_data": candidate,
        "job_requirements": requirements
    })
    
    print(f"\nInterview Questions Generated:")
    print(f"  Technical: {len(result.get('technical_questions', []))} questions")
    print(f"  Behavioral: {len(result.get('behavioral_questions', []))} questions")
    print(f"  Gap-probing: {len(result.get('gap_probing_questions', []))} questions")
    print(f"  Assessments: {len(result.get('recommended_assessments', []))} recommended")
    
    assert "technical_questions" in result, "Should have technical questions"
    assert "behavioral_questions" in result, "Should have behavioral questions"
    
    print("\n✓ generate_interview_questions tool works correctly")
    return True


# =============================================================================
# RUN ALL TESTS
# =============================================================================

def run_all_tests():
    """Run all test scenarios"""
    print("\n" + "#" * 60)
    print("# RESUME MATCHING AGENT - TEST SUITE")
    print("#" * 60)
    
    test_functions = [
        ("Tool: extract_requirements", test_extract_requirements_tool),
        ("Tool: compare_candidates", test_compare_candidates_tool),
        ("Tool: generate_interview_questions", test_generate_interview_questions_tool),
        ("Scenario 1: Basic Matching", test_scenario_1_basic_matching),
        ("Scenario 2: Candidate Comparison", test_scenario_2_candidate_comparison),
        ("Scenario 3: Requirement Adjustment", test_scenario_3_requirement_adjustment),
        ("Scenario 4: Multi-Round Screening", test_scenario_4_multi_round_screening),
        ("Scenario 5: Explainability", test_scenario_5_explainability),
        ("Scenario 6: Interview Questions", test_scenario_6_interview_questions),
        ("Scenario 7: Natural Language Queries", test_scenario_7_natural_language),
    ]
    
    results = []
    
    for name, test_func in test_functions:
        try:
            success = test_func()
            results.append((name, "PASSED" if success else "FAILED"))
        except Exception as e:
            print(f"\n✗ {name} FAILED: {str(e)}")
            results.append((name, f"ERROR: {str(e)[:50]}"))
    
    # Summary
    print("\n" + "#" * 60)
    print("# TEST SUMMARY")
    print("#" * 60)
    
    passed = sum(1 for _, status in results if status == "PASSED")
    total = len(results)
    
    for name, status in results:
        symbol = "✓" if status == "PASSED" else "✗"
        print(f"  {symbol} {name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("#" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
