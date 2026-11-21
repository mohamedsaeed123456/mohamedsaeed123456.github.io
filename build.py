#!/usr/bin/env python3
"""Static site builder for the portfolio.

Reads templates from src/, content from src/i18n/<lang>.json and shared data
from src/data/site.json, then writes:

    index.html          English page (site root)
    ar/index.html       Arabic page (right-to-left)
    assets/site.css     bundled stylesheet (from src/styles/)
    assets/site.js      bundled script (from src/scripts/)

Uses only the Python standard library. Run:  python3 build.py
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
LOCALES = ("en", "ar")  # first one is served at the site root

# Bundle order matters: tokens first, then base, components, sections, overrides.
STYLE_FILES = [
    "tokens.css", "base.css",
    "components/button.css", "components/chip.css", "components/theme-toggle.css",
    "components/tags.css", "components/header.css",
    "sections/hero.css", "sections/numbers.css", "sections/markly.css",
    "sections/roles.css", "sections/projects.css", "sections/skills.css",
    "sections/experience.css", "sections/contact.css", "sections/footer.css",
    "rtl.css", "motion.css", "responsive.css",
]
SCRIPT_FILES = [
    "modules/theme.js", "modules/reveal.js", "modules/roles.js",
    "modules/filter.js", "modules/analytics.js", "main.js",
]


class BuildError(RuntimeError):
    pass


# --------------------------------------------------------------------------
# Minimal template engine
#   {{ a.b }}        escaped value          {{ a.b|safe }}   raw value
#   {% for x in a.b %}...{% endfor %}       {% if a.b %}...{% endif %}
#   {% include name %}  inlines src/sections/<name>.html
# --------------------------------------------------------------------------
_TOKEN = re.compile(r"(\{%.*?%\}|\{\{.*?\}\})", re.S)
_INCLUDE = re.compile(r"\{%\s*include\s+([\w-]+)\s*%\}")


def expand_includes(text: str, depth: int = 0) -> str:
    if depth > 5:
        raise BuildError("include nesting too deep")

    def load(match: re.Match) -> str:
        path = SRC / "sections" / f"{match.group(1)}.html"
        if not path.is_file():
            raise BuildError(f"missing include: {path.relative_to(ROOT)}")
        return expand_includes(path.read_text(encoding="utf-8").rstrip("\n"), depth + 1)

    return _INCLUDE.sub(load, text)


def parse(text: str) -> list:
    root: list = []
    stack = [root]
    open_tags: list[tuple] = []
    for chunk in _TOKEN.split(text):
        if not chunk:
            continue
        if chunk.startswith("{{"):
            expr = chunk[2:-2].strip()
            path, _, flt = expr.partition("|")
            stack[-1].append(("var", path.strip(), flt.strip() == "safe"))
        elif chunk.startswith("{%"):
            words = chunk[2:-2].split()
            if words[0] == "for" and len(words) == 4 and words[2] == "in":
                node = ("for", words[1], words[3], [])
                stack[-1].append(node)
                stack.append(node[3])
                open_tags.append(node)
            elif words[0] == "if" and len(words) == 2:
                node = ("if", words[1], [])
                stack[-1].append(node)
                stack.append(node[2])
                open_tags.append(node)
            elif words[0] in ("endfor", "endif"):
                if not open_tags or open_tags[-1][0] != words[0][3:]:
                    raise BuildError(f"unbalanced {chunk}")
                open_tags.pop()
                stack.pop()
            else:
                raise BuildError(f"unknown tag {chunk}")
        else:
            stack[-1].append(("text", chunk))
    if open_tags:
        raise BuildError(f"unclosed {open_tags[-1][0]} block")
    return root


def lookup(path: str, scopes: list[dict], strict: bool = True):
    head, *rest = path.split(".")
    for scope in reversed(scopes):
        if head in scope:
            value = scope[head]
            break
    else:
        if strict:
            raise BuildError(f"undefined variable: {path}")
        return None
    for key in rest:
        if isinstance(value, dict) and key in value:
            value = value[key]
        elif strict:
            raise BuildError(f"undefined variable: {path}")
        else:
            return None
    return value


def render(nodes: list, scopes: list[dict]) -> str:
    out: list[str] = []
    for node in nodes:
        kind = node[0]
        if kind == "text":
            out.append(node[1])
        elif kind == "var":
            value = lookup(node[1], scopes)
            text = "" if value is None else str(value)
            out.append(text if node[2] else html.escape(text, quote=True))
        elif kind == "if":
            if lookup(node[1], scopes, strict=False):
                out.append(render(node[2], scopes))
        elif kind == "for":
            items = lookup(node[2], scopes)
            if not isinstance(items, list):
                raise BuildError(f"{node[2]} is not a list")
            for item in items:
                out.append(render(node[3], scopes + [{node[1]: item}]))
    return "".join(out)


# --------------------------------------------------------------------------
# Content assembly
# --------------------------------------------------------------------------
def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BuildError(f"{path.relative_to(ROOT)}: {exc}") from exc


def shape(value):
    """Structure of a JSON value without its text, used to compare languages."""
    if isinstance(value, dict):
        return {k: shape(v) for k, v in sorted(value.items())}
    if isinstance(value, list):
        return [shape(v) for v in value]
    return type(value).__name__


def interpolate(value, tokens: dict[str, str]):
    """Replace {khamsat}-style tokens in every string with values from site.json."""
    if isinstance(value, str):
        for key, replacement in tokens.items():
            value = value.replace("{" + key + "}", replacement)
        return value
    if isinstance(value, list):
        return [interpolate(v, tokens) for v in value]
    if isinstance(value, dict):
        return {k: interpolate(v, tokens) for k, v in value.items()}
    return value


def merge_by_id(shared: list[dict], translated: list[dict], name: str) -> list[dict]:
    by_id = {item["id"]: item for item in translated}
    if [i["id"] for i in shared] != [i["id"] for i in translated] and shared:
        raise BuildError(f"list '{name}': ids differ between site.json and translations")
    if not shared:
        return [dict(item) for item in translated]
    return [{**s, **by_id[s["id"]]} for s in shared]


def load_icons() -> dict[str, str]:
    return {p.stem: p.read_text(encoding="utf-8").strip() for p in (SRC / "icons").glob("*.svg")}


def build_context(lang: str, site: dict, t: dict, icons: dict[str, str]) -> dict:
    t = interpolate(t, {k: v for k, v in site.items() if isinstance(v, str)})
    locale = t["locale"]
    base = "" if lang == LOCALES[0] else "../"
    ctx: dict = {k: v for k, v in t.items() if k != "lists"}
    ctx.update(site=site, icons=icons, base=base)

    page_path = "" if lang == LOCALES[0] else f"{lang}/"
    ctx.update(
        page_url=f"{site['url']}/{page_path}",
        url_en=f"{site['url']}/",
        url_ar=f"{site['url']}/ar/",
    )

    lists = {name: merge_by_id(site.get(name, []), items, name) for name, items in t["lists"].items()}
    for name, items in lists.items():
        if name in ctx:  # a section dict shares the name, keep both
            ctx[f"{name}_ui"] = ctx[name]
        ctx[name] = items

    for i, item in enumerate(lists["filters"]):
        item.update(first=(i == 0), pressed=str(i == 0).lower())
    for i, item in enumerate(lists["roles"]):
        item.update(selected=str(i == 0).lower(), href=f"{base}cv/Mohamed_Saeed_{item['cv']}.pdf")
    for item in lists["langs"]:
        item["bars"] = "<i></i>" * item["filled"] + '<i class="off"></i>' * (5 - item["filled"])
    for item in lists["links"]:
        item["svg"] = icons[item["icon"]]
        if item.get("local"):
            item["href"] = base + item["href"]

    roles_payload = {
        "labels": {k: ctx["roles_ui"][k] for k in ("tools", "proof_title", "download")},
        "roles": {r["id"]: {k: r[k] for k in ("title", "sum", "tags", "proof", "note", "href") if k in r}
                  for r in lists["roles"]},
    }
    ctx["roles_json"] = json.dumps(roles_payload, ensure_ascii=False).replace("</", "<\\/")
    ctx["locale"] = locale
    return ctx


def build_page(lang: str, layout: list, site: dict, icons: dict[str, str]) -> Path:
    t = read_json(SRC / "i18n" / f"{lang}.json")
    ctx = build_context(lang, site, t, icons)
    page = render(layout, [ctx])
    leftover = re.search(r"\{\{|\{%|\{khamsat\}", page)
    if leftover:
        line = page[: leftover.start()].count("\n") + 1
        raise BuildError(f"{lang}: unresolved placeholder near line {line}")
    target = ROOT / ("index.html" if lang == LOCALES[0] else f"{lang}/index.html")
    target.parent.mkdir(exist_ok=True)
    target.write_text(page, encoding="utf-8")
    return target


def bundle(kind: str, folder: str, files: list[str], header: str) -> Path:
    parts = [header]
    for name in files:
        path = SRC / folder / name
        if not path.is_file():
            raise BuildError(f"missing {path.relative_to(ROOT)}")
        parts.append(f"\n/* ---- {name} ---- */\n" + path.read_text(encoding="utf-8").strip() + "\n")
    declared = {p.relative_to(SRC / folder).as_posix() for p in (SRC / folder).rglob(f"*.{kind}")}
    extra = declared - set(files)
    if extra:
        raise BuildError(f"{folder}/ files not in the bundle list: {', '.join(sorted(extra))}")
    target = ROOT / "assets" / f"site.{kind}"
    target.parent.mkdir(exist_ok=True)
    target.write_text("".join(parts), encoding="utf-8")
    return target


def main() -> int:
    try:
        site = read_json(SRC / "data" / "site.json")
        translations = {lang: read_json(SRC / "i18n" / f"{lang}.json") for lang in LOCALES}
        reference = shape(translations[LOCALES[0]])
        for lang in LOCALES[1:]:
            if shape(translations[lang]) != reference:
                raise BuildError(f"{lang}.json has a different structure from {LOCALES[0]}.json")

        layout = parse(expand_includes((SRC / "layout.html").read_text(encoding="utf-8")))
        icons = load_icons()
        outputs = [build_page(lang, layout, site, icons) for lang in LOCALES]
        outputs.append(bundle("css", "styles", STYLE_FILES, "/* Generated by build.py from src/styles. Do not edit. */\n"))
        outputs.append(bundle("js", "scripts", SCRIPT_FILES, "/* Generated by build.py from src/scripts. Do not edit. */\n"))
    except BuildError as exc:
        print(f"build failed: {exc}", file=sys.stderr)
        return 1
    for path in outputs:
        print(f"wrote {path.relative_to(ROOT)}  ({path.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
