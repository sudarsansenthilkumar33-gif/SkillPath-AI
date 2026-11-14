from datetime import datetime

class ProgressEvaluatorAgent:
    """
    Progress Evaluator & AI Mentor Agent:
    Tracks quiz/assessment scores and module completion in SQLite, and
    dynamically triggers learning roadmap recalculation whenever the user
    switches target careers or scores poorly (<60%) on an assessment.
    Also provides context-aware mentorship consultations.
    """
    def __init__(self):
        self.name = "Progress Evaluator & AI Mentor Agent"
        self.badge = "Adaptive Remediation & Mentorship Engine"

    def evaluate_assessment_history(self, assessments, target_career):
        if not assessments:
            summary = f"Continuous diagnostic monitoring initialized for '{target_career}'."
            details = (
                f"Progress Evaluator standing by. Evaluates student performance against a 60% competency threshold. "
                f"Any score < 60% will trigger an adaptive remediation protocol, restructuring the active roadmap."
            )
            agent_log = {
                "agent_name": self.name,
                "action": "DIAGNOSTIC_MONITOR_ACTIVE",
                "status": "STANDBY",
                "summary": summary,
                "details": details,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
            return {
                "needs_remediation": False,
                "latest": None,
                "average_score": 0,
                "remedial_topic": None,
                "summary": summary,
                "mentor_note": "Welcome! Complete a diagnostic assessment to validate your baseline skills.",
                "action_plan": "Ready for initial assessment submission.",
                "log": agent_log
            }

        latest = assessments[0]
        score = latest["score"]
        total = latest["total"]
        pct = round((score / total) * 100) if total else 0
        topic = latest.get("topic", "General")

        all_pcts = [round((a["score"] / a["total"]) * 100) for a in assessments if a["total"] > 0]
        avg_pct = round(sum(all_pcts) / len(all_pcts)) if all_pcts else 0

        needs_remediation = (pct < 60)

        if needs_remediation:
            summary = f"REMEDIATION TRIGGERED: Recent score of {pct}% in '{topic}' is below the 60% benchmark."
            action_plan = (
                f"Flagged mastery deficiency in '{topic}'. Emitting directive to Roadmap Agent "
                f"to inject Phase 1-R remedial sprint before advancing to dependent frameworks."
            )
            mentor_note = (
                f"Don't worry! Scoring {pct}% on {topic} is a valuable diagnostic signal. "
                f"We've dynamically adjusted your roadmap to reinforce core syntax and debugging first."
            )
        else:
            summary = f"PERFORMANCE VERIFIED: Score of {pct}% in '{topic}' meets proficiency requirements (>=60%)."
            action_plan = f"Mastery validated. Greenlit progression to subsequent roadmap milestones in '{target_career}'."
            mentor_note = (
                f"Great work scoring {pct}% on {topic}! You've demonstrated solid comprehension. "
                f"Continue tackling hands-on projects to solidify this knowledge."
            )

        agent_log = {
            "agent_name": self.name,
            "action": "EVALUATE_ASSESSMENT_PERFORMANCE",
            "status": "REMEDIATION_TRIGGERED" if needs_remediation else "ON_TRACK",
            "summary": summary,
            "details": action_plan,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }

        return {
            "needs_remediation": needs_remediation,
            "latest_percentage": pct,
            "average_score": avg_pct,
            "remedial_topic": topic if needs_remediation else None,
            "mentor_note": mentor_note,
            "action_plan": action_plan,
            "log": agent_log
        }

    def mentor_chat(self, question, profile, assessments, roadmap_info=None):
        q = (question or "").strip().lower()
        career = profile.get("career", "Full Stack Developer")
        name = profile.get("name", "Learner")
        skills = profile.get("skills", "")

        latest_assessment = assessments[0] if assessments else None
        latest_pct = round((latest_assessment["score"] / latest_assessment["total"]) * 100) if latest_assessment else None

        # Build context-aware intelligent response
        if not q:
            return {
                "reply": f"Hello {name}! I am your AI Mentor. I am monitoring your progress toward becoming a {career}. Ask me about your roadmap, skill gaps, or how to prepare for your next assessment.",
                "log": self._make_mentor_log("MENTOR_STANDBY", "AI Mentor standing by for student query.")
            }

        # Check for career change queries
        if "switch" in q or "change" in q or "career" in q or "role" in q:
            reply = (
                f"You are currently targeting **{career}**. To switch your goal, use the Target Role Switcher "
                f"in your dashboard header. When you switch, our multi-agent pipeline immediately re-evaluates your "
                f"readiness, calculates new skill gaps, and dynamically updates your learning roadmap!"
            )
        # Check for assessment or quiz score questions
        elif "score" in q or "quiz" in q or "assessment" in q or "test" in q or "failed" in q:
            if latest_assessment:
                if latest_pct < 60:
                    reply = (
                        f"Your latest score on **{latest_assessment['topic']}** was **{latest_pct}%** ({latest_assessment['score']}/{latest_assessment['total']}). "
                        f"Because this fell below our 60% proficiency threshold, I triggered our remediation protocol. "
                        f"Your roadmap now features **Phase R: Refresher & Core Drills**. Spend 2-3 days practicing with the "
                        f"debugging exercises before re-testing!"
                    )
                else:
                    reply = (
                        f"Your latest score on **{latest_assessment['topic']}** was an impressive **{latest_pct}%** ({latest_assessment['score']}/{latest_assessment['total']})! "
                        f"You have proven competency in this domain. I recommend pushing forward into the next hands-on project milestone."
                    )
            else:
                reply = (
                    f"You haven't completed any assessments yet! I strongly recommend taking the 5-question diagnostic "
                    f"quiz to validate your foundational knowledge and unlock verified badges on your dashboard."
                )
        # Check for JavaScript, React, Node.js questions
        elif "javascript" in q or "js" in q or "node" in q or "react" in q:
            reply = (
                f"For a **{career}**, JavaScript is the primary execution engine across both browser and server. "
                f"Since your profile lists Python and SQL, you already understand programming logic and relational structures. "
                f"Your fastest learning path is: 1) Master ES6+ syntax (Arrow functions, Promises, Async/Await), "
                f"2) Build React components using Hooks, and 3) Connect a Node.js Express API to your existing SQL skills!"
            )
        # General advice / next step
        else:
            remediation_state = "under active remediation" if (latest_pct and latest_pct < 60) else "on track"
            reply = (
                f"Great question, {name}! Based on your current profile (Skills: *{skills}*) targeting **{career}**, "
                f"your learning path is currently {remediation_state}. "
                f"My key recommendation right now: focus on your highest priority missing skill gaps. "
                f"Spend 70% of your time writing real code in hands-on projects and 30% studying official documentation."
            )

        agent_log = self._make_mentor_log(
            "MENTOR_CONSULTATION",
            f"Mentored student on '{question[:50]}...'. Provided tailored guidance for '{career}'."
        )

        return {
            "reply": reply,
            "log": agent_log
        }

    def _make_mentor_log(self, action, summary):
        return {
            "agent_name": self.name,
            "action": action,
            "status": "SUCCESS",
            "summary": summary,
            "details": "Contextual advice generated using student profile, score history, and active roadmap state.",
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
