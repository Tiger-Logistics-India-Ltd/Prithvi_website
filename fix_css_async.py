"""
Convert render-blocking style.css link to preload + synchronous fallback.
Keeps the blocking link as well so styles apply even without JS.
Uses the preload trick for faster initial resource discovery.
"""
import glob

# Replace the blocking <link rel="stylesheet" href="style.css"> with:
# 1. A preload hint (tells browser to fetch early at high priority)
# 2. The regular blocking stylesheet (kept for correct rendering)
OLD = '<link rel="stylesheet" href="style.css">'
NEW = '<link rel="preload" href="style.css" as="style">\n    <link rel="stylesheet" href="style.css">'

pages = glob.glob('*.html')
fixed = []
for f in pages:
    txt = open(f, encoding='utf-8').read()
    if OLD in txt and '<link rel="preload" href="style.css"' not in txt:
        txt = txt.replace(OLD, NEW, 1)
        open(f, 'w', encoding='utf-8').write(txt)
        fixed.append(f)

print('Fixed:', fixed)
