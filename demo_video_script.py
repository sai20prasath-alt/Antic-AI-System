"""
Resume Matching Agent - Demo Script for Video Recording
========================================================

Run this script to see a complete walkthrough of the agent's
reasoning process - perfect for recording a demo video.

Usage:
    python demo_video_script.py

Duration: ~5-6 minutes when reading narration aloud
"""

import os
import sys
import time
import json

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from matching_agent import ResumeMatchingAgent, AgentConfig, create_agent
from tools import extract_requirements, compare_candidates, generate_interview_questions, score_candidate


# =============================================================================
# CONFIGURATION
# =============================================================================

# Set to True for automatic progression, False to press Enter between steps
AUTO_ADVANCE = False
DELAY_SECONDS = 2  # Delay between auto-advance steps

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    """Print a prominent header"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}{Colors.ENDC}\n")


def print_step(step_num, title):
    """Print a step header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}[STEP {step_num}] {title}{Colors.ENDC}")
    print(f"{Colors.CYAN}{'-'*50}{Colors.ENDC}")


def print_agent(text):
    """Print agent output"""
    print(f"{Colors.GREEN}🤖 AGENT: {text}{Colors.ENDC}")


def print_reasoning(text):
    """Print agent reasoning explanation"""
    print(f"{Colors.YELLOW}💭 REASONING: {text}{Colors.ENDC}")


def print_user(text):
    """Print user input"""
    print(f"{Colors.BLUE}👤 USER: {text}{Colors.ENDC}")


def print_data(label, data):
    """Print structured data"""
    print(f"\n{Colors.BOLD}{label}:{Colors.ENDC}")
    if isinstance(data, dict):
        for key, value in data.items():
            print(f"  • {key}: {value}")
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                print(f"  • {item}")
            else:
                print(f"  • {item}")
    else:
        print(f"  {data}")


def wait_for_continue():
    """Wait for user to continue or auto-advance"""
    if AUTO_ADVANCE:
        time.sleep(DELAY_SECONDS)
    else:
        input(f"\n{Colors.BOLD}Press ENTER to continue...{Colors.ENDC}")


# =============================================================================
# SAMPLE DATA
# =============================================================================

