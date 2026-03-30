"""
Fix all HTML pages:
1. Correct logo img attrs to match display size (width=140 height=70)
2. Update favicon links to use PNG + ICO instead of SVG only
"""
import glob

LOGO_OLD = 'src="logo/Prithivi%20logo.png" alt="Prithvi Foundation Logo" width="500" height="250"'
LOGO_NEW = 'src="logo/Prithivi%20logo.png" alt="Prithvi Foundation Logo" width="140" height="70"'

FAVICON_OLD = '''    <link rel="icon" type="image/svg+xml" href="logo/fav_icon.svg">
    <link rel="shortcut icon" href="logo/fav_icon.svg">'''
FAVICON_NEW = '''    <link rel="icon" type="image/x-icon" href="logo/favicon.ico">
    <link rel="icon" type="image/png" sizes="32x32" href="logo/favicon-32.png">
    <link rel="icon" type="image/png" sizes="192x192" href="logo/favicon-192.png">
    <link rel="apple-touch-icon" href="logo/favicon-192.png">'''

pages = glob.glob('*.html')
fixed = []
for f in pages:
    txt = open(f, encoding='utf-8').read()
    orig = txt
    txt = txt.replace(LOGO_OLD, LOGO_NEW)
    txt = txt.replace(FAVICON_OLD, FAVICON_NEW)
    if txt != orig:
        open(f, 'w', encoding='utf-8').write(txt)
        fixed.append(f)

print('Fixed:', fixed)
