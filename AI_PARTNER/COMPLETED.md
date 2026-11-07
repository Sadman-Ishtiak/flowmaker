# flowmaker — Completed work

> Lives in `AI_PARTNER/` — the working documents shared with the AI pair
> programmer. The public face of the project is the root `README.md`.

A running log of finished work. Workflow when a task is done: tick its box
in `PLAN.md` §3, add a line here, and point `CURRENT.md` at the next task.

---

## Done

### Planning
- [x] Wrote `PLAN.md` — the full project plan: input language spec (§1),
      data model + project layout (§2), build order (§3), layout recipe (§4),
      pagination design (§5), SVG cheat sheet (§6), gotchas (§7),
      definition of done (§8)
- [x] Decomposed §3 "Build order" into **96 numbered micro-tasks**
      (`M0.1`–`M9.6`), each a single unit of work: one install, one file,
      one function, or one test group
      - Added **M0 — Bootstrap** for one-time setup (package skeleton,
        pytest, cairosvg/cairocffi backends, import smoke test)
      - Moved per-milestone tests next to the code they cover
        (M1.13, M2.16, M4.12, M6.11); M7 keeps only cross-cutting tests
        (golden harness, format × mode matrix, hostile inputs, suite budget)
      - Kept the format × mode table and the single/one-page/split
        definitions inside M5; every milestone keeps its acceptance line
      - Updated §8 definition of done to "All M0–M7 micro-tasks checked
        (M8 extras are optional)"
- [x] Reworked the entry point to a **single `main.py`**: optional
      positional directory argument (converts the `.flow` files in it);
      with no argument it falls back to `algorithm.txt` sitting next to
      `main.py`. Dropped the `flowmaker/__main__.py` + `cli.py` package
      entry from §2 and rewrote M0.1 + the whole M5 milestone for it
      (input resolution, directory mode, `algorithm.txt` fallback tests)
- [x] Added **M8 — GUI: text editor + live flowchart preview**
      (`python main.py --gui`): optional customtkinter editor (verified
      actively maintained — 6.0.0, MIT) with a live preview that re-renders
      as you type; preview prefers a zero-dependency native `tk.Canvas`
      drawn from layout geometry (Tk cannot render SVG natively), with a
      cairosvg-PNG fallback; debounced ~300 ms re-render on the Tk main
      thread; friendly error banner with line numbers; imports sit behind
      `try/except ImportError` so the CLI never requires the GUI. Former
      M8 "Extras" renumbered to **M9** (M8.x → M9.x) and all §1/§5/§8
      cross-references updated

### Environment
- [x] Created the virtualenv `venv/` (Python 3.13)
- [x] Installed libraries in the venv, all verified working
      (`pytest --version`; `import cairosvg`; `import customtkinter`):
      - `pytest` 9.2.0 → **M0.2 done** (ticked in `PLAN.md` §3)
      - `CairoSVG` 2.9.1 → M4.11 dependency (PNG export), installed early
      - `customtkinter` 6.0.0 → M8.1 dependency (optional GUI), installed early
      - plus transitive dependencies: cairocffi, cffi, pycparser, cssselect2,
        defusedxml, tinycss2, pillow, webencodings, darkdetect, packaging,
        iniconfig, pluggy, Pygments
- [x] `pycairo` **not installed — and no longer needed** (decision record,
      verified 2026-11-06 — nothing to install): pycairo is a set
      of compiled C extension modules linking libcairo; with no Linux wheels
      pip builds it from source, which requires system headers
      (`libcairo2-dev pkg-config python3-dev`). The plan now uses
      **cairocffi** (a pure-Python cffi binding, already present as a
      cairosvg transitive dep — its `PDFSurface.set_size`/`show_page` were
      verified in the venv) for PDF export instead, so nothing more to
      install; PDF export is now part of the cairosvg dependency set

### Code (M0 complete — 2026-11-07)
- [x] M0.1 finished: the user rewrote `main.py` into the stub CLI by hand —
      two small functions (`no_args_function`, `arg_given_function`)
      dispatched on `len(sys.argv)`, friendly one-line errors via
      `sys.exit(2)` inside the functions. Style note: no `main(argv=None)`
      returning an int — that was the plan's hint, the user chose the
      simpler style; revisit when M5 makes the CLI testable
- [x] M0.1 verified, all four behaviours: fallback announces `algorithm.txt`
      (exit 0), empty `examples/` directory (exit 0), nonexistent directory
      (exit 2), missing `algorithm.txt` (exit 2)
