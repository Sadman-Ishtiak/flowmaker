# flowmaker — Project Plan

> Lives in `AI_PARTNER/` — the working documents shared with the AI pair
> programmer. The public face of the project is the root `README.md`.

Turn simple pseudocode (`.flow` files) into flowchart diagrams (SVG / PNG).

**Entry point: one `main.py`.** Run it with an optional directory argument —
`python main.py [DIR]`. With a directory it converts the `.flow` files found
there; with no argument it looks for `algorithm.txt` next to `main.py` and
converts that. No `python -m flowmaker` package entry, no separate cli
module — `main.py` IS the CLI (arg parsing, exit codes, output naming).

**Optional GUI:** `python main.py --gui` opens a minimal text editor with a
**live flowchart preview** that re-renders as you type (M8, customtkinter).
The GUI is never a hard dependency — without it `main.py` stays a pure CLI.

```
program.flow ──► parser ──► statement tree ──► builder ──► flowchart graph ──► layout ──► pagination ──► one big SVG/PNG or page SVGs / PDF
```

Goal: write everything yourself. The core (language → SVG) comes with zero
dependencies. PNG and PDF export are first-class features backed by **one
pip dependency total**: `cairosvg` (for PNG rasterisation), whose
transitive dependency `cairocffi` also provides the PDF surface
(`PDFSurface`, `set_size`, `show_page`); when the dependency is missing the
tool says so instead of crashing.
Two output modes from the same layout: a single large canvas (SVG/PNG) for
screens and embedding, or automatic splitting across A4/A5 pages for print (§5).
Function definitions (`FUNC`) each get their own chart next to the main one.

---

## 1. The input language (`.flow`)

One statement per line. Keywords are case-insensitive (`IF` = `if`).
`#` starts a comment (except inside quoted strings).
Blocks are closed by explicit terminators, so indentation is cosmetic — don't
make the parser whitespace-sensitive.

**Input sources (`main.py`):** the optional positional argument is a
directory; inside it, `.flow` files are converted (alphabetically, for
deterministic output ordering). With **no argument**, `main.py` falls back
to `algorithm.txt` in the same directory as `main.py` itself — a missing
`algorithm.txt` is a friendly one-line error, not a traceback.

| Statement | Meaning |
|---|---|
| `START` / `STOP` | begin / end terminators (rounded). Optional — auto-add if missing. |
| `SET x = expr` or `x = expr` | assignment (rectangle). Also allow `+= -= *= /= %=` and `arr[i] = ...`. |
| `INPUT a, b` | read input (parallelogram) |
| `OUTPUT expr` | write output (parallelogram) |
| `CALL name(args)` | call a `FUNC` defined in the file (double box), or an external/built-in routine |
| `FUNC name(p1, p2) ... ENDFUNC` | function definition → gets its own flowchart (see below) |
| `RETURN [expr]` | leave the function; renders as a rounded "Return expr" terminator |
| `IF c THEN ... ELIF c THEN ... [ELSE ...] ENDIF` | decision diamond(s) |
| `WHILE cond ... ENDWHILE` | loop with test at the top |
| `REPEAT ... UNTIL cond` | loop with test at the bottom (body always runs once) |
| `FOR i = 1 TO 10 [STEP 2] ... ENDFOR` | counted loop → emit init / test / update nodes |
| `FOR x IN items ... ENDFOR` | collection loop → "more items?" diamond + fetch box |
| `BREAK` / `CONTINUE` | exit innermost loop / jump to its next iteration |

Design decisions to keep the parser simple:

- **Expressions are opaque text.** You never evaluate them; they only become
  labels on boxes. Validate only the cheap stuff: non-empty, balanced `()`,
  balanced quotes.
- **Anything unrecognised is an error** with a line number.
  `Unknown statement 'FROBNICATE' on line 12` beats a traceback every time.
- **Functions are charted separately, never inlined.** Each `FUNC` block gets
  its own flowchart; callers keep their CALL box. This keeps every chart
  readable and makes recursion harmless (no infinite graph).
- **Return values travel inside expressions.** Since expressions are opaque
  text, `SET f = fib(10)` works without extra syntax: the value returned by
  the callee's `RETURN expr` is what the expression means at run time —
  the chart never evaluates it.
- **Compound conditions stay one diamond.** `IF a > 0 AND b > 0` is a single
  decision labelled with the whole condition. Decomposing AND/OR into nested
  diamonds is an optional extra (M9) — keep the base language simple.
- **Placement rules are errors, not silent reinterpretations:** `STOP` inside
  a FUNC → "use RETURN inside a FUNC"; `RETURN` in the main program →
  "RETURN outside of a FUNC"; two FUNCs with the same name → error. All
  checked at parse time, where the context is known.
