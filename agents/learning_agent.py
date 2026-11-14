def make_roadmap(missing):
    if not missing:
        return [{"week": "Next step", "topic": "Build a portfolio project", "task": "Create and publish a project demonstrating your skills."}]
    return [{"week": f"Week {i+1}", "topic": skill.title(),
             "task": f"Learn {skill}, complete one hands-on exercise, and explain what you built."}
            for i, skill in enumerate(missing[:6])]