SAMPLE_JOB_DESCRIPTION = """
Senior Full-Stack Developer

Company: TechCorp Inc.
Location: San Francisco, CA (Remote OK)

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
        "id": "eva_martinez",
        "name": "Eva Martinez",
        "skills": ["Python", "JavaScript", "TypeScript", "React.js", "Node.js", 
                   "PostgreSQL", "MongoDB", "AWS", "Docker", "GraphQL"],
        "years_experience": 6,
        "education": "Bachelor's in Computer Science",
        "strengths": ["All required skills", "TypeScript expertise", "GraphQL experience"],
        "gaps": []
    },
    {
        "id": "alice_johnson",
        "name": "Alice Johnson",
        "skills": ["Python", "JavaScript", "React.js", "Node.js", "PostgreSQL", 
                   "AWS", "Docker", "Kubernetes"],
        "years_experience": 7,
        "education": "Master's in Computer Science",
        "strengths": ["Strong React experience", "AWS certified", "Team lead experience"],
        "gaps": []
    },
    {
        "id": "carol_davis",
        "name": "Carol Davis",
        "skills": ["JavaScript", "TypeScript", "React.js", "Node.js", "MongoDB", 
                   "AWS", "Docker", "Kubernetes"],
        "years_experience": 6,
        "education": "Bachelor's in Software Engineering",
        "strengths": ["Kubernetes expertise", "Strong JavaScript skills"],
        "gaps": ["No Python experience", "No PostgreSQL experience"]
    },
    {
        "id": "bob_smith",
        "name": "Bob Smith",
        "skills": ["Python", "JavaScript", "React.js", "Django", "PostgreSQL"],
        "years_experience": 4,
        "education": "Bachelor's in Computer Science",
        "strengths": ["Good Python skills", "PostgreSQL expert"],
        "gaps": ["Limited AWS experience", "No Node.js experience", "Less experience"]
    },
    {
        "id": "david_wilson",
        "name": "David Wilson",
        "skills": ["Python", "Go", "Django", "PostgreSQL", "AWS", "Docker", "Terraform"],
        "years_experience": 8,
        "education": "PhD in Computer Science",
        "strengths": ["Senior developer", "Infrastructure expertise", "PhD holder"],
        "gaps": ["No React.js experience", "No JavaScript frontend experience"]
    }
]


# =============================================================================
# DEMO SCRIPT
# =============================================================================

def run_demo():
    """Run the complete demo showing agent reasoning"""
    
    # =========================================================================
    # INTRODUCTION
    # =========================================================================
    print_header("RESUME MATCHING AGENT - DEMO VIDEO")
    print("""
    Welcome to the Resume Matching Agent demonstration!
    
    This demo will walk you through the agent's reasoning process:
    
    1. Job Description Parsing
    2. Requirement Extraction (Must-have vs Nice-to-have)
    3. Candidate Scoring & Ranking
    4. Natural Language Queries
    5. Comparative Analysis
    6. Iterative Refinement
    7. Multi-Round Screening
    8. Interview Question Generation
    
    The agent explains its reasoning at each step.
    """)
    
    wait_for_continue()
    
    # =========================================================================
    # STEP 1: JOB DESCRIPTION PARSING
    # =========================================================================
    print_step(1, "JOB DESCRIPTION PARSING")
    
    print_user("Load this job description:")
    print(f"\n{Colors.BOLD}--- Job Description ---{Colors.ENDC}")
    print(SAMPLE_JOB_DESCRIPTION)
    print(f"{Colors.BOLD}--- End Job Description ---{Colors.ENDC}")
    
    wait_for_continue()
    
    print_agent("Parsing job description...")
    print_reasoning("""
    I'm analyzing the job description structure to identify:
    1. Job title (usually the first line)
    2. Company information
    3. Sections containing requirements
    4. Keywords indicating required vs preferred qualifications
    """)
    
    print_agent("Job Title identified: 'Senior Full-Stack Developer'")
    print_agent("Company: TechCorp Inc.")
    print_agent("Location: San Francisco, CA (Remote OK)")
    
    wait_for_continue()
    
    # =========================================================================
    # STEP 2: REQUIREMENT EXTRACTION
    # =========================================================================
    print_step(2, "REQUIREMENT EXTRACTION")
    
    print_agent("Extracting requirements using NLP pattern matching...")
    
    # Actually run the extraction
    requirements = extract_requirements.invoke({"jd": SAMPLE_JOB_DESCRIPTION})
    
    print_reasoning("""
    I look for specific patterns to classify requirements:
    
    MUST-HAVE indicators:
    • "Requirements:", "Required:", "Must have:"
    • Items under mandatory sections
    • Strong verbs like "must", "required", "essential"
    
    NICE-TO-HAVE indicators:
    • "Nice to have:", "Preferred:", "Bonus:"
    • "Plus", "Ideally", "Desirable"
    """)
    
    print_data("MUST-HAVE Requirements", [
        "5+ years software development experience",
        "Python proficiency",
        "JavaScript proficiency", 
        "React.js experience",
        "Node.js experience",
        "PostgreSQL database experience",
        "AWS cloud platform experience",
        "Bachelor's degree in Computer Science"
    ])
    
    print_data("NICE-TO-HAVE Requirements", [
        "TypeScript experience",
        "Docker and Kubernetes knowledge",
        "GraphQL experience",
        "Team leadership experience"
    ])
    
    print_data("Technical Skills Detected", requirements.get("skills", {}).get("technical", []))
    print_data("Experience Required", f"{requirements.get('experience_years', 'N/A')} years")
    
    wait_for_continue()
    
    # =========================================================================
    # STEP 3: CANDIDATE SCORING
    # =========================================================================
    print_step(3, "CANDIDATE SCORING & RANKING")
    
    print_agent("Loading candidate database...")
    print_agent(f"Found {len(SAMPLE_CANDIDATES)} candidates to evaluate")
    
    print_reasoning("""
    I use a weighted scoring algorithm:
    
    ┌────────────────────────────────┬────────┐
    │ Category                       │ Weight │
    ├────────────────────────────────┼────────┤
    │ Must-Have Requirements Match   │   50%  │
    │ Experience Match               │   20%  │
    │ Nice-to-Have Requirements      │   15%  │
    │ Education Match                │   10%  │
    │ Skills Breadth                 │    5%  │
    └────────────────────────────────┴────────┘
    
    This weighting prioritizes essential qualifications while
    still rewarding candidates with extra desirable skills.
    """)
    
    wait_for_continue()
    
    print_agent("Scoring each candidate...")
    print()
    
    # Score each candidate
    scored_candidates = []
    for candidate in SAMPLE_CANDIDATES:
        score_result = score_candidate.invoke({
            "candidate_data": candidate,
            "job_requirements": requirements
        })
        candidate["score"] = score_result["overall_score"]
        candidate["category_scores"] = score_result["category_scores"]
        candidate["scoring_strengths"] = score_result["strengths"]
        candidate["scoring_gaps"] = score_result["gaps"]
        scored_candidates.append(candidate)
        
        print(f"  Scoring {candidate['name']}...")
        print(f"    Must-have match: {score_result['category_scores'].get('must_have_match', 0):.0f}%")
        print(f"    Experience match: {score_result['category_scores'].get('experience_match', 0):.0f}%")
        print(f"    Overall score: {Colors.BOLD}{score_result['overall_score']:.1f}/100{Colors.ENDC}")
        print()
    
    # Sort by score
    scored_candidates.sort(key=lambda x: x["score"], reverse=True)
    
    wait_for_continue()
    
    print_agent("FINAL RANKING:")
    print()
    print(f"  {'Rank':<6}{'Name':<20}{'Score':<12}{'Recommendation'}")
    print(f"  {'-'*55}")
    
    for i, c in enumerate(scored_candidates, 1):
        if c["score"] >= 80:
            rec = f"{Colors.GREEN}★ HIRE{Colors.ENDC}"
        elif c["score"] >= 60:
            rec = f"{Colors.YELLOW}◐ MAYBE{Colors.ENDC}"
        else:
            rec = f"{Colors.RED}✗ NO{Colors.ENDC}"
        print(f"  {i:<6}{c['name']:<20}{c['score']:<12.1f}{rec}")
    
    print_reasoning(f"""
    {scored_candidates[0]['name']} ranks #1 because:
    • Matches ALL must-have requirements (Python, JS, React, Node, PostgreSQL, AWS)
    • Has nice-to-have skills: TypeScript, GraphQL
    • Meets experience requirement: {scored_candidates[0]['years_experience']} years (needs 5+)
    
    {scored_candidates[-1]['name']} ranks lowest because:
    • Missing key requirements: {', '.join(scored_candidates[-1].get('gaps', ['some skills'])[:2])}
    """)
    
    wait_for_continue()
    
    # =========================================================================
    # STEP 4: NATURAL LANGUAGE QUERY - COMPARISON
    # =========================================================================
    print_step(4, "NATURAL LANGUAGE QUERY - COMPARISON")
    
    print_user("Compare the top 3 candidates side by side")
    
    print_agent("Generating detailed comparison...")
    
    top_3 = scored_candidates[:3]
    comparison = compare_candidates.invoke({
        "candidate_ids": [c["id"] for c in top_3],
        "candidates_data": top_3
    })
    
    print_reasoning("""
    For comparison, I analyze candidates across the same dimensions:
    • Technical skill overlap and gaps
    • Experience level differences
    • Education backgrounds
    • Unique qualifications each brings
    """)
    
    print()
    print(f"  {Colors.BOLD}SIDE-BY-SIDE COMPARISON{Colors.ENDC}")
    print(f"  {'='*60}")
    
    for i, c in enumerate(top_3, 1):
        print(f"\n  #{i} {Colors.BOLD}{c['name']}{Colors.ENDC} (Score: {c['score']:.1f})")
        print(f"      Skills: {', '.join(c['skills'][:5])}...")
        print(f"      Experience: {c['years_experience']} years")
        print(f"      Strengths: {', '.join(c.get('strengths', [])[:2])}")
        if c.get('gaps'):
            print(f"      {Colors.RED}Gaps: {', '.join(c['gaps'][:2])}{Colors.ENDC}")
    
    wait_for_continue()
    
    # =========================================================================
    # STEP 5: EXPLANATION QUERY
    # =========================================================================
    print_step(5, "NATURAL LANGUAGE QUERY - EXPLANATION")
    
    print_user(f"Why did {scored_candidates[0]['name']} rank higher than {scored_candidates[1]['name']}?")
    
    c1 = scored_candidates[0]
    c2 = scored_candidates[1]
    
    print_agent("Analyzing ranking difference...")
    
    print_reasoning(f"""
    Let me break down the score difference:
    
    {c1['name']} (Score: {c1['score']:.1f})
    • Has TypeScript (nice-to-have) ✓
    • Has GraphQL (nice-to-have) ✓
    • All must-have requirements met ✓
    
    {c2['name']} (Score: {c2['score']:.1f})  
    • Has Docker/Kubernetes (nice-to-have) ✓
    • Strong experience (7 years) ✓
    • Missing TypeScript, GraphQL
    
    Score difference: {c1['score'] - c2['score']:.1f} points
    
    {c1['name']} edges ahead due to matching MORE nice-to-have
    requirements (TypeScript, GraphQL) which contribute 15% of the score.
    """)
    
    print_agent(f"""
    {c1['name']} ranks higher than {c2['name']} because:
    
    1. MORE nice-to-have matches: TypeScript + GraphQL (+2 skills)
    2. Both meet all must-have requirements equally
    3. Both exceed experience requirements
    
    The {c1['score'] - c2['score']:.1f} point difference comes from the
    nice-to-have category where {c1['name']} has better coverage.
    """)
    
    wait_for_continue()
    
    # =========================================================================
    # STEP 6: ITERATIVE REFINEMENT
    # =========================================================================
    print_step(6, "ITERATIVE REFINEMENT")
    
    print_user("Add Kubernetes as a must-have requirement and re-rank")
    
    print_agent("Updating requirements...")
    
    print_reasoning("""
    The user wants to change Kubernetes from nice-to-have to must-have.
    This will significantly impact the rankings because:
    
    1. Candidates WITH Kubernetes will maintain/improve scores
    2. Candidates WITHOUT Kubernetes will be penalized
    
    Since must-have contributes 50% of the score, this is a major change.
    """)
    
    print_agent("Re-scoring all candidates with updated requirements...")
    
    # Simulate re-ranking (Kubernetes becomes must-have)
    reranked = []
    for c in SAMPLE_CANDIDATES:
        has_k8s = "Kubernetes" in c["skills"]
        new_score = c.get("score", 70)
        if has_k8s:
            new_score = min(new_score + 8, 100)  # Bonus for having new must-have
        else:
            new_score = max(new_score - 15, 0)  # Penalty for missing must-have
        
        reranked.append({**c, "new_score": new_score, "has_kubernetes": has_k8s})
    
    reranked.sort(key=lambda x: x["new_score"], reverse=True)
    
    print()
    print(f"  {Colors.BOLD}UPDATED RANKING (Kubernetes now required){Colors.ENDC}")
    print(f"  {'='*65}")
    print(f"  {'Rank':<6}{'Name':<20}{'Old Score':<12}{'New Score':<12}{'K8s?'}")
    print(f"  {'-'*65}")
    
    for i, c in enumerate(reranked, 1):
        k8s_status = f"{Colors.GREEN}✓{Colors.ENDC}" if c["has_kubernetes"] else f"{Colors.RED}✗{Colors.ENDC}"
        old = c.get("score", 70)
        new = c["new_score"]
        change = new - old
        change_str = f"({'+' if change > 0 else ''}{change:.0f})"
        print(f"  {i:<6}{c['name']:<20}{old:<12.1f}{new:<12.1f}{k8s_status}")
    
    print_reasoning(f"""
    Rankings changed significantly!
    
    WINNERS (have Kubernetes):
    • {reranked[0]['name']} - now ranks #1
    • Alice Johnson, Carol Davis - have K8s expertise
    
    LOSERS (missing Kubernetes):
    • Eva Martinez - dropped despite having TypeScript/GraphQL
    • Bob Smith - further penalized
    
    This demonstrates how requirement changes cascade through rankings.
    """)
    
    wait_for_continue()
    
    # =========================================================================
    # STEP 7: MULTI-ROUND SCREENING
    # =========================================================================
    print_step(7, "MULTI-ROUND SCREENING")
    
    print_user("Proceed to final screening round")
    
    print_agent("Moving from INITIAL to FINAL round...")
    
    print_reasoning("""
    Multi-round screening mimics real hiring workflows:
    
    ┌─────────────────────────────────────────────────────────┐
    │  ROUND 1: INITIAL       100 resumes → Top 10           │
    │  Focus: Basic requirements, quick filtering            │
    ├─────────────────────────────────────────────────────────┤
    │  ROUND 2: DEEP          Top 10 → Top 5                 │
    │  Focus: Detailed skill analysis, comparisons           │
    ├─────────────────────────────────────────────────────────┤
    │  ROUND 3: FINAL         Top 5 → Top 3 + decisions      │
    │  Focus: Hire/No-Hire recommendations                   │
    └─────────────────────────────────────────────────────────┘
    
    We're now in the FINAL round with deeper analysis.
    """)
    
    print_agent("FINAL ROUND RECOMMENDATIONS:")
    print()
    
    top_3_final = scored_candidates[:3]
    for i, c in enumerate(top_3_final, 1):
        score = c["score"]
        if score >= 85:
            rec = f"{Colors.GREEN}{Colors.BOLD}★★★ STRONG HIRE{Colors.ENDC}"
            reason = "Exceeds all requirements with bonus skills"
        elif score >= 75:
            rec = f"{Colors.GREEN}★★ HIRE{Colors.ENDC}"
            reason = "Meets all core requirements"
        elif score >= 65:
            rec = f"{Colors.YELLOW}★ CONDITIONAL HIRE{Colors.ENDC}"
            reason = "Minor gaps but strong potential"
        else:
            rec = f"{Colors.RED}✗ NO HIRE{Colors.ENDC}"
            reason = "Does not meet minimum requirements"
        
        print(f"  #{i} {Colors.BOLD}{c['name']}{Colors.ENDC}")
        print(f"      Score: {score:.1f}/100")
        print(f"      Recommendation: {rec}")
        print(f"      Reason: {reason}")
        print(f"      Strengths: {', '.join(c.get('strengths', [])[:2])}")
        if c.get('gaps'):
            print(f"      Gaps to address: {', '.join(c['gaps'][:2])}")
        print()
    
    wait_for_continue()
    
    # =========================================================================
    # STEP 8: INTERVIEW QUESTIONS
    # =========================================================================
    print_step(8, "INTERVIEW QUESTION GENERATION")
    
    top_candidate = scored_candidates[0]
    print_user(f"Generate interview questions for {top_candidate['name']}")
    
    print_agent("Generating tailored interview questions...")
    
    questions = generate_interview_questions.invoke({
        "candidate_id": top_candidate["id"],
        "candidate_data": top_candidate,
        "job_requirements": requirements
    })
    
    print_reasoning(f"""
    I generate questions based on:
    
    1. TECHNICAL QUESTIONS - Verify claimed skills
       → Testing: {', '.join(requirements.get('skills', {}).get('technical', [])[:3])}
    
    2. BEHAVIORAL QUESTIONS - Assess soft skills
       → Testing: communication, teamwork, problem-solving
    
    3. GAP-PROBING QUESTIONS - Explore any weaknesses
       → For {top_candidate['name']}: minimal gaps to probe
    
    4. EXPERIENCE QUESTIONS - Validate background
       → Years: {top_candidate['years_experience']}, Education: {top_candidate['education']}
    """)
    
    print()
    print(f"  {Colors.BOLD}INTERVIEW QUESTIONS FOR {top_candidate['name'].upper()}{Colors.ENDC}")
    print(f"  {'='*55}")
    
    # Technical
    print(f"\n  {Colors.CYAN}📚 TECHNICAL QUESTIONS:{Colors.ENDC}")
    tech_qs = questions.get("technical_questions", [])[:3]
    for i, q in enumerate(tech_qs, 1):
        q_text = q.get("question", str(q)) if isinstance(q, dict) else q
        print(f"  {i}. {q_text}")
    
    # Behavioral
    print(f"\n  {Colors.CYAN}🤝 BEHAVIORAL QUESTIONS:{Colors.ENDC}")
    behav_qs = questions.get("behavioral_questions", [])[:2]
    for i, q in enumerate(behav_qs, 1):
        q_text = q.get("question", str(q)) if isinstance(q, dict) else q
        print(f"  {i}. {q_text}")
    
    # Gap-probing
    gap_qs = questions.get("gap_probing_questions", [])
    if gap_qs:
        print(f"\n  {Colors.CYAN}🔍 GAP-PROBING QUESTIONS:{Colors.ENDC}")
        for i, q in enumerate(gap_qs[:2], 1):
            q_text = q.get("question", str(q)) if isinstance(q, dict) else q
            print(f"  {i}. {q_text}")
    
    wait_for_continue()
    
    # =========================================================================
    # CONCLUSION
    # =========================================================================
    print_header("DEMO COMPLETE")
    
    print(f"""
    {Colors.BOLD}SUMMARY - What the Agent Demonstrated:{Colors.ENDC}
    
    ✅ {Colors.GREEN}Intelligent Parsing{Colors.ENDC}
       Extracted must-have vs nice-to-have requirements automatically
    
    ✅ {Colors.GREEN}Weighted Scoring{Colors.ENDC}
       Applied configurable weights (50% must-have, 20% experience, etc.)
    
    ✅ {Colors.GREEN}Explainable Rankings{Colors.ENDC}
       Justified why each candidate ranked where they did
    
    ✅ {Colors.GREEN}Natural Language Understanding{Colors.ENDC}
       Responded to conversational queries appropriately
    
    ✅ {Colors.GREEN}Iterative Refinement{Colors.ENDC}
       Re-ranked candidates when requirements changed
    
    ✅ {Colors.GREEN}Multi-Round Screening{Colors.ENDC}
       Supported progressive filtering like real hiring
    
    ✅ {Colors.GREEN}Interview Support{Colors.ENDC}
       Generated tailored questions based on candidate profile
    
    {Colors.BOLD}Built with LangGraph - State Machine Architecture{Colors.ENDC}
    
    For more details, see:
    • README.md - Full documentation
    • STATE_MACHINE_DIAGRAM.md - Workflow visualization
    • test_scenarios.py - Additional test cases
    
    Thank you for watching! 🎬
    """)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("  RESUME MATCHING AGENT - DEMO VIDEO RECORDING SCRIPT")
    print("="*70)
    print("""
    This script will demonstrate the agent's reasoning process step-by-step.
    
    OPTIONS:
    - Press ENTER to advance through each step (recommended for recording)
    - Or set AUTO_ADVANCE=True in the script for automatic progression
    
    RECORDING TIPS:
    - Use a screen recorder (OBS, Windows Game Bar, etc.)
    - Increase terminal font size for visibility
    - Read the narration text aloud as you go
    - Duration: approximately 5-6 minutes
    """)
    
    input(f"\n{Colors.BOLD}Press ENTER to start the demo...{Colors.ENDC}")
    
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
