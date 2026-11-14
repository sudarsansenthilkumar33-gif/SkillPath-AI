import re
from datetime import datetime

# Standard canonical taxonomy for tech skills and domains
CANONICAL_ALIASES = {
    "basic html": ("html", "HTML (Basic)", "Beginner", "Frontend"),
    "html": ("html", "HTML5", "Proficient", "Frontend"),
    "html5": ("html", "HTML5", "Proficient", "Frontend"),
    "css": ("css", "CSS3 / Styling", "Proficient", "Frontend"),
    "css3": ("css", "CSS3 / Styling", "Proficient", "Frontend"),
    "javascript": ("javascript", "JavaScript (ES6+)", "Proficient", "Frontend"),
    "js": ("javascript", "JavaScript (ES6+)", "Proficient", "Frontend"),
    "react": ("react", "React.js", "Proficient", "Frontend"),
    "react.js": ("react", "React.js", "Proficient", "Frontend"),
    "reactjs": ("react", "React.js", "Proficient", "Frontend"),
    "node": ("node.js", "Node.js / Express", "Proficient", "Backend"),
    "node.js": ("node.js", "Node.js / Express", "Proficient", "Backend"),
    "nodejs": ("node.js", "Node.js / Express", "Proficient", "Backend"),
    "python": ("python", "Python 3", "Proficient", "Backend/Core"),
    "py": ("python", "Python 3", "Proficient", "Backend/Core"),
    "sql": ("sql", "SQL / Relational DB", "Proficient", "Database"),
    "postgres": ("sql", "PostgreSQL", "Proficient", "Database"),
    "postgresql": ("sql", "PostgreSQL", "Proficient", "Database"),
    "mysql": ("sql", "MySQL", "Proficient", "Database"),
    "git": ("git", "Git / GitHub", "Proficient", "DevOps/Tools"),
    "rest apis": ("rest apis", "RESTful APIs", "Proficient", "Backend"),
    "api": ("rest apis", "RESTful APIs", "Proficient", "Backend"),
    "apis": ("rest apis", "RESTful APIs", "Proficient", "Backend"),
    "pandas": ("pandas", "Pandas & Data Wrangling", "Proficient", "Data Science"),
    "statistics": ("statistics", "Inferential Statistics", "Proficient", "Data Science"),
    "stats": ("statistics", "Inferential Statistics", "Proficient", "Data Science"),
    "machine learning": ("machine learning", "Machine Learning (Scikit-Learn)", "Proficient", "AI/ML"),
    "ml": ("machine learning", "Machine Learning (Scikit-Learn)", "Proficient", "AI/ML"),
    "deep learning": ("deep learning", "Deep Learning / Neural Networks", "Proficient", "AI/ML"),
    "dl": ("deep learning", "Deep Learning / Neural Networks", "Proficient", "AI/ML"),
    "pytorch": ("pytorch", "PyTorch Framework", "Proficient", "AI/ML"),
    "llms": ("llms", "Large Language Models & Prompt Engineering", "Proficient", "AI/ML"),
    "prompt engineering": ("llms", "Prompt Engineering", "Proficient", "AI/ML"),
    "docker": ("docker", "Docker & Containers", "Proficient", "DevOps"),
    "kubernetes": ("kubernetes", "Kubernetes (K8s)", "Proficient", "DevOps"),
    "aws": ("aws", "AWS Cloud Services", "Proficient", "Cloud"),
    "linux": ("linux", "Linux Systems & Bash", "Proficient", "DevOps")
}

# Core required and secondary skills for targeted careers
ROLE_SKILL_REQUIREMENTS = {
    "Full Stack Developer": {
        "core": ["javascript", "react", "node.js", "html", "css", "sql", "git"],
        "critical_order": ["javascript", "react", "node.js", "css", "git"],
        "secondary": ["rest apis", "docker", "testing"],
        "domain": "Web & Cloud Software Engineering"
    },
    "Data Scientist": {
        "core": ["python", "sql", "pandas", "statistics", "machine learning"],
        "critical_order": ["pandas", "statistics", "machine learning"],
        "secondary": ["data visualization", "deep learning", "jupyter"],
        "domain": "Applied Analytics & Predictive Modeling"
    },
    "AI Engineer": {
        "core": ["python", "machine learning", "deep learning", "pytorch", "llms"],
        "critical_order": ["deep learning", "pytorch", "llms"],
        "secondary": ["vector databases", "math", "docker"],
        "domain": "Generative AI & Intelligent Systems"
    },
    "Python Developer": {
        "core": ["python", "sql", "git", "rest apis", "testing"],
        "critical_order": ["fastapi", "testing", "git"],
        "secondary": ["docker", "celery", "redis"],
        "domain": "Backend Architecture & Distributed Services"
    },
    "DevOps & Cloud Engineer": {
        "core": ["linux", "docker", "kubernetes", "aws", "git", "python"],
        "critical_order": ["docker", "kubernetes", "aws", "ci/cd"],
        "secondary": ["terraform", "monitoring"],
        "domain": "Infrastructure as Code & CI/CD Pipelines"
    }
}

