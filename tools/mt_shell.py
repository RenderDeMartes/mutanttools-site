# -*- coding: utf-8 -*-
"""Page shell for the new mutanttools.com docs pages.

The Astra theme ships as ~95 KB of inline CSS inside every page's <head>. Rather
than reimplement the site's look, the shell is lifted verbatim from the existing
/developer/ page (header, footer, fonts, palette) and only the <title>, meta and
main content are swapped. That keeps every new page pixel-identical to the rest
of the site and means a theme change upstream still applies here.
"""
import hashlib, io, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = HERE                   # the shell_*.html fragments sit beside this file
SITE = os.path.dirname(HERE)     # the site root is this folder's parent


def _part(name):
    return io.open(os.path.join(SCRATCH, "shell_%s.html" % name), encoding="utf-8").read()


HEAD = _part("HEAD")
PRE = _part("PRE")
HEADER = _part("HEADER")
MID = _part("MID")
FOOTER = _part("FOOTER")
TAIL = _part("TAIL")

# The nav's Wiki entry still points at the old Sphinx build. Every page the
# generator writes sends it to the new wiki instead; /docs/ stays reachable.
HEADER = HEADER.replace("/docs/_build/html/index.html", "/wiki/")

# The shell came off the Developer page, so it carries that page's "you are
# here" markers. Strip them here and re-apply per page in page(), or every
# generated page would highlight Developer in the nav.
HEADER = HEADER.replace(" current-menu-item page_item page-item-2578 current_page_item", "")
HEADER = HEADER.replace(' aria-current="page"', "")

# Add an Auto Rigger entry ahead of Rigger. It is the page search traffic lands
# on, so it needs a nav slot. Anchor on the Rigger link rather than on the li's
# id: the desktop and mobile menus use different ids for the same item.
AUTO_LI = ('<li class="menu-item menu-item-type-post_type menu-item-object-page menu-item-mt-auto">'
           '<a href="/maya-auto-rigger/" class="menu-link">Auto Rigger</a></li>\n')
RIGGER_LI = re.compile(r'<li\b[^>]*>(?=\s*<a href="/rigger/"[^>]*class="menu-link")')


def add_auto_rigger(header):
    """Insert the Auto Rigger nav item once per menu, if it is not already there."""
    if re.search(r'href="/maya-auto-rigger/"[^>]*class="menu-link"', header):
        return header
    return RIGGER_LI.sub(lambda mo: AUTO_LI + mo.group(0), header)


HEADER = add_auto_rigger(HEADER)


def _mark_current(header, href):
    """Re-apply Astra's current-page classes for one nav href."""
    if not href:
        return header
    pat = re.compile(r'(<li [^>]*class=")([^"]*)(")([^>]*>\s*<a href="%s")' % re.escape(href))
    header = pat.sub(lambda mo: mo.group(1) + mo.group(2) +
                     " current-menu-item current_page_item" + mo.group(3) +
                     mo.group(4) + ' aria-current="page"', header)
    return header

# Every generated page links the one shared stylesheet, assets/css/mt-ui.css.
# CSS is served with a one-year cache, so the URL carries a hash of the file:
# edit the CSS, rebuild, and the new hash is what reaches returning visitors.
UI_CSS_PATH = os.path.join(SITE, "assets", "css", "mt-ui.css")


def _ui_css_link():
    digest = hashlib.sha1(io.open(UI_CSS_PATH, "rb").read()).hexdigest()[:10]
    return '<link rel="stylesheet" id="mt-ui" href="/assets/css/mt-ui.css?v=%s">' % digest


DOC_CSS = _ui_css_link()


def page(title, description, canonical, body, extra_head="", nav_current="",
         og_image="/assets/img/santa_render.png"):
    """Assemble one page from the site shell plus `body`."""
    head = HEAD

    # swap <title>
    head = re.sub(r"<title>.*?</title>", lambda m: "<title>%s</title>" % _esc(title), head, count=1, flags=re.S)

    # swap description / canonical / og, which the static build injected right after <title>
    head = re.sub(r'<meta name="description" content="[^"]*">',
                  '<meta name="description" content="%s">' % _esc(description), head, count=1)
    head = re.sub(r'<link rel="canonical" href="[^"]*">',
                  '<link rel="canonical" href="%s">' % canonical, head, count=1)
    head = re.sub(r'<meta property="og:title" content="[^"]*">',
                  '<meta property="og:title" content="%s">' % _esc(title), head, count=1)
    head = re.sub(r'<meta property="og:description" content="[^"]*">',
                  '<meta property="og:description" content="%s">' % _esc(description), head, count=1)
    head = re.sub(r'<meta property="og:image" content="[^"]*">',
                  '<meta property="og:image" content="https://mutanttools.com%s">' % og_image, head, count=1)

    head = head.replace("</head>", DOC_CSS + extra_head + "\n</head>")

    return "".join([
        head, PRE, _mark_current(HEADER, nav_current), MID,
        '\n<div id="content" class="site-content"><div class="mt-doc">\n',
        body,
        '\n</div></div>\n',
        FOOTER, TAIL,
    ])


def _esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))


def write(rel_path, html):
    dest = os.path.join(SITE, *rel_path.split("/"))
    d = os.path.dirname(dest)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    io.open(dest, "w", encoding="utf-8", newline="\n").write(html)
    return dest, len(html)
