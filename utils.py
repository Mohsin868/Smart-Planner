def priority_to_score(priority):
    return {"High": 3, "Medium": 2, "Low": 1}.get(priority, 1)