- **FUNC placement is free; the main program is what's left.** FUNCs may
  appear anywhere at top level (before or after main statements) and may be
  called before they are defined — charts are built per FUNC, nothing runs.
  The main program is simply all non-FUNC top-level statements in source
  order. The name `main` is reserved: `FUNC main()` is an error (it would
  collide with the main chart's key in the Document).
- **No type or arity checking.** The tool charts code, it doesn't compile
  it: `CALL f(x, y)` charts fine even if `FUNC f(a)` declares one param.

Example (`factorial.flow`):

```
# Factorial with a WHILE loop
start
SET factorial = 1
INPUT n
SET counter = 1
WHILE counter <= n
    SET factorial = factorial * counter
    SET counter = counter + 1
ENDWHILE
OUTPUT factorial
stop
```

A program may also define functions; each gets its own chart:

```
# fib is charted separately, fib(k) in the main chart stays a CALL box
FUNC fib(n)
    IF n <= 1 THEN
        RETURN n
    ENDIF
    RETURN fib(n - 1) + fib(n - 2)
ENDFUNC

start
INPUT k
OUTPUT fib(k)
stop
```

---

## 2. Data model (one small module)

```
Node:  id, kind, text
Edge:  src_id, dst_id, label ("True"/"False"/"" for plain flow)
Flowchart: title, nodes[], edges[]  + add_node/add_edge helpers
Document: {"main": Flowchart, "<funcname>": Flowchart, ...}
          — main program chart first, one chart per FUNC
          (insertion-ordered: FUNC charts in definition order — pagination,
          file naming and PDF page order depend on this)
```

Node kinds and their shapes:

| kind | shape | used for |
|---|---|---|
| `terminal` | rounded / oval | START, STOP |
| `process` | rectangle | assignments, init/update of FOR |
| `decision` | diamond | IF / WHILE / FOR conditions |
| `io` | parallelogram | INPUT, OUTPUT |
| `subroutine` | double-edged box | CALL |
| `return` | rounded box | RETURN expr (function exit) |

Give nodes simple sequential ids (`n1`, `n2`, ...) — stable, readable in the
SVG output, and short enough to keep edge lines tidy.

### Project layout

```
main.py        # the whole CLI: optional dir arg (or algorithm.txt next to it),
               #   pipeline, exit codes, output naming
flowmaker/     # the library main.py drives (no __main__.py, no cli.py)
  parser.py    # .flow text -> statement tree (FlowSyntaxError lives here)
  model.py     # Node / Edge / Flowchart / Document
  builder.py   # statement tree -> charts (pending-edges wiring, loop stack)
  layout.py    # back-edge classification, levels/columns, sizes, positions
  paginate.py  # paper model, band packing, connector stubs, furniture
  render_svg.py # shapes, edges, text, XML escaping; viewport-parameterised
  export.py    # PNG via cairosvg, PDF via cairocffi; missing-backend messages
  gui.py       # optional customtkinter editor + live preview (M8)
tests/         # pytest suite incl. golden SVGs
examples/      # .flow samples, one per feature
algorithm.txt  # the default input when main.py gets no argument
```

---

## 3. Build order (milestones)

Work top to bottom. Every milestone is broken into **micro-tasks**: one
function, one file, or one install each, so every checkbox is a small unit
you can finish and verify in a single sitting. Read §4 before starting M3
and §5 before starting M6. Each group ends with its acceptance check.

### M0 — Bootstrap (one-time setup)
- [x] M0.1 Create the skeleton from the §2 layout: `main.py` with a stub
      `main()` that accepts an optional positional dir argument and falls
      back to `algorithm.txt` next to `main.py`, the empty `flowmaker/`
      package (`__init__.py` only — no `__main__.py`, no `cli.py`), empty
      `tests/` + `examples/` directories; `python main.py` runs and exits 0
- [x] M0.2 Install the test runner in the venv: `pip install pytest`;
      `pytest --version` works
- [x] M0.3 Verify the raster/print backends: `cairosvg` is installed and
      imports cleanly, and its transitive dependency `cairocffi` provides
      the PDF surface (`PDFSurface`, `set_size`, `show_page` — verified).
      pycairo is **dropped from the plan**: it needs system cairo headers
      to build and adds nothing cairocffi doesn't already provide
- [x] M0.4 Write `tests/test_imports.py` importing every module — pytest then
      catches stray syntax errors after each edit (§7 "compile early, often")
- Acceptance: `pytest` collects (even an empty suite) and `python main.py` runs.

### M1 — Parser
- [ ] M1.1 `FlowSyntaxError(message, line)` in `parser.py`; its `str()` prints
      `line N: message`
- [ ] M1.2 `strip_comment(line)` — quote-aware: `#` inside `"..."` is not a
      comment
- [ ] M1.3 `split_keyword(line)` → `(keyword, rest, line_no)`; lowercases the
      keyword for case-insensitive dispatch; blank/comment-only lines skipped
- [ ] M1.4 `parse_assignment` — accepts `SET x = expr` and bare `x = expr`;
      assignment detection needs a negative lookahead for `==` (§7 gotcha);
      support `+= -= *= /= %=` and `arr[i] = ...`
- [ ] M1.5 `parse_simple` for `INPUT a, b`, `OUTPUT expr`, `CALL name(args)`,
      `BREAK`, `CONTINUE`, `STOP` — one node type each, no sub-blocks
- [ ] M1.6 `parse_if` — `IF/ELIF/ELSE/ENDIF` → nested statement tree; every
      helper returns `(stmt, next_index)`; dangling `ELSE` and missing
      `ENDIF` raise with a line number
- [ ] M1.7 `parse_while` — `WHILE cond ... ENDWHILE` (same block mechanics)
- [ ] M1.8 `parse_repeat` — `REPEAT ... UNTIL cond`: body block first,
      condition after — like WHILE but with the test following the body
- [ ] M1.9 `parse_for` — both forms: counted `FOR i = 1 TO 10 [STEP 2]` and
      collection `FOR x IN items`; validate the `TO`/`IN` keyword
- [ ] M1.10 `parse_func` — `FUNC name(p1, p2) ... ENDFUNC`: parse the
      signature (name + parameters validated as identifiers), collect the
      body like any block; FUNCs only at top level (nested FUNC → error;
      RETURN inside the body is normal and required)
- [ ] M1.11 `parse_return` — `RETURN [expr]`: optional expression, bare
      `RETURN` allowed
- [ ] M1.12 `parse_program(text)` — top-level loop assembling main statements
      plus the FUNC list; context checks at parse time: STOP inside FUNC
      ("use RETURN inside a FUNC"), RETURN in the main program, duplicate
      FUNC names, a FUNC named `main` (reserved) — friendly messages per §1
- [ ] M1.13 Parser tests (parametrised): every statement kind, nested blocks,
      both FOR forms, REPEAT…UNTIL, FUNC/RETURN rules, and the error cases
      with exact message + line number
- Acceptance: parse all example files; good error messages on broken input.

### M2 — Flowchart graph + builder
- [ ] M2.1 `model.py`: `Node(id, kind, text)`, `Edge(src_id, dst_id, label)`,
      `Flowchart(title, nodes, edges)` with `add_node`/`add_edge` helpers;
      `add_edge` dedupes on the `(src, dst, label)` triple (§7 gotcha)
- [ ] M2.2 `Document` — insertion-ordered mapping: `"main"` first, then FUNC
      charts in definition order (pagination, file naming and PDF page order
      depend on it); each chart carries a `calls` list of callee names
- [ ] M2.3 Builder skeleton `build(program) -> Document`: emits Start, carries
      the *pending-edge* list `(source_id, label)` down the tree, each
      statement consumes pending edges into its entry and returns new ones
- [ ] M2.4 Sequence wiring for straight-line statements: assignment (process),
      INPUT/OUTPUT (io), CALL (subroutine double box)
- [ ] M2.5 IF/ELIF/ELSE wiring — one diamond per condition, each branch
      appends its exit to the pending list so branches merge naturally;
      empty branch `IF c THEN ENDIF` bypasses True straight to the merge
- [ ] M2.6 WHILE wiring — condition diamond, body exits loop back to the
      condition, False edge continues
- [ ] M2.7 REPEAT…UNTIL wiring — body runs before the condition; repeat on
      the diamond's **True** edge, fall through on **False** (inverted vs
      WHILE — §7 gotcha)
