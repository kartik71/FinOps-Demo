def run(mira_output, jordan_output):
    if not mira_output.get("budget_ok"):
        return {"approved": False, "reason": "Budget exceeded"}
    if not jordan_output.get("compliance_ok"):
        return {"approved": False, "reason": "Compliance issue"}
    return {"approved": True}