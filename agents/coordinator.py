from datetime import datetime
from .skill_analyzer_agent import SkillAnalyzerAgent
from .career_matcher_agent import CareerMatcherAgent
from .roadmap_agent import RoadmapAgent
from .progress_evaluator_agent import ProgressEvaluatorAgent

skill_analyzer = SkillAnalyzerAgent()
career_matcher = CareerMatcherAgent()
roadmap_generator = RoadmapAgent()
progress_evaluator = ProgressEvaluatorAgent()

def orchestrate_learning_path(profile, assessments=None, completed_module_ids=None):
    """
    Multi-Agent Coordination Pipeline:
    Coordinates Skill Analyzer, Career Matcher, Progress Evaluator, and Roadmap Recommender.
    Returns complete plan with step-by-step agent execution logs.
    """
    if assessments is None:
        assessments = []
    if completed_module_ids is None:
        completed_module_ids = set()

    target_career = profile.get("career", "Full Stack Developer")
    agent_logs = []

    # Step 1: Skill Analyzer Agent
    analysis = skill_analyzer.analyze(profile)
    agent_logs.append(analysis["log"])

    # Step 2: Career Matcher Agent
    matching = career_matcher.match(analysis["user_skills_map"], target_career)
    agent_logs.append(matching["log"])

    # Step 3: Progress Evaluator & AI Mentor Agent
    evaluation = progress_evaluator.evaluate_assessment_history(assessments, target_career)
    if evaluation.get("log"):
        agent_logs.append(evaluation["log"])

    # Step 4: Roadmap & Resource Recommender Agent (Adaptive to remediation & switches)
    remediation_data = {
        "needs_remediation": evaluation.get("needs_remediation", False),
        "topic": evaluation.get("remedial_topic", target_career)
    }
    roadmap_data = roadmap_generator.generate_roadmap(
        target_career=target_career,
        missing_skills=analysis["missing"],
        completed_module_ids=completed_module_ids,
        remediation_data=remediation_data
    )
    agent_logs.append(roadmap_data["log"])

    # Legacy mapping for backwards-compatibility
    gaps_legacy = {
        "matched": [s["name"] for s in analysis["strengths"]],
        "missing": [m["name"] for m in analysis["missing"]],
        "required": analysis["core_required"]
    }

    return {
        "analysis": analysis,
        "matching": matching,
        "evaluation": evaluation,
        "roadmap": roadmap_data,
        "gaps": gaps_legacy,
        "recommendations": [b["role"] for b in matching["benchmarks"][:3]],
        "agent_logs": agent_logs,
        "agents": [
            {"name": skill_analyzer.name, "badge": skill_analyzer.badge, "status": "Active"},
            {"name": career_matcher.name, "badge": career_matcher.badge, "status": "Active"},
            {"name": progress_evaluator.name, "badge": progress_evaluator.badge, "status": "Active"},
            {"name": roadmap_generator.name, "badge": roadmap_generator.badge, "status": "Active"}
        ]
    }

def build_learning_plan(skills_text, career, assessments=None, completed_module_ids=None):
    """Convenience wrapper for backward compatibility"""
    profile = {
        "name": "Learner",
        "skills": skills_text,
        "career": career
    }
    return orchestrate_learning_path(profile, assessments, completed_module_ids)

def mentor_reply(question, profile, assessments):
    """Invokes the Progress Evaluator & AI Mentor Agent for consultation"""
    result = progress_evaluator.mentor_chat(question, profile, assessments)
    return result
