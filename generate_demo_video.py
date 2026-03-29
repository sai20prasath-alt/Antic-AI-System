"""
Generate MP4 Demo Video for Resume Matching Agent
==================================================

This script creates an MP4 video showing the agent's reasoning process.

Requirements:
    pip install moviepy pillow numpy

Usage:
    python generate_demo_video.py

Output:
    resume_matching_agent_demo.mp4 (5-6 minutes)
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont
import numpy as np

try:
    from moviepy.editor import (
        ImageClip, TextClip, CompositeVideoClip, 
        concatenate_videoclips, ColorClip
    )
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    print("Installing moviepy...")
    os.system("pip install moviepy pillow numpy")
    try:
        from moviepy.editor import (
            ImageClip, TextClip, CompositeVideoClip, 
            concatenate_videoclips, ColorClip
        )
        MOVIEPY_AVAILABLE = True
    except:
        pass


# =============================================================================
# VIDEO CONFIGURATION
# =============================================================================

VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
FPS = 24
BACKGROUND_COLOR = (15, 23, 42)  # Dark blue
TEXT_COLOR = (226, 232, 240)  # Light gray
ACCENT_COLOR = (56, 189, 248)  # Cyan
SUCCESS_COLOR = (74, 222, 128)  # Green
WARNING_COLOR = (251, 191, 36)  # Yellow
ERROR_COLOR = (248, 113, 113)  # Red

# Font settings
try:
    # Try to use a monospace font
    FONT_PATH = "C:/Windows/Fonts/consola.ttf"  # Consolas on Windows
    if not os.path.exists(FONT_PATH):
        FONT_PATH = "C:/Windows/Fonts/cour.ttf"  # Courier New
    if not os.path.exists(FONT_PATH):
        FONT_PATH = None  # Use default
except:
    FONT_PATH = None


# =============================================================================
# DEMO CONTENT - Each scene with duration
# =============================================================================

SCENES = [
    # Scene 1: Title (5 seconds)
    {
        "duration": 5,
        "title": "RESUME MATCHING AGENT",
        "subtitle": "AI-Powered Candidate Screening with LangGraph",
        "content": [
            "",
            "Demo Video - Agent Reasoning Walkthrough",
            "",
            "Built with: LangGraph, Python, Streamlit",
        ]
    },
    
    # Scene 2: Overview (8 seconds)
    {
        "duration": 8,
        "title": "What This Agent Does",
        "content": [
            "",
            "✓ Parses job descriptions automatically",
            "✓ Extracts must-have vs nice-to-have requirements",
            "✓ Scores and ranks candidates using weighted algorithm",
            "✓ Answers natural language queries",
            "✓ Explains its reasoning at every step",
            "✓ Supports multi-round screening",
            "✓ Generates tailored interview questions",
        ]
    },
    
    # Scene 3: Job Description Input (10 seconds)
    {
        "duration": 10,
        "title": "STEP 1: Job Description Input",
        "content": [
            "┌─────────────────────────────────────────────────────────┐",
            "│  Senior Full-Stack Developer                           │",
            "│  Company: TechCorp Inc.                                │",
            "│                                                        │",
            "│  Requirements:                                         │",
            "│  - 5+ years of software development experience         │",
            "│  - Strong proficiency in Python and JavaScript         │",
            "│  - Experience with React.js and Node.js               │",
            "│  - PostgreSQL database experience                      │",
            "│  - AWS cloud platform experience                       │",
            "│                                                        │",
            "│  Nice to Have:                                         │",
            "│  - TypeScript, Docker, Kubernetes, GraphQL            │",
            "└─────────────────────────────────────────────────────────┘",
        ]
    },
    
    # Scene 4: Requirement Extraction (12 seconds)
    {
        "duration": 12,
        "title": "STEP 2: Requirement Extraction",
        "subtitle": "💭 Agent Reasoning",
        "content": [
            "",
            "🤖 AGENT: Analyzing job description structure...",
            "",
            "I look for specific patterns to classify requirements:",
            "",
            "  MUST-HAVE indicators:",
            "    • 'Requirements:', 'Required:', 'Must have:'",
            "    • Strong verbs: 'must', 'required', 'essential'",
            "",
            "  NICE-TO-HAVE indicators:",
            "    • 'Nice to have:', 'Preferred:', 'Bonus:'",
            "    • 'Plus', 'Ideally', 'Desirable'",
            "",
            "─────────────────────────────────────────────────────────",
            "EXTRACTED: 6 must-have requirements, 4 nice-to-have",
        ]
    },
    
    # Scene 5: Requirements List (10 seconds)
    {
        "duration": 10,
        "title": "Extracted Requirements",
        "content": [
            "",
            "┌─────────────────────────────────────────────────────────┐",
            "│  MUST-HAVE (Required):                                 │",
            "│  ✓ 5+ years software development experience            │",
            "│  ✓ Python proficiency                                  │",
            "│  ✓ JavaScript proficiency                              │",
            "│  ✓ React.js experience                                 │",
            "│  ✓ Node.js experience                                  │",
            "│  ✓ PostgreSQL database experience                      │",
            "│  ✓ AWS cloud platform experience                       │",
            "├─────────────────────────────────────────────────────────┤",
            "│  NICE-TO-HAVE (Preferred):                             │",
            "│  ○ TypeScript experience                               │",
            "│  ○ Docker and Kubernetes knowledge                     │",
            "│  ○ GraphQL experience                                  │",
            "│  ○ Team leadership experience                          │",
            "└─────────────────────────────────────────────────────────┘",
        ]
    },
    
    # Scene 6: Scoring Algorithm (12 seconds)
    {
        "duration": 12,
        "title": "STEP 3: Candidate Scoring",
        "subtitle": "💭 Weighted Scoring Algorithm",
        "content": [
            "",
            "🤖 AGENT: I use a weighted scoring algorithm:",
            "",
            "  ┌────────────────────────────────────┬────────┐",
            "  │ Category                           │ Weight │",
            "  ├────────────────────────────────────┼────────┤",
            "  │ Must-Have Requirements Match       │   50%  │",
            "  │ Experience Match                   │   20%  │",
            "  │ Nice-to-Have Requirements          │   15%  │",
            "  │ Education Match                    │   10%  │",
            "  │ Skills Breadth                     │    5%  │",
            "  └────────────────────────────────────┴────────┘",
            "",
            "This prioritizes essential qualifications while",
            "still rewarding candidates with extra skills.",
        ]
    },
    
    # Scene 7: Candidate Ranking (15 seconds)
    {
        "duration": 15,
        "title": "Candidate Ranking Results",
        "content": [
            "",
            "🤖 AGENT: Scoring complete. Here are the rankings:",
            "",
            "  Rank  Name                Score      Recommendation",
            "  ────────────────────────────────────────────────────",
            "  #1    Eva Martinez        92.0       ★ STRONG HIRE",
            "  #2    Alice Johnson       88.0       ★ HIRE",
            "  #3    Carol Davis         75.0       ◐ MAYBE",
            "  #4    Bob Smith           65.0       ◐ MAYBE",
            "  #5    David Wilson        58.0       ✗ NO HIRE",
            "",
            "💭 REASONING:",
            "  Eva ranks #1 because she matches ALL must-have requirements",
            "  AND has nice-to-have skills: TypeScript, GraphQL",
            "",
            "  David ranks lowest due to missing React.js experience",
            "  (a must-have requirement worth 50% of score)",
        ]
    },
    
    # Scene 8: Comparison Query (12 seconds)
    {
        "duration": 12,
        "title": "STEP 4: Natural Language Query",
        "content": [
            "",
            "👤 USER: Compare the top 3 candidates side by side",
            "",
            "🤖 AGENT: Generating detailed comparison...",
            "",
            "  #1 Eva Martinez (Score: 92.0)",
            "      Skills: Python, JS, React, Node, PostgreSQL, AWS, TS, GraphQL",
            "      Experience: 6 years",
            "      Strengths: All required skills, TypeScript, GraphQL",
            "",
            "  #2 Alice Johnson (Score: 88.0)",
            "      Skills: Python, JS, React, Node, PostgreSQL, AWS, Docker, K8s",
            "      Experience: 7 years",
            "      Strengths: AWS certified, Team lead experience",
            "",
            "  #3 Carol Davis (Score: 75.0)",
            "      Skills: JS, React, Node, MongoDB, AWS, Docker, Kubernetes",
            "      Gaps: No Python, No PostgreSQL",
        ]
    },
    
    # Scene 9: Explanation Query (15 seconds)
    {
        "duration": 15,
        "title": "STEP 5: Explainability",
        "content": [
            "",
            "👤 USER: Why did Eva rank higher than Alice?",
            "",
            "🤖 AGENT: Analyzing ranking difference...",
            "",
            "💭 REASONING:",
            "",
            "  Eva Martinez (Score: 92.0)",
            "    • Has TypeScript (nice-to-have) ✓",
            "    • Has GraphQL (nice-to-have) ✓",
            "    • All must-have requirements met ✓",
            "",
            "  Alice Johnson (Score: 88.0)",
            "    • Has Docker/Kubernetes (nice-to-have) ✓",
            "    • Strong experience: 7 years ✓",
            "    • Missing: TypeScript, GraphQL",
            "",
            "  Score difference: 4 points (from nice-to-have category)",
            "  Eva has MORE nice-to-have matches → higher score",
        ]
    },
    
    # Scene 10: Iterative Refinement (15 seconds)
    {
        "duration": 15,
        "title": "STEP 6: Iterative Refinement",
        "content": [
            "",
            "👤 USER: Add Kubernetes as a must-have requirement",
            "",
            "🤖 AGENT: Updating requirements and re-ranking...",
            "",
            "💭 REASONING:",
            "  Kubernetes changes from nice-to-have → must-have",
            "  This significantly impacts rankings because must-have",
            "  contributes 50% of the total score.",
            "",
            "  UPDATED RANKINGS:",
            "  ────────────────────────────────────────────────────",
            "  Rank  Name              Old Score → New Score   K8s?",
            "  #1    Alice Johnson     88.0      → 96.0        ✓",
            "  #2    Carol Davis       75.0      → 83.0        ✓",
            "  #3    Eva Martinez      92.0      → 77.0        ✗",
            "  #4    Bob Smith         65.0      → 50.0        ✗",
            "",
            "  Alice now ranks #1 because she has Kubernetes!",
        ]
    },
    
    # Scene 11: Multi-Round (12 seconds)
    {
        "duration": 12,
        "title": "STEP 7: Multi-Round Screening",
        "content": [
            "",
            "🤖 AGENT: Supporting progressive screening rounds:",
            "",
            "  ┌─────────────────────────────────────────────────────┐",
            "  │  ROUND 1: INITIAL    100 resumes → Top 10          │",
            "  │  Focus: Basic requirements, quick filtering        │",
            "  ├─────────────────────────────────────────────────────┤",
            "  │  ROUND 2: DEEP       Top 10 → Top 5                │",
            "  │  Focus: Detailed skill matching, comparisons       │",
            "  ├─────────────────────────────────────────────────────┤",
            "  │  ROUND 3: FINAL      Top 5 → Top 3 + Decisions     │",
            "  │  Focus: Hire/No-Hire recommendations               │",
            "  └─────────────────────────────────────────────────────┘",
            "",
            "  This mimics real hiring workflows with increasing depth.",
        ]
    },
    
    # Scene 12: Interview Questions (15 seconds)
    {
        "duration": 15,
        "title": "STEP 8: Interview Question Generation",
        "content": [
            "",
            "👤 USER: Generate interview questions for Eva Martinez",
            "",
            "🤖 AGENT: Generating tailored questions...",
            "",
            "  📚 TECHNICAL QUESTIONS:",
            "  1. Describe a project where you used React extensively?",
            "  2. What best practices do you follow with Node.js?",
            "  3. How would you design a scalable API with AWS?",
            "",
            "  🤝 BEHAVIORAL QUESTIONS:",
            "  1. Tell me about a time you had to learn a new",
            "     technology quickly to meet a deadline.",
            "  2. Describe a situation where you disagreed with a",
            "     team member. How did you resolve it?",
            "",
            "  Questions are specific to candidate's background,",
            "  not generic templates!",
        ]
    },
    
    # Scene 13: Summary (10 seconds)
    {
        "duration": 10,
        "title": "Summary",
        "content": [
            "",
            "What the Resume Matching Agent Demonstrated:",
            "",
            "  ✅ Intelligent Parsing - Must-have vs Nice-to-have",
            "  ✅ Weighted Scoring - 50% must-have, 20% experience...",
            "  ✅ Explainable Rankings - Justifies every decision",
            "  ✅ Natural Language - Conversational queries",
            "  ✅ Iterative Refinement - Re-ranks on requirement changes",
            "  ✅ Multi-Round Screening - Progressive filtering",
            "  ✅ Interview Support - Tailored questions",
            "",
            "Built with LangGraph State Machine Architecture",
        ]
    },
    
    # Scene 14: End (5 seconds)
    {
        "duration": 5,
        "title": "Thank You!",
        "subtitle": "Resume Matching Agent",
        "content": [
            "",
            "GitHub: github.com/your-repo",
            "",
            "Technologies: LangGraph, Python, Streamlit",
            "",
            "Questions? Contact: your-email@example.com",
        ]
    },
]


# =============================================================================
# VIDEO GENERATION FUNCTIONS
# =============================================================================

def create_frame(scene, width=VIDEO_WIDTH, height=VIDEO_HEIGHT):
    """Create a single frame image from scene data"""
    
    # Create image with background
    img = Image.new('RGB', (width, height), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Load fonts
    try:
        if FONT_PATH and os.path.exists(FONT_PATH):
            title_font = ImageFont.truetype(FONT_PATH, 48)
            subtitle_font = ImageFont.truetype(FONT_PATH, 32)
            content_font = ImageFont.truetype(FONT_PATH, 24)
        else:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            content_font = ImageFont.load_default()
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        content_font = ImageFont.load_default()
    
    y_offset = 80
    
    # Draw title
    if "title" in scene:
        title = scene["title"]
        # Center the title
        try:
            bbox = draw.textbbox((0, 0), title, font=title_font)
            title_width = bbox[2] - bbox[0]
        except:
            title_width = len(title) * 25
        x = (width - title_width) // 2
        draw.text((x, y_offset), title, fill=ACCENT_COLOR, font=title_font)
        y_offset += 70
    
    # Draw subtitle
    if "subtitle" in scene:
        subtitle = scene["subtitle"]
        try:
            bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
            sub_width = bbox[2] - bbox[0]
        except:
            sub_width = len(subtitle) * 18
        x = (width - sub_width) // 2
        draw.text((x, y_offset), subtitle, fill=WARNING_COLOR, font=subtitle_font)
        y_offset += 50
    
    y_offset += 20
    
    # Draw content lines
    if "content" in scene:
        for line in scene["content"]:
            # Color code certain lines
            color = TEXT_COLOR
            if line.startswith("✓") or line.startswith("✅"):
                color = SUCCESS_COLOR
            elif line.startswith("✗") or line.startswith("❌"):
                color = ERROR_COLOR
            elif line.startswith("👤"):
                color = ACCENT_COLOR
            elif line.startswith("🤖"):
                color = SUCCESS_COLOR
            elif line.startswith("💭"):
                color = WARNING_COLOR
            elif line.startswith("○") or line.startswith("◐"):
                color = WARNING_COLOR
            
            draw.text((100, y_offset), line, fill=color, font=content_font)
            y_offset += 35
    
    return img


def generate_video_with_pillow():
    """Generate video frames and save as images, then combine"""
    
    print("Generating video frames...")
    
    # Create frames directory
    frames_dir = "video_frames"
    os.makedirs(frames_dir, exist_ok=True)
    
    total_frames = 0
    frame_files = []
    
    for scene_idx, scene in enumerate(SCENES):
        print(f"  Scene {scene_idx + 1}/{len(SCENES)}: {scene.get('title', 'Untitled')}")
        
        # Create frame for this scene
        img = create_frame(scene)
        
        # Duplicate frame for duration at 24fps
        num_frames = scene["duration"] * FPS
        
        for frame_num in range(num_frames):
            frame_path = os.path.join(frames_dir, f"frame_{total_frames:05d}.png")
            img.save(frame_path)
            frame_files.append(frame_path)
            total_frames += 1
    
    print(f"\nGenerated {total_frames} frames in '{frames_dir}/'")
    return frame_files


def generate_video_with_moviepy():
    """Generate MP4 video using moviepy"""
    
    if not MOVIEPY_AVAILABLE:
        print("Error: moviepy not available. Install with: pip install moviepy")
        return None
    
    print("Generating video with moviepy...")
    clips = []
    
    for scene_idx, scene in enumerate(SCENES):
        print(f"  Scene {scene_idx + 1}/{len(SCENES)}: {scene.get('title', 'Untitled')}")
        
        # Create frame image
        img = create_frame(scene)
        
        # Convert PIL image to numpy array
        img_array = np.array(img)
        
        # Create clip from image
        clip = ImageClip(img_array).set_duration(scene["duration"])
        clips.append(clip)
    
    # Concatenate all clips
    print("\nCombining clips...")
    final_clip = concatenate_videoclips(clips, method="compose")
    
    # Write video file
    output_path = "resume_matching_agent_demo.mp4"
    print(f"Writing video to {output_path}...")
    
    final_clip.write_videofile(
        output_path,
        fps=FPS,
        codec="libx264",
        audio=False,
        preset="medium",
        threads=4
    )
    
    print(f"\n✅ Video saved to: {output_path}")
    print(f"   Duration: {sum(s['duration'] for s in SCENES)} seconds")
    print(f"   Resolution: {VIDEO_WIDTH}x{VIDEO_HEIGHT}")
    
    return output_path


def generate_video_simple():
    """Simple video generation using ffmpeg directly"""
    
    print("Generating video frames...")
    
    # Create frames directory
    frames_dir = "video_frames"
    os.makedirs(frames_dir, exist_ok=True)
    
    total_frames = 0
    
    for scene_idx, scene in enumerate(SCENES):
        print(f"  Scene {scene_idx + 1}/{len(SCENES)}: {scene.get('title', 'Untitled')}")
        
        # Create frame image
        img = create_frame(scene)
        
        # Save frames for this scene's duration
        num_frames = scene["duration"] * FPS
        
        for _ in range(num_frames):
            frame_path = os.path.join(frames_dir, f"frame_{total_frames:05d}.png")
            img.save(frame_path)
            total_frames += 1
    
    print(f"\n✅ Generated {total_frames} frames in '{frames_dir}/'")
    
    # Try to use ffmpeg to create video
    output_path = "resume_matching_agent_demo.mp4"
    ffmpeg_cmd = f'ffmpeg -y -framerate {FPS} -i {frames_dir}/frame_%05d.png -c:v libx264 -pix_fmt yuv420p {output_path}'
    
    print(f"\nTo create MP4, run:")
    print(f"  {ffmpeg_cmd}")
    
    # Try to run ffmpeg
    result = os.system(ffmpeg_cmd)
    
    if result == 0:
        print(f"\n✅ Video saved to: {output_path}")
        # Clean up frames
        import shutil
        shutil.rmtree(frames_dir)
    else:
        print(f"\n⚠️ ffmpeg not found. Frames saved in '{frames_dir}/'")
        print("Install ffmpeg and run the command above to create MP4.")
    
    return output_path


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("="*60)
    print("  RESUME MATCHING AGENT - VIDEO GENERATOR")
    print("="*60)
    
    total_duration = sum(s["duration"] for s in SCENES)
    print(f"\nVideo will be {total_duration} seconds ({total_duration/60:.1f} minutes)")
    print(f"Resolution: {VIDEO_WIDTH}x{VIDEO_HEIGHT}")
    print(f"Scenes: {len(SCENES)}")
    
    print("\nSelect generation method:")
    print("  1. MoviePy (best quality, requires: pip install moviepy)")
    print("  2. FFmpeg (requires ffmpeg installed)")
    print("  3. Frames only (save PNG frames)")
    
    try:
        choice = input("\nEnter choice (1/2/3) [default: 1]: ").strip() or "1"
    except:
        choice = "1"
    
    if choice == "1":
        try:
            generate_video_with_moviepy()
        except Exception as e:
            print(f"MoviePy error: {e}")
            print("Falling back to ffmpeg method...")
            generate_video_simple()
    elif choice == "2":
        generate_video_simple()
    else:
        generate_video_with_pillow()
        print("\nFrames saved. Use video editing software to combine.")


if __name__ == "__main__":
    main()
