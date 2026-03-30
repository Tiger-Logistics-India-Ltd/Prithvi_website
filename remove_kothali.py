"""
remove_kothali.py — Removes all "kothali" references from the entire website.
- Creates spiritual-centre.html from kothali.html (cleaned)
- Adds redirect in kothali.html → spiritual-centre.html (for old links)
- Updates all nav links, anchors, alt text, body text
- Updates sitemap.xml
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent

# ── Read kothali.html, clean it, save as spiritual-centre.html ─────────────────
kothali = (ROOT / "kothali.html").read_text(encoding="utf-8")

# Fix meta/canonical/OG URLs
kothali = kothali.replace(
    '<meta name="description" content="Prithvi Spiritual Centre at Kothali Village — a place of devotion, yoga, meditation, and community service.">',
    '<meta name="description" content="Prithvi Spiritual Centre — a place of devotion, yoga, meditation, and community service in Uttarakhand.">'
)
kothali = kothali.replace(
    'href="https://prithvifoundation.org/kothali.html"',
    'href="https://prithvifoundation.org/spiritual-centre.html"'
)
kothali = kothali.replace(
    'content="https://prithvifoundation.org/kothali.html"',
    'content="https://prithvifoundation.org/spiritual-centre.html"'
)
kothali = kothali.replace(
    'content="Prithvi Spiritual Centre at Kothali Village — a place of devotion, yoga, meditation, and community service."',
    'content="Prithvi Spiritual Centre — a place of devotion, yoga, meditation, and community service in Uttarakhand."'
)

# Fix nav links inside kothali (now spiritual-centre) page
kothali = kothali.replace(
    '<a href="kothali.html">Prithvi Spiritual Centre</a>',
    '<a href="spiritual-centre.html" class="active">Prithvi Spiritual Centre</a>'
)

# Fix section id
kothali = kothali.replace('id="kothali-centre"', 'id="spiritual-centre"')

# Fix alt texts
kothali = kothali.replace('alt="Kothali Centre"', 'alt="Prithvi Spiritual Centre"')
kothali = kothali.replace('alt="Yoga at Kothali"', 'alt="Yoga at Prithvi Spiritual Centre"')

# Fix body text — remove "Kothali Village" → "our serene spiritual centre"
kothali = kothali.replace(
    "Nestled in the serene surroundings of Kothali Village, the Prithvi Foundation's spiritual centre serves",
    "The Prithvi Foundation's spiritual centre serves"
)
kothali = kothali.replace(
    "Through these efforts, the Kothali centre continues to stand",
    "Through these efforts, the Prithvi Spiritual Centre continues to stand"
)

# Write spiritual-centre.html
(ROOT / "spiritual-centre.html").write_text(kothali, encoding="utf-8")
print("  ✓ Created spiritual-centre.html")

# ── kothali.html → 301-equivalent meta refresh redirect ────────────────────────
redirect_page = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0; url=spiritual-centre.html">
    <link rel="canonical" href="https://prithvifoundation.org/spiritual-centre.html">
    <title>Redirecting...</title>
</head>
<body>
    <p>This page has moved. <a href="spiritual-centre.html">Click here</a>.</p>
</body>
</html>"""
(ROOT / "kothali.html").write_text(redirect_page, encoding="utf-8")
print("  ✓ kothali.html → redirect to spiritual-centre.html")

