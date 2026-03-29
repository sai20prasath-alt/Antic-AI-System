# Resume Matching Agent

An AI-powered resume matching system built with LangGraph that provides intelligent candidate screening, ranking, and recommendations.

## 📋 Features

### Part A: Agent Architecture
- **LangGraph Workflow**: State-based agent with well-defined nodes and transitions
- **Multi-Stage Processing**: Parse JD → Extract Requirements → Search → Rank → Report → Feedback Loop
- **Tool Integration**: File system, RAG search, requirement extraction, candidate comparison, interview question generation

### Part B: Interactive Features
- **Natural Language Interface**: Accept conversational queries
  - "Find me candidates with React and 3+ years experience"
  - "Compare the top 3 matches side by side"
  - "Why did John rank higher than Jane?"
- **Iterative Refinement**: Adjust requirements mid-conversation with automatic re-ranking

### Part C: Advanced Capabilities
- **Multi-Round Screening**:
  - Initial: Top 10 from 100 resumes
  - Second: Deep analysis of top 10
  - Final: Hire/no-hire recommendations for top 3
- **Explainability**: Detailed match reports with strengths, gaps, and improvement suggestions

## 🏗️ Project Structure

```
resume_matching_agent/
├── matching_agent.py       # Main LangGraph agent implementation
├── agent_state.py          # State definitions and types
├── tools.py                # All tools (file system, RAG, extraction, etc.)
├── chat_interface.py       # Streamlit web interface
├── cli_interface.py        # Command-line interface
├── test_scenarios.py       # 7+ test conversation flows
├── state_machine_diagram.py # Visual diagram generators
├── requirements.txt        # Python dependencies
├── resumes/                # Sample resume data
│   ├── alice_johnson.json
│   ├── bob_smith.json
│   ├── carol_davis.json
│   ├── david_wilson.json
│   └── eva_martinez.json
└── job_descriptions/       # Sample job descriptions
    └── senior_fullstack_developer.md
```

## 🚀 Installation

1. **Clone or create the project directory**

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables** (optional, for LLM features):
   ```bash
   # Windows
   set OPENAI_API_KEY=your_api_key_here
   # Linux/Mac
   export OPENAI_API_KEY=your_api_key_here
   ```

## 💻 Usage

### Option 1: Streamlit Web Interface

```bash
streamlit run chat_interface.py
```

Then open http://localhost:8501 in your browser.

### Option 2: Command Line Interface

```bash
python cli_interface.py
```

Available commands:
- `/load <file>` - Load job description from file
- `/paste` - Paste job description (multi-line)
- `/report` - Show current match report
- `/next` - Move to next screening round
- `/interview <id>` - Get interview questions for candidate
- `/reset` - Reset and start over
- `/help` - Show help message
- `/quit` - Exit

### Option 3: Python API

```python
from matching_agent import create_agent

# Create agent
agent = create_agent()

# Start matching with a job description
job_description = """
Senior Software Engineer
Requirements:
- 5+ years experience
- Python and JavaScript
- React.js and Node.js
"""

results = agent.start_matching(job_description)
print(f"Found {len(results['shortlist'])} candidates")

# Process natural language queries
response = agent.process_query("Compare the top 3 candidates")
print(response['response'])

# Move to next round
response = agent.process_query("Proceed to next round")

# Get interview questions
questions = agent.get_interview_questions("candidate_001")
```

## 📊 State Machine Diagram

```
START → Parse JD → Extract Requirements → Search Resumes → 
Rank Candidates → Generate Report → Human Feedback Loop → END
                                          ↓
                              (Adjust/Re-rank/Next Round)
```

### Multi-Round Screening Flow

```
┌────────────────────────────────────────────────────────┐
│  ROUND 1: INITIAL        100 candidates → Top 10       │
│  ─────────────────────────────────────────────────────│
│  Quick scoring, basic requirements matching            │
└───────────────────────────┬────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────┐
│  ROUND 2: DEEP ANALYSIS   Top 10 → Top 5              │
│  ─────────────────────────────────────────────────────│
│  Detailed skill matching, comparison                   │
└───────────────────────────┬────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────┐
│  ROUND 3: FINAL          Top 5 → Top 3 + Recommendations│
│  ─────────────────────────────────────────────────────│
│  Hire/Maybe/No-hire, interview questions              │
└────────────────────────────────────────────────────────┘
```

Generate visual diagrams:
```bash
python state_machine_diagram.py
```

## 🧪 Testing

Run all test scenarios:
```bash
python test_scenarios.py
```

Test scenarios included:
1. Basic Matching Flow
2. Candidate Comparison
3. Requirement Adjustment
4. Multi-Round Screening
5. Explainability
6. Interview Questions Generation
7. Natural Language Queries

## 🛠️ Tools Available

| Tool | Description |
|------|-------------|
| `read_resume_file` | Read resume files (txt, json, md) |
| `list_resume_directory` | List all resumes in a directory |
| `save_report` | Save reports to file |
| `rag_search_resumes` | Semantic search using RAG |
| `extract_requirements` | Parse must-have vs nice-to-have from JD |
| `compare_candidates` | Head-to-head candidate comparison |
| `generate_interview_questions` | Create tailored screening questions |
| `score_candidate` | Score candidate against requirements |
| `rank_candidates` | Rank multiple candidates |
| `generate_match_report` | Create detailed match reports |

## 📝 Sample Queries

```
# Search queries
"Find me candidates with React and 3+ years experience"
"Show me Python developers with AWS knowledge"

# Comparison queries
"Compare the top 3 matches side by side"
"How does Alice compare to Bob?"

# Explanation queries
"Why did Eva rank higher than Carol?"
"Explain the scoring methodology"

# Adjustment queries
"Add Kubernetes as a must-have requirement"
"Increase weight for AWS experience"

# Control queries
"Proceed to the next screening round"
"Generate interview questions for the top candidate"
```

## 🎥 Demo Video Script

For a 5-6 minute demo video, cover:

1. **Introduction (30 sec)**
   - Overview of the system
   - Problem it solves

2. **Job Description Input (1 min)**
   - Show JD loading
   - Requirement extraction in action

3. **Initial Screening (1 min)**
   - Show candidate search and ranking
   - Explain scoring methodology

4. **Interactive Queries (1.5 min)**
   - Demonstrate comparison queries
   - Show explanation of rankings
   - Adjust requirements and re-rank

5. **Multi-Round Screening (1 min)**
   - Progress through rounds
   - Show deepening analysis

6. **Final Recommendations (1 min)**
   - Final report generation
   - Interview questions
   - Hire/no-hire recommendations

## 📄 License

MIT License

## 🤝 Contributing

Contributions welcome! Please submit pull requests or open issues.
