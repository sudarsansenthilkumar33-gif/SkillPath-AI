ROLE_SKILLS = {
    "Full Stack Developer": ["html", "css", "javascript", "react", "node.js", "sql", "git"],
    "Data Analyst": ["excel", "sql", "python", "statistics", "power bi", "data visualization"],
    "Python Developer": ["python", "oop", "sql", "git", "apis", "testing"],
    "AI Engineer": ["python", "math", "statistics", "machine learning", "deep learning", "pytorch"]
}
def analyze(skills, career):
    required = ROLE_SKILLS.get(career, ROLE_SKILLS["Full Stack Developer"])
    have = {s.lower().strip() for s in skills}
    matched = [s for s in required if s in have]
    missing = [s for s in required if s not in have]
    return {"required": required, "matched": matched, "missing": missing}
