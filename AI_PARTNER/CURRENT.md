# flowmaker — Current objective

> Lives in `AI_PARTNER/` — the working documents shared with the AI pair
> programmer. The public face of the project is the root `README.md`.

**Objective: M1 — Parser.** Current task: **M1.3 — `split_keyword(line)` in
`flowmaker/parser.py`**. Read §1 of `PLAN.md` (keywords are
case-insensitive; one statement per line). Work from the project root with
the venv active:

```zsh
cd /home/sadman/Desktop/code/lab/flowmaker
source venv/bin/activate
```

## Where you already are (as of 2026-11-07)

- ✅ **M0 complete** — pytest collects (`2 passed`), `python main.py` runs
- ✅ **M1.1 done** — `FlowSyntaxError(message, line)`; `str()` prints
  `line N: message`; verified
- ✅ **M1.2 done** — `strip_comment(line)`; quote-aware; 7 asserts pass
- ⬜ M1.3 `split_keyword` — not started (this task)
- ⬜ M1.4 onward — untouched

## What to do now — M1.3, step by step

1. Add `split_keyword(line)` to `flowmaker/parser.py` (below
   `strip_comment`). Contract from PLAN.md §3:
   - `split_keyword(line)` → `(keyword, rest)`: the first word lowercased
     (case-insensitive dispatch: `IF` = `if`), everything after the first
     space is `rest`
   - the plan writes the return as `(keyword, rest, line_no)`; the line
     number is attached by M1.12's caller, the only place that knows it —
     the helper stays two-valued (decision recorded here so M1.12 is not
     surprised)
   - blank input — empty or whitespace-only, which includes lines that
     were only a comment before `strip_comment` ran — returns `None`;
     that is how the caller skips such lines
   - `rest` is `''` when the line is the keyword alone (`STOP`)
   - raises nothing; unknown keywords are the caller's problem (M1.12)
2. Verify from the venv:

   ```zsh
   python -c "
   from flowmaker.parser import split_keyword
   assert split_keyword('SET x = 1') == ('set', 'x = 1')
   assert split_keyword('  if x > 0 then') == ('if', 'x > 0 then')
   assert split_keyword('stop') == ('stop', '')
   assert split_keyword('') is None
   assert split_keyword('   ') is None
   assert split_keyword('# only a comment') is None
   print('ok')"
   ```

   Expected: `ok`. Then `pytest` — still `2 passed`.
3. Bookkeeping: tick M1.3 in `PLAN.md` §3, log it in `COMPLETED.md`,
   repoint this file at **M1.4 — `parse_assignment`** (`SET x = e` / bare
   `x = e`, the `==` negative-lookahead gotcha from §7, compound ops,
   `arr[i]`).

## Why this tiny task next

`split_keyword` is the router every other parser piece plugs into: M1.4
and M1.5 each receive `(keyword, rest)` and handle only their own keyword;
case-insensitivity lives here exactly once, not in every handler.

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