class SkillAnalyzerAgent:
    """
    Skill Analyzer Agent:
    Evaluates learner profile, existing skills, certifications, and projects
    against target career requirements to separate strengths from missing skills.
    """
    def __init__(self):
        self.name = "Skill Analyzer Agent"
        self.badge = "Taxonomy & Gap Specialist"

    def analyze(self, profile):
        raw_skills_text = profile.get("skills", "")
        career = profile.get("career", "Full Stack Developer")
        certifications = profile.get("certifications", "")
        projects = profile.get("projects", "")
        experience = profile.get("experience_level", "Junior")

        # Parse and normalize raw skills
        tokens = [s.strip().lower() for s in re.split(r"[,;]+", raw_skills_text) if s.strip()]
        user_skills_map = {}
        for tok in tokens:
            # check alias mapping
            if tok in CANONICAL_ALIASES:
                canon_id, display_name, level, category = CANONICAL_ALIASES[tok]
                user_skills_map[canon_id] = {
                    "id": canon_id,
                    "name": display_name,
                    "level": level,
                    "category": category,
                    "score": 60 if "basic" in tok else 85
                }
            else:
                user_skills_map[tok] = {
                    "id": tok,
                    "name": tok.title(),
                    "level": "Proficient",
                    "category": "General",
                    "score": 75
                }

        # Project and certification boosting
        proj_text_lower = (projects + " " + certifications).lower()
        if "sql" in proj_text_lower and "sql" in user_skills_map:
            user_skills_map["sql"]["score"] = min(95, user_skills_map["sql"]["score"] + 15)
            user_skills_map["sql"]["evidence"] = "Validated by project / certification"
        if "python" in proj_text_lower and "python" in user_skills_map:
            user_skills_map["python"]["score"] = min(95, user_skills_map["python"]["score"] + 15)
            user_skills_map["python"]["evidence"] = "Validated by project / certification"

        # Benchmark against target career
        role_req = ROLE_SKILL_REQUIREMENTS.get(career, ROLE_SKILL_REQUIREMENTS["Full Stack Developer"])
        core_required = role_req["core"]

        strengths = []
        missing_skills = []
        partial_skills = []

        for req_id in core_required:
            alias_info = CANONICAL_ALIASES.get(req_id, (req_id, req_id.title(), "Required", "Core"))
            display_name = alias_info[1]
            category = alias_info[3]

            if req_id in user_skills_map:
                item = user_skills_map[req_id]
                if item["level"] == "Beginner" or item["score"] < 70:
                    partial_skills.append({
                        "id": req_id,
                        "name": display_name,
                        "score": item["score"],
                        "category": category,
                        "status": "Partial/Needs Polish"
                    })
                else:
                    strengths.append({
                        "id": req_id,
                        "name": display_name,
                        "score": item["score"],
                        "category": category,
                        "status": "Strength"
                    })
            else:
                missing_skills.append({
                    "id": req_id,
                    "name": display_name,
                    "score": 0,
                    "category": category,
                    "status": "Missing Gap",
                    "priority": "High" if req_id in role_req.get("critical_order", []) else "Standard"
                })

        # Also add non-core strengths that the user has (e.g. Python for Full Stack Developer is a strong backend strength)
        for user_skill_id, item in user_skills_map.items():
            if user_skill_id not in core_required:
                strengths.append({
                    "id": user_skill_id,
                    "name": item["name"],
                    "score": item["score"],
                    "category": item["category"],
                    "status": "Transferable Strength"
                })

        # Generate agent execution log trace
        missing_names = [m["name"] for m in missing_skills]
        strength_names = [s["name"] for s in strengths]
        summary = f"Identified {len(strengths)} strengths and {len(missing_skills)} skill gaps for '{career}'."
        details = (
            f"Evaluated input skills: {list(user_skills_map.keys())}. "
            f"Validated verified strengths: {', '.join(strength_names) if strength_names else 'None'}. "
            f"Detected missing prerequisite proficiencies: {', '.join(missing_names)}. "
            f"Target benchmark: {len(core_required)} core competencies for {role_req['domain']}."
        )

        agent_log = {
            "agent_name": self.name,
            "action": "EVALUATE_PROFILE_AND_GAPS",
            "status": "SUCCESS",
            "summary": summary,
            "details": details,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }

        return {
            "strengths": strengths,
            "missing": missing_skills,
            "partial": partial_skills,
            "user_skills_map": user_skills_map,
            "target_career": career,
            "core_required": core_required,
            "log": agent_log
        }
