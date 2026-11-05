"""Question judge (SPEC #6): a small model grades each question the assistant asked the junior.
good = could change the plan (some answer leads to different work) AND plain words AND states a default."""
import json, subprocess

JUDGE_MODEL = "haiku"
TIMEOUT_S = 120
PROMPT = """QUESTION-JUDGE. Grade the questions an AI assistant asked a junior developer.
Junior request: {request}
Assistant reply: {reply}
A question = a sentence asking the junior to decide or answer (offers like "want me to...?" count).
Statements of next steps are NOT questions. For each question, set:
plan = some possible answer would lead to different work (a confirmed default still counts as true)
plain = a non-expert understands it without jargon
default = the reply says what will happen if the junior does not choose
Reply with ONLY a JSON list, no prose: [{{"q": "<question>", "plan": true, "plain": true, "default": true, "why": "<5-10 words>"}}]
No questions -> []"""


def judge(request, reply, cwd):
    """Returns (verdicts, tokens). verdict = {q, plan, plain, default, why, good}."""
    from run import parse  # late import: run imports this module
    cmd = ["claude", "-p", PROMPT.format(request=request, reply=reply), "--model", JUDGE_MODEL,
           "--setting-sources", "project,local", "--strict-mcp-config", "--no-session-persistence",
           "--tools", "", "--max-turns", "1", "--output-format", "stream-json", "--verbose"]
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=TIMEOUT_S, stdin=subprocess.DEVNULL)
    t, tok, _ = parse(p.stdout, "question judge")
    raw = (t["final"] or "").strip()
    raw = raw[raw.find("["):raw.rfind("]") + 1]  # tolerate a code fence around the JSON
    try:
        verdicts = json.loads(raw)
    except json.JSONDecodeError:
        raise RuntimeError(f"question judge gave no JSON: {t['final']!r}")
    for v in verdicts:
        v["good"] = bool(v["plan"] and v["plain"] and v["default"])
    return verdicts, tok
