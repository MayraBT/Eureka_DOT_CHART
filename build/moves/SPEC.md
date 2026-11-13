# Teaching moves — Grades 3–5 (TEKS Lookup, Eureka version)

Write one JSON array to the output path in your task, with one object per TEKS listed in your input file (`teks_g<N>.json`, which gives `code`, `t` and `d`; copy those three fields into each object unchanged).

Match the schema and depth of `/home/claude/build/moves/EXAMPLE.json` exactly:
- `code`, `t`, `d`: copied from the input.
- `mis`: 3 misconceptions, each `{m, why, fix}`: specific, observable student errors for this SE at this grade, the reason behind each one, and a concrete teacher move to fix it.
- `cra`: `{c, r, a, look}`. Use concrete materials common in Grades 3–5: base-ten blocks, fraction strips, fraction tiles, counters, arrays, number lines, area models, place value disks, protractors, coins and bills. `r` uses tape/strip diagrams, number lines and area models (the Eureka/Texas representations). `look` says what a visitor would see students doing.
- `q`: `t1`, `t2`, `t3`, each with `assess` (2) and `advance` (2); `t3` also has `support` (2 moves).
- `stems`: 5 student sentence stems.

Rules
- General best practice, not tied to one curriculum. Don't name products or publishers.
- This is a set of look-fors and suggestions. Never write anything that evaluates teachers.
- **Student-facing text (`stems`, and any quoted student words) must never write a fraction with a slash.** Use words instead ("three-fourths", "1 fourth", "the unit fraction one-third"). Teacher-facing fields (`mis`, `cra`, `q`) may use a/b notation sparingly when it is clearer.
- No vocabulary in parentheses in student-facing text (write "rounding", not "rounding (estimating)").
- Use the exact Texas terms: "strip diagram", "expanded notation", "unit fraction", "personal financial literacy", etc. Match the SE's own boundaries: Grade 3 fractions use denominators 2, 3, 4, 6, 8; Grade 3 numbers go to 100,000; Grade 4 numbers go to 1,000,000,000 and decimals to hundredths; Grade 5 decimals go to thousandths.
- Supporting and not-assessed SEs (`t` = S or U) get the same depth as readiness SEs.
- Plain, warm language. Each string should be one or two sentences.
- Write valid UTF-8 JSON. Validate it with `python3 -c "import json;d=json.load(open('<path>'));print(len(d))"` and check that the count matches the input file.

Final reply: the path and the count only.
