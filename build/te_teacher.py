"""Wording for the Teacher-Edition-only teacher build (run after teacherize.py).

usage: python3 te_teacher.py eureka_teacher/index.html
The data comes from TE_ONLY=1 build_data.py: every Eureka lesson, TEKS from the Teacher Edition
topic overviews (and Supplement overviews), no IPC pacing, TEKS or Scope & Sequence data."""
import sys
f = sys.argv[1]; s = open(f).read()
SRC = ("each lesson lists the TEKS of its topic in the module’s Overview of Module Topics and Lesson Objectives; "
       "supplemental lessons list the TEKS in the Supplement Overview")
R = [
    ("Lessons, lesson objectives and TEKS: Eureka Math TEKS Edition, Grade ${g} (● = lesson TEKS, ○ = bundled standards). "
     "Modules, topics, focus and included TEKS, and omitted lessons: Eureka Math TEKS Edition Grade ${g} Scope and Sequence, 2026-27.",
     "Lessons, lesson objectives, modules, topics and TEKS: Eureka Math TEKS Edition Teacher Editions, Grade ${g} (" + SRC + ")."),
    ("Lessons, lesson objectives and TEKS: Eureka Math TEKS Edition, ${g==='K'?'Kindergarten':'Grade '+g} (● = lesson TEKS, ○ = bundled standards). "
     "Modules, topics and TEKS: Eureka Math TEKS Edition Scope and Sequence, 2026-27.",
     "Lessons, lesson objectives, modules, topics and TEKS: Eureka Math TEKS Edition Teacher Editions, ${g==='K'?'Kindergarten':'Grade '+g} (" + SRC + ")."),
    ("with its TEKS: ● lesson TEKS, ○ bundled standard. Each module starts with its Scope &amp; Sequence TEKS and omitted lessons.",
     "with the TEKS its Teacher Edition lists for it. Every Eureka lesson is here, supplemental lessons included."),
    ('<span><i class="dot"></i>bundled standard</span>', ''),
    ("<p class=\"note\">● marks a lesson's TEKS; ○ marks a bundled standard.", "<p class=\"note\">TEKS as listed in each lesson’s Teacher Edition topic overview."),
]
miss = [a[:60] for a, b in R if a not in s]
for a, b in R: s = s.replace(a, b)
open(f, 'w').write(s)
print('te_teacher:', 'missing ' + str(miss) if miss else 'ok')
