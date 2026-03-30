import glob

pages = glob.glob('*.html')
fixed = []
for f in pages:
    txt = open(f, encoding='utf-8').read()
    orig = txt
    # Replace webp logo with original PNG, fixing wrong width/height attrs
    txt = txt.replace(
        'src="logo/opt/Prithivi%20logo.webp" alt="Prithvi Foundation Logo" width="400" height="200"',
        'src="logo/Prithivi%20logo.png" alt="Prithvi Foundation Logo" width="500" height="250"'
    )
    # Add missing width/height to index.html's logo (no attrs version)
    txt = txt.replace(
        'src="logo/Prithivi%20logo.png" alt="Prithvi Foundation Logo">',
        'src="logo/Prithivi%20logo.png" alt="Prithvi Foundation Logo" width="500" height="250">'
    )
    if txt != orig:
        open(f, 'w', encoding='utf-8').write(txt)
        fixed.append(f)

print('Fixed:', fixed)
print('Total:', len(fixed), 'files')