- [ ] M2.8 Counted FOR wiring — init / test / update nodes; test operator
      follows STEP's sign (`<=` for positive, `>=` for negative step);
      CONTINUE targets the update node, not the test
- [ ] M2.9 Collection FOR wiring — fetch box + "more items?" diamond
- [ ] M2.10 Loop stack — one frame per enclosing loop `{breaks, continue_to}`;
      REPEAT pushes a frame whose `continue_to` is the UNTIL diamond and
      whose exit pending edge is the diamond's False side; BREAK/CONTINUE
      consume pending edges via the frame; track "flow consumed" so
      statements after STOP/BREAK never become orphan boxes
- [ ] M2.11 STOP wiring — consumes the pending flow, wires to the chart exit
- [ ] M2.12 FUNC charts — Start → params box (`params: n`) → body → shared
      function-exit terminator; a never-CALLed FUNC still gets its chart; a
      CALL to an undefined name keeps its box (may be external) — no error
- [ ] M2.13 RETURN wiring — rounded "Return expr" node flowing to the shared
      exit; pops past any number of loop frames (overrides BREAK/CONTINUE
      routing); several RETURN nodes per FUNC are fine, all land on the one
      exit; unreachable statements after RETURN are dropped like after STOP
- [ ] M2.14 Empty input (comments/blank lines only) → main chart is just
      Start → Stop; empty FUNC body → Start → params box → exit
- [ ] M2.15 Graph validator utility `validate(chart)`: every edge endpoint
      exists, no duplicate `(src, dst, label)` triples, every non-exit node
      has ≥1 incoming edge, every node reachable from Start
- [ ] M2.16 Builder tests: branch merge points, loop-back edges,
      BREAK/CONTINUE targets, REPEAT exit on UNTIL-False, empty loops
      (`WHILE c ENDWHILE` self-loop, no crash, no orphan), single-exit
      invariant on every chart — run `validate` after each build
- Acceptance: for each example, the validator passes on every chart.

### M3 — Layout (assign x/y to every node)
- [ ] M3.1 `layout.py` skeleton + drawing constants (font size, 0.6
      char-width factor, wrap width ~28 chars, row/column gaps)
- [ ] M3.2 `node_size(node)` — width from text length × 0.6 × font size,
      wrap into lines and add line height; diamonds ≈ 2× text width and
      2× line height; widen the factor for wide glyphs (measure with
      `unicodedata.east_asian_width`)
- [ ] M3.3 Back-edge classification — DFS from START; an edge is a back edge
      iff its target is on the current DFS path (ancestor). Plain
      "target already visited" is wrong: cross-edges to finished nodes are
      forward flow and must be kept. Self-loops are back edges
- [ ] M3.4 Longest-path leveling on the remaining DAG (topological order,
      `level[dst] = max(level[dst], level[src] + 1)`); guaranteed to
      terminate because every cycle passed through a removed back edge
- [ ] M3.5 y positions from real heights: `y(L) = top + sum(height of levels
      < L) + L × gap` — no global row-height constant
- [ ] M3.6 Column assignment — children placed left→right in edge-creation
      order (body before else, first branch first); a child keeps its
      parent's column unless taken on its level, then the next free column
      to the right; arrays only, no sets/dict iteration (determinism rule)
