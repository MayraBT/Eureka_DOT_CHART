"""Give a TEKS Lookup page the shared neutral navy theme (yellow highlights kept).

usage: python3 retheme.py FILE.html carnegie|eureka   (edits in place; safe to rerun)
Also importable: from retheme import retheme

Colors are taken from the publishers' own teacher PDFs:
  Carnegie Learning TIGs (Grade 6 and Geometry): blue #007CBB, #3495C8, #8DBCDD, #E9F1F8,
    charcoal #231F20, grays #58595B #BCBEC0 #D1D3D4 #E6E7E8.
  Eureka Math TEKS Edition TEs: teal #00739A, plum #98204E, sage #839F68, slate #5F6878/#556577,
    near-black #251F1A, tints #E1F1FB #D0EAFA.
Semantic colors (amber highlights, red low scores, purple Dallas ISD bars) are left alone.
"""
import re, sys

NAVY = dict(ink='#1c2330', ink2='#4a5568', ink3='#7f8794', paper2='#f4f6f9', line='#d5dae2',
            brand='#1b365d', deep='#12263f', tint='#dce4f0', ghost='#f0f4f9',
            slate='#e5e8ee', slateink='#4f5b6b',
            mid='#3a5a8c', soft='#9fb3d1', pale='#f3f6fa', wash='#e6ecf4', gl='#e6e9ee', k50='#b8c0cc')
# Both curricula now share one neutral navy theme (the tools belong to the district, not a publisher).
TOKENS = {'carnegie': NAVY, 'eureka': NAVY, 'navy': NAVY}
# every color an earlier version used -> the navy role it now plays
LEGACY = {
    # original teal theme
    '#008c84': 'brand', '#00736c': 'deep', '#8fcbc7': 'soft', '#7fb8b4': 'soft', '#f2faf9': 'pale',
    '#e9f0ef': 'wash', '#e8eeed': 'gl', '#b9c6c5': 'k50', '#eceff0': 'gl', '#0d5f5c': 'deep',
    # Carnegie and Eureka publisher themes
    '#007cbb': 'brand', '#005a8c': 'deep', '#d9e9f5': 'tint', '#eef5fb': 'ghost', '#3495c8': 'mid',
    '#8dbcdd': 'soft', '#f2f7fb': 'pale', '#e9f1f8': 'wash', '#00739a': 'brand', '#00546f': 'deep',
    '#d6ebf6': 'tint', '#eef7fc': 'ghost', '#2f8fb3': 'mid', '#8cc3dc': 'soft', '#f1f8fc': 'pale',
    '#e1f1fb': 'wash', '#e6e8ec': 'gl', '#b9c3cc': 'k50',
}
# purples (they read as another publisher's palette) -> navy family / gold highlight
PURPLES = {'#7a5af5': '#c99a22', '#5b3fd1': '#7a5a00', '#7a5ea8': '#4f5b6b', '#b9a6da': '#b8c0cc',
           '#5b4a80': '#4f5b6b', '#f3f0fa': '#f1f3f6', '#f4f0fa': '#f1f3f6', '#f7f4fb': '#f3f6fa', '#4b3a6e': '#1b365d'}

ROOT = re.compile(r'(:root\s*\{)([^}]*)(\})')


def retheme(s, kind):
    t = TOKENS[kind]
    def root(m):
        body = m.group(2)
        for var, key in [('--ink', 'ink'), ('--ink-2', 'ink2'), ('--ink-3', 'ink3'), ('--paper-2', 'paper2'),
                         ('--line', 'line'), ('--teal', 'brand'), ('--teal-deep', 'deep'), ('--teal-tint', 'tint'),
                         ('--teal-ghost', 'ghost'), ('--slate', 'slate'), ('--slate-ink', 'slateink')]:
            body = re.sub(r'(%s\s*:\s*)#[0-9a-fA-F]{6}' % re.escape(var), r'\g<1>' + t[key], body)
        return m.group(1) + body + m.group(3)
    s = ROOT.sub(root, s, count=1)
    for old, key in LEGACY.items():
        s = re.sub(re.escape(old) + r'(?![0-9a-fA-F])', t[key], s, flags=re.I)
    for old, new in PURPLES.items():
        s = re.sub(re.escape(old) + r'(?![0-9a-fA-F])', new, s, flags=re.I)
    # the select-arrow icon is an encoded SVG
    s = re.sub(r'%23(147c78|007cbb|00739a)', '%23' + t['brand'][1:], s, flags=re.I)
    # drop the old Eureka plum/sage accents
    s = re.sub(r'/\*eureka-accents\*/[^\n]*\n', '', s)
    # yellow highlights on the navy: a gold rule under the header and on the selected tab
    if '/*navy-accents*/' not in s:
        extra = ('/*navy-accents*/ header{box-shadow:0 3px 0 #f2b705}'
                 ' .tabs button[aria-selected="true"]{border-left-color:#f2b705}'
                 ' @media (max-width:820px){.tabs button[aria-selected="true"]{border-bottom-color:#f2b705}}'
                 ' .hnav button[aria-current="true"]{box-shadow:inset 3px 0 0 #f2b705}')
        s = s.replace('</style>', extra + '\n</style>', 1)
    return s


if __name__ == '__main__':
    f, kind = sys.argv[1], sys.argv[2]
    s = open(f).read(); n = retheme(s, kind)
    open(f, 'w').write(n)
    print(f, kind, 'changed' if n != s else 'same')
