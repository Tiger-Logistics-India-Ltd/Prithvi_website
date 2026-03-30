"""
HTML updater for Prithvi Foundation website.
Transforms all HTML files to:
1. Use optimized WebP images (Images/opt/... and logo/opt/...)
2. Add loading="lazy" to below-the-fold images
3. Add explicit width & height attributes (prevents CLS)
4. Add fetchpriority="high" to the first hero/above-fold image
5. Preconnect for Google Fonts and async font loading (reduce render-blocking)
6. Add <meta name="description"> to pages missing it
"""

import re
from pathlib import Path
from PIL import Image as PILImage

ROOT = Path(__file__).parent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def webp_path(src: str) -> str:
    """
    Convert an image src attribute value to its optimized WebP counterpart.
    Handles both forward- and back-slash paths, URL-encoded spaces, etc.

    Examples:
      Images/Prayer_Mandir/final/WhatsApp%20Image….jpeg
        → Images/opt/Prayer_Mandir/final/WhatsApp%20Image….webp
      Images\Sports Activity\sports.jpeg
        → Images/opt/Sports%20Activity/sports.webp
      logo/Prithivi%20logo.png
        → logo/opt/Prithivi%20logo.webp
    """
    # Normalise back-slashes
    s = src.replace("\\", "/")

    # Insert /opt/ after the base folder (Images or logo)
    if s.startswith("Images/"):
        s = "Images/opt/" + s[len("Images/"):]
    elif s.startswith("logo/"):
        s = "logo/opt/" + s[len("logo/"):]

    # URL-encode spaces that appear as literal spaces (e.g. Images\Sports Activity)
    s = s.replace(" ", "%20")

    # Change extension to .webp
    s = re.sub(r'\.(jpe?g|png)$', '.webp', s, flags=re.IGNORECASE)

    return s


def get_img_dimensions(src: str) -> tuple[int, int] | None:
    """
    Return (width, height) in pixels of the optimised WebP image, or None.
    src is the NEW webp src value (URL-encoded, forward slashes).
    """
    # Build filesystem path from src
    decoded = src.replace("%20", " ")
    img_path = ROOT / decoded
    if not img_path.exists():
        return None
    try:
        with PILImage.open(img_path) as im:
            return im.size  # (width, height)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# CSS/Font render-blocking fix helpers
# ---------------------------------------------------------------------------

FONT_PRECONNECT = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '    '
)

def fix_font_loading(html: str) -> str:
    """
    Replace synchronous Google Fonts <link> with async loading pattern
    and add preconnect hints.
    Font URL pattern: fonts.googleapis.com/css2?...
    """
    # Match: <link rel="stylesheet" href="https://fonts.googleapis.com/css2?...">
    font_link_re = re.compile(
        r'<link\s[^>]*href="(https://fonts\.googleapis\.com/css2[^"]*)"[^>]*>',
        re.IGNORECASE
    )

    def replace_font(m):
        url = m.group(1)
        # Ensure display=swap is present
        if "display=swap" not in url:
            url += ("&" if "?" in url else "?") + "display=swap"
        return (
            f'<link rel="preload" as="style" href="{url}">\n'
            f'    <link rel="stylesheet" href="{url}" media="print" onload="this.media=\'all\'">\n'
            f'    <noscript><link rel="stylesheet" href="{url}"></noscript>'
        )

    html = font_link_re.sub(replace_font, html)
    return html


def add_preconnect(html: str) -> str:
    """Add Google Fonts preconnect if font is referenced but preconnect isn't there yet."""
    if "fonts.googleapis.com" in html and 'preconnect" href="https://fonts.googleapis.com"' not in html:
        html = html.replace(
            '<link rel="preload" as="style" href="https://fonts.googleapis.com',
            FONT_PRECONNECT + '<link rel="preload" as="style" href="https://fonts.googleapis.com',
        )
    return html


# ---------------------------------------------------------------------------
# Core image-tag transformer
# ---------------------------------------------------------------------------

# Hero / above-fold images per page — these get fetchpriority="high", no lazy
HERO_SRCS = {
    # index.html hero slider images (first one is LCP)
    "Images/Prayer_Mandir/final/WhatsApp%20Image%202025-03-02%20at%208.04.42%20PM.jpeg",
    "Images/Prayer_Havan%20Group/Final/Group%20Prayer.jpeg",
    "Images/Yoga%20in%20Open%20Meditation%20Area/final/WhatsApp%20Image%202025-03-02%20at%208.09.19%20PM.jpeg",
    "Images/Shaanti%20Puja/WhatsApp%20Image%202025-03-02%20at%204.41.07%20PM.jpeg",
    "Images/Community%20Lunch/final/WhatsApp%20Image%202025-03-02%20at%208.24.33%20PM.jpeg",
    # logo always eager
    "logo/Prithivi%20logo.png",
}

# This is the very first hero image (LCP candidate) — add fetchpriority="high"
PRIORITY_SRC = "Images/Prayer_Mandir/final/WhatsApp%20Image%202025-03-02%20at%208.04.42%20PM.jpeg"


