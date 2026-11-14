def evaluate(score, total):
    pct = round((score / total) * 100) if total else 0
    if pct < 60:
        return {"percentage": pct, "status": "Needs practice", "action": "Review the basics and retry a short quiz."}
    return {"percentage": pct, "status": "On track", "action": "Continue to the next topic and build a small project."}