# ── Per-file replacements ───────────────────────────────────────────────────────
REPLACEMENTS = {
    "index.html": [
        # Nav dropdown link
        ('<a href="about.html#kothali-centre">Kothali Spiritual Centre</a>',
         '<a href="spiritual-centre.html">Prithvi Spiritual Centre</a>'),
        # Section comment + heading
        ('<!-- Kothali Spiritual Centre Section -->\n<div class="kothali-section">\n    <h2>Kothali Spiritual Centre</h2>',
         '<!-- Prithvi Spiritual Centre Section -->\n<div class="kothali-section">\n    <h2>Prithvi Spiritual Centre</h2>'),
        # Alt texts
        ('alt="Kothali Centre"', 'alt="Prithvi Spiritual Centre"'),
        # Body text (paragraph 1)
        ("Nestled in the serene surroundings of Kothali Village, the Prithvi Foundation's spiritual centre serves as a place of devotion, community service, and collective well-being. Rooted in the spirit of seva and spiritual harmony, the centre brings together people from nearby villages and visiting devotees through a range of spiritual, cultural, and community-focused activities.",
         "The Prithvi Foundation's spiritual centre serves as a place of devotion, community service, and collective well-being. Rooted in the spirit of seva and spiritual harmony, the centre brings together people from nearby villages and visiting devotees through a range of spiritual, cultural, and community-focused activities."),
        # Read more link
        ('<a href="about.html#kothali-centre">Read more about Kothali Spiritual Centre &raquo;</a>',
         '<a href="spiritual-centre.html">Read more about Prithvi Spiritual Centre &raquo;</a>'),
        # Address — remove "Kothali Village" line
        ('        Kothali Village<br>\n', ''),
    ],
    "gallery.html": [
        ('<a href="kothali.html">Prithvi Spiritual Centre</a>',
         '<a href="spiritual-centre.html">Prithvi Spiritual Centre</a>'),
        ('alt="Kothali Mandir"', 'alt="Prithvi Foundation Mandir"'),
        ('<span>Kothali Mandir</span>', '<span>Prithvi Foundation Mandir</span>'),
    ],
    "sports-activity.html": [
        ('<a href="kothali.html">Prithvi Spiritual Centre</a>',
         '<a href="spiritual-centre.html">Prithvi Spiritual Centre</a>'),
        ('children and youth from Kothali and surrounding villages',
         'children and youth from surrounding villages'),
    ],
    "tulsi-distribution.html": [
        ('<a href="kothali.html">Prithvi Spiritual Centre</a>',
         '<a href="spiritual-centre.html">Prithvi Spiritual Centre</a>'),
        ('distributes Tulsi saplings to families in Kothali and surrounding villages',
         'distributes Tulsi saplings to families in surrounding villages'),
    ],
    "yoga-meditation.html": [
        ('<a href="kothali.html">Prithvi Spiritual Centre</a>',
         '<a href="spiritual-centre.html">Prithvi Spiritual Centre</a>'),
        ('Prithvi Spiritual Centre, Kothali, Uttarakhand',
         'Prithvi Spiritual Centre, Uttarakhand'),
    ],
}

# Pages that only need the nav link updated
NAV_ONLY_PAGES = [
    "about.html", "brahman-bhoj.html", "community-lunch.html",
    "educational-material-distribution.html", "havan-pooja.html",
    "spiritual-workshops.html",
]
for p in NAV_ONLY_PAGES:
    REPLACEMENTS.setdefault(p, []).append((
        '<a href="kothali.html">Prithvi Spiritual Centre</a>',
        '<a href="spiritual-centre.html">Prithvi Spiritual Centre</a>'
    ))

# Apply all replacements
for fname, changes in REPLACEMENTS.items():
    path = ROOT / fname
    if not path.exists():
        print(f"  ! Skipped (not found): {fname}")
        continue
    content = path.read_text(encoding="utf-8")
    modified = False
    for old, new in changes:
        if old in content:
            content = content.replace(old, new)
            modified = True
    if modified:
        path.write_text(content, encoding="utf-8")
        print(f"  ✓ Updated: {fname}")
    else:
        print(f"  - No match in: {fname}")

# ── sitemap.xml ────────────────────────────────────────────────────────────────
sitemap_path = ROOT / "sitemap.xml"
sitemap = sitemap_path.read_text(encoding="utf-8")
sitemap = sitemap.replace(
    "https://prithvifoundation.org/kothali.html",
    "https://prithvifoundation.org/spiritual-centre.html"
)
sitemap_path.write_text(sitemap, encoding="utf-8")
print("  ✓ Updated: sitemap.xml")

print("\nDone.")
