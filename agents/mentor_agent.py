from .assessment_agent import evaluate
def respond(question, profile, assessments):
    q = (question or "").lower()
    if not q.strip():
        return "Ask me about your skills, career goal, or next learning step."
    if "change" in q and "career" in q:
        return "Update your target career on the profile page. The Skill Gap Agent will recalculate the missing skills and roadmap."
    if assessments:
        latest = assessments[0]
        result = evaluate(latest["score"], latest["total"])
        return (f"Your latest assessment was {latest['score']}/{latest['total']} in {latest['topic']} "
                f"({result['percentage']}%). {result['status']}: {result['action']}")
    return (f"Your current goal is {profile.get('career','your career goal')}. "
            "Start by checking your missing skills, then study one topic at a time and complete a practical exercise.")
