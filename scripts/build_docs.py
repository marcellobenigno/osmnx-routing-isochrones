"""
Builds the documentation site in docs/ (GitHub Pages): docs/<lang>/index.html for English,
Brazilian Portuguese and Spanish from one layout, plus docs/index.html (language picker).
docs/ is a worktree of the gh-pages branch: git worktree add docs gh-pages

    python scripts/build_docs.py

Texts live in scripts/docs_texts.py (same keys in every language). Figures are made by
scripts/build_docs_figures.py.
"""
import html
import os

from docs_texts import AUTHOR_LINKS, FIELDS, INSTALL_CODE, PYTHON_CODE, REPO, TEXTS, VERIFY_CODE

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
LANGS = (("en", "English", "EN"), ("pt-br", "Português", "PT"), ("es", "Español", "ES"))
PANEL_SHOTS = {"en": "en", "pt-br": "pt", "es": "es"}     # plugin UI language of the shots

SECTION_IDS = ["overview", "install", "quick-start", "map-tools", "algorithms",
               "how-it-works", "help", "author"]


def code(text):
    return f"<pre><code>{html.escape(text)}</code></pre>"


def workflow_svg(w):
    """Download -> GeoPackage -> inspect / route / isochrones."""
    def box(x, y, wd, title, sub, fill, stroke):
        return (f'<rect x="{x}" y="{y}" width="{wd}" height="64" rx="12" fill="{fill}" '
                f'stroke="{stroke}" stroke-width="2"/>'
                f'<text x="{x + wd / 2}" y="{y + 28}" text-anchor="middle" font-weight="700" '
                f'font-size="15">{html.escape(title)}</text>'
                f'<text x="{x + wd / 2}" y="{y + 48}" text-anchor="middle" font-size="12" '
                f'opacity=".75">{html.escape(sub)}</text>')

    def arrow(x1, y1, x2, y2, color):
        return (f'<path d="M{x1} {y1} C{(x1 + x2) / 2} {y1} {(x1 + x2) / 2} {y2} {x2} {y2}" '
                f'fill="none" stroke="{color}" stroke-width="3" marker-end="url(#ah)"/>')
    parts = ['<svg viewBox="0 0 980 250" role="img" aria-label="workflow">'
             '<defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" '
             'markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" fill="#888"/></marker>'
             '</defs>',
             box(10, 93, 150, w[0], "", "#fff7e6", "#f2b134"),
             arrow(160, 125, 200, 125, "#888"),
             box(200, 93, 150, w[1], "Nominatim + Overpass", "#e3f4e6", "#1a9641"),
             arrow(350, 125, 390, 125, "#888"),
             box(390, 93, 220, w[2], w[3], "#ffffff", "#5b636d")]
    for i, (y, title, sub, fill, stroke) in enumerate((
            (13, w[4], w[5], "#e4f0f8", "#2b83ba"),
            (93, w[6], w[7], "#fde8e8", "#d62728"),
            (173, w[8], w[9], "#fdf0e1", "#f28e2b"))):
        parts.append(arrow(610, 125, 680, y + 32, stroke))
        parts.append(box(680, y, 290, title, sub, fill, stroke))
    parts.append("</svg>")
    return "".join(parts)


def arcs_svg(a):
    """Two-way street = 2 arcs; one-way street = 1 arc."""
    def street(y, label, n, arcs):
        s = (f'<line x1="40" y1="{y}" x2="300" y2="{y}" stroke="#b9b4aa" stroke-width="16" '
             f'stroke-linecap="round"/>'
             f'<circle cx="40" cy="{y}" r="9" fill="#fff" stroke="#333" stroke-width="2"/>'
             f'<circle cx="300" cy="{y}" r="9" fill="#fff" stroke="#333" stroke-width="2"/>'
             f'<text x="170" y="{y - 30}" text-anchor="middle" font-weight="700" '
             f'font-size="15">{html.escape(label)}</text>')
        for dy, d, color in arcs:
            x1, x2 = (70, 270) if d > 0 else (270, 70)
            s += (f'<line x1="{x1}" y1="{y + dy}" x2="{x2}" y2="{y + dy}" stroke="{color}" '
                  f'stroke-width="4" marker-end="url(#a{color[1:]})"/>')
        s += (f'<text x="340" y="{y + 5}" font-size="15" font-weight="700" '
              f'fill="{arcs[0][2]}">{html.escape(n)}</text>')
        return s
    return ('<svg viewBox="0 0 440 230" role="img" aria-label="arcs">'
            '<defs>' + "".join(
                f'<marker id="a{c}" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" '
                f'markerHeight="5" orient="auto"><path d="M0 0L10 5L0 10z" fill="#{c}"/>'
                '</marker>' for c in ("1a9641", "d62728")) + '</defs>' +
            street(70, a[0], a[1], [(-20, 1, "#1a9641"), (20, -1, "#1a9641")]) +
            street(180, a[2], a[3], [(-20, 1, "#d62728")]) + "</svg>")


