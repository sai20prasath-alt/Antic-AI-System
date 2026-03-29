"""
State Machine Diagram Generator for Resume Matching Agent

Generates visual representation of the agent workflow using:
1. Mermaid diagram (markdown compatible)
2. ASCII diagram
3. Graphviz DOT format
"""

import os

def generate_mermaid_diagram() -> str:
    """Generate Mermaid diagram of the agent workflow"""
    
    diagram = """
```mermaid
stateDiagram-v2
    [*] --> ParseJD: Start
    
    ParseJD --> ExtractRequirements: JD Parsed
    
    ExtractRequirements --> SearchResumes: Requirements Extracted
    
    SearchResumes --> RankCandidates: Candidates Found
    
    RankCandidates --> GenerateReport: Candidates Ranked
    
    GenerateReport --> HumanFeedback: Initial/Second Round
    GenerateReport --> End: Final Round
    
    HumanFeedback --> ProcessFeedback: Feedback Received
    
    ProcessFeedback --> ExtractRequirements: Adjust Requirements
    ProcessFeedback --> RankCandidates: Re-rank
    ProcessFeedback --> GenerateReport: Next Round
    ProcessFeedback --> End: Complete
    
    End --> [*]
    
    note right of ParseJD
        Analyze job description
        Extract title, company, summary
    end note
    
    note right of ExtractRequirements
        Must-have vs Nice-to-have
        Skills, experience, education
    end note
    
    note right of SearchResumes
        RAG-based search
        Semantic matching
    end note
    
    note right of RankCandidates
        Score candidates
        Create shortlist
    end note
    
    note right of GenerateReport
        Detailed match reports
        Interview questions
        Recommendations
    end note
    
    note right of HumanFeedback
        Wait for user input
        Natural language queries
    end note
```
"""
    return diagram


def generate_ascii_diagram() -> str:
    """Generate ASCII art diagram of the workflow"""
    
    diagram = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                     RESUME MATCHING AGENT - STATE MACHINE                     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║   ┌─────────────────────────────────────────────────────────────────────┐   ║
║   │                              START                                  │   ║
║   └────────────────────────────────┬────────────────────────────────────┘   ║
║                                    │                                        ║
║                                    ▼                                        ║
║   ┌─────────────────────────────────────────────────────────────────────┐   ║
║   │                           PARSE JD                                  │   ║
║   │    • Analyze job description text                                   │   ║
║   │    • Extract title, company, summary                                │   ║
║   └────────────────────────────────┬────────────────────────────────────┘   ║
║                                    │                                        ║
║                                    ▼                                        ║
║   ┌─────────────────────────────────────────────────────────────────────┐   ║
║   │                     EXTRACT REQUIREMENTS                            │   ║
║   │    • Parse must-have requirements                                   │   ║
║   │    • Parse nice-to-have requirements                                │   ║
║   │    • Identify skills, experience, education                         │   ║
║   └────────────────────────────────┬────────────────────────────────────┘   ║
║                                    │                                        ║
║                                    ▼                                        ║
║   ┌─────────────────────────────────────────────────────────────────────┐   ║
║   │                        SEARCH RESUMES                               │   ║
║   │    • RAG-based semantic search                                      │   ║
║   │    • Load candidates from directory                                 │   ║
║   │    • Initial: 100 candidates → Second: 10 → Final: 5               │   ║
║   └────────────────────────────────┬────────────────────────────────────┘   ║
║                                    │                                        ║
║                                    ▼                                        ║
║   ┌─────────────────────────────────────────────────────────────────────┐   ║
║   │                       RANK CANDIDATES                               │   ║
║   │    • Score against requirements                                     │   ║
║   │    • Weighted scoring (must-have: 50%, experience: 20%, etc.)      │   ║
║   │    • Create shortlist                                               │   ║
║   └────────────────────────────────┬────────────────────────────────────┘   ║
║                                    │                                        ║
║                                    ▼                                        ║
║   ┌─────────────────────────────────────────────────────────────────────┐   ║
║   │                      GENERATE REPORT                                │   ║
║   │    • Create detailed match reports                                  │   ║
║   │    • Generate interview questions                                   │   ║
║   │    • Provide hire/maybe/no-hire recommendations                    │   ║
║   └────────────────────────────────┬────────────────────────────────────┘   ║
║                                    │                                        ║
║                      ┌─────────────┴─────────────┐                          ║
║                      │     Round Check           │                          ║
║                      │  Final Round?             │                          ║
║                      └─────────────┬─────────────┘                          ║
║                            No │          │ Yes                              ║
║                               ▼          ▼                                  ║
║   ┌────────────────────────────────┐    ┌─────────────────────────────┐    ║
║   │        HUMAN FEEDBACK          │    │           END               │    ║
║   │  • Wait for user input         │    │   • Complete matching       │    ║
║   │  • Accept natural language     │    │   • Return final report     │    ║
║   │  • Queries and commands        │    └─────────────────────────────┘    ║
║   └────────────────┬───────────────┘                                       ║
║                    │                                                        ║
║                    ▼                                                        ║
║   ┌─────────────────────────────────────────────────────────────────────┐   ║
║   │                     PROCESS FEEDBACK                                │   ║
║   │    • Analyze user input                                             │   ║
║   │    • Determine action type                                          │   ║
║   └────────────────┬───────────────────────────────────────────────────┘   ║
║                    │                                                        ║
║         ┌─────────┼─────────────────┬─────────────────┐                    ║
║         │         │                 │                 │                    ║
║         ▼         ▼                 ▼                 ▼                    ║
║   ┌──────────┐ ┌───────────┐ ┌────────────┐ ┌───────────────┐             ║
║   │ Adjust   │ │ Re-rank   │ │ Next Round │ │   Complete    │             ║
║   │ Require- │ │ Candidates│ │ (deeper    │ │   (END)       │             ║
║   │ ments    │ │           │ │ analysis)  │ │               │             ║
║   └────┬─────┘ └─────┬─────┘ └─────┬──────┘ └───────────────┘             ║
║        │             │             │                                       ║
║        └──────┬──────┴──────┬──────┘                                       ║
║               │             │                                               ║
║               ▼             │                                               ║
║        [Back to Extract     │                                               ║
║         Requirements]       │                                               ║
║                             ▼                                               ║
║                      [Back to Rank Candidates                               ║
║                       or Generate Report]                                   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝


SCREENING ROUNDS DETAIL:
════════════════════════

┌────────────────────────────────────────────────────────────────────────────┐
│  ROUND 1: INITIAL SCREEN                                                   │
│  ─────────────────────────                                                 │
│  • Input: Up to 100 resumes                                                │
│  • Output: Top 10 candidates                                               │
│  • Focus: Basic requirements match                                         │
│  • Actions: Quick scoring, broad filtering                                 │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────┐
│  ROUND 2: DEEP ANALYSIS                                                    │
│  ─────────────────────────                                                 │
│  • Input: Top 10 from Round 1                                              │
│  • Output: Top 5 candidates                                                │
│  • Focus: Detailed skill matching                                          │
│  • Actions: In-depth scoring, comparison                                   │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────┐
│  ROUND 3: FINAL RECOMMENDATIONS                                            │
│  ──────────────────────────────────                                        │
│  • Input: Top 5 from Round 2                                               │
│  • Output: Top 3 with recommendations                                      │
│  • Focus: Hire/Maybe/No-hire decision                                      │
│  • Actions: Final report, interview questions                              │
└────────────────────────────────────────────────────────────────────────────┘


SUPPORTED QUERIES:
══════════════════

┌─────────────────────────────────────────────────────────────────────┐
│  SEARCH QUERIES                                                     │
│  • "Find candidates with React and 3+ years experience"            │
│  • "Show me Python developers with AWS knowledge"                   │
│  • "Looking for senior developers with leadership experience"       │
├─────────────────────────────────────────────────────────────────────┤
│  COMPARISON QUERIES                                                 │
│  • "Compare the top 3 matches side by side"                        │
│  • "How do Alice and Bob compare?"                                 │
│  • "Give me a detailed comparison"                                 │
├─────────────────────────────────────────────────────────────────────┤
│  EXPLANATION QUERIES                                                │
│  • "Why did John rank higher than Jane?"                           │
│  • "Explain the ranking methodology"                               │
│  • "What are Alice's strengths and weaknesses?"                    │
├─────────────────────────────────────────────────────────────────────┤
│  ADJUSTMENT QUERIES                                                 │
│  • "Add Kubernetes as a must-have requirement"                     │
│  • "Remove the education requirement"                              │
│  • "Increase weight for AWS experience"                            │
├─────────────────────────────────────────────────────────────────────┤
│  CONTROL QUERIES                                                    │
│  • "Proceed to next round"                                         │
│  • "Show me the final report"                                      │
│  • "Generate interview questions for the top candidate"            │
└─────────────────────────────────────────────────────────────────────┘
"""
    return diagram


def generate_graphviz_dot() -> str:
    """Generate Graphviz DOT format diagram"""
    
    dot = """
