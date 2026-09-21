# -*- coding: utf-8 -*-
"""Small markup helpers: a Python highlighter and the block builders the
generators use. No runtime JS highlighting - everything is coloured at build
time so the pages stay fast and work with scripting off.
"""
import re, textwrap

KEYWORDS = set("""and as assert break class continue def del elif else except finally for from
global if import in is lambda nonlocal not or pass raise return try while with yield True False
None self print""".split())


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


_TOKEN = re.compile(r"""
    (?P<comment>\#[^\n]*)
  | (?P<string>'''(?:.|\n)*?'''|\"\"\"(?:.|\n)*?\"\"\"|'(?:\\.|[^'\\\n])*'|\"(?:\\.|[^\"\\\n])*\")
  | (?P<call>\b[A-Za-z_][A-Za-z0-9_]*(?=\s*\())
  | (?P<word>\b[A-Za-z_][A-Za-z0-9_]*\b)
""", re.X)


def py(code):
    """Colour Python source. Escapes first, then wraps tokens in spans."""
    code = textwrap.dedent(code).strip("\n")

    def sub(m):
        raw = m.group(0)
        if m.lastgroup == "comment":
            return '<span class="tok-c">%s</span>' % esc(raw)
        if m.lastgroup == "string":
            return '<span class="tok-s">%s</span>' % esc(raw)
        if m.lastgroup == "call":
            if raw in KEYWORDS:
                return '<span class="tok-k">%s</span>' % esc(raw)
            return '<span class="tok-f">%s</span>' % esc(raw)
        if raw in KEYWORDS:
            return '<span class="tok-k">%s</span>' % esc(raw)
        if raw in ("mt", "cmds", "nc", "setup", "curve_data", "config", "block"):
            return '<span class="tok-n">%s</span>' % esc(raw)
        return esc(raw)

    return _TOKEN.sub(sub, code)


def code(source, label="python"):
    return ('<div class="mt-code-head"><span class="mt-dot"></span>%s</div>\n<pre><code>%s</code></pre>\n'
            % (esc(label), py(source)))


def plain(source, label="text"):
    return ('<div class="mt-code-head"><span class="mt-dot"></span>%s</div>\n<pre><code>%s</code></pre>\n'
            % (esc(label), esc(textwrap.dedent(source).strip("\n"))))


def note(body, tag="Note", kind=""):
    cls = "mt-note" + (" " + kind if kind else "")
    return '<div class="%s"><b class="mt-tag">%s</b>%s</div>\n' % (cls, esc(tag), body)


def warn(body, tag="Trap"):
    return note(body, tag, "mt-warn")


def ok(body, tag="Do this"):
    return note(body, tag, "mt-ok")


def table(headers, rows):
    th = "".join("<th>%s</th>" % h for h in headers)
    trs = []
    for r in rows:
        trs.append("<tr>%s</tr>" % "".join("<td>%s</td>" % c for c in r))
    return ('<div class="mt-table-wrap"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>\n'
            % (th, "".join(trs)))


def cards(items, cols=2):
    out = ['<div class="mt-grid mt-grid--%d">' % cols]
    for title, body in items:
        out.append('<div class="mt-card"><h4>%s</h4><p>%s</p></div>' % (title, body))
    out.append("</div>\n")
    return "".join(out)


def slug(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s


def h2(text, anchor=None):
    a = anchor or slug(text)
    return '<h2 id="%s">%s<a class="mt-anchor" href="#%s" aria-label="Link to this section">#</a></h2>\n' % (a, text, a)


def h3(text, anchor=None):
    a = anchor or slug(text)
    return '<h3 id="%s">%s<a class="mt-anchor" href="#%s" aria-label="Link to this section">#</a></h3>\n' % (a, text, a)


def toc(entries):
    """entries: list of (anchor, label)."""
    lis = "".join('<li><a href="#%s">%s</a></li>' % (a, l) for a, l in entries)
    return ('<nav class="mt-toc" aria-label="On this page"><h2>On this page</h2><ol>%s</ol></nav>\n' % lis)


TOC_JS = """
<script>
(function(){
  var links = [].slice.call(document.querySelectorAll('.mt-toc a[href^="#"]'));
  if(!links.length || !('IntersectionObserver' in window)) return;
  var map = {};
  links.forEach(function(a){
    var el = document.getElementById(a.getAttribute('href').slice(1));
    if(el) map[el.id] = a;
  });
  var seen = {};
  var io = new IntersectionObserver(function(entries){
    entries.forEach(function(e){ seen[e.target.id] = e.isIntersecting; });
    var current = null;
    Object.keys(map).forEach(function(id){ if(seen[id] && !current) current = id; });
    links.forEach(function(a){ a.classList.remove('is-on'); });
    if(current && map[current]) map[current].classList.add('is-on');
  }, {rootMargin: '-80px 0px -70% 0px'});
  Object.keys(map).forEach(function(id){ io.observe(document.getElementById(id)); });
})();
</script>
"""