def table(cols, rows):
    head = "<tr>" + "".join(f"<th>{c}</th>" for c in cols) + "</tr>" if cols else ""
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="table"><table>{head}{body}</table></div>'


def blocks(items):
    return "".join(f"<h3>{h}</h3><p>{p}</p>" for h, p in items)


def page(lang):
    t = TEXTS[lang]
    shot = PANEL_SHOTS[lang]
    img = "../assets/img"
    nav = "".join(f'<a href="#{i}">{html.escape(n)}</a>' for i, n in zip(SECTION_IDS, t["nav"]))
    langs = "".join(
        f'<a href="../{code_}/" data-lang="{code_}" class="{"on" if code_ == lang else ""}" '
        f'hreflang="{code_}" title="{name}">{short}</a>' for code_, name, short in LANGS)
    alternates = "".join(f'<link rel="alternate" hreflang="{c}" href="../{c}/">'
                         for c, _, _ in LANGS)
    features = "".join(
        f'<div class="card"><div class="ico {tone}">{ico}</div><h4>{h}</h4><p>{p}</p></div>'
        for ico, tone, h, p in t["features"])
    notdo = "".join(f"<li>{x}</li>" for x in t["notdo"])
    req = "".join(f"<li>{x}</li>" for x in t["req"])

    def steps(items, extra=None):
        out = "".join(
            f"<li><h4>{h}</h4><p>{p}</p>{(extra or {}).get(i, '')}</li>"
            for i, (h, p) in enumerate(items))
        return f'<ol class="steps">{out}</ol>'

    def details(items):
        return "".join(f"<details><summary>{q}</summary><div>{a}</div></details>"
                       for q, a in items)

    algs = ""
    for name, alg_id, icon_name, color, use, params, outputs, read, limits in t["algs"]:
        rows = "".join(f"<tr><td><b>{p}</b></td><td>{d}</td></tr>" for p, d in params)
        algs += (f'<div class="alg" style="--c:{color}"><h3><img src="../assets/{icon_name}.svg" '
                 f'alt="">{html.escape(name)}</h3><p class="id"><code>{alg_id}</code></p>'
                 f'<p><b>{t["use_l"]}</b> {use}</p>'
                 f'<div class="table"><table><tr><th>{t["param"]}</th>'
                 f'<th>{t["desc"]}</th></tr>{rows}</table></div>'
                 f'<dl class="facts"><dt>{t["outputs"]}</dt><dd>{outputs}</dd>'
                 f'<dt>{t["read_l"]}</dt><dd>{read}</dd>'
                 f'<dt>{t["limits_l"]}</dt><dd>{limits}</dd></dl></div>')
    faq = "".join(
        f'<details><summary>{q}</summary><div><p><b>{t["cause_l"]}:</b> {cause}</p>'
        f'<p><b>{t["action_l"]}:</b> {action}</p></div></details>'
        for q, cause, action in t["faq"])
    iso_legend = (f'<span class="legend">{t["near"]} <span class="ramp iso"></span> '
                  f'{t["far"]}</span>')
    lg = t["legend"]
    legend = (f'<span class="legend"><span class="sw line" style="background:#d62728"></span>'
              f'{lg[0]}</span><span class="legend"><span class="sw dash"></span>{lg[1]}</span>'
              f'<span class="legend"><span class="sw dot" style="background:#1a9641"></span>'
              f'{lg[2]}</span><span class="legend"><span class="sw dot" '
              f'style="background:#d62728"></span>{lg[3]}</span>')
    roads_legend = (f'<span class="legend">{t["near"]} <span class="ramp roads"></span> '
                    f'{t["far"]}</span>')

    links = "".join(f'<a class="chip" href="{u}">{n}</a>' for n, u in AUTHOR_LINKS)

    def alt(key):
        return html.escape(t[key])

    return f"""<!doctype html>
<html lang="{lang}" data-copy="{t['copy']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(t['title'])}</title>
<meta name="description" content="{html.escape(t['description'])}">
<meta property="og:title" content="{html.escape(t['title'])}">
<meta property="og:description" content="{html.escape(t['description'])}">
<meta property="og:image" content="{img}/hero.png">
{alternates}
<link rel="icon" href="../assets/icon.svg">
<link rel="stylesheet" href="../assets/style.css">
<script src="https://cdn.tailwindcss.com/3.4.17"></script>
<script>tailwind.config = {{ corePlugins: {{ preflight: false }} }};  // keep style.css base styles</script>
</head>
<body>
<header class="topbar"><div class="wrap">
  <a class="brand min-w-0" href="#top"><img class="shrink-0" src="../assets/icon.svg" alt="">\
<span class="truncate">OSMnx Routing &amp; Isochrones</span></a>
  <nav class="topnav hidden xl:flex items-center gap-4 ml-auto">{nav}</nav>
  <div class="lang shrink-0 ml-auto xl:ml-0">{langs}</div>
  <button class="menu-btn xl:hidden shrink-0" type="button" aria-controls="mobile-nav"
    aria-expanded="false" aria-label="{t['menu']}">
    <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
      stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
  </button>
</div>
<nav id="mobile-nav" class="topnav mobile-nav hidden xl:hidden">
  <div class="wrap flex flex-col py-2">{nav}</div>
</nav></header>

<div class="hero" id="top"><div class="wrap">
  <div>
    <div class="badges">{"".join(f"<span>{b}</span>" for b in t["hero_badges"])}</div>
    <h1>{t['hero_h1']}</h1>
    <p class="lead">{t['hero_lead']}</p>
    <a class="btn primary" href="#install">⬇ {t['hero_install']}</a>
    <a class="btn ghost" href="{REPO}">★ {t['hero_github']}</a>
  </div>
  <figure><img src="{img}/hero.png" alt="{alt('hero_alt')}" width="1200" height="900"></figure>
</div></div>

<section id="overview"><div class="wrap">
  <p class="kicker k-green">{t['feat_k']}</p><h2>{t['feat_h']}</h2>
  <p class="intro">{t['feat_intro']}</p>
  <div class="note tip"><b>{t['before_h']}.</b> {t['before']}</div>
  <div class="grid c4">{features}</div>
  <h3>{t['notdo_h']}</h3>
  <ul class="plain">{notdo}</ul>
  <h3>{t['choose_h']}</h3>
  {table(t['choose_cols'], t['choose_rows'])}
  <p>{t['paths_note']}</p>
</div></section>

<section id="install"><div class="wrap">
  <p class="kicker k-orange">{t['inst_k']}</p><h2>{t['inst_h']}</h2>
  <p class="intro">{t['inst_intro']}</p>
  <h3>{t['req_h']}</h3>
  <ul class="plain">{req}</ul>
  {steps(t['inst_steps'], {0: code(INSTALL_CODE), 1: code(VERIFY_CODE)})}
  <div style="margin-top:18px">{details(t['inst_more'])}</div>
  <div class="note warn">{t['inst_note']}</div>
</div></section>

<section id="quick-start"><div class="wrap">
  <p class="kicker k-blue">{t['qs_k']}</p><h2>{t['qs_h']}</h2>
  <p class="intro">{t['qs_intro']}</p>
  <div class="diagram" style="margin-bottom:22px">{workflow_svg(t['wf'])}</div>
  {steps(t['qs_steps'])}
</div></section>

<section id="map-tools"><div class="wrap">
  <p class="kicker k-red">{t['tools_k']}</p><h2>{t['tools_h']}</h2>
  <p class="intro">{t['tools_intro']}</p>
  <h3><img class="inline-ico" src="../assets/route.svg" alt=""> {t['route_h']}</h3>
  <p>{t['route_p']}</p>
  <figure class="shot"><img src="{img}/panel_route_{shot}.png"
    alt="{alt('route_cap')}" loading="lazy">
    <figcaption>{t['route_cap']}</figcaption></figure>
  <h3><img class="inline-ico" src="../assets/isochrones.svg" alt=""> {t['iso_h']}</h3>
  <p>{t['iso_p']}</p>
  <figure class="shot"><img src="{img}/panel_isochrones_{shot}.png"
    alt="{alt('iso_cap')}" loading="lazy">
    <figcaption>{t['iso_cap']} {iso_legend}</figcaption></figure>
  <div class="note tip">💡 {t['tools_tip']}</div>
  <div class="note">{t['tools_stop']}</div>
  <p class="small">{t['shots_note']}</p>
</div></section>

<section id="algorithms"><div class="wrap">
  <p class="kicker k-blue">{t['alg_k']}</p><h2>{t['alg_h']}</h2>
  <p class="intro">{t['alg_intro']}</p>
  {algs}
  <h3>{t['fields_h']}</h3>
  {table(t['fields_cols'], zip(FIELDS, t['fields']))}
  <h3>{t['py_h']}</h3>
  <p>{t['py_intro']}</p>
  {code(PYTHON_CODE[lang])}
</div></section>

<section id="how-it-works"><div class="wrap">
  <p class="kicker k-orange">{t['how_k']}</p><h2>{t['how_h']}</h2>
  <p class="intro">{t['how_intro']}</p>
  {blocks(t['how'])}
  <div class="grid c2" style="align-items:center">
    <div class="diagram">{arcs_svg(t['arcs'])}</div>
    <div><p>{t['dir_side']}</p><p>{legend}</p></div>
  </div>
  <figure class="shot"><img src="{img}/oneway.png" alt="{alt('oneway_alt')}" loading="lazy">
    <div class="pair"><div>{t['oneway_left']}</div><div>{t['oneway_right']}</div></div></figure>
  {blocks(t['how2'])}
  <figure class="shot"><img src="{img}/coverage.png" alt="{alt('cov_alt')}" loading="lazy">
    <figcaption>{t['cov_cap']} {iso_legend}</figcaption></figure>
  {blocks(t['how3'])}
  <figure class="shot"><img src="{img}/methods.png" alt="{alt('meth_alt')}" loading="lazy">
    <div class="pair"><div>{t['meth_left']}</div><div>{t['meth_right']}</div></div></figure>
  <figure class="shot"><img src="{img}/reached_roads.png" alt="{alt('roads_alt')}"
    loading="lazy"><figcaption>{t['roads_cap']} {roads_legend}</figcaption></figure>
  {blocks([(t['cache_h'], t['cache'])])}
  <h3>{t['gloss_h']}</h3>
  {table(None, [(f"<b>{a}</b>", b) for a, b in t['gloss']])}
</div></section>

<section id="help"><div class="wrap">
  <p class="kicker k-red">{t['faq_k']}</p><h2>{t['faq_h']}</h2>
  <p class="intro">{t['faq_intro']}</p>
  {faq}
  <div class="note tip"><b>{t['report_h']}.</b> {t['report']}</div>
</div></section>

<section id="author"><div class="wrap">
  <p class="kicker k-green">{t['author_k']}</p>
  <div class="author">
    <img src="{img}/author.jpg" alt="{alt('author_photo')}" width="200" height="200"
      loading="lazy">
    <div>
      <h2>{t['author_h']}</h2>
      <p class="role">{t['author_role']}</p>
      {"".join(f"<p>{x}</p>" for x in t['author_bio'])}
      <p class="links">{links}</p>
    </div>
  </div>
</div></section>

<footer><div class="wrap">
  <span>{t['footer_data']}</span>
  <span>{t['footer_license']} · <a href="{REPO}">GitHub</a> · <a href="{REPO}/issues">Issues</a></span>
</div></footer>
<script src="../assets/site.js"></script>
</body>
</html>
"""


