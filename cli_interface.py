"""
Command Line Interface for Resume Matching Agent

A simple CLI for interacting with the Resume Matching Agent
without needing Streamlit.
"""

import os
import sys
import json
from typing import Optional

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from matching_agent import ResumeMatchingAgent, AgentConfig, create_agent


class CLIInterface:
    """Command Line Interface for Resume Matching Agent"""
    
    def __init__(self):
        self.agent: Optional[ResumeMatchingAgent] = None
        self.running = True
    
    def print_header(self):
        """Print application header"""
        print("\n" + "=" * 60)
        print("  RESUME MATCHING AGENT - CLI Interface")
        print("=" * 60)
        print("\nCommands:")
        print("  /load <file>   - Load job description from file")
        print("  /paste         - Paste job description (multi-line)")
        print("  /report        - Show current match report")
        print("  /next          - Move to next screening round")
        print("  /interview <id> - Get interview questions for candidate")
        print("  /reset         - Reset and start over")
        print("  /help          - Show this help message")
        print("  /quit          - Exit the application")
        print("\nOr type any natural language query:")
        print("  - 'Find candidates with Python and AWS experience'")
        print("  - 'Compare the top 3 candidates'")
        print("  - 'Why does John rank higher than Jane?'")
        print("-" * 60 + "\n")
    
    def print_results(self, results: dict):
        """Print matching results"""
        shortlist = results.get("shortlist", [])
        
        if not shortlist:
            print("\nNo candidates in shortlist yet.")
            return
        
        print(f"\n{'='*50}")
        print(f"SCREENING ROUND: {results.get('current_round', 'initial').upper()}")
        print(f"{'='*50}")
        print(f"\nTop {len(shortlist)} Candidates:")
        print("-" * 50)
        
        for i, candidate in enumerate(shortlist, 1):
            score = candidate.get("score", 0)
            name = candidate.get("name", "Unknown")
            rec = candidate.get("recommendation", "unknown")
            
            # Recommendation symbol
            if rec == "hire":
                rec_symbol = "★ HIRE"
            elif rec == "maybe":
                rec_symbol = "◐ MAYBE"
            else:
                rec_symbol = "✗ NO"
            
            print(f"\n{i}. {name}")
            print(f"   Score: {score:.1f}/100  [{rec_symbol}]")
            
            strengths = candidate.get("strengths", [])
            if strengths:
                print(f"   Strengths: {', '.join(strengths[:2])}")
            
            gaps = candidate.get("gaps", [])
            if gaps:
                print(f"   Gaps: {', '.join(gaps[:2])}")
        
        print("\n" + "-" * 50)
        
        if results.get("awaiting_feedback"):
            print("\n💡 Provide feedback or ask questions to refine results.")
    
    def load_jd_from_file(self, file_path: str) -> Optional[str]:
        """Load job description from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Error: File not found: {file_path}")
            return None
        except Exception as e:
            print(f"Error reading file: {e}")
            return None
    
    def get_multiline_input(self, prompt: str) -> str:
        """Get multi-line input from user"""
        print(prompt)
        print("(Enter an empty line to finish)")
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
        return "\n".join(lines)
    
    def handle_command(self, command: str) -> bool:
        """Handle a command input. Returns False if should exit."""
        parts = command.strip().split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if cmd == "/quit" or cmd == "/exit":
            print("\nGoodbye!")
            return False
        
        elif cmd == "/help":
            self.print_header()
        
        elif cmd == "/reset":
            self.agent = create_agent()
            print("\n✓ Agent reset. Ready for new job description.")
        
        elif cmd == "/load":
            if not args:
                print("Usage: /load <file_path>")
                return True
            
            jd = self.load_jd_from_file(args)
            if jd:
                print(f"\nLoaded job description from: {args}")
                print("Starting matching process...")
                self.agent = create_agent()
                results = self.agent.start_matching(jd)
                self.print_results(results)
        
        elif cmd == "/paste":
            jd = self.get_multiline_input("\nPaste job description:")
            if jd.strip():
                print("\nStarting matching process...")
                self.agent = create_agent()
                results = self.agent.start_matching(jd)
                self.print_results(results)
            else:
                print("No job description provided.")
        
        elif cmd == "/report":
            if not self.agent:
                print("No matching in progress. Load a job description first.")
            else:
                report = self.agent.get_report()
                print("\n" + report)
        
        elif cmd == "/next":
            if not self.agent:
                print("No matching in progress. Load a job description first.")
            else:
                result = self.agent.process_query("proceed to next round")
                print("\n" + result.get("response", "Moving to next round..."))
                self.print_results(self.agent._get_results())
        
        elif cmd == "/interview":
            if not self.agent:
                print("No matching in progress. Load a job description first.")
            elif not args:
                print("Usage: /interview <candidate_id>")
            else:
                questions = self.agent.get_interview_questions(args)
                self.print_interview_questions(questions)
        
        else:
            print(f"Unknown command: {cmd}")
            print("Type /help for available commands.")
        
        return True
    
    def print_interview_questions(self, questions: dict):
        """Print interview questions"""
        if "error" in questions:
            print(f"\nError: {questions['error']}")
            return
        
        print(f"\n{'='*50}")
        print(f"INTERVIEW QUESTIONS")
        print(f"Candidate: {questions.get('candidate_name', 'Unknown')}")
        print(f"{'='*50}")
        
        # Technical questions
        tech_qs = questions.get("technical_questions", [])
        if tech_qs:
            print("\n📚 Technical Questions:")
            for i, q in enumerate(tech_qs[:3], 1):
                question = q.get("question", str(q)) if isinstance(q, dict) else q
                print(f"  {i}. {question}")
        
        # Behavioral questions
        behav_qs = questions.get("behavioral_questions", [])
        if behav_qs:
            print("\n🤝 Behavioral Questions:")
            for i, q in enumerate(behav_qs[:3], 1):
                question = q.get("question", str(q)) if isinstance(q, dict) else q
                print(f"  {i}. {question}")
        
        # Gap-probing questions
        gap_qs = questions.get("gap_probing_questions", [])
        if gap_qs:
            print("\n🔍 Gap-Probing Questions:")
            for i, q in enumerate(gap_qs[:2], 1):
                question = q.get("question", str(q)) if isinstance(q, dict) else q
                print(f"  {i}. {question}")
        
        print("\n" + "-" * 50)
    
    def handle_query(self, query: str):
        """Handle a natural language query"""
        if not self.agent:
            print("\nNo matching in progress.")
            print("Please load a job description first with /load or /paste")
            return
        
        print("\nProcessing query...")
        result = self.agent.process_query(query)
        
        response = result.get("response", "")
        print(f"\n{response}")
        
        # Update results display if shortlist changed
        if result.get("shortlist"):
            self.print_results(self.agent._get_results())
    
    def run(self):
        """Main run loop"""
        self.print_header()
        
        while self.running:
            try:
                user_input = input("\n> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.startswith("/"):
                    self.running = self.handle_command(user_input)
                else:
                    self.handle_query(user_input)
                    
            except KeyboardInterrupt:
                print("\n\nInterrupted. Type /quit to exit.")
            except EOFError:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")


def main():
    """Main entry point"""
    cli = CLIInterface()
    cli.run()


if __name__ == "__main__":
    main()
