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
if '--focus' in sys.argv:
    # option 2: ● = Module Overview focus standard, ○ = other TEKS the topic lists
    SRC2 = SRC + "; ● marks the module’s Focus Grade Level Standards (Module Overview), ○ the other TEKS listed for the lesson’s topic"
    R = [(a, b.replace(SRC, SRC2)) for a, b in R[:3]] + [
        ('<span><i class="dot"></i>bundled standard</span>', '<span><i class="dot"></i>also listed for the topic</span>'),
        ("<p class=\"note\">● marks a lesson's TEKS; ○ marks a bundled standard.",
         "<p class=\"note\">● module focus standard (Module Overview); ○ also listed for the lesson’s topic."),
        ('<span><i class="dot F"></i>lesson TEKS</span>', '<span><i class="dot F"></i>module focus standard</span>')]
if '--dots' in sys.argv:
    # Grades 3-5: lesson-by-lesson dot chart (dot_marks/); K-2 keep the Teacher Edition topic lists
    R[0] = (R[0][0], R[0][1].replace(SRC + ").", SRC + ")." + "${'K12'.includes(g)?'':' Dots come from a lesson-by-lesson reading of the Teacher Edition: ● the lesson’s Exit Ticket assesses the TEKS; ○ students use it in the lesson but the Exit Ticket does not assess it (fluency warm-ups not counted).'}"))
    R[1] = (R[1][0], R[1][1].replace(SRC + ").", SRC + ")." + "${'K12'.includes(g)?'':' Dots come from a lesson-by-lesson reading of the Teacher Edition: ● the lesson’s Exit Ticket assesses the TEKS; ○ students use it in the lesson but the Exit Ticket does not assess it (fluency warm-ups not counted).'}"))
    R[2] = (R[2][0], "with its TEKS. Grades 3–5: ● the lesson’s Exit Ticket assesses the TEKS, ○ students use it in the lesson; open a lesson to see why. Every Eureka lesson is here, supplemental lessons included.")
    R[4] = (R[4][0], "<p class=\"note\">${'K12'.includes(gradeOf(s.code))?'TEKS as listed in each lesson’s Teacher Edition topic overview.':'● the lesson’s Exit Ticket assesses this TEKS; ○ students use it in the lesson but the Exit Ticket does not assess it.'}")
    R.append(('<span class="sep" aria-hidden="true"></span><span><i class="dot F"></i>lesson TEKS</span>',
              '<span class="sep" aria-hidden="true"></span>${k2?\'<span><i class="dot F"></i>lesson TEKS</span>\':\'<span><i class="dot F"></i>assessed on the Exit Ticket</span><span><i class="dot"></i>used in the lesson, not assessed</span>\'}'))
miss = [a[:60] for a, b in R if a not in s]
for a, b in R: s = s.replace(a, b)
open(f, 'w').write(s)
print('te_teacher:', 'missing ' + str(miss) if miss else 'ok')
