import re
import os

BASE_URL = "https://prithvifoundation.org"
OG_IMAGE = "https://prithvifoundation.org/logo/Prithivi%20logo.png"

html_files = [
    ("index.html", "/"),
    ("about.html", "/about.html"),
    ("gallery.html", "/gallery.html"),
    ("kothali.html", "/kothali.html"),
    ("brahman-bhoj.html", "/brahman-bhoj.html"),
    ("community-lunch.html", "/community-lunch.html"),
    ("educational-material-distribution.html", "/educational-material-distribution.html"),
    ("havan-pooja.html", "/havan-pooja.html"),
    ("spiritual-workshops.html", "/spiritual-workshops.html"),
    ("sports-activity.html", "/sports-activity.html"),
    ("tulsi-distribution.html", "/tulsi-distribution.html"),
    ("yoga-meditation.html", "/yoga-meditation.html"),
]

for filename, path in html_files:
    if not os.path.exists(filename):
        print(f"SKIP (not found): {filename}")
        continue

    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Revert logo in navbar (WebP → original PNG, fix dimensions to match PNG 500x250)
    content = content.replace(
        'src="logo/opt/Prithivi%20logo.webp" alt="Prithvi Foundation Logo" width="400" height="200"',
        'src="logo/Prithivi%20logo.png" alt="Prithvi Foundation Logo" width="500" height="250"'
    )

    # 2. Update favicon: SVG → PNG logo
    content = content.replace(
        '<link rel="icon" type="image/svg+xml" href="logo/fav_icon.svg">',
        '<link rel="icon" type="image/png" href="logo/Prithivi%20logo.png">\n    <link rel="apple-touch-icon" href="logo/Prithivi%20logo.png">'
    )

    # 3. Extract title and description for OG tags
    title_match = re.search(r'<title>(.*?)</title>', content)
    desc_match = re.search(r'<meta name="description" content="(.*?)"', content)
    title = title_match.group(1) if title_match else "Prithvi Foundation"
    description = desc_match.group(1) if desc_match else "Prithvi Foundation - NGO in Tehri Garhwal, Uttarakhand"
    url = BASE_URL + path

    # 4. Add canonical + OG tags after <meta name="robots"> (only if not already present)
    robots_line = '    <meta name="robots" content="index, follow">'
    og_block = f'''    <meta name="robots" content="index, follow">
    <link rel="canonical" href="{url}">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{url}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="{OG_IMAGE}">
    <meta property="og:site_name" content="Prithvi Foundation">'''

    if 'property="og:title"' not in content:
        content = content.replace(robots_line, og_block, 1)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Updated: {filename}")

print("\nAll done!")
