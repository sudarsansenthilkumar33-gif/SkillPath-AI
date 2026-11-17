import unittest
import json
from app import app
from database import load_demo_profile, get_profile, get_assessments, get_completed_modules, get_db

class SkillPathMultiAgentTestSuite(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        self.client = app.test_client()

    def test_01_index_and_demo_load(self):
        # Test index page
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"SkillPath", res.data)

        # Test authentic real user onboarding
        res = self.client.get("/load-demo", follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Elena Rostova", res.data)
        self.assertIn(b"Full Stack Developer", res.data)

        profile = get_profile()
        self.assertEqual(profile["career"], "Full Stack Developer")
        self.assertIn("Python", profile["skills"])
        self.assertIn("SQL", profile["skills"])
        self.assertIn("HTML", profile["skills"])
        print("[PASS] Test 1: Index and Real-User Profile Loader passed.")

    def test_02_dashboard_and_multi_agent_pipeline(self):
        # Pre-load demo
        self.client.get("/load-demo")
        res = self.client.get("/dashboard")
        self.assertEqual(res.status_code, 200)

        # Check Deliverable 1: 4 Collaborating Agents present on the UI
        self.assertIn(b"Skill Analyzer Agent", res.data)
        self.assertIn(b"Career Matcher Agent", res.data)
        self.assertIn(b"Progress Evaluator", res.data)
        self.assertIn(b"AI Mentor Agent", res.data)
        self.assertIn(b"Roadmap &amp; Resource Recommender Agent", res.data)

        # Check Deliverable 2: Skill-gap breakdown (Missing: JavaScript, React, Node.js)
        self.assertIn(b"JavaScript", res.data)
        self.assertIn(b"React", res.data)
        self.assertIn(b"Node.js", res.data)

        # Check Strengths
        self.assertIn(b"Python", res.data)
        self.assertIn(b"SQL", res.data)

        # Check Agent Collaboration Feed
        self.assertIn(b"Live Agent Collaboration Feed", res.data)
        self.assertIn(b"EVALUATE_PROFILE_AND_GAPS", res.data)
        self.assertIn(b"BENCHMARK_CAREERS_AND_READINESS", res.data)
        self.assertIn(b"DYNAMIC_ROADMAP_SYNTHESIS", res.data)

        print("[PASS] Test 2: Dashboard and Multi-Agent Collaboration Feed passed.")

    def test_03_role_switcher_dynamic_recalculation(self):
        # Switch to Data Scientist
        res = self.client.post("/switch-role", data={"career": "Data Scientist"}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        profile = get_profile()
        self.assertEqual(profile["career"], "Data Scientist")
        self.assertIn(b"Data Scientist", res.data)

        # Switch to AI Engineer
        res = self.client.post("/switch-role", data={"career": "AI Engineer"}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        profile = get_profile()
        self.assertEqual(profile["career"], "AI Engineer")
        self.assertIn(b"AI Engineer", res.data)

        # Switch back to Full Stack Developer
        res = self.client.post("/switch-role", data={"career": "Full Stack Developer"}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        print("[PASS] Test 3: Dynamic Role Switcher passed.")

    def test_04_dynamic_remediation_trigger_on_low_score(self):
        # Ensure demo profile is set
        self.client.get("/load-demo")

        # Simulate low score (2/5 = 40% < 60%)
        res = self.client.post("/quick-assessment-demo", data={
            "mode": "fail",
            "topic": "JavaScript & Frontend Core"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # Verify dynamic remediation alert banner is visible
        self.assertIn(b"Adaptive Intervention Active", res.data)
        self.assertIn(b"Phase R: Refresher & Core Drills", res.data)
        self.assertIn(b"REMEDIATION TRIGGERED", res.data)

        # Now simulate 100% pass to clear remediation
        res = self.client.post("/quick-assessment-demo", data={
            "mode": "pass",
            "topic": "JavaScript & Frontend Core"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Mastery verified", res.data)
        print("[PASS] Test 4: Dynamic Roadmap Remediation (<60% Trigger) passed.")

    def test_05_interactive_module_completion_tracking(self):
        self.client.get("/load-demo")
        # Toggle module completion
        res = self.client.post("/toggle-module", data={
            "career": "Full Stack Developer",
            "module_id": "fs-mod-1"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        completed = get_completed_modules("Full Stack Developer")
        self.assertIn("fs-mod-1", completed)

        # Toggle back
        res = self.client.post("/toggle-module", data={
            "career": "Full Stack Developer",
            "module_id": "fs-mod-1"
        }, follow_redirects=True)
        completed = get_completed_modules("Full Stack Developer")
        self.assertNotIn("fs-mod-1", completed)
        print("[PASS] Test 5: Interactive Module Completion Tracking passed.")

    def test_06_ai_mentor_consultation(self):
        self.client.get("/load-demo")
        res = self.client.post("/mentor", data={
            "question": "Why is JavaScript critical before React?"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"JavaScript", res.data)
        self.assertIn(b"React", res.data)
        print("[PASS] Test 6: AI Mentor Consultation passed.")

    def test_07_api_agent_feed(self):
        res = self.client.get("/api/agent-feed")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["status"], "success")
        self.assertGreater(len(data["logs"]), 0)
        print("[PASS] Test 7: Agent JSON Feed API passed.")

    def test_08_tailwind_cdn_in_every_template(self):
        import os
        template_files = ["base.html", "login.html", "dashboard.html", "assessments.html", "mentor.html", "admin.html", "interview.html", "certificate.html"]
        templates_dir = os.path.join(os.path.dirname(__file__), "templates")
        for tf in template_files:
            file_path = os.path.join(templates_dir, tf)
            self.assertTrue(os.path.exists(file_path), f"Template {tf} must exist")
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("https://cdn.tailwindcss.com", content, f"Template {tf} must include Tailwind CDN")
        print("[PASS] Test 8: Tailwind CSS CDN verified in all specified templates.")

    def test_09_social_and_manual_authentication(self):
        # 1. Test Social OAuth-style demo sign-in
        for provider in ["google", "github", "linkedin", "demo"]:
            res = self.client.get(f"/auth/social/{provider}", follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"Successfully authenticated", res.data)
            self.assertIn(b"Dashboard", res.data)

        # 2. Test manual sign-up
        with get_db() as con:
            con.execute("DELETE FROM users WHERE email = 'jordan.lee@courserademo.edu'")
            con.commit()
        res = self.client.post("/login", data={
            "action": "signup",
            "name": "Jordan Lee",
            "email": "jordan.lee@courserademo.edu",
            "password": "securepassword123",
            "career": "AI Engineer"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Jordan Lee", res.data)

        # 3. Test logout
        res = self.client.get("/logout", follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"signed out successfully", res.data)

        # 4. Test manual sign-in
        res = self.client.post("/login", data={
            "action": "login",
            "email": "jordan.lee@courserademo.edu",
            "password": "securepassword123"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Welcome back, Jordan Lee", res.data)
        print("[PASS] Test 9: Social & Manual Authentication (Google, GitHub, LinkedIn, Demo, Email) passed.")

    def test_10_admin_portal_and_curriculum_manager(self):
        # Test Admin Portal view
        res = self.client.get("/admin")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"COHORT PERFORMANCE MATRIX", res.data)
        self.assertIn(b"TOTAL COHORT LEARNERS", res.data)
        self.assertIn(b"Curriculum &amp; Role Benchmarks", res.data)
        self.assertIn(b"Add / Update Role Benchmark", res.data)

        # Test adding a custom benchmark to SQLite
        res = self.client.post("/admin/add-benchmark", data={
            "role": "Cloud Solutions Architect",
            "demand": "Explosive",
            "estimated_weeks": "12 - 16 Weeks",
            "core_skills": "AWS, Azure, Terraform, Kubernetes, Microservices, Python",
            "description": "Design resilient, fault-tolerant enterprise cloud architectures."
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Cloud Solutions Architect", res.data)
        self.assertIn(b"Terraform", res.data)
        print("[PASS] Test 10: Admin Portal, Platform KPIs, and Benchmark Manager passed.")

    def test_11_ai_mock_interview_simulator(self):
        # 1. Test GET /interview
        res = self.client.get("/interview")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"AI Mock Interview Simulator", res.data)
        self.assertIn(b"TECHNICAL INTERVIEW PREPARATION", res.data)
        self.assertIn(b"Earn +200 XP", res.data)

        # 2. Test POST /interview with answer submission
        res = self.client.post("/interview?q=0", data={
            "question": "Explain the Event Loop in JavaScript. How does it handle asynchronous tasks, the call stack, microtasks, and macrotasks?",
            "answer": "The event loop continuously monitors the call stack and callback queues. Synchronous code executes on the call stack. Asynchronous promises queue into the microtask queue, which has priority over macrotasks like setTimeout. Once the stack is clear, microtasks drain before the next macrotask executes."
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"AI Mentor Evaluation Report", res.data)
        self.assertIn(b"+200 XP", res.data)
        print("[PASS] Test 11: AI Mock Interview Simulator (/interview) passed.")

    def test_12_verifiable_career_certificate(self):
        # Test GET /certificate
        res = self.client.get("/certificate")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Certificate of Achievement", res.data)
        self.assertIn(b"SKILLPATH-", res.data)
        self.assertIn(b"Cryptographically Verifiable Credential Active", res.data)
        self.assertIn(b"Print / Save PDF Certificate", res.data)
        print("[PASS] Test 12: Verifiable Career Certificate Generator (/certificate) passed.")

    def test_13_resume_bio_auto_skill_extraction(self):
        # Test POST /extract-resume
        res = self.client.post("/extract-resume", data={
            "resume_text": "Experienced software developer with strong background in Python, Docker, Kubernetes, FastAPI, PostgreSQL, and React. Built distributed microservices architectures and cloud pipelines."
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Resume Parsed", res.data)
        self.assertIn(b"Docker", res.data)
        print("[PASS] Test 13: Resume & Bio Auto-Skill Extraction (/extract-resume) passed.")

    def test_14_live_agent_pipeline_api(self):
        # Test POST /api/run-agents
        res = self.client.post("/api/run-agents")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["status"], "success")
        self.assertIn("agent_steps", data)
        self.assertGreater(len(data["agent_steps"]), 0)
        self.assertIn("target_readiness_pct", data)
        print("[PASS] Test 14: Live 4-Agent Pipeline Execution API (/api/run-agents) passed.")

    def test_15_gamified_xp_and_streak(self):
        # Load demo user
        self.client.get("/auth/social/demo", follow_redirects=True)
        # Check that dashboard renders gamified XP and streak
        res = self.client.get("/dashboard")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"XP Leaderboard", res.data)
        self.assertIn(b"Streak", res.data)
        print("[PASS] Test 15: Gamified XP, Streak, and Leaderboard passed.")

    def test_16_job_description_match_analyzer(self):
        res = self.client.post("/api/match-jd", data={
            "jd_text": "We are seeking a Full Stack Engineer experienced with React, Node.js, Python, PostgreSQL, and Docker."
        })
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["status"], "success")
        self.assertIn("analysis", data)
        self.assertIn("match_pct", data["analysis"])
        self.assertIn("matched_skills", data["analysis"])
        self.assertIn("missing_skills", data["analysis"])
        self.assertIn("recommendation", data["analysis"])
        print("[PASS] Test 16: Job Description (JD) Match Analyzer (/api/match-jd) passed.")

if __name__ == "__main__":
    unittest.main()