- [ ] M3.7 x positions from real column widths: `x(C) = left + sum(width of
      columns < C) + C × gap`; a column's width must exceed its widest box
- [ ] M3.8 Within-level order: sort by column, then source-line number —
      natural reading order, fully deterministic
- [ ] M3.9 Edge routing v1 — straight/elbow lines between shape borders
      (compute border intersections, never draw into the box); loop-backs
      routed down one side outside the boxes; parallel branch edges to the
      same merge node must not overlap (True straight into the top, False
      elbows right/down into the side)
- [ ] M3.10 Expose the level/column grouping and drawing extents for
      pagination (§5 packs these verbatim) and for tests
- [ ] M3.11 Overlap check on all examples: assert no two node rectangles
      intersect and loop-back edges stay visible
- Acceptance: no two nodes overlap; arrows have room; loop-back edges are visible.

### M4 — SVG renderer (+ PNG export)
- [ ] M4.1 `render_svg.py` skeleton — SVG root, `<defs>` with the shared
      arrow `<marker>`, and the `escape_xml` helper (`& < > "`)
- [ ] M4.2 `draw_rect` / `draw_rounded` — terminal rx=18, process rx=0,
      return uses the rounded shape
- [ ] M4.3 `draw_diamond` — 4-point polygon
- [ ] M4.4 `draw_parallelogram` — skewed top/bottom edges
- [ ] M4.5 `draw_subroutine` — rect + inner rect inset by 4px
- [ ] M4.6 `draw_edge` — line with `marker-end` + label text (True/False)
- [ ] M4.7 Text centering + wrapping into `<tspan>` lines; long unbroken
      tokens wider than the max box width are force-chopped mid-token —
      text never overflows its shape
- [ ] M4.8 File hygiene — `<?xml version="1.0" encoding="UTF-8"?>` first
      line, UTF-8 output, pinned `font-family="Helvetica, Arial, sans-serif"`
      on the drawing root
- [ ] M4.9 Viewport parameter (content rect + translate) so the identical
      draw calls render any page region (needed by M6)
- [ ] M4.10 Canvas sizing — extents + margin in single mode, printable rect
      in paginated mode, same draw calls either way
- [ ] M4.11 `export.py` PNG path — rasterise with cairosvg `svg2png` at
      `--dpi` (96 screen / 300 print); pixel size = canvas_px × dpi / 96;
      clamp with a clear warning past cairo's 32767 px surface limit
- [ ] M4.12 Renderer tests: output parses as XML, every id referenced by an
      edge exists, first line is the XML declaration
- Acceptance: output opens in a browser/Inkscape; XML parses; an example's PNG
  has exactly the pixel size `canvas_px × dpi / 96` predicts.

### M5 — CLI (`main.py`)
- [ ] M5.1 `main.py` argument parser — `python main.py [DIR]
      [-o out.svg] [--format svg|png|pdf]`; the optional positional
      argument is a directory; `-` reads stdin (bypasses the
      dir/`algorithm.txt` fallback)
- [ ] M5.2 Input resolution — no argument: use `algorithm.txt` sitting next
      to `main.py`; if it is missing, print a friendly one-line message and
      exit 2. With a directory: convert every `*.flow` inside it,
      alphabetically for deterministic ordering; a directory with no `.flow`
      files gets a friendly message and exit 0
- [ ] M5.3 Mode flags — `--fit single|one-page|split` (default `single`;
      `--page-size` implies `split`): `single` = whole chart on one
      unconstrained canvas, `one-page` = scale down to fit one sheet
      (readability floor applies), `split` = paginate at true size with
      off-page connectors; plus `--page-size a4|a5|letter`, `--orientation
      portrait|landscape|auto`, `--margin MM`, `--dpi N`
- [ ] M5.4 Reading + output paths — read input files with
      `encoding="utf-8-sig"` (strips a Windows BOM); create parent
      directories for `-o` paths or fail cleanly with exit 2; in directory
      mode outputs land next to their source files unless `-o` redirects them
- [ ] M5.5 Exit codes — 0 ok (an empty directory counts as ok), 1 syntax
      error with the line number printed, 2 I/O error or missing backend
- [ ] M5.6 Single-mode pipeline per input file — parse → build → layout →
      render; naming `<stem>.svg` for main + `<stem>-<func>.svg` per FUNC;
      stdin without `-o` uses stem `main`
- [ ] M5.7 Missing-backend detection — when cairosvg (PNG/PDF backend) is
      absent print "install cairosvg or use -f svg" and exit 2, never a
      traceback
- [ ] M5.8 Format × mode matrix — implement all nine combinations of the
      table below (one file per chart / per page `{chart}-{NN}`; PNG at
      `--dpi`; PDF one page per chart, or multi-page in split mode):

      | format | single | one-page | split |
      |---|---|---|---|
      | svg   | one file per chart: `<stem>.svg` + `<stem>-<func>.svg` | one file per chart (scaled) | one file per page `{chart}-{NN}.svg` |
      | png   | one file per chart at `--dpi` | one file per chart at `--dpi` (scaled) | one PNG per page `{chart}-{NN}.png` at `--dpi` (page mm × dpi / 96 px) |
      | pdf   | one PDF, one page per chart (main first, then FUNCs in definition order) | one PDF, one page per chart (scaled) | one multi-page PDF: every page of every chart, one sheet per page |
