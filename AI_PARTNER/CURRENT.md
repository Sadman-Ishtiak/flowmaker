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
- ✅ **M1.3 done** — `split_keyword(line)` → `(keyword, rest)`; runs
  `strip_comment` itself (raw line in → keyword out); 8 asserts pass
- ⬜ **Migration task: merge parser into `main.py`** (this task)
- ⬜ M1.4 `parse_assignment` — next code task, appended to main.py

## What to do now — merge, step by step

1. Open `main.py` in nano. Jump to the guard line with Ctrl+_ (type 28,
   Enter) — the line that reads `if __name__ == "__main__" :`
2. **Insert the parser section directly above that line** (so the guard
   automatically ends up last, per the §2 amendment). The section needs
   no imports — none of its three pieces use `sys` or `Path`; the
   imports already at the top of `main.py` cover the CLI section. Type:

   ```python
   # ---------- parser section (M1) ----------

   class FlowSyntaxError(Exception):
       def __init__(self, message, line):
           super().__init__(f"line {line}: {message}")
           self.message = message
           self.line = line


   def strip_comment(line):
       in_string = False
       for index, char in enumerate(line):
           if char == '"':
               in_string = not in_string
           elif char == "#" and not in_string:
               return line[:index].rstrip()
       return line.rstrip()


   def split_keyword(line):
       line = strip_comment(line)
       if not line.strip():
           return None
       parts = line.strip().split(" ", 1)
       keyword = parts[0].lower()
       rest = parts[1] if len(parts) == 2 else ""
       return keyword, rest


   ```
3. Save (Ctrl+O, Enter), exit (Ctrl+X). `python main.py` must behave
   exactly as before (announces algorithm.txt; exit 0).
4. Say "done" — the AI partner verifies, dictates the one-line
   `tests/test_imports.py` fix (drop `import flowmaker`), and asks
   before deleting the retired `flowmaker/` directory.

## Then continue with M1.4 — parse_assignment

Appended to the *new parser section in main.py* (directly above the
`# guard` block at the bottom of the file — never below it):

```python
def parse_assignment(rest, line=0):
    t = rest.strip()
    if "==" in t:
        raise FlowSyntaxError("'==' is a comparison, not an assignment", line)
    for op in ("+=", "-=", "*=", "/=", "%=", "="):
        if op in t:
            target, expr = t.split(op, 1)
            if not target.strip() or not expr.strip():
                raise FlowSyntaxError("assignment needs a variable and an expression", line)
            return {"kind": "assignment", "target": target.strip(), "op": op, "expr": expr.strip()}
    raise FlowSyntaxError("assignment needs an '='", line)
```

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
