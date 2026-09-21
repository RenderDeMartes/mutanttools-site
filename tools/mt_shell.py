# -*- coding: utf-8 -*-
"""Page shell for the new mutanttools.com docs pages.

The Astra theme ships as ~95 KB of inline CSS inside every page's <head>. Rather
than reimplement the site's look, the shell is lifted verbatim from the existing
/developer/ page (header, footer, fonts, palette) and only the <title>, meta and
main content are swapped. That keeps every new page pixel-identical to the rest
of the site and means a theme change upstream still applies here.
"""
import io, os, re

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

DOC_CSS = """
<style id="mt-docs">
:root{
  --mt-ink:#140B06; --mt-panel:#1C0D0A; --mt-panel-2:#241310;
  --mt-line:#3A241C; --mt-text:#FEF1E4; --mt-dim:#B79E92;
  --mt-orange:#FF6210; --mt-orange-2:#F15808; --mt-code:#0E0805;
  --mt-green:#7CD992; --mt-blue:#79C0FF; --mt-pink:#FF9BD2; --mt-yellow:#FFD479;
}
/* The homepage carries its own inline CSS: a global `*{font-family:Inter}` that
   beats an inherited family, and something inside .entry-content that shrinks
   the base size to ~12px. Both are answered explicitly rather than inherited,
   so this block renders the same wherever it is dropped. */
.mt-doc{background:var(--mt-ink);color:var(--mt-text);line-height:1.7;
  font-size:15px;padding:0 0 6rem;overflow-x:clip}
.mt-doc *{box-sizing:border-box}
.mt-doc,.mt-doc p,.mt-doc li,.mt-doc a,.mt-doc span,.mt-doc div,.mt-doc td,.mt-doc th,
.mt-doc h1,.mt-doc h2,.mt-doc h3,.mt-doc h4,.mt-doc button,.mt-doc summary,.mt-doc input,
.mt-doc b,.mt-doc strong,.mt-doc i,.mt-doc nav,.mt-doc ol,.mt-doc ul
  {font-family:'Montserrat',system-ui,-apple-system,sans-serif}
.mt-doc code,.mt-doc pre,.mt-doc pre *,.mt-doc .mt-sig,.mt-doc .mt-sig *
  {font-family:ui-monospace,'SFMono-Regular',Menlo,Consolas,monospace}
.mt-body p,.mt-body li{font-size:1rem}
.mt-wrap{max-width:1180px;margin:0 auto;padding:0 20px}

/* ---- hero ---- */
.mt-hero{padding:5.5rem 0 3rem;border-bottom:1px solid var(--mt-line)}
.mt-kicker{font-size:.72rem;letter-spacing:.22em;text-transform:uppercase;
  color:var(--mt-orange);font-weight:700;margin:0 0 1.1rem}
.mt-hero h1{font-size:clamp(2.1rem,5.4vw,3.6rem);line-height:1.08;margin:0 0 1.2rem;
  letter-spacing:-.02em;color:#fff}
.mt-lede{font-size:clamp(1rem,2.1vw,1.2rem);color:var(--mt-dim);max-width:62ch;margin:0 0 2rem}
.mt-stats{display:flex;flex-wrap:wrap;gap:2.4rem;margin:2.4rem 0 0;padding:0;list-style:none}
.mt-stats b{display:block;font-size:1.9rem;color:var(--mt-orange);line-height:1}
.mt-stats span{font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;color:var(--mt-dim)}

/* ---- layout ---- */
.mt-layout{display:grid;grid-template-columns:240px minmax(0,1fr);gap:3.5rem;margin-top:3rem}
@media(max-width:940px){.mt-layout{grid-template-columns:1fr;gap:0}}
.mt-toc{position:sticky;top:90px;align-self:start;max-height:calc(100vh - 120px);
  overflow-y:auto;font-size:.86rem;padding-right:.5rem}
@media(max-width:940px){.mt-toc{position:static;max-height:none;margin-bottom:2.5rem;
  border-bottom:1px solid var(--mt-line);padding-bottom:1.5rem}}
.mt-toc h2{font-size:.7rem;letter-spacing:.2em;text-transform:uppercase;color:var(--mt-dim);
  margin:0 0 .9rem;font-weight:700}
.mt-toc ol{list-style:none;margin:0;padding:0;counter-reset:toc}
.mt-toc li{margin:0 0 .15rem}
.mt-toc a{display:block;padding:.34rem .6rem;color:var(--mt-dim);text-decoration:none;
  border-left:2px solid transparent;border-radius:0 4px 4px 0;transition:.15s}
.mt-toc a:hover{color:var(--mt-text);background:var(--mt-panel)}
.mt-toc a.is-on{color:var(--mt-orange);border-left-color:var(--mt-orange);background:var(--mt-panel)}

/* ---- prose ---- */
.mt-body h2{font-size:clamp(1.5rem,3.2vw,2.1rem);margin:3.6rem 0 1rem;color:#fff;
  letter-spacing:-.015em;scroll-margin-top:90px}
.mt-body h2:first-child{margin-top:0}
.mt-body h3{font-size:1.16rem;margin:2.4rem 0 .8rem;color:var(--mt-orange);scroll-margin-top:90px}
.mt-body h4{font-size:.98rem;margin:1.8rem 0 .6rem;color:var(--mt-text)}
.mt-body p{margin:0 0 1.1rem;color:#E8D9CF}
.mt-body ul,.mt-body ol{margin:0 0 1.2rem;padding-left:1.3rem;color:#E8D9CF}
.mt-body li{margin:.34rem 0}
.mt-body a{color:var(--mt-orange);text-decoration:none;border-bottom:1px solid rgba(255,98,16,.35)}
.mt-body a:hover{color:var(--mt-orange-2);border-bottom-color:var(--mt-orange-2)}
.mt-body strong{color:#fff}
.mt-body hr{border:0;border-top:1px solid var(--mt-line);margin:3rem 0}

/* ---- code ---- */
.mt-body code{font-family:ui-monospace,'SFMono-Regular',Menlo,Consolas,monospace;
  font-size:.86em;background:var(--mt-panel-2);color:var(--mt-yellow);
  padding:.14em .42em;border-radius:4px;border:1px solid var(--mt-line)}
.mt-body pre{background:var(--mt-code);border:1px solid var(--mt-line);border-radius:10px;
  padding:1.15rem 1.25rem;overflow-x:auto;margin:0 0 1.4rem;font-size:.845rem;line-height:1.65}
.mt-body pre code{background:none;border:0;padding:0;color:#E6DCD4;font-size:inherit}
.mt-code-head{display:flex;align-items:center;gap:.6rem;background:var(--mt-panel-2);
  border:1px solid var(--mt-line);border-bottom:0;border-radius:10px 10px 0 0;
  padding:.5rem 1rem;font-size:.72rem;letter-spacing:.12em;text-transform:uppercase;
  color:var(--mt-dim);font-weight:700}
.mt-code-head+pre{border-radius:0 0 10px 10px;margin-top:0}
.mt-code-head .mt-dot{width:8px;height:8px;border-radius:50%;background:var(--mt-orange)}
.tok-k{color:var(--mt-pink)}.tok-s{color:var(--mt-green)}.tok-c{color:#8A7568;font-style:italic}
.tok-n{color:var(--mt-blue)}.tok-f{color:var(--mt-yellow)}

/* ---- callouts ---- */
.mt-note{border-left:3px solid var(--mt-orange);background:var(--mt-panel);
  padding:1rem 1.2rem;border-radius:0 8px 8px 0;margin:0 0 1.4rem}
.mt-note p:last-child{margin-bottom:0}
.mt-note b.mt-tag{display:block;font-size:.7rem;letter-spacing:.16em;text-transform:uppercase;
  color:var(--mt-orange);margin-bottom:.4rem}
.mt-warn{border-left-color:#FF4D4D}
.mt-warn b.mt-tag{color:#FF7A7A}
.mt-ok{border-left-color:var(--mt-green)}
.mt-ok b.mt-tag{color:var(--mt-green)}

/* ---- tables ---- */
.mt-table-wrap{overflow-x:auto;margin:0 0 1.5rem;border:1px solid var(--mt-line);border-radius:10px}
.mt-body table{width:100%;border-collapse:collapse;font-size:.855rem;margin:0}
.mt-body th{text-align:left;background:var(--mt-panel-2);color:var(--mt-dim);
  font-size:.7rem;letter-spacing:.13em;text-transform:uppercase;padding:.7rem .9rem;
  border-bottom:1px solid var(--mt-line);white-space:nowrap}
.mt-body td{padding:.65rem .9rem;border-bottom:1px solid rgba(58,36,28,.6);
  vertical-align:top;color:#E8D9CF}
.mt-body tr:last-child td{border-bottom:0}
.mt-body td code{white-space:nowrap}

/* ---- cards ---- */
.mt-grid{display:grid;gap:1rem;margin:0 0 1.6rem}
.mt-grid--2{grid-template-columns:repeat(auto-fit,minmax(255px,1fr))}
.mt-grid--3{grid-template-columns:repeat(auto-fit,minmax(215px,1fr))}
.mt-card{background:var(--mt-panel);border:1px solid var(--mt-line);border-radius:10px;padding:1.15rem 1.25rem}
.mt-card h4{margin:0 0 .45rem;color:var(--mt-orange);font-size:.95rem}
.mt-card p{margin:0;font-size:.875rem;color:var(--mt-dim)}
.mt-card code{font-size:.8rem}

/* ---- api entries ---- */
.mt-api{border:1px solid var(--mt-line);border-radius:10px;margin:0 0 .75rem;background:var(--mt-panel);overflow:hidden}
.mt-api>summary{cursor:pointer;padding:.8rem 1.1rem;list-style:none;display:flex;
  gap:.7rem;align-items:baseline;flex-wrap:wrap}
.mt-api>summary::-webkit-details-marker{display:none}
.mt-api>summary:hover{background:var(--mt-panel-2)}
.mt-api .mt-sig{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.88rem;color:var(--mt-yellow)}
.mt-api .mt-sig b{color:#fff;font-weight:700}
.mt-api .mt-from{font-size:.68rem;letter-spacing:.1em;text-transform:uppercase;
  color:var(--mt-dim);margin-left:auto;white-space:nowrap}
.mt-api-body{padding:0 1.1rem 1.1rem;border-top:1px solid var(--mt-line)}
.mt-api-body p{margin:.9rem 0 .6rem;font-size:.9rem}
.mt-api-body table{font-size:.82rem}
/* The raw docstring under an expanded command. NOT .mt-doc - that is the page
   container, and reusing the name leaked pre-wrap and a .79rem font onto every
   paragraph on the site. */
.mt-docstring{background:transparent!important;border:0!important;
  border-left:2px solid var(--mt-line)!important;
  border-radius:0!important;padding:.2rem 0 .2rem 1rem!important;margin:1rem 0 0!important;
  font-size:.79rem!important;color:#B79E92!important;white-space:pre-wrap;line-height:1.55}
.mt-docstring code{color:inherit!important}

/* ---- search ---- */
.mt-search{position:relative;margin:0 0 1.6rem}
.mt-search input{width:100%;background:var(--mt-panel);border:1px solid var(--mt-line);
  border-radius:9px;padding:.85rem 1rem .85rem 2.6rem;color:var(--mt-text);
  font-family:inherit;font-size:.95rem}
.mt-search input:focus{outline:2px solid var(--mt-orange);outline-offset:1px;border-color:transparent}
.mt-search input::placeholder{color:#8A7568}
.mt-search svg{position:absolute;left:.95rem;top:50%;transform:translateY(-50%);
  width:16px;height:16px;fill:none;stroke:#8A7568;stroke-width:2}
.mt-count{font-size:.78rem;color:var(--mt-dim);margin:0 0 1rem}
.mt-hide{display:none!important}

/* ---- pills ---- */
.mt-pills{display:flex;flex-wrap:wrap;gap:.45rem;margin:0 0 1.6rem;padding:0;list-style:none}
.mt-pill{background:var(--mt-panel);border:1px solid var(--mt-line);color:var(--mt-dim);
  border-radius:999px;padding:.34rem .85rem;font-size:.76rem;cursor:pointer;
  font-family:inherit;letter-spacing:.04em}
.mt-pill:hover{color:var(--mt-text);border-color:var(--mt-orange)}
.mt-pill[aria-pressed="true"]{background:var(--mt-orange);color:#180C07;border-color:var(--mt-orange);font-weight:700}

/* ---- cta ---- */
.mt-cta{background:linear-gradient(135deg,var(--mt-panel),var(--mt-panel-2));
  border:1px solid var(--mt-line);border-radius:14px;padding:2.4rem;margin:3.5rem 0 0;text-align:center}
.mt-cta h2{margin:0 0 .8rem!important;font-size:1.7rem}
.mt-cta p{color:var(--mt-dim);max-width:52ch;margin:0 auto 1.6rem}
.mt-btn{display:inline-block;background:var(--mt-orange);color:#180C07!important;
  border:0;border-bottom:0!important;border-radius:999px;padding:.85rem 1.9rem;
  font-weight:700;font-size:.85rem;letter-spacing:.07em;text-transform:uppercase;
  text-decoration:none;margin:.3rem}
.mt-btn:hover{background:var(--mt-orange-2);color:#180C07!important}
.mt-btn--ghost{background:transparent;color:var(--mt-orange)!important;
  box-shadow:inset 0 0 0 1px var(--mt-orange)}
.mt-btn--ghost:hover{background:rgba(255,98,16,.12);color:var(--mt-orange)!important}

/* ---- misc ---- */
.mt-anchor{color:var(--mt-line);text-decoration:none!important;border:0!important;
  margin-left:.4rem;font-weight:400;opacity:0}
h2:hover .mt-anchor,h3:hover .mt-anchor{opacity:1}
.mt-anchor:hover{color:var(--mt-orange)}
.mt-updated{font-size:.75rem;color:#8A7568;margin-top:3rem;padding-top:1.4rem;
  border-top:1px solid var(--mt-line)}
</style>
"""


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
