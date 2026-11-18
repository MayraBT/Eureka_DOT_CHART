# Eureka TEKS Lookup: maintainer notes

This is a TEKS chart and TEKS lookup for **Eureka Math TEKS Edition, Kindergarten through Grade 5** (Dallas ISD 2026-27). Eureka doesn't publish a lesson-by-TEKS chart, so this tool builds one from the district's weekly IPCs. The views are the same as in the Carnegie tool (`MayraBT/Carnegie_DOT_CHART`): Calendar, By lesson, By standard, STAAR performance, Teaching moves and Full grid.

- `index.html` holds everything. It has no build step at runtime.
- `items/` holds the released STAAR item images (`g<grade>_<year>_Q<n>.jpg`, 192 files).
- `build/` holds the scripts and extracted data used to regenerate `index.html`.

## Where the data comes from

| Constant | What it holds | Source |
|---|---|---|
| `COURSES.g3/g4/g5.data.lessons[].marks` | ● `F` = the day's **TEKS** line on the weekly IPC, ○ `O` = **Bundled standards** | Weekly IPCs, Q1–Q2 (`build/ipc/g*_w*.json`) |
| lesson titles | Eureka lesson objective | Quarterly calendars Q1–Q3 (`build/ipc/cal_g*.json`) |
| modules, topics, focus/included TEKS, omitted lessons | Scope & Sequence 2026-27 | `cal_g*.json` → `ss`; lesson→topic map in `ipc/topics.json` |
| `pace`, `cal` | Day-by-day pacing. Q3 comes from the Q3 quarterly calendar | weekly IPCs + Q3 calendar |
| `TIG` | Teacher-edition link for each lesson, as linked on the weekly IPC | weekly IPCs |
| `PERF` | Released STAAR items 2025 and 2026, % of Texas students | lead4ward IQ Tool exports (`build/perf.json`) |
| `SCAF`, `TEKS` | Vertical alignment K–8, SE text, R/S/not-tested | lead4ward TEKS Scaffold, Grades 3–5 |
| `VOCAB` | Academic vocabulary, English with the matching Spanish block | lead4ward Academic Vocabulary, EN + SP |
| `MOVES` | Teaching moves for all 131 Grade 3–5 SEs | Written for this tool; general best practice. These are look-fors and suggestions, not for evaluating teachers |

## Rebuilding

1. Put fresh extracts in `build/ipc/`. Weekly IPCs follow `build/ipc/SPEC.md`.
2. From `build/`, run `python3 build_data.py`. It writes `data.js` and `report.txt`; check the report for unmapped topics or TEKS that aren't in the grade.
3. Run `python3 assemble.py`. It needs the Carnegie template at `/home/claude/mayrabt/carnegie_dot_chart/index.html` (clone `MayraBT/Carnegie_DOT_CHART`) and writes `out/index.html`.
4. Run `node test.js` with a local server on port 8765. It checks desktop and phone width, page errors and overflow.

## K–2

- **IPCs:** weekly IPCs come from the 26-27 K-2 tab of the IPC links sheet. K and Grade 1 have 2026-27 Q3 weeklies; Grade 2 Q3 is paced from the Q3 calendar only.
- **TEKS text:** 19 TAC §111.2–111.4, TEA (`build/teks_k2.json`). Readiness marks come from the lead4ward scaffold where it lists the SE.
- **Grade 2 Scope & Sequence:** no Dallas ISD Grade 2 S&S was found, so Grade 2 modules and topics come from the Great Minds Guide to Content and the calendars.
- **No STAAR:** the STAAR performance view is hidden for K–2.
- **Vertical alignment and vocabulary:** these are partial for K–2 until the K–2 lead4ward files are added.

## Open items

- **Q3.** K, Grade 1, Grade 4 and Grade 5 use the 2026-27 Q3 weekly IPCs for all nine weeks (TEKS, pacing and Teacher links). Grades 2 and 3 use the 2026-27 Q3 weeklies for weeks 1–4 (`ipc/g2_w19-22.json`, `g3_w19-22.json`); weeks 5–9 were not posted yet (checked Nov 17), so they are paced from the Q3 calendar. Grade 3 lessons in those weeks take TEKS and Teacher links from the 2025-26 Q3 IPC for the same lesson (`ipc/g3_q3_2526.json`); Grade 2 lessons there have no TEKS or Teacher link yet. Grade 2 week 4 Friday is listed as Module 6 Lesson 8 (omitted in the S&S) with Lesson 7's Teacher link and a blank LO, so it is treated as a second day of M6 L7. Grade 3 week 4 shows Tue–Thu as "Snow Day" on the posted IPC. When the remaining weeklies are posted, extract them per `ipc/SPEC.md` and rebuild.
- **Q4.** Eureka instruction ends in March. Q4 uses district-created materials, so it has no lessons in the tool.
- **STAAR dates.** None of the source documents give 2027 Grade 3–5 STAAR dates, so no lesson is flagged "after STAAR".
- **Cut-off items.** A few IQ Tool items run past the page in the PDF export, so their images are cut off at the bottom (e.g. Grade 4 2025 Q4).
- **Topic placement.** A few lessons had to be placed in a topic by judgment because merged calendar cells shift the columns. The list is in the hand-off summary.
- **Dallas ISD results.** 2026 only (SchoolCity Item Analysis, Assessment Level State, Grades 3–5; `build/dist.json` via `parse_dist.py`). All 96 items matched the released tests by item number, standard and points. To add 2025, run the same report for 2024-25.
- **Public repository.** This repository is public, and lead4ward data (item percents, scaffold, vocabulary) is subject to the district's lead4ward license.