digraph ResumeMatchingAgent {
    // Graph settings
    graph [
        rankdir=TB
        fontname="Helvetica"
        fontsize=12
        bgcolor="white"
        label="Resume Matching Agent - State Machine"
        labelloc="t"
    ];
    
    node [
        shape=box
        style="rounded,filled"
        fontname="Helvetica"
        fontsize=10
    ];
    
    edge [
        fontname="Helvetica"
        fontsize=9
    ];
    
    // Nodes
    start [label="START" shape=circle fillcolor="#4CAF50" fontcolor="white"];
    
    parse_jd [
        label="Parse JD\\n───────────\\n• Analyze text\\n• Extract title\\n• Create structure"
        fillcolor="#E3F2FD"
    ];
    
    extract_req [
        label="Extract Requirements\\n──────────────────\\n• Must-have items\\n• Nice-to-have items\\n• Skills & experience"
        fillcolor="#E3F2FD"
    ];
    
    search [
        label="Search Resumes\\n────────────────\\n• RAG semantic search\\n• Load from directory\\n• Filter pool"
        fillcolor="#E3F2FD"
    ];
    
    rank [
        label="Rank Candidates\\n──────────────────\\n• Score matching\\n• Weighted criteria\\n• Create shortlist"
        fillcolor="#FFF3E0"
    ];
    
    report [
        label="Generate Report\\n────────────────────\\n• Match reports\\n• Interview Qs\\n• Recommendations"
        fillcolor="#F3E5F5"
    ];
    
    feedback [
        label="Human Feedback\\n──────────────────\\n• Await input\\n• Natural language\\n• Queries/commands"
        fillcolor="#E8F5E9"
    ];
    
    process [
        label="Process Feedback\\n─────────────────────\\n• Analyze input\\n• Determine action"
        fillcolor="#E8F5E9"
    ];
    
    end [label="END" shape=doublecircle fillcolor="#f44336" fontcolor="white"];
    
    // Edges
    start -> parse_jd [label="Begin"];
    parse_jd -> extract_req [label="JD Parsed"];
    extract_req -> search [label="Requirements Ready"];
    search -> rank [label="Candidates Found"];
    rank -> report [label="Ranked"];
    
    // Conditional: Report to Feedback or End
    report -> feedback [label="Initial/Second\\nRound"];
    report -> end [label="Final Round"];
    
    // Feedback loop
    feedback -> process [label="Input Received"];
    
    // Process feedback outcomes
    process -> extract_req [label="Adjust\\nRequirements" style=dashed];
    process -> rank [label="Re-rank" style=dashed];
    process -> report [label="Next Round" style=dashed];
    process -> end [label="Complete"];
    
    // Subgraph for rounds
    subgraph cluster_rounds {
        label="Screening Rounds";
        style=dashed;
        color=gray;
        
        round1 [label="Round 1: Initial\\n100 → 10" shape=ellipse fillcolor="#BBDEFB"];
        round2 [label="Round 2: Deep\\n10 → 5" shape=ellipse fillcolor="#90CAF9"];
        round3 [label="Round 3: Final\\n5 → 3" shape=ellipse fillcolor="#64B5F6"];
        
        round1 -> round2 [style=dotted];
        round2 -> round3 [style=dotted];
    }
}
"""
    return dot


def save_diagram_files(output_dir: str = "."):
    """Save all diagram formats to files"""
    
    # Mermaid diagram (markdown)
    mermaid_path = os.path.join(output_dir, "state_machine_diagram.md")
    with open(mermaid_path, 'w') as f:
        f.write("# Resume Matching Agent - State Machine Diagram\n\n")
        f.write(generate_mermaid_diagram())
        f.write("\n\n## ASCII Representation\n\n```\n")
        f.write(generate_ascii_diagram())
        f.write("\n```\n")
    print(f"Saved Mermaid diagram to: {mermaid_path}")
    
    # Graphviz DOT file
    dot_path = os.path.join(output_dir, "state_machine.dot")
    with open(dot_path, 'w') as f:
        f.write(generate_graphviz_dot())
    print(f"Saved Graphviz DOT file to: {dot_path}")
    
    # ASCII diagram text file
    ascii_path = os.path.join(output_dir, "state_machine_ascii.txt")
    with open(ascii_path, 'w') as f:
        f.write(generate_ascii_diagram())
    print(f"Saved ASCII diagram to: {ascii_path}")
    
    print("\nTo generate image from DOT file:")
    print("  dot -Tpng state_machine.dot -o state_machine.png")
    print("  dot -Tsvg state_machine.dot -o state_machine.svg")


if __name__ == "__main__":
    # Print ASCII diagram to console
    print(generate_ascii_diagram())
    
    # Save all formats
    save_diagram_files()
