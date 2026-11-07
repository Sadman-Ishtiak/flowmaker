# flowmaker — Current objective

> Lives in `AI_PARTNER/` — the working documents shared with the AI pair
> programmer. The public face of the project is the root `README.md`.

**Objective: M1 — Parser.** Current task: **M1.4 — `parse_assignment(rest)`
in `flowmaker/parser.py`**. Read §1 of `PLAN.md` (assignments) and §7
(the `==` gotcha). Work from the project root with the venv active:

```zsh
cd /home/sadman/Desktop/code/lab/flowmaker
source venv/bin/activate
```

## Where you already are (as of 2026-11-07)

- ✅ **M0 complete** — pytest collects (`2 passed`), `python main.py` runs
- ✅ **M1.1 done** — `FlowSyntaxError(message, line)`; `str()` prints
  `line N: message`; verified
- ✅ **M1.2 done** — `strip_comment(line)`; quote-aware; 7 asserts pass
- ✅ **M1.3 done** — `split_keyword(line)` → `(keyword, rest)`; blanks and
  `#`-lines return `None`; all asserts + `pytest` `2 passed`
- ⬜ M1.4 `parse_assignment` — not started (this task)
- ⬜ M1.5 onward — untouched

## What to do now — M1.4, step by step

1. Read PLAN.md §7 first — it holds the `==` gotcha this task exists for:
   a bare line like `x == 5` is a *condition*, not an assignment, and must
   NOT match. The trick: an `=` only counts when it is NOT followed by
   another `=` (a negative lookahead in regex, or the equivalent
   plain-Python check).
2. Add `parse_assignment(rest)` to `flowmaker/parser.py`. Contract:
   - input: `rest` — everything after the keyword `set`, or the whole
     stripped line for a bare assignment (`x = 1` without `SET`)
   - accepts: `x = expr`, `x += expr`, `x -= expr`, `x *= expr`,
     `x /= expr`, `x %= expr`, and indexed targets `arr[i] = expr`
   - rejects (raise `FlowSyntaxError`): nothing on the right of the
     operator, nothing on the left, no operator at all, and a line whose
     operator is actually `==` (comparison, not assignment)
   - returns a dict for now — `{"kind": "assignment", "target": ...,
     "op": ..., "expr": ...}` — the statement tree gets finalised with
     M1.12; expression text stays opaque (never evaluated, per §1)
   - whitespace-flexible around the operator; expression and target keep
     their inner spacing exactly as written
3. Verify from the venv:

   ```zsh
   python -c "
   from flowmaker.parser import parse_assignment
   a = parse_assignment('x = 1')
   assert a == {'kind': 'assignment', 'target': 'x', 'op': '=', 'expr': '1'}
   assert parse_assignment('y += n * 2')['op'] == '+='
   assert parse_assignment('arr[i] = fib(n)')['target'] == 'arr[i]'
   assert parse_assignment('x=1')['op'] == '='
   try:
       parse_assignment('x == 5')
       print('BAD: == accepted')
   except Exception:
       print('ok')"
   ```

   Expected: `ok` (the last check proves `==` is rejected). Then
   `pytest` — still `2 passed`.
4. Bookkeeping: tick M1.4 in `PLAN.md` §3, log it in `COMPLETED.md`,
   repoint this file at **M1.5 — `parse_simple`** (`INPUT`, `OUTPUT`,
   `CALL`, `BREAK`, `CONTINUE`, `STOP` — one node type each).

## Why this tiny task next

Assignments are the most common statement in real pseudocode, and the `==`
gotcha is the only real trap in the parser worth isolating in its own
task. Get this one right and M1.5's simple statements are trivial.

## M1 roadmap (after M1.3, in order)

M1.4 `parse_assignment` (`SET x = e` / bare `x = e`, negative lookahead for
`==`, compound ops, `arr[i]`) → M1.5 `parse_simple` (`INPUT`, `OUTPUT`,
`CALL`, `BREAK`, `CONTINUE`, `STOP`) → M1.6–M1.9 block statements
(`IF/ELIF/ELSE`, `WHILE`, `REPEAT…UNTIL`, both `FOR` forms) → M1.10
`parse_func` → M1.11 `parse_return` → M1.12 `parse_program` (parse-time
context checks: STOP inside FUNC, RETURN in main, duplicate FUNC names,
`FUNC main()` reserved) → M1.13 parametrised parser tests. **M1
acceptance:** every `examples/*.flow` parses; broken input gets a friendly
one-line error with a line number.

Later milestones: M2 builder, M3 layout, M4 SVG+PNG, M5 CLI, M6 pagination,
M7 cross-cutting tests, M8 optional GUI (`python main.py --gui`,
customtkinter — no GUI work needed before then), M9 extras.

## Venv packages — installed and verified working

| package | version | milestone | note |
|---|---|---|---|
| pytest | 9.2.0 | **M0.2 done** | test runner |
| CairoSVG | 2.9.1 | M4.11 | PNG export; installed early |
| cairocffi | 1.7.1 | M6.10 | PDF export (cairosvg transitive dep, verified) |
| customtkinter | 6.0.0 | M8.1 | optional GUI; installed early |
| pycairo | — | dropped | cairocffi covers PDF; needs system headers to build |

Everything except pytest is optional per the plan: missing cairosvg →
SVG-only fallback (M5.7); missing customtkinter → CLI still works (M8's
`try/except ImportError`). Python: 3.13.5. On Parrot/Debian, the M8 GUI
preview will additionally need the system package `python3-tk` (Tk itself
is not pip-installable).

---

## Workflow

When a micro-task is finished: tick its box in `PLAN.md` §3, log it in
`COMPLETED.md`, then update this file to point at the next task.
