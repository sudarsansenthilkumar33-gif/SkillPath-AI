from .skill_gap_agent import ROLE_SKILLS
def recommend_career(skills):
    have = {s.lower().strip() for s in skills}
    scores = []
    for role, required in ROLE_SKILLS.items():
        matches = len(have.intersection(required))
        scores.append((matches, role))
    scores.sort(reverse=True)
    return [role for score, role in scores[:3]]
