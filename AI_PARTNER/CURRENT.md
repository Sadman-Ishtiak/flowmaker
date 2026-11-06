# flowmaker — Current objective

**Objective: M0 — Bootstrap (one-time setup)** — finish the runnable,
testable skeleton before any real feature work. Two tasks remain: **M0.1**
(the §2 skeleton) and **M0.4** (the import smoke test). Read §2 of
`PLAN.md` (data model + project layout) before touching files.

## Where you already are (as of 2026-11-06)

- ✅ `flowmaker.py` placeholder deleted, `flowmaker/` package created with
  an empty `__init__.py`, empty `tests/` and `examples/` directories
  created — **that is half of M0.1 already done by you**
- ⬜ `main.py` is still the template placeholder (tkinter IDE print) — it
  must become the stub CLI
- ⬜ `algorithm.txt` exists but is **0 bytes** — it needs sample content
- ⬜ M0.4 (`tests/test_imports.py`) not started

## What to do now — step by step

Work from the project root with the venv active:

```zsh
cd /home/sadman/Desktop/code/lab/flowmaker
source venv/bin/activate
```

### Step 1 — finish M0.1: rewrite `main.py`

Replace the whole placeholder body of `main.py` with a stub CLI. What it
must do (and nothing more):

- a `main()` function plus the `if __name__ == "__main__": main()` guard
- accept **one optional positional argument**: a directory —
  `python main.py [DIR]`
- **no argument** → fall back to `algorithm.txt` sitting next to
  `main.py` (resolve it relative to `__file__`, not the current working
  directory, so the fallback works from anywhere)
- with a directory: look for `*.flow` files inside it (sorted, so the
  order is deterministic); with none, say so but still exit 0
- a missing/invalid input gets a **friendly one-line message and exit
  code 2**, never a traceback
- since there is no parser yet (that is M1), the CLI only *announces*
  what it would convert. Hint: build it testable — `def main(argv=None)`
  that `return`s an int instead of calling `sys.exit()`, with
  `sys.exit(main())` at the bottom
- real input resolution, output naming and formats stay for M5

### Step 2 — give `algorithm.txt` some content

It is the default input, so give it the §1 sample from `PLAN.md` — the
factorial program with a WHILE loop. It does not need to parse yet; it
just has to be a real file the CLI can find.

### Step 3 — verify M0.1

Both of these must run and exit 0:

```zsh
python main.py            # announces the algorithm.txt fallback
python main.py examples   # accepts a directory (empty for now)
```

And the error paths must behave:

```zsh
python main.py does-not-exist   # friendly message, exit 2
mv algorithm.txt /tmp/a.bak; python main.py; mv /tmp/a.bak algorithm.txt
                                # friendly message, exit 2, then restore
```

When all pass, **tick M0.1 in `PLAN.md` §3**.

### Step 4 — M0.4: write `tests/test_imports.py`

In `tests/`, create a small test module that imports every module the
project has so far (the `flowmaker` package and `main`), so pytest catches
stray syntax errors after every later edit. Two tests are enough: one that
imports each module, one that asserts `main` exposes a callable
`main`. Tip: insert the project root into `sys.path` first so the tests
work from any working directory. Keep the module list easy to extend —
M1.1 will add `flowmaker.parser` to it.

### Step 5 — verify M0.4

```zsh
pytest
```

Today bare `pytest` exits 5 ("no tests ran"); this task is what turns the
suite green. After it, M0's acceptance holds: **`pytest` collects and
`python main.py` runs.** Tick M0.4 in `PLAN.md` §3.

### Step 6 — bookkeeping

Log both tasks in `COMPLETED.md`, then repoint this file at the next
task: **M1.1 — `FlowSyntaxError(message, line)` in `flowmaker/parser.py`**
(its `str()` prints `line N: message`).

## After M0 — M1 Parser preview

Start **M1 — Parser** (read §1 of `PLAN.md` and §7 gotchas first), in order:
**M1.1** `FlowSyntaxError(message, line)` in `flowmaker/parser.py` (its
`str()` prints `line N: message`) → M1.2 quote-aware `strip_comment` →
M1.3 `split_keyword` (case-insensitive) → M1.4 `parse_assignment`
(`SET x = e` / bare `x = e`, negative lookahead for `==`, compound ops,
`arr[i]`) → M1.5 `parse_simple` (`INPUT`, `OUTPUT`, `CALL`, `BREAK`,
`CONTINUE`, `STOP`) → M1.6–M1.9 block statements (`IF/ELIF/ELSE`,
`WHILE`, `REPEAT…UNTIL`, both `FOR` forms) → M1.10 `parse_func` →
M1.11 `parse_return` → M1.12 `parse_program` (with the parse-time context
checks: STOP inside FUNC, RETURN in main, duplicate FUNC names,
`FUNC main()` reserved) → M1.13 parametrised parser tests.
**M1 acceptance:** every `examples/*.flow` parses; broken input gets a
friendly one-line error with a line number.

Later milestones: M2 builder, M3 layout, M4 SVG+PNG, M5 CLI, M6 pagination,
M7 cross-cutting tests, M8 optional GUI (`python main.py --gui`,
customtkinter — no GUI work needed before then), M9 extras.

## Where M0 stands

- **M0.1 half done** — package/directories exist (your work, see above);
  remaining: rewrite `main.py` into the stub CLI and fill `algorithm.txt`
- **M0.2 done** — pytest 9.2.0 in the venv
- **M0.3 done** — cairosvg 2.9.1 imports cleanly; cairocffi 1.7.1 provides
  the PDF surface (`PDFSurface`, `set_size`, `show_page` verified);
  pycairo dropped from the plan
- **M0.4 open** — waits on M0.1 (there must be modules to import)

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
