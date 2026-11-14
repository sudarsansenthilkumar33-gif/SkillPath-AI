def summarize_profile(skills, career):
    skill_list = [s.strip().lower() for s in skills.split(",") if s.strip()]
    return {"skills": skill_list, "career": career.strip()}
