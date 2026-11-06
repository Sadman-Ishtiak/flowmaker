# flowmaker

Turn simple pseudocode (`.flow` files) into flowchart diagrams — SVG, PNG,
or PDF — without drawing anything by hand or wiring up a graphical
flowchart editor.

You write plain statements like `SET`, `IF ... THEN`, `WHILE`, `FOR`,
`INPUT`, `OUTPUT`, and `CALL`; flowmaker parses them and renders the
matching flowchart: rectangles for assignments, diamonds for decisions,
parallelograms for I/O, loop-backs for `WHILE`/`REPEAT`/`FOR`, and a
separate chart for every `FUNC`.

```
program.flow ──► parser ──► statement tree ──► builder ──► flowchart graph
                                                        ──► layout ──► pagination ──► SVG / PNG / PDF
```

**Status: early development — planning complete, bootstrap (M0) in
progress. No parser yet.**

## Features (planned)

- **Pseudocode in, flowchart out** — one statement per line,
  case-insensitive keywords, `#` comments, explicit block terminators
  (`ENDIF`, `ENDWHILE`, …) so indentation is cosmetic
- **Zero-dependency core** — the language→SVG pipeline uses only the
  standard library
- **Three output formats** — SVG (default), PNG at `--dpi`, and PDF;
  one large canvas, scaled to one page, or automatically split across
  A4/A5/Letter pages with off-page connectors
- **Function charts** — every `FUNC` gets its own flowchart next to the
  main one; recursion can't blow up the graph
- **Optional GUI** (`python main.py --gui`) — a text editor with a live
  flowchart preview that re-renders as you type; the CLI works fine
  without it

## Current state

What exists today:

- `flowmaker/` package skeleton (empty `__init__.py`) plus empty
  `tests/` and `examples/` directories
- `main.py` — still the placeholder (a tkinter-IDE print statement);
  becomes the CLI in milestone M0.1
- `algorithm.txt` — the default input file, still empty
- `autopush.sh` — a small helper that loops once a minute, auto-commits
  with a timestamped message, and pushes to GitHub (run
  `./autopush.sh`; `AUTOPUSH_INTERVAL=10 ./autopush.sh` for a faster
  loop)
- `PLAN.md` — the full project plan: language spec, data model, 96
  micro-tasks across milestones M0–M9, layout recipe, pagination
  design, gotchas
- `CURRENT.md` / `COMPLETED.md` — work-tracking log pointing at the
  next micro-task

Milestones:

| milestone | scope | status |
|---|---|---|
| M0 | Bootstrap: skeleton, pytest, backends, import test | in progress (2 of 4 tasks done) |
| M1 | Parser: `.flow` → statement tree | not started |
| M2 | Builder: statement tree → flowchart graph | not started |
| M3 | Layout: level/column assignment, edge routing | not started |
| M4 | SVG renderer + PNG export | not started |
| M5 | CLI: modes, exit codes, output naming | not started |
| M6 | Pagination: page packing, connectors, PDF | not started |
| M7 | Cross-cutting tests | not started |
| M8 | Optional GUI (customtkinter) | not started |
| M9 | Extras (Mermaid output, themes, …) | not started |

Environment, verified working: Python 3.13.5 in `venv/`, with
`pytest` 9.2.0, `cairosvg` 2.9.1 (PNG), `cairocffi` 1.7.1 (PDF, via
`cairosvg`), and `customtkinter` 6.0.0 (optional GUI) installed. The
only hard dependency for later PNG/PDF export is `cairosvg`; everything
except pytest is optional — missing backends degrade gracefully
(SVG-only output, CLI without GUI).

## The input language (planned)

One statement per line; keywords are case-insensitive; `#` starts a
comment (except inside quoted strings); blocks end with explicit
terminators.

```
# Factorial with a WHILE loop
START
SET factorial = 1
INPUT n
SET counter = 1
WHILE counter <= n
    SET factorial = factorial * counter
    SET counter = counter + 1
ENDWHILE
OUTPUT factorial
STOP
```

Functions are charted separately — `CALL fib(k)` stays a single
subroutine box in the main chart while `FUNC fib(n) ... ENDFUNC` gets
its own flowchart:

```
FUNC fib(n)
    IF n <= 1 THEN
        RETURN n
    ENDIF
    RETURN fib(n - 1) + fib(n - 2)
ENDFUNC
```

Full statement reference: `PLAN.md` §1.

## Usage (target — not implemented yet)

```bash
python main.py              # converts algorithm.txt next to main.py
python main.py examples/    # converts every *.flow in the directory
python main.py examples/ --format png --dpi 300
python main.py examples/ --format pdf --page-size a4 --mode split
python main.py --gui        # editor + live preview (optional, M8)
```

Exit codes: `0` ok, `1` syntax error (message with line number), `2`
I/O error or missing backend.

## Development

```bash
python -m venv venv
source venv/bin/activate
pip install pytest cairosvg customtkinter
pytest          # test suite (M0.4 adds the first tests)
python main.py  # currently prints a placeholder message
```

Project docs:

- `PLAN.md` — the plan of record: language (§1), data model + layout
  (§2), milestones (§3), layout recipe (§4), pagination (§5), SVG
  notes (§6), gotchas (§7), definition of done (§8)
- `CURRENT.md` — the current objective and step-by-step instructions
- `COMPLETED.md` — log of finished work

## License

CC0 1.0 (public domain) — see `LICENSE`.
