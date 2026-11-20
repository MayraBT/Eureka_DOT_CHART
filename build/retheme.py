"""Give a TEKS Lookup page its curriculum's colors.

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

TOKENS = {
    'carnegie': dict(ink='#231f20', ink2='#58595b', ink3='#808285', paper2='#f5f6f7', line='#d1d3d4',
                     brand='#007cbb', deep='#005a8c', tint='#d9e9f5', ghost='#eef5fb',
                     slate='#e6e7e8', slateink='#58595b',
                     mid='#3495c8', soft='#8dbcdd', pale='#f2f7fb', wash='#e9f1f8', gl='#e6e7e8', k50='#bcbec0'),
    'eureka':   dict(ink='#251f1a', ink2='#556577', ink3='#8a909c', paper2='#f5f6f8', line='#d8d7d6',
                     brand='#00739a', deep='#00546f', tint='#d6ebf6', ghost='#eef7fc',
                     slate='#e4e6ea', slateink='#5f6878',
                     mid='#2f8fb3', soft='#8cc3dc', pale='#f1f8fc', wash='#e1f1fb', gl='#e6e8ec', k50='#b9c3cc'),
}

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
    # hard-coded teal family from the original theme -> curriculum equivalents
    for old, key in [('#008c84', 'brand'), ('#00736c', 'deep'), ('#8fcbc7', 'soft'), ('#7fb8b4', 'soft'),
                     ('#f2faf9', 'pale'), ('#e9f0ef', 'wash'), ('#e8eeed', 'gl'), ('#b9c6c5', 'k50'),
                     ('#eceff0', 'gl')]:
        s = re.sub(re.escape(old), t[key], s, flags=re.I)
    # the select-arrow icon is an encoded SVG
    s = re.sub(r'%23147c78', '%23' + t['brand'][1:], s, flags=re.I)
    # Eureka: its plum section headings and sage accents, as in the TE
    if kind == 'eureka' and '/*eureka-accents*/' not in s:
        extra = ('/*eureka-accents*/ .modlist>details>summary{color:#98204e;border-left:4px solid #98204e}'
                 ' .modlist>details[open]>summary{border-left-color:#839f68}'
                 ' .detail details>summary{color:#98204e}')
        s = s.replace('</style>', extra + '\n</style>', 1)
    return s


if __name__ == '__main__':
    f, kind = sys.argv[1], sys.argv[2]
    s = open(f).read(); n = retheme(s, kind)
    open(f, 'w').write(n)
    print(f, kind, 'changed' if n != s else 'same')