- [ ] M5.9 one-page mode — uniform scale-down to fit one sheet, refusing
      (and splitting instead) when text would drop below the 9 pt / 12 px
      readability floor
- [ ] M5.10 CLI tests — exit codes, stdin mode, the `algorithm.txt`
      fallback (including its missing-file message), directory mode
      (multi-file run, per-file naming), output naming for main + FUNC
      charts in every mode, missing-backend message text
- Acceptance: usable without reading the source.

### M6 — Pagination (split large charts across pages, §5)
- [ ] M6.1 Paper model — A4 210×297, A5 148×210, Letter 216×279 in mm;
      landscape swaps the dimensions, margins stay; printable rect =
      paper − 2×margin; mm→px = mm × 96 / 25.4; reject margins leaving no
      printable area (2×margin ≥ paper side) with a clear error
- [ ] M6.2 Greedy row-band packing — accumulate whole levels until the next
      would exceed the printable height (reserve header/footer space
      *before* packing); one node on one page, never sliced; a single level
      too tall for a page is an error, not a cut
- [ ] M6.3 Greedy col-band packing — same rule over columns against the
      printable width; a page = one row-band × one col-band
- [ ] M6.4 Page ordering + naming — row-major (down first, then right);
      numbering restarts per chart; filenames `{chart}-{NN}.svg`
      zero-padded (`main-01.svg`, `fib-01.svg`; `-o out.svg` → `out-01.svg`)
- [ ] M6.5 Per-page rendering — wrap the full drawing in
      `<g transform="translate(-ox,-oy)">` with the band's cumulative
      top-left corner; drawing code unchanged, SVG root in physical units
      (`width="210mm"` + matching viewBox) for true-size printing
- [ ] M6.6 Cut-edge pass (runs once, after packing) — endpoints in different
      bands ⇒ both sides get a stub on the band side facing the other band
      (right/bottom for exits, left/top for entries); dedupe stubs landing
      on the same border point
- [ ] M6.7 Off-page connector circles — "→ p.N" on the leaving page, "from
      p.N" on the landing page; jump straight to the target page even if
      pages sit in between
- [ ] M6.8 Page furniture — header (chart title; `FUNC name(params)` for
      function charts), footer "Page i of j"
- [ ] M6.9 `auto` orientation — pack under both orientations, keep the one
      with fewer pages, tie → portrait; chosen once for the whole document
- [ ] M6.10 PDF output (cairocffi) — one `PDFSurface`, `set_size()` per
      page, `show_page()` per sheet; per-page SVGs remain the
      zero-dependency default
- [ ] M6.11 Pagination tests — no node on two pages, every cut edge has both
      stubs, connector page numbers match the packing, page count reacts to
      paper size/margins, `auto` picks the fewer-page orientation
- Acceptance: a 60-node chart splits with no cut shapes; every cut edge has
  matching "to/from" stubs with correct page numbers; pages print at true size.

### M7 — Tests (cross-cutting)
- [ ] M7.1 Golden-test harness — byte-identical SVG for fixed inputs; update
      goldens only on purpose; run the suite twice in a row to prove
      determinism
- [ ] M7.2 Format × mode matrix test — every combination produces exactly
      the files the M5 table names (right count, right names, PNG pixel
      size right)
- [ ] M7.3 Function-chart tests — one chart per FUNC, RETURN exits route
      correctly (including RETURN from inside a loop), unknown CALL targets
      do not crash
- [ ] M7.4 Hostile-but-legal end-to-end inputs — BOM-prefixed file, FUNC
      defined after its CALL, `FUNC main()` rejected with the friendly
      message, `FOR i = 10 TO 1 STEP -1`, empty FUNC bodies
- [ ] M7.5 Suite budget — `pytest` green in < 1 s
- Acceptance: `pytest` green, runs in < 1 s.

### M8 — GUI: text editor + live flowchart preview (`python main.py --gui`)
The GUI is **optional**: every import of customtkinter sits behind
`try/except ImportError`, so `main.py` (and pytest) work with zero GUI
packages installed. customtkinter 6.x is actively maintained (6.0.0, June
2026, MIT). Preview backends, in order of preference:
1. **Zero-dependency native canvas:** the layout's node geometry
   (M3.10 exposes positions/sizes) drawn directly on a `tk.Canvas` —
   rectangles/polygons/text, no SVG in sight, crisp at any window size.
2. **cairosvg PNG:** rasterise the single-canvas SVG to PNG bytes and show
   it in a `tk.PhotoImage` (needs the M4 backend; Tk has no native SVG
   support, so a PNG or direct canvas drawing is the only live-preview path).
- [ ] M8.1 `pip install customtkinter`; `import customtkinter` works (only
      requirement is Python ≥ 3.7; Tk ships with Python on Windows/macOS,
      on Linux it is the `python3-tk` system package)
- [ ] M8.2 `gui.py` app shell — customtkinter window, top bar (Open…, Save,
      Export SVG/PNG buttons + chart selector for main/FUNC charts), and
      `--gui` wired in `main.py`'s arg parser behind the optional import
- [ ] M8.3 Left pane: scrollable text editor for the `.flow` source
      (monospaced `CTkTextbox`, line-number gutter optional)
- [ ] M8.4 Right pane: live preview — native `tk.Canvas` drawn from layout
      geometry (positions, sizes, edges, labels) with scrollbars and
      mouse-wheel zoom; cairosvg-PNG fallback if the canvas path is skipped