- [x] M0.1 finished: `algorithm.txt` filled with the §1 factorial sample
      (START / SET / INPUT / WHILE / OUTPUT / STOP)
- [x] M0.4 done: `tests/test_imports.py` — two tests (imports of `flowmaker`
      + `main`; callability of both functions). First attempt was named
      `tests_imports.py` (pytest only collects `test_*.py` → "collected 0
      items", exit 5) and its bodies had lost indentation when retyped;
      renamed and fixed → `2 passed in 0.05s`, exit 0. M0 acceptance holds:
      pytest collects and `python main.py` runs

### Code (M1 in progress — as of 2026-11-07)
- [x] M1.1 done: `flowmaker/parser.py` created with `FlowSyntaxError(message,
      line)` subclassing Exception. `str()` prints `line N: message` (passed
      to `super().__init__`, so the formatting lives in one place) while
      `.message` and `.line` stay available as attributes. Two failed
      attempts first (class header missing / stray space before the colon,
      nano save lost) — final version written in one piece and verified:
      assert passes, `pytest` still `2 passed`

- [x] M1.2 done: `strip_comment(line)` in `flowmaker/parser.py` — a `#` starts
      a comment only outside `"..."` (an `in_string` flag toggles on each
      `"`); the comment and the spaces before it are `rstrip()`ed; a line
      with no comment comes back unchanged, indentation kept. Three paste
      mishaps fixed along the way (a literal `EOF` line pasted from a
      `cat` heredoc, `nor` for `not`, `lstrip` where `rstrip` was meant —
      the last one caught by asserting indented no-comment lines survive
      intact). Verified: 7 asserts pass, `pytest` still `2 passed`
- [x] M1.3 done: `split_keyword(line)` in `flowmaker/parser.py` — design
      improved at the user's suggestion: the function calls
      `strip_comment(line)` itself, so its contract is "raw line in →
      (keyword, rest) out" and comment handling lives in exactly one
      place; the earlier standalone `#`-check became dead code (any
      comment-only line is already `""` after stripping) and was removed.
      Blank/whitespace-only input returns `None` (how the caller skips
      lines), `split(" ", 1)` keeps inner spaces of `rest`, keyword is
      lowercased once. Verified: 8 asserts (including trailing-comment
      and quoted-`#` lines) + regression on M1.1/M1.2, `pytest` still
      `2 passed`. Note for M1.12: returns `(keyword, rest)` — the plan's
      `line_no` third slot is attached by the caller, the only place
      that knows it

### Architecture (2026-11-07)
- [x] **Single-file decision** (user, time-constrained): the whole program
      lives in one `main.py` (~500–600 lines target), organised as marked
      sections in pipeline order — CLI, parser, model, builder, layout,
      pagination, render, export, gui, guard-last. PLAN.md §2 rewritten,
      §3 carries a global amendment note. Consequences:
      `flowmaker/` package (parser.py, `__init__.py`) is retired — parser
      code merges into main.py, then the directory is deleted;
      `tests/test_imports.py` drops the `import flowmaker` line so the
      suite stays green; all M1.4+ tasks append to main.py directly, no
      future big move. Verification (asserts + pytest) is run by the AI
      partner, not the user — user only hand-types the code blocks

### Audit (2026-11-06)
- [x] Full verification sweep of the project state against these three
      files: filesystem (only the two stubs + venv exist — no `flowmaker/`
      package, `tests/`, `examples/`, `algorithm.txt`), venv packages and
      versions (`pytest --version`; imports of cairosvg / cairocffi /
      customtkinter; full `pip list` cross-checked against the dependency
      list above), behaviour (`python main.py` placeholder exits 0; bare
      `pytest` exits 5 "no tests ran"), and `PLAN.md` checkbox integrity
      (96 micro-tasks; only M0.2/M0.3 ticked; 107 open = 94 micro-tasks +
      13 §8 definition-of-done items). No discrepancies found beyond the
      two formatting fixes above; at audit time M0.1/M0.4 were still open
      (both completed later the same day — see "Code (M0 complete)")

---

## Not started yet

**M0 is complete** (M0.1–M0.4 all ticked, 2026-11-07): pytest collects and
`python main.py` runs.

Next up: **M1 — Parser**, starting with **M1.1** — `FlowSyntaxError(message,
line)` in `flowmaker/parser.py`, whose `str()` prints `line N: message`
(see the step-by-step guide in `CURRENT.md`).
