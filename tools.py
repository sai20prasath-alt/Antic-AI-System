"""
Tools for Resume Matching Agent

Includes:
1. File system tools (from Milestone 1)
2. RAG search tool (from Milestone 2)
3. Additional tools:
   - extract_requirements: Parse must-have vs nice-to-have
   - compare_candidates: Head-to-head comparison
   - generate_interview_questions: Create screening questions
"""

import os
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
from langchain.tools import tool
from pydantic import BaseModel, Field

# Try to import vector store dependencies
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


# =============================================================================
# FILE SYSTEM TOOLS (Milestone 1)
# =============================================================================

@tool
def read_resume_file(file_path: str) -> str:
    """
    Read a resume file (supports .txt, .json, .md formats).
    
    Args:
        file_path: Path to the resume file
        
    Returns:
        Content of the resume file as string
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File not found at {file_path}"
        
        if path.suffix == '.json':
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return json.dumps(data, indent=2)
        else:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


@tool  
def list_resume_directory(directory_path: str) -> List[str]:
    """
    List all resume files in a directory.
    
    Args:
        directory_path: Path to the directory containing resumes
        
    Returns:
        List of resume file paths
    """
    try:
        path = Path(directory_path)
        if not path.exists():
            return [f"Error: Directory not found at {directory_path}"]
        
        resume_extensions = {'.txt', '.json', '.md', '.pdf', '.docx'}
        files = []
        for f in path.iterdir():
            if f.is_file() and f.suffix.lower() in resume_extensions:
                files.append(str(f))
        return files
    except Exception as e:
        return [f"Error listing directory: {str(e)}"]


@tool
def save_report(file_path: str, content: str) -> str:
    """
    Save a report to a file.
    
    Args:
        file_path: Path where to save the report
        content: Report content to save
        
    Returns:
        Success or error message
    """
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully saved report to {file_path}"
    except Exception as e:
        return f"Error saving report: {str(e)}"


@tool
def load_job_description(file_path: str) -> str:
    """
    Load a job description from a file.
    
    Args:
        file_path: Path to the job description file
        
    Returns:
        Job description content
    """
    return read_resume_file.invoke({"file_path": file_path})


# =============================================================================
# RAG SEARCH TOOL (Milestone 2)
# =============================================================================

class ResumeVectorStore:
    """Simple vector store for resume search using ChromaDB"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.collection_name = "resumes"
        self.client = None
        self.collection = None
        self.embedding_model = None
        self._initialize()
    
    def _initialize(self):
        """Initialize the vector store"""
        if CHROMADB_AVAILABLE:
            self.client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=self.persist_directory,
                anonymized_telemetry=False
            ))
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def add_resume(self, resume_id: str, content: str, metadata: Dict[str, Any] = None):
        """Add a resume to the vector store"""
        if not self.collection or not self.embedding_model:
            return
        
        embedding = self.embedding_model.encode(content).tolist()
        self.collection.add(
            ids=[resume_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[metadata or {}]
        )
    
    def search(self, query: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """Search resumes by semantic similarity"""
        if not self.collection or not self.embedding_model:
            return []
        
        query_embedding = self.embedding_model.encode(query).tolist()
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        search_results = []
        for i, doc_id in enumerate(results['ids'][0]):
            search_results.append({
                'id': doc_id,
                'content': results['documents'][0][i] if results['documents'] else "",
                'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                'distance': results['distances'][0][i] if results['distances'] else 0
            })
        return search_results


# Global vector store instance (will be initialized when needed)
_vector_store: Optional[ResumeVectorStore] = None


def get_vector_store() -> ResumeVectorStore:
    """Get or create the vector store singleton"""
    global _vector_store
    if _vector_store is None:
        _vector_store = ResumeVectorStore()
    return _vector_store


@tool
def rag_search_resumes(query: str, num_results: int = 10) -> List[Dict[str, Any]]:
    """
    Search resumes using RAG (Retrieval Augmented Generation) with semantic similarity.
    
    Args:
        query: Natural language search query (e.g., "React developer with 3+ years experience")
        num_results: Number of results to return (default: 10)
        
    Returns:
        List of matching resume documents with scores
    """
    vector_store = get_vector_store()
    
    # If vector store not available, fall back to keyword search
    if not CHROMADB_AVAILABLE or not SENTENCE_TRANSFORMERS_AVAILABLE:
        return _fallback_keyword_search(query, num_results)
    
    return vector_store.search(query, num_results)


def _fallback_keyword_search(query: str, num_results: int) -> List[Dict[str, Any]]:
    """Fallback keyword-based search when vector store is not available"""
    # This would search through loaded resumes using keyword matching
    # For demo purposes, returns empty list
    return []


@tool
def index_resumes(directory_path: str) -> str:
    """
    Index all resumes in a directory for RAG search.
    
    Args:
        directory_path: Path to directory containing resume files
        
    Returns:
        Status message
    """
    vector_store = get_vector_store()
    files = list_resume_directory.invoke({"directory_path": directory_path})
    
    if isinstance(files, list) and len(files) > 0 and files[0].startswith("Error"):
        return files[0]
    
    indexed = 0
    for file_path in files:
        content = read_resume_file.invoke({"file_path": file_path})
        if not content.startswith("Error"):
            resume_id = Path(file_path).stem
            vector_store.add_resume(
                resume_id=resume_id,
                content=content,
                metadata={"file_path": file_path}
            )
            indexed += 1
    
    return f"Successfully indexed {indexed} resumes"


# =============================================================================
# ADDITIONAL TOOLS
# =============================================================================

@tool
def extract_requirements(jd: str) -> Dict[str, Any]:
    """
    Parse job description to extract must-have vs nice-to-have requirements.
    
    Args:
        jd: Job description text
        
    Returns:
        Dictionary with categorized requirements including:
        - must_have: List of required qualifications
        - nice_to_have: List of preferred qualifications
        - experience_years: Required years of experience
        - skills: Technical and soft skills
        - education: Education requirements
    """
    result = {
        "must_have": [],
        "nice_to_have": [],
        "experience_years": None,
        "skills": {
            "technical": [],
            "soft": []
        },
        "education": None,
        "title": "",
        "summary": ""
    }
    
    # Convert to lowercase for pattern matching
    jd_lower = jd.lower()
    lines = jd.split('\n')
    
    # Extract job title (usually first non-empty line)
    for line in lines:
        if line.strip():
            result["title"] = line.strip()
            break
    
    # Pattern matching for must-have requirements
    must_have_patterns = [
        r"required[:\s]*(.*?)(?=\n\n|\Z)",
        r"requirements?[:\s]*(.*?)(?=\n\n|\Z)",
        r"must\s+have[:\s]*(.*?)(?=\n\n|\Z)",
        r"essential[:\s]*(.*?)(?=\n\n|\Z)",
        r"mandatory[:\s]*(.*?)(?=\n\n|\Z)"
    ]
    
    nice_to_have_patterns = [
        r"nice\s+to\s+have[:\s]*(.*?)(?=\n\n|\Z)",
        r"preferred[:\s]*(.*?)(?=\n\n|\Z)",
        r"bonus[:\s]*(.*?)(?=\n\n|\Z)",
        r"plus[:\s]*(.*?)(?=\n\n|\Z)",
        r"desirable[:\s]*(.*?)(?=\n\n|\Z)"
    ]
    
    # Extract must-have requirements
    for pattern in must_have_patterns:
        matches = re.findall(pattern, jd_lower, re.IGNORECASE | re.DOTALL)
        for match in matches:
            items = _extract_list_items(match)
            result["must_have"].extend(items)
    
    # Extract nice-to-have requirements
    for pattern in nice_to_have_patterns:
        matches = re.findall(pattern, jd_lower, re.IGNORECASE | re.DOTALL)
        for match in matches:
            items = _extract_list_items(match)
            result["nice_to_have"].extend(items)
    
    # Extract experience years
    exp_patterns = [
        r"(\d+)\+?\s*years?\s*(?:of\s+)?experience",
        r"experience[:\s]*(\d+)\+?\s*years?",
        r"minimum\s+(\d+)\s*years?"
    ]
    for pattern in exp_patterns:
        match = re.search(pattern, jd_lower)
        if match:
            result["experience_years"] = int(match.group(1))
            break
    
    # Extract technical skills (common programming keywords)
    tech_keywords = [
        "python", "javascript", "java", "c++", "c#", "ruby", "go", "rust",
        "react", "angular", "vue", "node.js", "django", "flask", "spring",
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
        "sql", "postgresql", "mongodb", "redis", "elasticsearch",
        "git", "ci/cd", "jenkins", "github actions", "agile", "scrum",
        "machine learning", "deep learning", "nlp", "computer vision",
        "rest api", "graphql", "microservices", "data engineering"
    ]
    
    for skill in tech_keywords:
        if skill in jd_lower:
            result["skills"]["technical"].append(skill)
    
    # Extract soft skills
    soft_skills = [
        "communication", "leadership", "teamwork", "problem-solving",
        "analytical", "creative", "self-motivated", "detail-oriented",
        "collaborative", "adaptable"
    ]
    
    for skill in soft_skills:
        if skill in jd_lower:
            result["skills"]["soft"].append(skill)
    
    # Extract education requirements
    edu_patterns = [
        r"(bachelor'?s?|master'?s?|phd|doctorate)\s+(?:degree\s+)?(?:in\s+)?([\w\s]+)",
        r"(bs|ba|ms|ma|mba|phd)\s+(?:in\s+)?([\w\s]+)"
    ]
    for pattern in edu_patterns:
        match = re.search(pattern, jd_lower)
        if match:
            result["education"] = f"{match.group(1)} {match.group(2)}".strip()
            break
    
    # Remove duplicates
    result["must_have"] = list(set(result["must_have"]))
    result["nice_to_have"] = list(set(result["nice_to_have"]))
    result["skills"]["technical"] = list(set(result["skills"]["technical"]))
    result["skills"]["soft"] = list(set(result["skills"]["soft"]))
    
    return result


def _extract_list_items(text: str) -> List[str]:
    """Extract individual items from list-formatted text"""
    items = []
    
    # Split by common list delimiters
    for delimiter in ['\n', '•', '-', '*', ';']:
        if delimiter in text:
            parts = text.split(delimiter)
            for part in parts:
                cleaned = part.strip()
                if cleaned and len(cleaned) > 3:
                    items.append(cleaned)
            return items
    
    # If no delimiters, return the whole text as one item
    if text.strip():
        items.append(text.strip())
    
    return items


@tool
def compare_candidates(candidate_ids: List[str], candidates_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Perform head-to-head comparison of candidates.
    
    Args:
        candidate_ids: List of candidate IDs to compare
        candidates_data: List of candidate data dictionaries with scores and details
        
    Returns:
        Detailed comparison report including:
        - ranking: Ordered list of candidates
        - comparison_matrix: Side-by-side comparison
        - key_differentiators: What sets each candidate apart
        - recommendation: Suggested best candidate with reasoning
    """
    if not candidates_data:
        return {"error": "No candidate data provided"}
    
    # Filter to only requested candidates
    candidates_to_compare = [
        c for c in candidates_data 
        if c.get("id") in candidate_ids or c.get("candidate_id") in candidate_ids
    ]
    
    if not candidates_to_compare:
        return {"error": f"No candidates found matching IDs: {candidate_ids}"}
    
    comparison = {
        "candidates_compared": len(candidates_to_compare),
        "ranking": [],
        "comparison_matrix": [],
        "key_differentiators": {},
        "recommendation": None,
        "detailed_breakdown": []
    }
    
    # Sort by score
    sorted_candidates = sorted(
        candidates_to_compare, 
        key=lambda x: x.get("score", 0), 
        reverse=True
    )
    
    # Build ranking
    for i, candidate in enumerate(sorted_candidates, 1):
        cid = candidate.get("id") or candidate.get("candidate_id", f"Unknown-{i}")
        comparison["ranking"].append({
            "rank": i,
            "id": cid,
            "name": candidate.get("name", "Unknown"),
            "score": candidate.get("score", 0)
        })
    
    # Build comparison matrix
    categories = ["technical_skills", "experience", "education", "soft_skills", "culture_fit"]
    
    for category in categories:
        row = {"category": category}
        for candidate in sorted_candidates:
            cid = candidate.get("id") or candidate.get("candidate_id", "Unknown")
            row[cid] = candidate.get(category, candidate.get("scores", {}).get(category, "N/A"))
        comparison["comparison_matrix"].append(row)
    
    # Identify key differentiators
    for candidate in sorted_candidates:
        cid = candidate.get("id") or candidate.get("candidate_id", "Unknown")
        strengths = candidate.get("strengths", [])
        gaps = candidate.get("gaps", [])
        
        comparison["key_differentiators"][cid] = {
            "strengths": strengths[:3] if strengths else ["Data not available"],
            "gaps": gaps[:3] if gaps else ["Data not available"],
            "unique_qualifications": candidate.get("unique_qualifications", [])
        }
    
    # Generate recommendation
    if sorted_candidates:
        top_candidate = sorted_candidates[0]
        top_id = top_candidate.get("id") or top_candidate.get("candidate_id", "Unknown")
        
        comparison["recommendation"] = {
            "candidate_id": top_id,
            "candidate_name": top_candidate.get("name", "Unknown"),
            "score": top_candidate.get("score", 0),
            "reasoning": _generate_recommendation_reasoning(top_candidate, sorted_candidates[1:] if len(sorted_candidates) > 1 else [])
        }
    
    return comparison


def _generate_recommendation_reasoning(top: Dict, others: List[Dict]) -> str:
    """Generate reasoning for why top candidate is recommended"""
    reasons = []
    
    score = top.get("score", 0)
    if score >= 90:
        reasons.append("Excellent overall match score")
    elif score >= 75:
        reasons.append("Strong overall match score")
    
    strengths = top.get("strengths", [])
    if strengths:
        reasons.append(f"Key strengths: {', '.join(strengths[:3])}")
    
    if others:
        score_diff = score - others[0].get("score", 0)
        if score_diff > 10:
            reasons.append(f"Significantly outscores next candidate by {score_diff:.1f} points")
    
    gaps = top.get("gaps", [])
    if not gaps:
        reasons.append("No significant gaps identified")
    elif len(gaps) <= 2:
        reasons.append("Minimal gaps that can be addressed through training")
    
    return "; ".join(reasons) if reasons else "Highest scoring candidate based on requirements match"


@tool
def generate_interview_questions(
    candidate_id: str, 
    candidate_data: Dict[str, Any],
    job_requirements: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate tailored screening questions for a specific candidate.
    
    Args:
        candidate_id: ID of the candidate
        candidate_data: Candidate's resume data and match analysis
        job_requirements: Parsed job requirements
        
    Returns:
        Set of interview questions including:
        - technical_questions: Skills verification questions
        - behavioral_questions: Soft skills and culture fit
        - gap_probing_questions: Questions about identified gaps
        - experience_questions: Questions about specific experiences
    """
    questions = {
        "candidate_id": candidate_id,
        "candidate_name": candidate_data.get("name", "Unknown"),
        "technical_questions": [],
        "behavioral_questions": [],
        "gap_probing_questions": [],
        "experience_questions": [],
        "recommended_assessments": []
    }
    
    # Get candidate info
    skills = candidate_data.get("skills", [])
    experience = candidate_data.get("experience", [])
    gaps = candidate_data.get("gaps", [])
    strengths = candidate_data.get("strengths", [])
    
    # Get job requirements
    must_have = job_requirements.get("must_have", [])
    nice_to_have = job_requirements.get("nice_to_have", [])
    required_skills = job_requirements.get("skills", {}).get("technical", [])
    
    # Generate technical questions based on required skills
    technical_templates = [
        "Can you describe a project where you used {skill} extensively?",
        "What are the key differences between {skill} and alternative approaches?",
        "How would you solve [specific problem] using {skill}?",
        "What best practices do you follow when working with {skill}?",
        "Can you walk me through your experience with {skill}?"
    ]
    
    for skill in required_skills[:5]:
        template = technical_templates[len(questions["technical_questions"]) % len(technical_templates)]
        questions["technical_questions"].append({
            "question": template.format(skill=skill),
            "skill_tested": skill,
            "expected_topics": [skill, "problem-solving", "best practices"]
        })
    
    # Generate behavioral questions
    behavioral_templates = [
        {
            "question": "Tell me about a time when you had to quickly learn a new technology to meet a project deadline.",
            "competency": "adaptability",
            "follow_up": "What was your learning approach?"
        },
        {
            "question": "Describe a situation where you disagreed with a team member about a technical approach. How did you resolve it?",
            "competency": "collaboration",
            "follow_up": "What was the outcome?"
        },
        {
            "question": "Can you give an example of when you had to meet a tight deadline? How did you prioritize your work?",
            "competency": "time management",
            "follow_up": "What would you do differently?"
        },
        {
            "question": "Tell me about a project that failed or didn't meet expectations. What did you learn?",
            "competency": "self-awareness",
            "follow_up": "How have you applied those lessons?"
        },
        {
            "question": "Describe a time when you had to explain a complex technical concept to a non-technical stakeholder.",
            "competency": "communication",
            "follow_up": "How did you ensure they understood?"
        }
    ]
    
    questions["behavioral_questions"] = behavioral_templates[:4]
    
    # Generate gap-probing questions based on identified gaps
    for gap in gaps[:3]:
        gap_lower = gap.lower()
        
        if "experience" in gap_lower or "years" in gap_lower:
            questions["gap_probing_questions"].append({
                "gap": gap,
                "question": f"We noticed {gap}. Can you describe how your existing experience has prepared you to handle this requirement?",
                "intent": "Assess transferable skills and growth potential"
            })
        elif any(skill in gap_lower for skill in ["python", "java", "react", "aws"]):
            questions["gap_probing_questions"].append({
                "gap": gap,
                "question": f"Regarding {gap}, what's your plan for getting up to speed? Do you have any related experience?",
                "intent": "Assess learning ability and related skills"
            })
        else:
            questions["gap_probing_questions"].append({
                "gap": gap,
                "question": f"We're looking for someone with {gap}. While your resume doesn't highlight this, do you have any relevant experience?",
                "intent": "Uncover hidden relevant experience"
            })
    
    # Generate experience-specific questions based on resume
    for exp in experience[:3]:
        role = exp.get("title", exp.get("role", "your previous role"))
        company = exp.get("company", "your previous company")
        questions["experience_questions"].append({
            "question": f"In your role as {role} at {company}, what was your biggest technical achievement?",
            "context": exp,
            "follow_up": "What challenges did you face and how did you overcome them?"
        })
    
    # Recommend assessments based on role requirements
    if any(skill in required_skills for skill in ["python", "java", "javascript", "c++", "coding"]):
        questions["recommended_assessments"].append({
            "type": "coding_assessment",
            "description": "Live coding or take-home coding challenge",
            "focus": required_skills[:3]
        })
    
    if "leadership" in str(job_requirements).lower() or "manager" in str(job_requirements).lower():
        questions["recommended_assessments"].append({
            "type": "case_study",
            "description": "Team leadership scenario analysis",
            "focus": ["decision making", "team management", "conflict resolution"]
        })
    
    if any(skill in required_skills for skill in ["aws", "azure", "gcp", "devops", "infrastructure"]):
        questions["recommended_assessments"].append({
            "type": "system_design",
            "description": "Architecture design discussion",
            "focus": ["scalability", "reliability", "cloud architecture"]
        })
    
    return questions


# =============================================================================
# SCORING AND RANKING TOOLS
# =============================================================================

@tool
def score_candidate(
    candidate_data: Dict[str, Any],
    job_requirements: Dict[str, Any],
    weights: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Score a candidate against job requirements.
    
    Args:
        candidate_data: Candidate's resume information
        job_requirements: Parsed job requirements
        weights: Optional custom scoring weights
        
    Returns:
        Detailed scoring breakdown
    """
    default_weights = {
        "must_have_match": 0.50,
        "nice_to_have_match": 0.15,
        "experience_match": 0.20,
        "education_match": 0.10,
        "skills_breadth": 0.05
    }
    weights = weights or default_weights
    
    scores = {
        "overall_score": 0,
        "category_scores": {},
        "must_have_breakdown": {},
        "nice_to_have_breakdown": {},
        "strengths": [],
        "gaps": []
    }
    
    candidate_text = json.dumps(candidate_data).lower()
    candidate_skills = [s.lower() for s in candidate_data.get("skills", [])]
    
    # Score must-have requirements
    must_have = job_requirements.get("must_have", [])
    must_have_score = 0
    for req in must_have:
        req_lower = req.lower()
        matched = req_lower in candidate_text or any(req_lower in skill for skill in candidate_skills)
        scores["must_have_breakdown"][req] = matched
        if matched:
            must_have_score += 1
            scores["strengths"].append(f"Has required: {req}")
        else:
            scores["gaps"].append(f"Missing required: {req}")
    
    if must_have:
        scores["category_scores"]["must_have_match"] = (must_have_score / len(must_have)) * 100
    else:
        scores["category_scores"]["must_have_match"] = 100
    
    # Score nice-to-have requirements
    nice_to_have = job_requirements.get("nice_to_have", [])
    nice_to_have_score = 0
    for req in nice_to_have:
        req_lower = req.lower()
        matched = req_lower in candidate_text or any(req_lower in skill for skill in candidate_skills)
        scores["nice_to_have_breakdown"][req] = matched
        if matched:
            nice_to_have_score += 1
            scores["strengths"].append(f"Has preferred: {req}")
    
    if nice_to_have:
        scores["category_scores"]["nice_to_have_match"] = (nice_to_have_score / len(nice_to_have)) * 100
    else:
        scores["category_scores"]["nice_to_have_match"] = 100
    
    # Score experience match
    required_years = job_requirements.get("experience_years", 0)
    candidate_years = candidate_data.get("years_experience", 0)
    
    if required_years > 0:
        exp_ratio = min(candidate_years / required_years, 1.5)  # Cap at 150%
        scores["category_scores"]["experience_match"] = min(exp_ratio * 100, 100)
        if candidate_years >= required_years:
            scores["strengths"].append(f"Meets experience requirement: {candidate_years}+ years")
        else:
            scores["gaps"].append(f"Experience gap: Has {candidate_years} years, needs {required_years}")
    else:
        scores["category_scores"]["experience_match"] = 100
    
    # Score education match
    required_edu = job_requirements.get("education", "").lower()
    candidate_edu = candidate_data.get("education", "").lower()
    
    edu_levels = ["high school", "associate", "bachelor", "master", "phd", "doctorate"]
    req_level = next((i for i, e in enumerate(edu_levels) if e in required_edu), -1)
    cand_level = next((i for i, e in enumerate(edu_levels) if e in candidate_edu), -1)
    
    if req_level >= 0 and cand_level >= 0:
        if cand_level >= req_level:
            scores["category_scores"]["education_match"] = 100
            scores["strengths"].append(f"Meets education requirement")
        else:
            scores["category_scores"]["education_match"] = (cand_level / req_level) * 100
            scores["gaps"].append(f"Education gap: Has {edu_levels[cand_level]}, needs {edu_levels[req_level]}")
    else:
        scores["category_scores"]["education_match"] = 100
    
    # Score skills breadth
    required_skills = job_requirements.get("skills", {}).get("technical", [])
    skills_matched = sum(1 for s in required_skills if s.lower() in candidate_text)
    if required_skills:
        scores["category_scores"]["skills_breadth"] = (skills_matched / len(required_skills)) * 100
    else:
        scores["category_scores"]["skills_breadth"] = 100
    
    # Calculate overall weighted score
    total_score = 0
    for category, weight in weights.items():
        category_score = scores["category_scores"].get(category, 0)
        total_score += category_score * weight
    
    scores["overall_score"] = round(total_score, 2)
    
    return scores


@tool
def rank_candidates(
    candidates: List[Dict[str, Any]],
    job_requirements: Dict[str, Any],
    top_n: int = 10
) -> List[Dict[str, Any]]:
    """
    Rank multiple candidates against job requirements.
    
    Args:
        candidates: List of candidate data dictionaries
        job_requirements: Parsed job requirements
        top_n: Number of top candidates to return
        
    Returns:
        Ranked list of candidates with scores
    """
    scored_candidates = []
    
    for candidate in candidates:
        score_result = score_candidate.invoke({
            "candidate_data": candidate,
            "job_requirements": job_requirements
        })
        
        scored_candidates.append({
            **candidate,
            "score": score_result["overall_score"],
            "category_scores": score_result["category_scores"],
            "strengths": score_result["strengths"],
            "gaps": score_result["gaps"],
            "must_have_breakdown": score_result["must_have_breakdown"],
            "nice_to_have_breakdown": score_result["nice_to_have_breakdown"]
        })
    
    # Sort by overall score descending
    ranked = sorted(scored_candidates, key=lambda x: x["score"], reverse=True)
    
    # Return top N
    return ranked[:top_n]


# =============================================================================
# REPORT GENERATION TOOLS
# =============================================================================

@tool
def generate_match_report(
    candidate: Dict[str, Any],
    job_requirements: Dict[str, Any],
    include_interview_questions: bool = True
) -> str:
    """
    Generate a detailed match report for a candidate.
    
    Args:
        candidate: Candidate data with scores
        job_requirements: Parsed job requirements
        include_interview_questions: Whether to include interview questions
        
    Returns:
        Formatted match report as string
    """
    report = []
    report.append("=" * 60)
    report.append(f"CANDIDATE MATCH REPORT")
    report.append("=" * 60)
    report.append("")
    
    # Basic info
    report.append(f"Candidate: {candidate.get('name', 'Unknown')}")
    report.append(f"ID: {candidate.get('id', candidate.get('candidate_id', 'N/A'))}")
    report.append(f"Overall Match Score: {candidate.get('score', 0):.1f}/100")
    report.append("")
    
    # Category scores
    report.append("-" * 40)
    report.append("CATEGORY SCORES")
    report.append("-" * 40)
    for category, score in candidate.get("category_scores", {}).items():
        category_name = category.replace("_", " ").title()
        report.append(f"  {category_name}: {score:.1f}%")
    report.append("")
    
    # Strengths
    report.append("-" * 40)
    report.append("STRENGTHS")
    report.append("-" * 40)
    strengths = candidate.get("strengths", [])
    if strengths:
        for s in strengths[:5]:
            report.append(f"  ✓ {s}")
    else:
        report.append("  No specific strengths identified")
    report.append("")
    
    # Gaps
    report.append("-" * 40)
    report.append("GAPS / AREAS FOR DEVELOPMENT")
    report.append("-" * 40)
    gaps = candidate.get("gaps", [])
    if gaps:
        for g in gaps[:5]:
            report.append(f"  ✗ {g}")
    else:
        report.append("  No significant gaps identified")
    report.append("")
    
    # Improvement suggestions for borderline candidates
    score = candidate.get("score", 0)
    if 60 <= score < 80:
        report.append("-" * 40)
        report.append("IMPROVEMENT SUGGESTIONS (Borderline Candidate)")
        report.append("-" * 40)
        for gap in gaps[:3]:
            if "missing" in gap.lower():
                skill = gap.replace("Missing required: ", "").replace("Missing preferred: ", "")
                report.append(f"  → Consider training/certification in: {skill}")
        report.append("")
    
    # Recommendation
    report.append("-" * 40)
    report.append("RECOMMENDATION")
    report.append("-" * 40)
    if score >= 80:
        report.append("  ★ HIRE - Strong match for the position")
    elif score >= 60:
        report.append("  ◐ MAYBE - Consider for further evaluation")
    else:
        report.append("  ✗ NO HIRE - Does not meet minimum requirements")
    report.append("")
    
    # Interview questions
    if include_interview_questions:
        questions = generate_interview_questions.invoke({
            "candidate_id": candidate.get("id", "unknown"),
            "candidate_data": candidate,
            "job_requirements": job_requirements
        })
        
        report.append("-" * 40)
        report.append("RECOMMENDED INTERVIEW QUESTIONS")
        report.append("-" * 40)
        
        # Technical questions
        report.append("\nTechnical Questions:")
        for q in questions.get("technical_questions", [])[:3]:
            report.append(f"  • {q.get('question', q) if isinstance(q, dict) else q}")
        
        # Gap-probing questions
        if questions.get("gap_probing_questions"):
            report.append("\nGap-Probing Questions:")
            for q in questions["gap_probing_questions"][:2]:
                report.append(f"  • {q.get('question', q) if isinstance(q, dict) else q}")
    
    report.append("")
    report.append("=" * 60)
    report.append(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 60)
    
    return "\n".join(report)


# =============================================================================
# TOOL DEFINITIONS FOR LANGGRAPH
# =============================================================================

# List of all tools for LangGraph agent
ALL_TOOLS = [
    read_resume_file,
    list_resume_directory,
    save_report,
    load_job_description,
    rag_search_resumes,
    index_resumes,
    extract_requirements,
    compare_candidates,
    generate_interview_questions,
    score_candidate,
    rank_candidates,
    generate_match_report
]


def get_tool_by_name(name: str):
    """Get a tool by its name"""
    tools_dict = {tool.name: tool for tool in ALL_TOOLS}
    return tools_dict.get(name)