- [ ] M8.5 Debounced re-render pipeline — re-parse → re-build → re-layout →
      redraw on every edit pause (~300 ms via `after`), on the Tk main
      thread only (Tk is not thread-safe)
- [ ] M8.6 Parse/builder errors in the GUI are shown as a friendly banner
      (message + line number) instead of crashing the app; the last good
      chart stays visible while the text is broken
- [ ] M8.7 Editor actions — Open…/Save/Save As… (`filedialog`, default
      `algorithm.txt` next to `main.py`), Export SVG/PNG via the same
      pipeline the CLI uses
- [ ] M8.8 GUI smoke test — parse+layout+canvas-draw path tested headlessly
      (no window): fake the widget calls, assert the pipeline runs and the
      error banner path triggers on broken input; `--gui` without
      customtkinter prints the friendly "install customtkinter or use the
      CLI" message and exits 2
- Acceptance: launch `--gui`, type `START / OUTPUT "hi" / STOP` and the chart
  appears within a second of typing stopping; with customtkinter uninstalled
  the CLI still works and the GUI prints the friendly message.

### M9 — Extras (only after everything above works)
- [ ] M9.1 Mermaid output — another renderer over the same graph
- [ ] M9.2 AND/OR condition decomposition into nested diamonds (opt-in flag)
- [ ] M9.3 Cross-reference appendix — for each CALL box, list the callee's
      chart (name and page numbers)
- [ ] M9.4 Binding margin (gutter) — extra inner margin on alternating page
      sides for glued or book-bound printing
- [ ] M9.5 Custom `--page-size WxH` in mm for non-standard book trim sizes
- [ ] M9.6 `--title`, themes, `--direction LR`

---

## 4. Layout: the hard part (read before M3)

Flowchart layout is the only genuinely tricky milestone. A pragmatic recipe:

1. **Level assignment (y).** Two passes, and the order matters:
   - *Classify edges with a DFS from START:* an edge `src → dst` is a
     **back edge** iff `dst` is already on the current DFS path (ancestor) —
     that is exactly the set of loop-backs and self-loops. Plain "target
     already visited" is *not* the test: cross-edges to already-finished
     nodes are forward flow and must be kept.
   - *Longest-path leveling on the remaining DAG* (topological order,
     `level[dst] = max(level[dst], level[src] + 1)`). Longest-path (not
     BFS/shortest-path) so loop bodies don't cram onto their condition's row.
     The DAG is guaranteed acyclic because every cycle in a flowchart passes
     through a loop's back edge, which we removed.
   - y is computed from **real heights**: `y(level L) = top + sum(height of
     each level < L) + L * gap` — not one global `row_height` constant
     (tall boxes and diamonds make rows different heights; pagination §5
     depends on the real numbers).
2. **Order within a row (x).** Depth-first order works well for flowcharts:
   the "main path" stays in column 0 and each branch (decision's False path,
   loop bodies) shifts one column to the right.
   `x(column C) = left + sum(width of each column < C) + C * gap` — real
   column widths again, where a column's width must exceed the widest box
   in it (diamonds need ~2× the text width!).
3. **Compute box sizes before positions.** Estimate text width as
   `len(text) * 0.6 * font_size`; wrap at ~28 chars into multiple lines and
   add line height. Diamonds: width ≈ 2 × text width, height ≈ 2 × line height.
