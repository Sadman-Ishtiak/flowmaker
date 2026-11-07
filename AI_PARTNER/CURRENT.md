# flowmaker — Current objective

> Lives in `AI_PARTNER/` — the working documents shared with the AI pair
> programmer. The public face of the project is the root `README.md`.

**Objective: M1 — Parser.** Current task: **M1.1 — `FlowSyntaxError(message,
line)` in `flowmaker/parser.py`**, whose `str()` prints `line N: message`.
Read §1 of `PLAN.md` (the input language) and §7 (gotchas) before writing
parser code. Work from the project root with the venv active:

```zsh
cd /home/sadman/Desktop/code/lab/flowmaker
source venv/bin/activate
```

## Where you already are (as of 2026-11-07)

- ✅ **M0 complete** — M0.1 (skeleton + stub CLI + filled `algorithm.txt`)
  and M0.4 (`tests/test_imports.py`, `2 passed`) done and verified;
  M0.2 (pytest 9.2.0) and M0.3 (cairosvg/cairocffi) were done earlier.
  M0 acceptance holds: pytest collects, `python main.py` runs.
- ⬜ `flowmaker/parser.py` does not exist yet — M1.1 creates it
- ⬜ Everything in M1 after M1.1 is untouched

## What to do now — M1.1, step by step

1. Create `flowmaker/parser.py` with one thing in it: the exception class.
   Contract from the plan:
   - `FlowSyntaxError(message, line)` — two arguments
   - `str(err)` prints exactly `line N: message` (N = the line number)
   - it must subclass `Exception` so normal `try/except` and pytest work
   - nothing else in the file yet — `strip_comment` and friends are M1.2+
2. Verify it from the venv (no test file needed yet — M1.13 tests the
   parser properly; M0.4's import test will already catch syntax errors
   once the module exists):

   ```zsh
   python -c "
   from flowmaker.parser import FlowSyntaxError
   e = FlowSyntaxError('unknown statement', 12)
   print(str(e)); assert str(e) == 'line 12: unknown statement'
   print('ok')"
   ```

   Expected output: `line 12: unknown statement` then `ok`.
3. Run `pytest` — should still be `2 passed` (the import smoke test now
   covers `flowmaker.parser` transitively via the package import).
4. Bookkeeping: tick M1.1 in `PLAN.md` §3, log it in `COMPLETED.md`,
   repoint this file at **M1.2 — quote-aware `strip_comment(line)`**.

## Why this tiny task first

Every later parser task raises `FlowSyntaxError` with a line number, so the
error type is the foundation. Getting `str()` right now means every future
error message ("line 12: unknown statement") is one `raise` away, and the
M1 acceptance ("broken input gets a friendly one-line error with a line
number") falls out naturally.

## M1 roadmap (after M1.1, in order)

M1.2 quote-aware `strip_comment` → M1.3 `split_keyword` (case-insensitive)
→ M1.4 `parse_assignment` (`SET x = e` / bare `x = e`, negative lookahead
for `==`, compound ops, `arr[i]`) → M1.5 `parse_simple` (`INPUT`, `OUTPUT`,
`CALL`, `BREAK`, `CONTINUE`, `STOP`) → M1.6–M1.9 block statements
(`IF/ELIF/ELSE`, `WHILE`, `REPEAT…UNTIL`, both `FOR` forms) → M1.10
`parse_func` → M1.11 `parse_return` → M1.12 `parse_program` (parse-time
context checks: STOP inside FUNC, RETURN in main, duplicate FUNC names,
`FUNC main()` reserved) → M1.13 parametrised parser tests.
**M1 acceptance:** every `examples/*.flow` parses; broken input gets a
friendly one-line error with a line number.

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
