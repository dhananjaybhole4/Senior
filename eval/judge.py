"""Question judge (SPEC #6): a small model grades each question the assistant asked the junior.
good = could change the plan (some answer leads to different work) AND plain words AND states a default."""
import json, re, subprocess

JUDGE_MODEL = "haiku"
TIMEOUT_S = 120
VOTES = 1  # a majority of 3 passes did not help on borderline items (4/6 vs 8/10 single) and costs 3x; kept as a knob
PROMPT = """QUESTION-JUDGE. An AI assistant answered a junior developer's request. Grade each numbered question it asked.
Junior request: {request}
Assistant reply: {reply}
Questions to grade (extracted from the reply, in order):
{items}
For each, set:
real = it asks the junior to decide or answer something; false for a pure go-ahead ("say go", "ok to proceed?") with no choice offered
plan = some possible answer would lead to different work (a confirmed default still counts as true)
plain = a junior who knows Claude Code and sees this project's own files and function names understands it; only unexplained concepts count as jargon, project names do not
default = the reply says what will happen if the junior does not choose
Reply with ONLY a JSON list with one object per numbered question, same order: [{{"n": 1, "real": true, "plan": true, "plain": true, "default": true, "why": "<5-10 words>"}}]"""


def extract_questions(reply):
    """Sentences that end in '?': mechanical, so every judge call grades the same items."""
    text = re.sub(r"[*_`]", "", reply)
    return [m.strip(" -•\t\n") for m in re.findall(r"[^.!?\n]*[^.!?\n]\?", text) if len(m.strip()) > 8]


def grade_once(request, reply, items, cwd):
    """One judge pass. Returns (list of per-item dicts, tokens)."""
    from run import parse  # late import: run imports this module
    numbered = "\n".join(f"{i}. {q}" for i, q in enumerate(items, 1))
    cmd = ["claude", "-p", PROMPT.format(request=request, reply=reply, items=numbered), "--model", JUDGE_MODEL,
           "--setting-sources", "project,local", "--strict-mcp-config", "--no-session-persistence",
           "--tools", "", "--max-turns", "1", "--output-format", "stream-json", "--verbose"]
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=TIMEOUT_S, stdin=subprocess.DEVNULL)
    t, tok, _ = parse(p.stdout, "question judge")
    raw = (t["final"] or "").strip()
    raw = raw[raw.find("["):raw.rfind("]") + 1]  # tolerate a code fence around the JSON
    try:
        graded = json.loads(raw)
    except json.JSONDecodeError:
        raise RuntimeError(f"question judge gave no JSON: {t['final']!r}")
    if [g["n"] for g in graded] != list(range(1, len(items) + 1)):
        raise RuntimeError(f"question judge graded {[g['n'] for g in graded]}, expected 1..{len(items)}")
    return graded, tok


def judge(request, reply, cwd):
    """Returns (verdicts, tokens): per-criterion majority over VOTES passes. verdict = {q, real, plan, plain, default, why, good}."""
    items = extract_questions(reply)
    if not items:
        return [], 0
    passes, tokens = [], 0
    for _ in range(VOTES):
        graded, tok = grade_once(request, reply, items, cwd)
        passes.append(graded); tokens += tok
    verdicts = []
    for i, q in enumerate(items):
        v = {k: sum(bool(p[i][k]) for p in passes) * 2 > VOTES for k in ("real", "plan", "plain", "default")}
        if v["real"]:
            verdicts.append({"q": q, **v, "why": passes[0][i]["why"], "good": v["plan"] and v["plain"] and v["default"]})
    return verdicts, tokens
