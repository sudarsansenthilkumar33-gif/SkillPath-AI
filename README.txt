================================================================================
SKILLPATH AI - VENTURE-GRADE MULTI-AGENT AUTONOMOUS LEARNING & CAREER PLATFORM
PromptWars X RTC Challenge Submission
================================================================================

SkillPath AI is a production-grade, venture-ready EdTech and Career Intelligence
SaaS platform built strictly with Python 3, Flask, SQLite, and Tailwind CSS.
Inspired by Coursera and Linear, it delivers a 100% responsive experience across
mobile, tablet, and desktop viewports.

--------------------------------------------------------------------------------
1. CORE ARCHITECTURAL PILLARS (8 VENTURE-GRADE DELIVERABLES)
--------------------------------------------------------------------------------

1. Coursera + Linear Design System (100% Responsive):
   - Crisp off-white canvas (#F8FAFC), pure white elevated cards with soft shadows,
     Coursera Royal Blue (#0056D2), Emerald (#10B981) for verified mastery,
     Amber (#F59E0B) for skill gaps, and Plus Jakarta Sans typography.
   - Dedicated slide-out mobile drawer navigation with full tablet & phone support.

2. Dynamic Personalized Profiles + Resume Skill Auto-Extractor:
   - Dynamic user session persistence supporting custom accounts and social logins.
   - 1-click "Paste Resume / Bio to Auto-Extract Skills" engine on /dashboard and /profile.
   - Parses unstructured resumes, auto-detects canonical tech skills (Docker, React,
     Kubernetes, Python, AWS, etc.), identifies target career, and triggers agents.
   - Preserves 1-click "Load Demo Profile (Alex Chen)" judge fast-track.

3. Live 4-Agent Pipeline Execution Visualizer:
   - Dedicated "⚡ Run Live 4-Agent Analysis" modal on /dashboard.
   - Interactive sequential visualizer animating each agent step-by-step:
     Skill Analyzer -> Career Matcher -> Roadmap Architect -> AI Mentor Evaluator
   - Emits structured JSON logs and dynamic readiness calculations via /api/run-agents.

4. Interactive Course Lesson Drawer & Hands-On Labs:
   - Every roadmap module card opens an interactive drawer modal with:
     * High-yield core architectural concepts and learning objectives.
     * Hands-on portfolio mini-project challenge.
     * Direct links to official docs (MDN, React, Node.js, CS50).
     * 1-click "Complete Module (+250 XP)" button updating SQLite & readiness % live.

5. AI Mock Interview Simulator (/interview):
   - Dedicated technical interview prep portal for all 6 target career tracks.
   - AI Mentor Agent generates deep technical & architectural questions.
   - Evaluates candidate typed answers on concept accuracy, algorithmic tradeoffs,
     and technical depth; awards +200 XP and provides actionable coaching.

6. Verifiable Career Certificate Generator (/certificate):
   - Generates an official, printable Coursera-style Certificate of Achievement.
   - Cryptographically hashed Credential ID (SKILLPATH-XXXXXXXXXX), verified readiness %,
     dynamic candidate name, issue date, and QR audit seal.
   - Built-in print stylesheet (@media print) for instant PDF generation.

7. India & Global Job Market Intelligence:
   - Real-time role telemetry card on /dashboard for selected career tracks:
     * Salary Ranges: INR ₹ Lakhs per Annum (LPA) & USD ($).
     * Hiring Demand Momentum & Open Positions.
     * Top demanded tech stack benchmarks.

8. Gamified XP, Streak & Enterprise Admin Portal (/admin):
   - Gamification engine tracking learning streaks (🔥 5d Streak), XP progression,
     and Cohort Leaderboard.
   - Admin & Cohort Analytics Portal with platform KPIs (Total Active Learners,
     Avg Readiness %, Top Skill Gaps, Remedial Interventions Triggered).
   - Live Learner Cohort Performance Matrix & Curriculum Role Benchmark Manager.

--------------------------------------------------------------------------------
2. MULTI-AGENT ARCHITECTURE (agents/)
--------------------------------------------------------------------------------
1. Skill Analyzer Agent (agents/skill_analyzer_agent.py):
   Normalizes profile skills and separates verified strengths from missing critical gaps.

2. Career Matcher Agent (agents/career_matcher_agent.py):
   Computes weighted role-readiness match percentages across 6 industry roles:
   * Full Stack Developer
   * Data Scientist
   * AI Engineer
   * Python Developer
   * DevOps & Cloud Engineer
   * Cloud Solutions Architect

3. Progress Evaluator Agent (agents/progress_evaluator_agent.py):
   Monitors assessment performance (<60% threshold) and module completions.
   Autonomously commands the Roadmap Agent to inject Phase R Remedial Sprints.

4. Roadmap Architect & Resource Recommender Agent (agents/roadmap_agent.py):
   Synthesizes phased, milestone-based curriculum paired with curated external
   learning links and hands-on portfolio deliverables.

--------------------------------------------------------------------------------
3. FAST JUDGING GUIDE (1-CLICK DEMO TRACK)
--------------------------------------------------------------------------------
1. Click "⚡ Load Demo Profile" in the top navbar:
   - Pre-loads Alex Chen (Python, SQL, HTML -> Full Stack Developer).
   - Identified gaps: JavaScript, React.js, Node.js.
   - Initial Readiness: ~27%.

2. Dynamic Role Switching:
   - Select "Data Scientist" or "AI Engineer" from the navbar dropdown.
   - All 4 agents instantly recalculate benchmarks, gaps, and roadmap phases.

3. Dynamic Remediation Trigger (<60% Trigger):
   - On /dashboard, click "⚡ Trigger <60% Score (Test Remediation)".
   - Recorded score: 2/5 (40%). Progress Evaluator Agent flags intervention and
     Roadmap Agent injects "Phase R: Priority Remediation Alert" at the top.
   - Click "⚡ Trigger 100% Score (Test Mastery)" to clear remediation.

4. AI Mock Interview Simulator:
   - Click "🎙️ AI Mock Interview" in navbar (/interview).
   - Type an explanation and submit to see the AI Mentor's instant evaluation & score.

5. Verifiable Certificate:
   - Click "🎓 Verified Certificate" on dashboard or visit /certificate.
   - View your official credential with unique SKILLPATH hash and click Print / Save PDF.

6. Enterprise Admin Portal:
   - Click "Admin" in navbar (/admin) to inspect platform KPIs, learner matrix,
     and add custom role benchmarks to SQLite.

--------------------------------------------------------------------------------
4. HOW TO RUN THE PLATFORM & TEST SUITE
--------------------------------------------------------------------------------
1. Run application:
   .venv\Scripts\python.exe app.py
   Open: http://127.0.0.1:5000

2. Run automated test suite (15/15 Tests Passing):
   .venv\Scripts\python.exe test_suite.py
================================================================================
