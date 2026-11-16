"""Replace the term "dot chart" with neutral wording.

usage: python3 dechart.py FILE [FILE ...]   (edits in place)
Also importable: from dechart import dechart
"""
import re, sys

PAIRS = [
    # Eureka subtitles and help
    ('Eureka Math TEKS Edition · dot chart built from the 2026-27 IPCs', 'Eureka Math TEKS Edition · TEKS Lookup built from the 2026-27 IPCs'),
    ('Eureka Math TEKS Edition has no dot chart, so this tool builds one from', 'Eureka Math TEKS Edition has no lesson-by-TEKS chart, so this tool builds one from'),
    ('Eureka doesn\'t publish a dot chart, so this tool builds one from', 'Eureka doesn\'t publish a lesson-by-TEKS chart, so this tool builds one from'),
    ('Full grid — The dot chart built from the IPCs', 'Full grid — every lesson and TEKS from the IPCs'),
    ('Full grid — The dot chart', 'Full grid — every lesson and TEKS'),
    ('The dot chart itself: lessons down the side', 'The whole grid: lessons down the side'),
    ('The whole dot chart: lessons down the side', 'The whole grid: lessons down the side'),
    # Carnegie's own document is the "TEKS Overview"
    ('Fully covered (dot chart)', 'Fully covered (TEKS Overview)'),
    ('Partially covered (dot chart)', 'Partially covered (TEKS Overview)'),
    ('neither the Grade 8 dot chart nor', 'neither the Grade 8 TEKS Overview nor'),
    ('marked “Omitted” on the dot chart', 'marked “Omitted” on the TEKS Overview'),
    ('(same dot chart as Algebra I HS)', '(same TEKS Overview as Algebra I HS)'),
    (' (dot chart as supplied in Word form)', ' (as supplied in Word form)'),
    ('since no dot chart was supplied for them', 'since no TEKS Overview was supplied for them'),
    ('share one dot chart', 'share one TEKS Overview'),
    ('Carnegie Learning dot charts (TEKS Overview)', 'Carnegie Learning TEKS Overviews'),
    ('Carnegie dot charts', 'Carnegie TEKS Overviews'),
    ('dot chart lookup', 'TEKS lookup'),
]


def dechart(s):
    for a, b in PAIRS:
        s = s.replace(a, b)
    # anything left: generic wording
    s = re.sub(r'\bdot charts\b', 'TEKS charts', s)
    s = re.sub(r'\bdot chart\b', 'TEKS chart', s)
    s = re.sub(r'\bDot charts\b', 'TEKS charts', s)
    s = re.sub(r'\bDot chart\b', 'TEKS chart', s)
    s = re.sub(r'\bDOT CHART\b', 'TEKS LOOKUP', s)
    return s


if __name__ == '__main__':
    for f in sys.argv[1:]:
        s = open(f).read(); t = dechart(s)
        if t != s: open(f, 'w').write(t)
        left = len(re.findall(r'(?i)dot[ -]?chart', t))
        print(f, 'changed' if t != s else 'same', '· left:', left)