INDEX = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>OSMnx Routing &amp; Isochrones — QGIS plugin</title>
<link rel="icon" href="assets/icon.svg">
<link rel="stylesheet" href="assets/style.css">
<script>
(function () {
  var langs = ["en", "pt-br", "es"], pick = null;
  try { pick = localStorage.getItem("osmnx-doc-lang"); } catch (e) {}
  if (langs.indexOf(pick) < 0) {
    var nav = (navigator.languages || [navigator.language || "en"]).map(function (l) {
      return l.toLowerCase(); });
    pick = "en";
    for (var i = 0; i < nav.length; i++) {
      if (nav[i].indexOf("pt") === 0) { pick = "pt-br"; break; }
      if (nav[i].indexOf("es") === 0) { pick = "es"; break; }
      if (nav[i].indexOf("en") === 0) { pick = "en"; break; }
    }
  }
  location.replace(pick + "/");
})();
</script>
</head>
<body>
<div class="hero"><div class="wrap" style="grid-template-columns:1fr">
  <div><h1>OSMnx Routing &amp; Isochrones</h1>
  <p class="lead">Documentation · Documentação · Documentación</p>
  <a class="btn primary" href="en/">English</a>
  <a class="btn primary" href="pt-br/">Português</a>
  <a class="btn primary" href="es/">Español</a></div>
</div></div>
</body>
</html>
"""


def main():
    keys = set(TEXTS["en"])
    for lang, t in TEXTS.items():
        missing = keys ^ set(t)
        assert not missing, f"{lang}: keys differ {sorted(missing)}"
    import shutil
    icons = os.path.join(ROOT, "osmnx_routing_isochrones", "icons")
    for name in ("icon.svg", "route.svg", "isochrones.svg"):
        shutil.copy(os.path.join(icons, name), os.path.join(DOCS, "assets", name))
    for lang, _, _ in LANGS:
        os.makedirs(os.path.join(DOCS, lang), exist_ok=True)
        with open(os.path.join(DOCS, lang, "index.html"), "w", encoding="utf-8") as f:
            f.write(page(lang))
    with open(os.path.join(DOCS, "index.html"), "w", encoding="utf-8") as f:
        f.write(INDEX)
    open(os.path.join(DOCS, ".nojekyll"), "w").close()
    print("written docs/index.html and docs/{en,pt-br,es}/index.html")


if __name__ == "__main__":
    main()
