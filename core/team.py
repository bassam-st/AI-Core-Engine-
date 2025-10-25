# core/team.py — منسّق فريق (Planner/Researcher/Developer/Reviewer)
from __future__ import annotations
from typing import Any, Dict
from core.agents.planner import make_plan
from core.agents.researcher import research
from core.agents.developer import build_files
from core.agents.reviewer import review

def build_project(goal: str, urls: list[str] | None = None) -> Dict[str, Any]:
    plan = make_plan(goal, urls)
    res  = research(goal, urls or [], k=6)
    files = build_files(goal, res.get("brief", []))
    problems = review(files)

    return {
        "ok": True,
        "goal": goal,
        "plan": plan,
        "brief": res.get("brief", []),
        "sources": res.get("sources", []),
        "files": files,          # {filename: content}
        "issues": problems,      # ملاحظات مراجعة
    }
