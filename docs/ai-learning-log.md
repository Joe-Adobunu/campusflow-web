# AI Learning Log — CampusFlow

Each entry records one full learning loop: a specific gap in my
understanding, the AI interaction, my own experiment, verification from
output or a test, and a decision.

**Fellow: Joe-Adobunu**

---

## Interaction #1 — Why priority rules must be evaluated in order

**Problem.**
The spec lists four priority rules and says "apply the first match." I
didn't understand why reordering them would change the answer — I assumed
the rules were independent and that only one could ever apply.

**My initial understanding.**
I planned to write the rules as four independent `if` statements, then
return whichever value was set last.

**Prompt to AI.**
"Explain why order matters in a first-match rule set. Give me a small
unrelated example where reordering the rules changes the outcome — not
helpdesk tickets."

**Useful AI guidance.**
AI pointed out that the rules overlap. A `high`-urgency ticket with 12
users satisfies Rule 1, Rule 2, and Rule 3 simultaneously. If Rule 3 is
evaluated first, the ticket is classified as `medium` instead of
`critical`. First-match ordering is what makes overlapping rules safe.

**My independent experiment.**
In a scratch file I ran:

```python
def wrong(a, b):
    if b >= 3: return "medium"
    if a == "high" and b >= 10: return "critical"
    return "low"

def right(a, b):
    if a == "high" and b >= 10: return "critical"
    if b >= 3: return "medium"
    return "low"

print(wrong("high", 12), right("high", 12))
