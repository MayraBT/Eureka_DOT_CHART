# Weekly IPC extraction spec (Eureka Math TEKS Edition, Dallas ISD 2026-27)

Read each Google Doc with the Google Drive `read_file_content` tool (load it first with ToolSearch "select:mcp__Google_Drive__read_file_content"). Do not edit any Drive file.

Write ONE JSON file (path given in your task) with this shape. See `/home/claude/build/ipc/g3_q1.json` for a worked example.

```
{"grade":3,"weeks":[
 {"q":1,"wk":5,"start":"2026-09-07","title":"<doc title>","days":[
   {"dow":"Mon","kind":"off","text":"Labor Day"},
   {"dow":"Tue","kind":"lesson","les":["M1.L20"],"teks":["3.4K"],"bundled":["3.5A"],
    "lo":"<the LO: text>","sc":["<each SC bullet>"],
    "te":{"M1.L20":"<full URL of the Teacher link for that lesson>"},
    "note":"<optional: e.g. 'Supplemental Lesson 3-1', 'Reteach or Flex Day', 'lessons combined'>"},
   ...5 days Mon–Fri...]}
]}
```

Rules
- One object per weekday Mon–Fri, in order, even when the IPC leaves a day blank (then `"kind":"blank"`).
- `kind`: `lesson` (an Eureka lesson is taught), `assess` (Learning Check, SMC, i-Ready, Mid-Module/End-of-Module assessment, STAAR practice), `flex` (reteach / flex / review day with no new lesson), `off` (holiday, teacher work day, fair day, early release with no lesson, break), `blank`.
- `les`: lesson ids as `M<module>.L<lesson>` from the "Eureka Math Lesson: Module X Lesson Y" text. Two lessons combined on one day → list both. Supplemental lessons: `M<module>.S<n>` (e.g. "Supplemental Lesson 3-1" in Module 2 → `M2.S3-1`) and put the name in `note`.
- `teks`: the bold TEKS after "TEKS:" (uppercase letter, e.g. "3.4E"). `bundled`: codes after "Bundled standards:". Strip duplicates and stray punctuation; keep order. Do not include ELPS.
- `lo`, `sc`: copy text exactly (trim whitespace; SC bullets as an array).
- `te`: the URL of the link labelled "Teacher" for each lesson (unescape `\_` → `_`, `\&` → `&`). Omit if absent.
- Columns can be misaligned when a day is merged; use the Monday–Friday header order and the lesson numbers to place content. If a cell spans two days (same lesson both days), repeat it for both days.
- `start` = the Monday date of that week (2026-27 calendar). Week numbers and Mondays:
  W1 Aug 10, W2 Aug 17, W3 Aug 24, W4 Aug 31, W5 Sep 7, W6 Sep 14, W7 Sep 21, W8 Sep 28, W9 Oct 5 (Q1);
  W10 Oct 12, W11 Oct 19, W12 Oct 26, W13 Nov 2, W14 Nov 9, W15 Nov 16, W16 Nov 30, W17 Dec 7, W18 Dec 14 (Q2);
  W19 Jan 4, W20 Jan 11, W21 Jan 18, W22 Jan 25, W23 Feb 1, W24 Feb 8, W25 Feb 15, W26 Feb 22, W27 Mar 1 (Q3).
- Validate the file with `python3 -m json.tool <file>` before finishing.

Final reply: just the file path, the count of weeks/lesson-days written, and any doc you could not read or anything ambiguous (one line each). Do not paste the JSON.
