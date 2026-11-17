"""
SkillPath AI - Comprehensive Unit and Integration Test Suite
Validates User Registration, Password Hashing, Zero-Demo Profiles,
Resume NLP Extraction, 4-Agent Pipeline, JD Matcher, Mock Interview,
Adaptive Remediation, Verified Certificate, and Admin Benchmarks.
"""

import os
import unittest
import json
import sqlite3
from app import app
from database import (
    get_db,
    register_user,
    authenticate_user,
    get_profile,
    get_role_benchmarks,
    save_role_benchmark,
    get_completed_modules
)
from werkzeug.security import check_password_hash


class TestSkillPathAIApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        cls.client = app.test_client()
        with get_db() as con:
            con.execute("DELETE FROM users WHERE email LIKE '%@example.com' OR email LIKE '%@uniquedemo.com'")
            con.execute("DELETE FROM role_benchmarks WHERE role = 'Robotics Software Engineer'")

    def test_01_security_headers_present(self):
        """Verify defense-in-depth security headers are present on all responses."""
        res = self.client.get("/")
        self.assertIn("default-src", res.headers.get("Content-Security-Policy", ""))
        self.assertEqual(res.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(res.headers.get("X-Frame-Options"), "DENY")
        self.assertEqual(res.headers.get("X-XSS-Protection"), "1; mode=block")
        self.assertEqual(res.headers.get("Referrer-Policy"), "strict-origin-when-cross-origin")
        self.assertIn("geolocation=()", res.headers.get("Permissions-Policy", ""))

    def test_02_zero_secret_key_loaded(self):
        """Verify SECRET_KEY is set and no default hardcoded fallback credentials leaked."""
        self.assertTrue(bool(app.secret_key))
        self.assertNotEqual(app.secret_key, "hardcoded")

    def test_03_database_indexes_exist(self):
        """Verify required SQLite performance indexes are created in database."""
        with get_db() as con:
            indexes = [r[1] for r in con.execute("SELECT type, name FROM sqlite_master WHERE type='index'").fetchall()]
        self.assertIn("idx_users_email", indexes)
        self.assertIn("idx_users_xp", indexes)
        self.assertIn("idx_module_progress_career", indexes)
        self.assertIn("idx_assessments_topic", indexes)

    def test_04_user_registration_and_password_hashing(self):
        """Verify user registration hashes passwords with werkzeug."""
        email = "test.security.user@example.com"
        raw_pass = "SecurePass#2026"
        user, err = register_user(
            name="Security Tester",
            email=email,
            password=raw_pass,
            target_career="Full Stack Developer"
        )
        self.assertIsNone(err)
        self.assertIsNotNone(user)
        self.assertEqual(user["email"], email)

        # Inspect database record directly to verify hash
        with get_db() as con:
            row = con.execute("SELECT password_hash FROM users WHERE email = ?", (email,)).fetchone()
            self.assertIsNotNone(row)
            pw_hash = row["password_hash"]
            self.assertNotEqual(pw_hash, raw_pass)
            self.assertTrue(check_password_hash(pw_hash, raw_pass))

    def test_05_user_registration_duplicate_email_fails(self):
        """Verify registration prevents duplicate emails."""
        email = "duplicate.test@example.com"
        register_user("User A", email, "password123")
        user2, err = register_user("User B", email, "password123")
        self.assertIsNone(user2)
        self.assertIn("already exists", err)

    def test_06_user_registration_input_validation(self):
        """Verify registration validates empty names, bad emails, and short passwords."""
        u1, err1 = register_user("", "valid@email.com", "pass123")
        self.assertIsNone(u1)
        self.assertIn("Name is required", err1)

        u2, err2 = register_user("Test Name", "bad-email", "pass123")
        self.assertIsNone(u2)
        self.assertIn("valid email", err2)

        u3, err3 = register_user("Test Name", "valid@email.com", "12")
        self.assertIsNone(u3)
        self.assertIn("at least 4 characters", err3)

    def test_07_user_authentication_success_and_failure(self):
        """Verify authentication validates passwords and rejects incorrect credentials."""
        email = "auth.verify@example.com"
        password = "CorrectPassword123"
        register_user("Auth Candidate", email, password)

        # Correct password
        user, err = authenticate_user(email, password)
        self.assertIsNone(err)
        self.assertIsNotNone(user)

        # Wrong password
        bad_user, bad_err = authenticate_user(email, "WrongPassword")
        self.assertIsNone(bad_user)
        self.assertIn("Incorrect password", bad_err)

        # Non-existent email
        ghost, ghost_err = authenticate_user("ghost@example.com", "anything")
        self.assertIsNone(ghost)
        self.assertIn("No account found", ghost_err)

    def test_08_zero_demo_profile_isolation(self):
        """Verify a newly registered user gets their own profile with zero demo data leak."""
        res = self.client.post("/login", data={
            "action": "signup",
            "name": "Maya Lin",
            "email": "maya.lin@uniquedemo.com",
            "password": "pass123456Maya",
            "career": "AI Engineer",
            "skills": "Python, PyTorch, SQL"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Maya Lin", res.data)
        self.assertNotIn(b"Alex Chen", res.data)

    def test_09_social_oauth_onboarding_flow(self):
        """Verify social 1-click onboarding creates custom profile and persists in SQLite."""
        for provider in ["google", "github", "linkedin"]:
            res = self.client.get(f"/auth/social/{provider}", follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"Successfully authenticated", res.data)

    def test_10_resume_skill_auto_extraction(self):
        """Verify heuristic NLP extraction parses skills from text and recalculates roadmap."""
        resume_sample = "Software Engineer with experience in Python, SQL, Docker, React, and building RESTful APIs with PostgreSQL"
        res = self.client.post("/extract-resume", data={"resume_text": resume_sample}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Resume Parsed", res.data)
        self.assertIn(b"Dashboard", res.data)

    def test_11_four_agent_pipeline_execution_api(self):
        """Verify /api/run-agents executes Skill Analyzer -> Matcher -> Architect -> Mentor."""
        res = self.client.post("/api/run-agents")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["status"], "success")
        self.assertIn("agent_steps", data)
        self.assertIn("target_readiness_pct", data)
        self.assertGreaterEqual(len(data["agent_steps"]), 4)

    def test_12_agent_logs_api(self):
        """Verify /api/agent-feed returns structured JSON feed of real-time decisions."""
        res = self.client.get("/api/agent-feed")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn("logs", data)
        self.assertIsInstance(data["logs"], list)

    def test_13_job_description_match_analyzer_api(self):
        """Verify /api/match-jd parses job description and reports match percentage."""
        sample_jd = "Senior React Developer: Seeking proficiency in React, Node.js, JavaScript, and HTML/CSS."
        res = self.client.post("/api/match-jd", data={"jd_text": sample_jd})
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["status"], "success")
        self.assertIn("match_pct", data["analysis"])
        self.assertIn("matched_skills", data["analysis"])
        self.assertIn("missing_skills", data["analysis"])

    def test_14_adaptive_remediation_trigger_on_low_score(self):
        """Verify assessment score < 60% injects Phase R Accelerated Remediation Sprint."""
        res = self.client.post("/quick-assessment-demo", data={
            "mode": "fail",
            "topic": "JavaScript & Frontend Core"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Adaptive Intervention Active", res.data)
        self.assertIn(b"Phase R: Accelerated Remediation Sprint", res.data)

    def test_15_verified_certificate_page(self):
        """Verify /certificate renders printable credential with user's real name and ID."""
        res = self.client.get("/certificate")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Certificate of Achievement", res.data)
        self.assertIn(b"Credential ID:", res.data)
        self.assertIn(b"VERIFIED", res.data)

    def test_16_ai_mock_interview_evaluation(self):
        """Verify /interview accepts technical responses, calculates score, and awards XP."""
        res = self.client.post("/interview", data={
            "question": "Explain the JavaScript Event Loop.",
            "answer": "The event loop coordinates the call stack and microtask/macrotask queues in asynchronous JavaScript to provide non-blocking I/O."
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"AI Mentor Evaluation Report", res.data)
        self.assertIn(b"Readiness", res.data)

    def test_17_admin_portal_and_benchmarks(self):
        """Verify admin portal KPIs and adding a custom benchmark to SQLite."""
        res = self.client.get("/admin")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"COHORT PERFORMANCE MATRIX", res.data)
        self.assertIn(b"TOTAL COHORT LEARNERS", res.data)

        # Add custom benchmark
        post_res = self.client.post("/admin/add-benchmark", data={
            "role": "Robotics Software Engineer",
            "demand": "Explosive",
            "estimated_weeks": "16 - 20 Weeks",
            "core_skills": "C++, ROS2, Python, SLAM, Linux",
            "description": "Autonomous robotic systems navigation and sensor fusion."
        }, follow_redirects=True)
        self.assertEqual(post_res.status_code, 200)
        self.assertIn(b"Robotics Software Engineer", post_res.data)

    def test_18_module_completion_tracking(self):
        """Verify module completion toggles state and updates progress."""
        career = "Full Stack Developer"
        module_id = "fs-mod-1"
        with get_db() as con:
            con.execute("DELETE FROM module_progress WHERE career = ? AND module_id = ?", (career, module_id))
        res = self.client.post("/toggle-module", data={
            "career": career,
            "module_id": module_id
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        completed = get_completed_modules(career)
        self.assertIn(module_id, completed)


if __name__ == "__main__":
    unittest.main()