def transform_img_tag(m: re.Match, page_file: str) -> str:
    """
    Transform a single <img ...> tag:
    - Rewrite src to WebP optimised path
    - Add loading="lazy" (unless hero)
    - Add fetchpriority="high" to LCP candidate
    - Add width & height from actual image file
    - Keep all other attributes
    """
    tag = m.group(0)

    # Extract current src
    src_m = re.search(r'\bsrc="([^"]*)"', tag)
    if not src_m:
        return tag
    old_src = src_m.group(1)

    # Skip data URIs and external images
    if old_src.startswith("data:") or old_src.startswith("http"):
        return tag

    # New WebP src
    new_src = webp_path(old_src)

    # Determine if above-fold
    is_hero = old_src in HERO_SRCS
    is_priority = old_src == PRIORITY_SRC

    # Build replacement tag — start fresh from existing attributes
    # Preserve: alt, class, style, id, aria-*, data-*
    # Replace: src
    # Add: loading (if not hero), fetchpriority (if priority), width, height

    tag = re.sub(r'\bsrc="[^"]*"', f'src="{new_src}"', tag)

    # Add loading="lazy" if not already there and not hero
    if not is_hero and 'loading=' not in tag:
        tag = tag.replace('<img ', '<img loading="lazy" ')

    # Add fetchpriority="high" to priority image
    if is_priority and 'fetchpriority=' not in tag:
        tag = tag.replace('<img ', '<img fetchpriority="high" ')

    # Add width/height if missing
    if 'width=' not in tag and 'height=' not in tag:
        dims = get_img_dimensions(new_src)
        if dims:
            w, h = dims
            # Insert before closing >
            tag = re.sub(r'\s*/?>$', f' width="{w}" height="{h}">', tag.rstrip())

    return tag


IMG_RE = re.compile(r'<img\b[^>]*/?>|<img\b[^>]*>', re.IGNORECASE)


def transform_html(html: str, page_file: str) -> str:
    """Apply all transformations to the full HTML content."""
    # Fix font loading (render-blocking)
    html = fix_font_loading(html)
    html = add_preconnect(html)

    # Transform image tags
    html = IMG_RE.sub(lambda m: transform_img_tag(m, page_file), html)

    # Add meta description if missing (SEO fix)
    if '<meta name="description"' not in html and '<meta name="robots"' in html:
        desc_map = {
            "index.html": "Prithvi Foundation is an NGO serving society through spiritual, humanitarian, and community-focused initiatives in Tehri Garhwal, Uttarakhand.",
            "about.html": "Learn about Prithvi Foundation, an NGO based in Tehri Garhwal, Uttarakhand, dedicated to spiritual and community service.",
            "gallery.html": "Photo gallery of Prithvi Foundation activities including yoga, Havan, community lunch, educational distribution, and more.",
            "kothali.html": "Prithvi Spiritual Centre at Kothali Village — a place of devotion, yoga, meditation, and community service.",
            "brahman-bhoj.html": "Brahman Bhoj by Prithvi Foundation — honouring the tradition of serving Brahmans through community meals.",
            "community-lunch.html": "Community Lunch initiatives by Prithvi Foundation bringing people together through shared meals.",
            "educational-material-distribution.html": "Prithvi Foundation distributes educational materials and school stationery to support children in Tehri Garhwal.",
            "havan-pooja.html": "Havan and Pooja ceremonies organized by Prithvi Foundation for spiritual well-being and community harmony.",
            "spiritual-workshops.html": "Spiritual Workshops and meditation retreats organized by Prithvi Foundation in Uttarakhand.",
            "sports-activity.html": "Sports activities and programs organized by Prithvi Foundation to promote health and well-being.",
            "tulsi-distribution.html": "Herbal Plantation Drive by Prithvi Foundation — distributing Tulsi and medicinal plants to promote green living.",
            "yoga-meditation.html": "Yoga and Meditation programs by Prithvi Foundation at the Prithvi Spiritual Centre, Kothali, Uttarakhand.",
        }
        p = Path(page_file).name
        desc = desc_map.get(p, "Prithvi Foundation - Serving society through spirituality and seva.")
        html = html.replace(
            '<meta name="robots"',
            f'<meta name="description" content="{desc}">\n    <meta name="robots"'
        )

    return html


# ---------------------------------------------------------------------------
# Process all HTML files
# ---------------------------------------------------------------------------

def main():
    html_files = sorted(ROOT.glob("*.html"))
    for html_file in html_files:
        original = html_file.read_text(encoding="utf-8")
        updated = transform_html(original, str(html_file))
        if updated != original:
            html_file.write_text(updated, encoding="utf-8")
            print(f"  ✓ Updated: {html_file.name}")
        else:
            print(f"  - No changes: {html_file.name}")

    print(f"\nDone. Processed {len(html_files)} HTML files.")


if __name__ == "__main__":
    main()
