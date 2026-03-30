"""
apply_all.py — Full update for Prithvi Foundation website.
- Fixes index.html (restored from git): applies image optimization paths, lazy loading,
  favicon, async fonts, meta tags, OG tags, keyword meta, canonical.
- Adds OG tags + keyword meta + canonical to ALL pages.
- Uses original logo (logo/Prithivi logo.png) for nav, OG image.
"""

import re
from pathlib import Path
from PIL import Image as PILImage

ROOT = Path(__file__).parent

SITE_URL = "https://prithvifoundation.org"
OG_IMAGE = f"{SITE_URL}/logo/Prithivi%20logo.png"   # original logo for OG preview

# ── Per-page metadata ──────────────────────────────────────────────────────────
PAGE_META = {
    "index.html": {
        "title": "Prithvi Foundation - Tehri Garhwal, Uttarakhand",
        "desc": "Prithvi Foundation is an NGO serving society through spiritual, humanitarian, and community-focused initiatives in Tehri Garhwal, Uttarakhand.",
        "canonical": f"{SITE_URL}/",
        "og_url": f"{SITE_URL}/",
    },
    "about.html": {
        "title": "About - Prithvi Foundation",
        "desc": "Learn about Prithvi Foundation, an NGO based in Tehri Garhwal, Uttarakhand, dedicated to spiritual and community service.",
        "canonical": f"{SITE_URL}/about.html",
        "og_url": f"{SITE_URL}/about.html",
    },
    "gallery.html": {
        "title": "Gallery - Prithvi Foundation",
        "desc": "Photo gallery of Prithvi Foundation activities including yoga, Havan, community lunch, educational distribution, and more.",
        "canonical": f"{SITE_URL}/gallery.html",
        "og_url": f"{SITE_URL}/gallery.html",
    },
    "kothali.html": {
        "title": "Prithvi Spiritual Centre - Prithvi Foundation",
        "desc": "Prithvi Spiritual Centre at Kothali Village — a place of devotion, yoga, meditation, and community service.",
        "canonical": f"{SITE_URL}/kothali.html",
        "og_url": f"{SITE_URL}/kothali.html",
    },
    "brahman-bhoj.html": {
        "title": "Brahman Bhoj - Prithvi Foundation",
        "desc": "Brahman Bhoj by Prithvi Foundation — honouring the tradition of serving Brahmans through community meals.",
        "canonical": f"{SITE_URL}/brahman-bhoj.html",
        "og_url": f"{SITE_URL}/brahman-bhoj.html",
    },
    "community-lunch.html": {
        "title": "Community Lunch - Prithvi Foundation",
        "desc": "Community Lunch initiatives by Prithvi Foundation bringing people together through shared meals.",
        "canonical": f"{SITE_URL}/community-lunch.html",
        "og_url": f"{SITE_URL}/community-lunch.html",
    },
    "educational-material-distribution.html": {
        "title": "Educational Material Distribution - Prithvi Foundation",
        "desc": "Prithvi Foundation distributes educational materials and school stationery to support children in Tehri Garhwal.",
        "canonical": f"{SITE_URL}/educational-material-distribution.html",
        "og_url": f"{SITE_URL}/educational-material-distribution.html",
    },
    "havan-pooja.html": {
        "title": "Havan & Pooja - Prithvi Foundation",
        "desc": "Havan and Pooja ceremonies organized by Prithvi Foundation for spiritual well-being and community harmony.",
        "canonical": f"{SITE_URL}/havan-pooja.html",
        "og_url": f"{SITE_URL}/havan-pooja.html",
    },
    "spiritual-workshops.html": {
        "title": "Spiritual Workshops - Prithvi Foundation",
        "desc": "Spiritual Workshops and meditation retreats organized by Prithvi Foundation in Uttarakhand.",
        "canonical": f"{SITE_URL}/spiritual-workshops.html",
        "og_url": f"{SITE_URL}/spiritual-workshops.html",
    },
    "sports-activity.html": {
        "title": "Sports Activity - Prithvi Foundation",
        "desc": "Sports activities and programs organized by Prithvi Foundation to promote health and well-being.",
        "canonical": f"{SITE_URL}/sports-activity.html",
        "og_url": f"{SITE_URL}/sports-activity.html",
    },
    "tulsi-distribution.html": {
        "title": "Herbal Plantation Drive - Prithvi Foundation",
        "desc": "Herbal Plantation Drive by Prithvi Foundation — distributing Tulsi and medicinal plants to promote green living.",
        "canonical": f"{SITE_URL}/tulsi-distribution.html",
        "og_url": f"{SITE_URL}/tulsi-distribution.html",
    },
    "yoga-meditation.html": {
        "title": "Yoga & Meditation - Prithvi Foundation",
        "desc": "Yoga and Meditation programs by Prithvi Foundation at the Prithvi Spiritual Centre, Kothali, Uttarakhand.",
        "canonical": f"{SITE_URL}/yoga-meditation.html",
        "og_url": f"{SITE_URL}/yoga-meditation.html",
    },
}

KEYWORDS = "Prithvi Foundation, NGO Uttarakhand, Tehri Garhwal, spiritual centre, community service, seva, yoga meditation, havan pooja"

ASYNC_FONTS = """    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&display=swap">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&display=swap" media="print" onload="this.media='all'">
    <noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&display=swap"></noscript>"""

# ── Image helpers ──────────────────────────────────────────────────────────────

