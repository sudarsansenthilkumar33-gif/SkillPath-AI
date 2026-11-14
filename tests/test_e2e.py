"""
SkillPath AI - End-to-End Integration and User Journey Test Suite
Validates complete user lifecycles across Onboarding, Skill Extraction,
Role Switching, Adaptive Remediation, Mock Interview, and Admin Benchmark Management.
"""

import unittest
from app import app
from database import get_db, get_completed_modules, get_user_by_id


class TestSkillPathAIE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        cls.client = app.test_client()
        with get_db() as con:
            con.execute("DELETE FROM users WHERE email LIKE 'e2e.%'")
            con.execute("DELETE FROM module_progress WHERE module_id = 'fs-mod-2'")

    def test_e2e_01_registration_to_dashboard_journey(self):
        """E2E Journey 1: New user registers -> extracts resume -> loads custom dashboard."""
        email = "e2e.journey.learner@skillpath.ai"
        signup_res = self.client.post("/login", data={
            "action": "signup",
            "name": "Avery Brooks",
            "email": email,
            "password": "SecurePassword#2026",
            "career": "Full Stack Developer",
            "skills": "Python, SQL, HTML"
        }, follow_redirects=True)
        self.assertEqual(signup_res.status_code, 200)
        self.assertIn(b"Avery Brooks", signup_res.data)

        # Extract resume to enrich skills
        resume = "Senior Full Stack Dev with React, TypeScript, Node.js, Docker, and PostgreSQL."
        extract_res = self.client.post("/extract-resume", data={"resume_text": resume}, follow_redirects=True)
        self.assertEqual(extract_res.status_code, 200)
        self.assertIn(b"Resume Parsed", extract_res.data)

        # Verify on dashboard
        dash_res = self.client.get("/dashboard")
        self.assertEqual(dash_res.status_code, 200)
        self.assertIn(b"Avery Brooks", dash_res.data)

    def test_e2e_02_role_switcher_multi_agent_recalculation(self):
        """E2E Journey 2: Switch target career and verify dynamic agent recalculation."""
        # Switch to Data Scientist
        res = self.client.post("/switch-role", data={"career": "Data Scientist"}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Data Scientist", res.data)
        self.assertIn(b"Pandas", res.data)

        # Switch to AI Engineer
        res2 = self.client.post("/switch-role", data={"career": "AI Engineer"}, follow_redirects=True)
        self.assertEqual(res2.status_code, 200)
        self.assertIn(b"AI Engineer", res2.data)
        self.assertIn(b"PyTorch", res2.data)

    def test_e2e_03_diagnostic_assessment_remediation_lifecycle(self):
        """E2E Journey 3: Test failure (<60%) injects Phase R, retest with pass clears remediation."""
        # Trigger failure
        fail_res = self.client.post("/quick-assessment-demo", data={
            "mode": "fail",
            "topic": "JavaScript & Frontend Core"
        }, follow_redirects=True)
        self.assertEqual(fail_res.status_code, 200)
        self.assertIn(b"Adaptive Intervention Active", fail_res.data)
        self.assertIn(b"Phase R: Accelerated Remediation Sprint", fail_res.data)

        # Retest and verify pass clears remediation banner
        pass_res = self.client.post("/quick-assessment-demo", data={
            "mode": "pass",
            "topic": "JavaScript & Frontend Core"
        }, follow_redirects=True)
        self.assertEqual(pass_res.status_code, 200)
        self.assertIn(b"Mastery verified", pass_res.data)

    def test_e2e_04_mock_interview_evaluation_and_xp_award(self):
        """E2E Journey 4: Navigate to /interview, submit answer, verify scoring and feedback."""
        # View interview question
        get_res = self.client.get("/interview")
        self.assertEqual(get_res.status_code, 200)
        self.assertIn(b"AI Mock Interview Simulator", get_res.data)

        # Submit technical explanation
        post_res = self.client.post("/interview?q=0", data={
            "question": "What is the primary role of the JavaScript Event Loop?",
            "answer": "The JavaScript event loop manages asynchronous tasks by continuously pushing microtasks from promises and macrotasks from setTimeout to the main call stack once empty."
        }, follow_redirects=True)
        self.assertEqual(post_res.status_code, 200)
        self.assertIn(b"AI Mentor Evaluation Report", post_res.data)

    def test_e2e_05_lesson_modal_module_completion_flow(self):
        """E2E Journey 5: Toggle module completion and verify persistent status."""
        mod_id = "fs-mod-2"
        with get_db() as con:
            con.execute("DELETE FROM module_progress WHERE career = 'Full Stack Developer' AND module_id = ?", (mod_id,))
        toggle_res = self.client.post("/toggle-module", data={
            "career": "Full Stack Developer",
            "module_id": mod_id
        }, follow_redirects=True)
        self.assertEqual(toggle_res.status_code, 200)
        completed = get_completed_modules("Full Stack Developer")
        self.assertIn(mod_id, completed)

    def test_e2e_06_admin_governance_benchmark_workflow(self):
        """E2E Journey 6: Admin inspects cohort matrix and registers new market benchmark."""
        admin_res = self.client.get("/admin")
        self.assertEqual(admin_res.status_code, 200)
        self.assertIn(b"COHORT PERFORMANCE MATRIX", admin_res.data)
        self.assertIn(b"Curriculum &amp; Role Benchmarks", admin_res.data)

        # Add new curriculum benchmark
        role = "Site Reliability Engineer"
        add_res = self.client.post("/admin/add-benchmark", data={
            "role": role,
            "demand": "Very High",
            "estimated_weeks": "12 - 16 Weeks",
            "core_skills": "Linux, Kubernetes, Go, Python, Prometheus, Grafana, Terraform",
            "description": "Production observability, SLO/SLA management, and automated incident recovery."
        }, follow_redirects=True)
        self.assertEqual(add_res.status_code, 200)
        self.assertIn(role.encode(), add_res.data)


if __name__ == "__main__":
    unittest.main()