4. **Edge routing v1:** straight or elbow lines between shape borders
   (compute border intersection points, don't draw into the box).
   Loop-back edges: route down one side (x offset outside the boxes).
   **Parallel branch edges must not overlap:** when both the True and the
   False branch merge on the same node directly below a diamond, both edges
   would be straight vertical lines on top of each other — offset one of
   them (True goes straight down into the merge top; False elbows right,
   down, and into the merge node's side).
   Fancy orthogonal routing can come much later.

Simplest first version: TB flow, False-branches to the right, merge points
pull back to column 0, loop-backs on the far side. That gets you 90 % of the
visual quality for 10 % of the effort.

Level ordering inside a level (same row): sort by column first, then
source-line number — keeps reading order natural and is fully deterministic.
Edge cases that must not crash the layout:
- a node with many incoming edges from different columns (merge point)
- a diamond with both branches landing on the same node (True and False)
- disconnected pieces: cannot happen — the builder wires everything from
  START, and the validator (M2) asserts reachability
- a level containing only loop-back targets (e.g. the condition row when all
  body paths CONTINUE): the row still exists and holds the condition itself

---

## 5. Output sizing: one big canvas or paginated pages (read before M6)

Principle: **split along layout boundaries, never through shapes.**

This is the mode for **books**: every page is a self-contained, readable
sheet — header, footer with page number, connector stubs pointing at the page
that continues the flow — so the printed stack can be bound as-is. Pages are
emitted in row-major order (down first, then right) so page numbering matches
the way a reader turns pages.

### Single-canvas mode (default): the entire chart in one file
- No page math at all: canvas = drawing extents + one margin ring.
- SVG is the natural single-file format — infinitely zoomable, tiny files.
- PNG rasterises the same canvas at `--dpi` (96 = screen, 300 = print);
  pixel width = `canvas_px × dpi / 96`.
- Hard limit: cairo image surfaces max out at **32767 px per side**. A
  wall-sized chart at 300 dpi can exceed that — clamp with a clear warning
  and point the user at SVG, or auto-switch to paginated output.
- Pagination only kicks in when `--page-size`/`--fit split` is requested;
  the splitter is skipped entirely in single mode.

### Page geometry
- Paper in mm: A4 210×297, A5 148×210, Letter 216×279. Margins default ~12 mm.
- **Orientation: portrait | landscape | auto** (default `auto`, see below).
  Landscape simply swaps the paper's two dimensions (A4 landscape = 297×210);
  margins stay as given. Pick orientation **once for the whole document** —
  mixed orientations within one print job confuse printers and staplers.
- `auto` heuristic: run the level/column packing under both orientations and
  keep the one that produces **fewer pages** (tie → portrait). Flowcharts laid
  out top-to-bottom are usually tall, so portrait wins most of the time;
  landscape mainly rescues wide branch spreads that waste half a portrait page.
- Printable area = paper − 2×margin (in the chosen orientation). Convert
  mm→px: `px = mm × 96 / 25.4` (≈3.78).
- Set the SVG root in physical units — e.g. portrait `width="210mm"
  height="297mm" viewBox="0 0 794 1123"`, landscape `width="297mm"
  height="210mm" viewBox="0 0 1123 794"` — so print dialogs produce true-size
  sheets instead of rescaling your pixels.

### The split algorithm
1. Reuse the layout's existing level (row) and column grouping verbatim.
   Never compute a second layout for pagination.
2. **Page-rows:** greedily accumulate whole levels until adding the next would
   exceed the printable height; then start a new page-row band. Whole levels
   only ⇒ no shape is ever sliced.
3. **Page-cols:** same greedy packing over columns against the printable width
   (wide branch spreads need this too). A page = one row-band × one col-band.
4. Render each page by wrapping the full drawing in
   `<g transform="translate(-ox,-oy)">`, where (ox, oy) is the band's
   cumulative top-left corner: `ox = sum(width of col-bands left of this
   one)`, `oy = sum(height of row-bands above this one)`. The drawing code
   is unchanged — only the viewport moves.
5. An edge crossing between bands becomes two stubs; each stub sits on the
   side of the band rectangle that faces the other band (right/bottom side
   for exits to a band right/below, left/top for entries from a band
   left/above) — deterministic, no search.

### Edges that cross a page boundary
- Don't route edges across pages. Terminate them at the border with an
  **off-page connector**: a small circle labelled "→ p.4" on the leaving page,
  and a matching "from p.2" stub on the landing page.
- Jump straight to the target page even if pages sit in between.
- Assign stubs *after* packing (page numbers don't exist before packing) and
  keep the rule simple: endpoints in different bands ⇒ both sides get stubs.

### Page furniture
- Header: chart title (the `--title` for the main chart; `FUNC name(params)`
  for a function chart); footer: "Page i of j".
- **Page numbering restarts per chart** (`main` 1..n, each FUNC 1..m); the
  chart name in the header makes every reference unambiguous ("fib p.2").
  Book assembly order: main chart pages first, then FUNC charts in
  definition order — matches how the cross-reference appendix (M9) cites them.
- Filenames: `{chart}-{NN}.svg` where `{chart}` is `main` or the FUNC name
  (`main-01.svg`, `fib-01.svg`); with `-o out.svg` the stem replaces `main`
  (`out-01.svg`, `fib-01.svg`). Zero-padded `NN` so files sort naturally.
- `--fit one-page`: allow uniform scale-down only while no text drops below
  **9 pt** (≈12 px at 96 dpi); otherwise refuse and split instead.

### PDF (the real print format)
SVG has no multi-page concept. For actual printing emit one PDF with one page
per sheet — with cairocffi: `PDFSurface`, `set_size()` per page,
`show_page()` after each sheet. Keep per-page SVG as the default (zero
dependencies) and PDF as the print option.

---

## 6. SVG cheat sheet (M4 reference)

```xml
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" viewBox="0 0 800 600">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="black"/>
    </marker>
  </defs>

  <!-- terminal -->  <rect x=".." y=".." width=".." height=".." rx="18" fill="white" stroke="black"/>
  <!-- return   -->  same rounded shape, text "Return expr" (function exit)
  <!-- process  -->  same, rx="0"
  <!-- decision -->  <polygon points="cx,cy-h/2 cx+w/2,cy cx,cy+h/2 cx-w/2,cy" .../>
  <!-- io       -->  <polygon points="skewed top/bottom edges" .../>
  <!-- subroutine--> rect + a second inner rect inset by 4px

  <!-- edge with label -->
  <line x1=".." y1=".." x2=".." y2=".." stroke="black" marker-end="url(#arrow)"/>
  <text x=".." y=".." font-size="12" text-anchor="middle">True</text>

  <!-- centered, wrapped text -->
  <text x="cx" y="cy" text-anchor="middle" dominant-baseline="middle">
    <tspan x="cx" dy="0">first line</tspan>
    <tspan x="cx" dy="16">second line</tspan>
  </text>
</svg>
```

Escape text with `& < > "` — `OUTPUT "a & b"` must not produce
invalid XML.

---

## 7. Gotchas (learned the hard way — check these before you ship)

- **Duplicate edges.** A decision's False edge and a merge edge can produce
  the same (src, dst, label) twice → double lines in the diagram. Dedupe on insert.
- **Unreachable code.** Statements after `STOP`/`BREAK` must not become orphan
  boxes floating in the chart. Track "flow consumed" and skip the rest.
- **CONTINUE must target the update node, not the test** (counted loops).
  Otherwise the `i = i + 1` step is silently skipped in the diagram.
- **Empty branches.** `IF c THEN ENDIF` → the diamond's True edge simply
  bypasses to the merge point. No empty boxes.
- **`#` inside strings** is not a comment. Handle quotes when stripping comments.
- **`=` vs `==`.** Assignment detection needs a negative lookahead for `==`,
  or `IF x == 1` parses as an assignment.
- **Wiring model that works:** carry a list of *pending edges*
  `(source_id, label)` down the builder. Each statement consumes the pending
  edges into its entry node and returns new ones. Branches append their exits
  to the list (they merge naturally); loops add body-exits back to the
  condition; STOP/BREAK consume the pending edges instead of passing them on.
- **Sizes before positions:** compute all box dimensions first, then place —
  otherwise columns overlap as soon as one label is long.
- **Compile early, often:** a stray triple-quote in a module kills the whole
  package; run `python -m compileall .` or import everything after each edit.
- **`FOR i = 1 TO 0`** and `FOR i = 10 TO 1 STEP -1` are legal: the chart
  shows init → test (`i <= 0` / `i >= 1`... i.e. operator follows STEP's
  sign) → body → update exactly like any loop; whether it runs zero times is
  a run-time concern the chart doesn't judge.
- **Self-loops are real:** `WHILE c ENDWHILE` (empty body) makes the diamond's
  True edge point at the diamond itself. Leveling must not loop forever on it
  (the loop-back edge is exactly the kind you skip), and the renderer must
  draw it without dividing by zero. Test it on day one, not at the end.
- **Leveling must classify back edges first:** don't "skip already-visited
  targets" and don't relax forever. A relaxation loop over the raw graph
  will not terminate — the body→condition edge of every loop raises the
  condition's level without end. DFS-stack classification, then longest-path
  on the DAG, is the whole trick.
- **Determinism is a feature:** never iterate a `set` or rely on `dict`
  insertion luck anywhere in parser/builder/layout — every array order must be
  derivable from the source text. Otherwise golden tests flicker and the same
  input renders differently on different runs/machines.
- **Bottom-test loops invert the exits:** REPEAT's body runs *before* the
  condition; the loop repeats on the diamond's **True** edge and falls through
  on **False** — the exact opposite of WHILE. Wiring them the same way is the
  classic first-bug of flowchart generators.

Pagination-specific:

- **Compute pagination from *final* geometry** (pixel extents after margins,
  furniture and loop-back edge offsets are reserved), not from box positions
  alone — otherwise page 2's header overlaps page 1's last row.
- **One node, one page.** Never allow a node on two pages; if a single level
  band still overflows a page (one huge diamond?), that's an error, not a cut.
- **Dedupe connector stubs.** An edge cut on its source side and a different
  edge cut on its target side can produce two circles at the same border
  point — offset them or merge into one circle with two labels.
- **Footer/header space counts as margin.** Reserve header/footer height
  before greedy packing, not after.
- **Page numbering is only known after packing** — do connector labelling as a
  separate pass that runs once, after all bands are fixed.
- **A5 is small.** At default font sizes a 3-column chart nearly fills an A5
  width; expect most non-trivial charts to split on A5, and test with it.

Function-specific:

- **RETURN behaves like STOP for wiring** — it consumes the pending flow.
  Unreachable statements after a RETURN must be dropped, same rule as STOP.
- **A function can have several RETURN nodes** (one per exit path). They all
  flow into one shared function-exit terminator — that's the chart's "Stop".
- **RETURN inside a loop overrides the loop stack:** when the builder meets
  RETURN it must not route to the loop's condition/update — pop past any
  number of loop frames and wire to the function exit.
- **Recursion is a non-event** because FUNCs are charted separately: `fib`
  calling `fib` just produces a CALL box in fib's own chart. Never try to
  inline calls.

---

## 8. Definition of done

- [ ] All M0–M7 micro-tasks checked (M8 GUI and M9 extras are optional)
- [ ] (Optional, M8) `--gui` opens a text editor with a live preview that
      re-renders as you type, and shows friendly errors instead of crashing
- [ ] `pytest` passes; every example file parses and renders
- [ ] Every example exports to **SVG and PNG** from the same source file
      (and to a multi-page PDF in split mode — cairocffi, installed with
      cairosvg)
- [ ] Golden tests pass on a fresh clone: run the suite twice in a row —
      identical output both times (catches hidden nondeterminism)
- [ ] Opening each generated SVG in a browser shows a correct chart:
      branches merge, loops visibly cycle back, no overlapping boxes
- [ ] A deliberately large chart (40+ nodes) auto-splits into numbered pages:
      no shape is cut, every cut edge has matching to/from connector stubs,
      footers read "Page i of j", filenames sort correctly
- [ ] Hostile-but-legal inputs parse and render: BOM-prefixed files, FUNC
      defined after its CALL, a FUNC named `main` (rejected with the
      friendly message), `FOR i = 10 TO 1 STEP -1`, empty FUNC bodies
- [ ] A file with FUNC definitions produces one correct chart per function
      (plus the main chart), each independently layouted and paginated
- [ ] A5 page output stays readable (no text below ~9 pt)
- [ ] The same large chart also exports as ONE oversized SVG/PNG (single mode):
      full content, no page furniture, PNG pixel size matches `--dpi`
- [ ] Bad input produces a friendly one-line error with a line number
- [ ] README shows one example source next to its rendered image,
      plus a note on the page-splitting flags