HERO_SRCS_OLD = {
    "Images/Prayer_Mandir/final/WhatsApp%20Image%202025-03-02%20at%208.04.42%20PM.jpeg",
    "Images/Prayer_Havan%20Group/Final/Group%20Prayer.jpeg",
    "Images/Yoga%20in%20Open%20Meditation%20Area/final/WhatsApp%20Image%202025-03-02%20at%208.09.19%20PM.jpeg",
    "Images/Shaanti%20Puja/WhatsApp%20Image%202025-03-02%20at%204.41.07%20PM.jpeg",
    "Images/Community%20Lunch/final/WhatsApp%20Image%202025-03-02%20at%208.24.33%20PM.jpeg",
}
LCP_SRC = "Images/Prayer_Mandir/final/WhatsApp%20Image%202025-03-02%20at%208.04.42%20PM.jpeg"


def webp_path(src: str) -> str:
    s = src.replace("\\", "/").replace(" ", "%20")
    if s.startswith("Images/"):
        s = "Images/opt/" + s[len("Images/"):]
    elif s.startswith("logo/") and "opt" not in s:
        s = "logo/opt/" + s[len("logo/"):]
    return re.sub(r'\.(jpe?g|png)$', '.webp', s, flags=re.IGNORECASE)


def get_dims(webp_src: str):
    path = ROOT / webp_src.replace("%20", " ")
    if not path.exists():
        return None
    try:
        with PILImage.open(path) as im:
            return im.size
    except Exception:
        return None


IMG_RE = re.compile(r'<img\b[^>]*/?>|<img\b[^>]*>', re.IGNORECASE)


def transform_img(m: re.Match) -> str:
    tag = m.group(0)
    src_m = re.search(r'\bsrc="([^"]*)"', tag)
    if not src_m:
        return tag
    old_src = src_m.group(1)
    if old_src.startswith("data:") or old_src.startswith("http"):
        return tag

    # Keep original logo in nav (do not webp-ify logo in navbar)
    # But DO apply webp to logo/opt which is already done in other pages
    is_nav_logo = "Prithivi%20logo.png" in old_src or "Prithivi logo.png" in old_src

    if is_nav_logo:
        # Always use original logo in navbar
        new_src = "logo/Prithivi%20logo.png"
        tag = re.sub(r'\bsrc="[^"]*"', f'src="{new_src}"', tag)
        # Remove any width/height that was for the webp version; add correct ones
        tag = re.sub(r'\s+width="\d+"', '', tag)
        tag = re.sub(r'\s+height="\d+"', '', tag)
        # Remove loading=lazy from logo
        tag = tag.replace('loading="lazy" ', '').replace(' loading="lazy"', '')
        return tag

    # Already a webp opt path — skip
    if "/opt/" in old_src and old_src.endswith(".webp"):
        return tag

    new_src = webp_path(old_src)
    tag = re.sub(r'\bsrc="[^"]*"', f'src="{new_src}"', tag)

    is_hero = old_src in HERO_SRCS_OLD
    is_priority = old_src == LCP_SRC

    if not is_hero and 'loading=' not in tag:
        tag = tag.replace('<img ', '<img loading="lazy" ')
    if is_priority and 'fetchpriority=' not in tag:
        tag = tag.replace('<img ', '<img fetchpriority="high" ')

    if 'width=' not in tag and 'height=' not in tag:
        dims = get_dims(new_src)
        if dims:
            tag = re.sub(r'\s*/?>$', f' width="{dims[0]}" height="{dims[1]}">', tag.rstrip())

    return tag


# ── Head block builder ─────────────────────────────────────────────────────────

def build_head(fname: str, existing_head: str) -> str:
    meta = PAGE_META.get(fname, {})
    title = meta.get("title", "Prithvi Foundation")
    desc = meta.get("desc", "")
    canonical = meta.get("canonical", SITE_URL + "/")
    og_url = meta.get("og_url", canonical)

    # Start fresh with a clean, ordered head
    head = f"""<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{desc}">
    <meta name="keywords" content="{KEYWORDS}">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="{canonical}">

    <!-- Open Graph / Social Preview -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="{og_url}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{desc}">
    <meta property="og:image" content="{OG_IMAGE}">
    <meta property="og:image:width" content="500">
    <meta property="og:image:height" content="250">
    <meta property="og:site_name" content="Prithvi Foundation">

    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{desc}">
    <meta name="twitter:image" content="{OG_IMAGE}">

    <link rel="stylesheet" href="style.css">
    <link rel="icon" type="image/svg+xml" href="logo/fav_icon.svg">
    <link rel="shortcut icon" href="logo/fav_icon.svg">

    <!-- Async Google Fonts -->
{ASYNC_FONTS}
    <!-- LCP preload (index only) -->"""

    if fname == "index.html":
        head += f'\n    <link rel="preload" as="image" href="Images/opt/Prayer_Mandir/final/WhatsApp%20Image%202025-03-02%20at%208.04.42%20PM.webp" type="image/webp">'

    head += "\n</head>"
    return head


# ── Main transform ──────────────────────────────────────────────────────────────

def transform(fname: str, html: str) -> str:
    # 1. Replace entire <head>…</head>
    head_m = re.search(r'<head>.*?</head>', html, re.DOTALL | re.IGNORECASE)
    if head_m:
        new_head = build_head(fname, head_m.group(0))
        html = html[:head_m.start()] + new_head + html[head_m.end():]

    # 2. Transform all image tags
    html = IMG_RE.sub(transform_img, html)

    return html


def main():
    print("=" * 60)
    for f in sorted(ROOT.glob("*.html")):
        original = f.read_text(encoding="utf-8")
        updated = transform(f.name, original)
        if updated != original:
            f.write_text(updated, encoding="utf-8")
            print(f"  ✓ {f.name}")
        else:
            print(f"  - {f.name} (no change)")
    print("=" * 60)
    print("Done.")


if __name__ == "__main__":
    main()
