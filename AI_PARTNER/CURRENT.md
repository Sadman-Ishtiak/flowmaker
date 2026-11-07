# flowmaker — Current objective

> Lives in `AI_PARTNER/` — the working documents shared with the AI pair
> programmer. The public face of the project is the root `README.md`.

**Objective: M1 — Parser.** Current task: **M1.2 — quote-aware
`strip_comment(line)` in `flowmaker/parser.py`**. Read §1 of `PLAN.md`
(the input language: "`#` starts a comment, except inside quoted strings").
Work from the project root with the venv active:

```zsh
cd /home/sadman/Desktop/code/lab/flowmaker
source venv/bin/activate
```

## Where you already are (as of 2026-11-07)

- ✅ **M0 complete** — pytest collects (`2 passed`), `python main.py` runs
- ✅ **M1.1 done** — `FlowSyntaxError(message, line)` in
  `flowmaker/parser.py`; `str()` prints `line N: message`; verified
- ⬜ M1.2 `strip_comment` — not started (this task)
- ⬜ M1.3 onward — untouched

## What to do now — M1.2, step by step

1. Add `strip_comment(line)` to `flowmaker/parser.py` (below the class).
   Contract:
   - takes one line of `.flow` text, returns the same line with any
     comment removed
   - a `#` starts a comment **only when it is not inside `"..."` quotes**
   - strip trailing whitespace left behind (the spaces before the `#`)
   - keep it character-simple: toggle an `in_string` flag on each `"`;
     no escape handling yet (the plan doesn't require it in M1.2)
2. Verify from the venv — the four cases that matter:

   ```zsh
   python -c "
   from flowmaker.parser import strip_comment
   assert strip_comment('SET x = 1  # init') == 'SET x = 1'
   assert strip_comment('OUTPUT \"has # inside\"') == 'OUTPUT \"has # inside\"'
   assert strip_comment('# whole line') == ''
   assert strip_comment('SET url = \"a#b\"  # note') == 'SET url = \"a#b\"'
   print('ok')"
   ```

   Expected output: `ok` (any other output: read the traceback).
3. Run `pytest` — still `2 passed`.
4. Bookkeeping: tick M1.2 in `PLAN.md` §3, log it in `COMPLETED.md`,
   repoint this file at **M1.3 — `split_keyword(line)`** (lowercases the
   keyword for case-insensitive dispatch; returns `(keyword, rest)` and
   blank/comment-only lines are skipped by the caller).

## Why this tiny task next

Every later parser step works on comment-free text: M1.3's keyword split,
M1.4's `==` lookahead, all of it would misfire on `x = 5 # not == 6`.
Stripping comments once, in one tested place, keeps every later rule simple.

## M1 roadmap (after M1.2, in order)

M1.3 `split_keyword` (case-insensitive) → M1.4 `parse_assignment` (`SET x = e`
/ bare `x = e`, negative lookahead for `==`, compound ops, `arr[i]`) →
M1.5 `parse_simple` (`INPUT`, `OUTPUT`, `CALL`, `BREAK`, `CONTINUE`, `STOP`)
→ M1.6–M1.9 block statements (`IF/ELIF/ELSE`, `WHILE`, `REPEAT…UNTIL`, both
`FOR` forms) → M1.10 `parse_func` → M1.11 `parse_return` → M1.12
`parse_program` (parse-time context checks: STOP inside FUNC, RETURN in
main, duplicate FUNC names, `FUNC main()` reserved) → M1.13 parametrised
parser tests. **M1 acceptance:** every `examples/*.flow` parses; broken
input gets a friendly one-line error with a line number.

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
