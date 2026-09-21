# -*- coding: utf-8 -*-
"""Read a Mutant_Tools checkout and write the two data files the docs build from.

    python extract_mt.py <path-to-Mutant_Tools-checkout>

Produces, next to this script:
    mt_api.json   every method on the mt inheritance chain: name, signature,
                  summary, line number, full docstring
    blocks.json   every block's launcher JSON, grouped by category

Both are read by build_mtdocs.py. Nothing here imports Maya, so it runs on a
plain Python 3 with no Autodesk anything installed - which is the whole reason
the docs are generated this way instead of with sphinx-autodoc.
"""
from __future__ import absolute_import
import ast, collections, io, json, os, re, sys, textwrap

HERE = os.path.dirname(os.path.abspath(__file__))

# The mt object is one instance whose methods come from four files.
API_FILES = ("tools.py", "kinematics.py", "modules.py", "main_mutant.py")


def extract_api(repo):
    base = os.path.join(repo, "Utils", "Rigging")
    out = {}
    for fname in API_FILES:
        path = os.path.join(base, fname)
        if not os.path.exists(path):
            print("  missing %s" % path)
            continue
        tree = ast.parse(io.open(path, encoding="utf-8", errors="replace").read())
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            methods = []
            for item in node.body:
                if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                methods.append(_method(item))
            out[node.name] = {
                "file": fname,
                "bases": [ast.unparse(b) for b in node.bases],
                "methods": methods,
            }
    return out


def _method(item):
    args = item.args
    names = [a.arg for a in args.args]
    defaults = [None] * (len(names) - len(args.defaults)) + \
               [ast.unparse(d) for d in args.defaults]

    sig = []
    for name, default in zip(names, defaults):
        if name == "self":
            continue
        sig.append(name if default is None else "%s=%s" % (name, default))
    if args.vararg:
        sig.append("*" + args.vararg.arg)
    for name, default in zip([a.arg for a in args.kwonlyargs],
                             [ast.unparse(d) if d else None for d in args.kw_defaults]):
        sig.append(name if default is None else "%s=%s" % (name, default))
    if args.kwarg:
        sig.append("**" + args.kwarg.arg)

    doc = textwrap.dedent(ast.get_docstring(item) or "").strip()
    doc = re.sub(r"\n{3,}", "\n\n", doc)
    summary = next((line.strip() for line in doc.split("\n") if line.strip()), "")
    return [item.name, ", ".join(sig), summary, item.lineno, doc]


def extract_blocks(repo):
    """One entry per block folder, keyed on the launcher JSON.

    The launcher is the JSON with no _vNNN suffix - it is the stable filename
    that points at whichever version is currently live.
    """
    root = os.path.join(repo, "Blocks")
    cats = collections.OrderedDict()
    for cat in sorted(os.listdir(root)):
        cat_dir = os.path.join(root, cat)
        if not os.path.isdir(cat_dir):
            continue
        items = []
        for block in sorted(os.listdir(cat_dir)):
            block_dir = os.path.join(cat_dir, block)
            if not os.path.isdir(block_dir):
                continue
            launchers = [f for f in os.listdir(block_dir)
                         if f.endswith(".json") and not re.search(r"_v\d+\.json$", f)]
            if not launchers:
                continue
            try:
                data = json.load(io.open(os.path.join(block_dir, launchers[0]), encoding="utf-8"))
            except ValueError as exc:
                print("  skipping %s/%s: %s" % (cat, block, exc))
                continue
            attrs = data.get("attrs", {})
            items.append({
                "folder": block,
                "name": data.get("Name", ""),
                "desc": data.get("Description", ""),
                "icon": data.get("Icon", ""),
                "enable": data.get("Enable", ""),
                "build": data.get("build_command", ""),
                "create": data.get("exec_command", ""),
                "pyfile": data.get("python_file", ""),
                "attrs": dict((k, v) for k, v in attrs.items() if k != "Help_string"),
                "help": attrs.get("Help_string", ""),
            })
        if items:
            cats[cat] = items
    return cats


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    repo = sys.argv[1]
    if not os.path.isdir(os.path.join(repo, "Blocks")):
        print("Not a Mutant_Tools checkout: %s" % repo)
        return 1

    api = extract_api(repo)
    blocks = extract_blocks(repo)

    io.open(os.path.join(HERE, "mt_api.json"), "w", encoding="utf-8").write(
        json.dumps(api, indent=1, ensure_ascii=False))
    io.open(os.path.join(HERE, "blocks.json"), "w", encoding="utf-8").write(
        json.dumps(blocks, indent=1, ensure_ascii=False))

    public = sum(len([m for m in c["methods"] if not m[0].startswith("_")])
                 for c in api.values())
    print("mt_api.json   %d classes, %d public methods" % (len(api), public))
    print("blocks.json   %d categories, %d blocks"
          % (len(blocks), sum(len(v) for v in blocks.values())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
