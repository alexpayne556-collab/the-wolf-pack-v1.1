# GitHub Issue Templates

Brother, here are issue templates for different types of contributions. You can set these up in GitHub under Settings → Issues → Set up templates.

---

## Template 1: Bug Report

**File:** `.github/ISSUE_TEMPLATE/bug_report.md`

```markdown
---
name: 🐛 Bug Report
about: Something isn't working as expected
title: '[BUG] '
labels: bug
assignees: ''
---

## What Happened?

Describe the bug clearly.

## What Did You Expect?

What should have happened instead?

## Steps to Reproduce

1. 
2. 
3. 

## Environment

- Python version:
- OS:
- Which script:

## Screenshots/Logs

If applicable, paste error messages or logs here.
```

---

## Template 2: Theory to Test

**File:** `.github/ISSUE_TEMPLATE/theory_test.md`

```markdown
---
name: 💡 Theory to Test
about: Propose a trading theory for backtesting
title: '[THEORY] '
labels: research
assignees: ''
---

## The Claim

What's the theory? (e.g., "Stocks that gap up 5%+ on earnings tend to continue higher")

## Source

Where did this come from? (Book, trader, your own observation?)

## How to Test

Describe the backtest setup:
- Timeframe:
- Entry conditions:
- Exit conditions:
- Position sizing:

## Expected Result

What would validate this theory? What would bust it?

## Why This Matters

Why is this worth testing?
```

---

## Template 3: Code Contribution

**File:** `.github/ISSUE_TEMPLATE/code_contribution.md`

```markdown
---
name: 🔧 Code Contribution
about: Propose a code improvement or new feature
title: '[CODE] '
labels: enhancement
assignees: ''
---

## What Does This Do?

Describe the improvement/feature clearly.

## Why Is This Useful?

How does this help the pack?

## Approach

How would you implement this?

## Testing Plan

How do we validate it works?

## Breaking Changes?

Will this break existing functionality?
```

---

## Template 4: Research Findings

**File:** `.github/ISSUE_TEMPLATE/research_findings.md`

```markdown
---
name: 📊 Research Findings
about: Share research or analysis results
title: '[RESEARCH] '
labels: research
assignees: ''
---

## What Did You Test?

Be specific.

## Methodology

How did you test it?
- Data source:
- Timeframe:
- Sample size:
- Filters applied:

## Results

Numbers, charts, observations.

## Conclusion

Does this work? Should we integrate it?

## Concerns/Limitations

What are the weaknesses of this analysis?
```

---

## Template 5: Help Wanted

**File:** `.github/ISSUE_TEMPLATE/help_wanted.md`

```markdown
---
name: 🆘 Help Wanted
about: Need pack assistance on something
title: '[HELP] '
labels: help wanted
assignees: ''
---

## What Do You Need Help With?

Be specific about the problem.

## What Have You Tried?

Show your work so far.

## What's Blocking You?

Why can't you solve this alone?

## Ideal Outcome

What would success look like?
```
