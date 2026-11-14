from datetime import datetime
from .skill_analyzer_agent import ROLE_SKILL_REQUIREMENTS, CANONICAL_ALIASES

class CareerMatcherAgent:
    """
    Career Matcher Agent:
    Calculates a role-readiness match percentage and benchmarks current skills
    against selected job roles (Full Stack Developer, Data Scientist, AI Engineer, Python Developer, DevOps).
    """
    def __init__(self):
        self.name = "Career Matcher Agent"
        self.badge = "Role Benchmarking Engine"

    def match(self, user_skills_map, target_career):
        benchmarks = []
        user_skill_ids = set(user_skills_map.keys())

        # Metadata for roles
        meta = {
            "Full Stack Developer": {"demand": "Very High", "avg_salary": "$115,000", "weeks_base": 12},
            "Data Scientist": {"demand": "High", "avg_salary": "$125,000", "weeks_base": 14},
            "AI Engineer": {"demand": "Surging", "avg_salary": "$145,000", "weeks_base": 16},
            "Python Developer": {"demand": "High", "avg_salary": "$110,000", "weeks_base": 8},
            "DevOps & Cloud Engineer": {"demand": "Very High", "avg_salary": "$130,000", "weeks_base": 14}
        }

        target_readiness_pct = 0

        for role_name, req in ROLE_SKILL_REQUIREMENTS.items():
            core_skills = req["core"]
            matched_skills = []
            missing_skills = []
            weighted_points = 0.0

            for sk in core_skills:
                display_name = CANONICAL_ALIASES.get(sk, (sk, sk.title(), "", ""))[1]
                if sk in user_skills_map:
                    item = user_skills_map[sk]
                    weight = item.get("score", 70) / 100.0
                    weighted_points += weight
                    matched_skills.append(display_name)
                else:
                    missing_skills.append(display_name)

            # Bonus for transferable skills in user profile
            transferable = [
                s for s in user_skill_ids
                if s not in core_skills and (s in ["python", "sql", "linux", "docker"])
            ]
            bonus_points = min(1.0, len(transferable) * 0.35)
            total_score = weighted_points + bonus_points
            max_possible = len(core_skills)

            readiness_pct = min(100, max(10, round((total_score / max_possible) * 100)))

            if role_name.lower() == target_career.lower():
                target_readiness_pct = readiness_pct

            role_meta = meta.get(role_name, {"demand": "High", "avg_salary": "$110,000", "weeks_base": 12})
            weeks_est = max(3, round(role_meta["weeks_base"] * (1 - (readiness_pct / 100.0))))

            benchmarks.append({
                "role": role_name,
                "readiness_pct": readiness_pct,
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "matched_count": len(matched_skills),
                "total_required": len(core_skills),
                "demand": role_meta["demand"],
                "avg_salary": role_meta["avg_salary"],
                "estimated_weeks": f"{weeks_est} - {weeks_est + 4} weeks",
                "is_target": (role_name.lower() == target_career.lower())
            })

        # Sort benchmarks by readiness score descending
        benchmarks.sort(key=lambda x: x["readiness_pct"], reverse=True)

        # Agent collaborative log
        best_fit = benchmarks[0]
        summary = (
            f"Calculated readiness: {target_readiness_pct}% for target role '{target_career}'. "
            f"Alternative best fit: '{best_fit['role']}' at {best_fit['readiness_pct']}%."
        )
        details = (
            f"Evaluated skill taxonomy across {len(benchmarks)} industry profiles. "
            f"Target role '{target_career}' stands at {target_readiness_pct}% readiness. "
            f"Identified transferable synergies ({len(transferable)} complementary capabilities). "
            f"Handing off readiness benchmarks to Progress Evaluator and Roadmap Agents."
        )

        agent_log = {
            "agent_name": self.name,
            "action": "BENCHMARK_CAREERS_AND_READINESS",
            "status": "SUCCESS",
            "summary": summary,
            "details": details,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }

        return {
            "target_readiness_pct": target_readiness_pct,
            "benchmarks": benchmarks,
            "best_fit": best_fit,
            "log": agent_log
        }
