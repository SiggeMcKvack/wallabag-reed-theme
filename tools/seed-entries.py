#!/usr/bin/env python3
"""Print Wallabag v2 import JSON with entries that exercise the theme.

    tools/seed-entries.py > /tmp/seed.json
    docker cp /tmp/seed.json Wallabag:/tmp/seed.json
    docker exec Wallabag php bin/console -e prod wallabag:import \
        --importer=v2 --disableContentUpdate wallabag /tmp/seed.json

Entries are keyed by URL, so re-importing skips ones that already exist.
"""

import json

BASE = "https://reed-theme.test/"
LOREM = (
    "The river ran slow and brown past the mill, carrying leaves from upstream "
    "orchards. Nobody in the village could remember when the wheel last turned, "
    "but everyone agreed it had been a better sound than the silence that "
    "replaced it. In the evenings, the miller's daughter would sit on the "
    "sluice gate and read aloud to no one in particular."
)


def img(seed, w=1200, h=800):
    return f"https://picsum.photos/seed/{seed}/{w}/{h}"


def entry(slug, title, content, *, tags=(), starred=False, archived=False,
          language="en", picture=None, created="2026-10-01T09:00:00+00:00"):
    return {
        "url": BASE + slug,
        "title": title,
        "content": content,
        "mimetype": "text/html",
        "language": language,
        "tags": list(tags),
        "is_starred": int(starred),
        "is_archived": int(archived),
        "preview_picture": picture,
        "created_at": created,
    }


KITCHEN_SINK = f"""
<p>{LOREM} With <a href="https://example.com">a link</a>, <strong>bold</strong>,
<em>italic</em>, <code>inline code</code>, <kbd>Ctrl</kbd>+<kbd>C</kbd>,
<abbr title="HyperText Markup Language">HTML</abbr>, H<sub>2</sub>O and E=mc<sup>2</sup>,
<mark>highlighted text</mark>, <s>struck</s> and <small>small print</small>.</p>
<h2>Second-level heading</h2>
<p>{LOREM}</p>
<h3>Third-level heading</h3>
<ul><li>Unordered item</li><li>Item with a nested list
  <ul><li>Nested one</li><li>Nested two
    <ol><li>Deep ordered</li><li>Deep ordered</li></ol></li></ul></li>
<li>Last item</li></ul>
<ol><li>First</li><li>Second</li><li>Third</li></ol>
<blockquote><p>A blockquote that runs long enough to wrap across a few lines, so
the left rule and the italic or serif treatment can be checked at length.</p>
<p>— Someone quotable</p></blockquote>
<h4>Fourth-level heading</h4>
<pre><code>def mill(wheel):
    # a line long enough to force horizontal scrolling inside the pre block, which should not widen the page
    return [spoke for spoke in wheel if spoke.turns]</code></pre>
<figure><img src="{img('sink')}" alt="Random landscape"><figcaption>A figure with a
caption underneath it.</figcaption></figure>
<table><caption>Table caption</caption>
<thead><tr><th>Name</th><th>Role</th><th style="text-align:right">Count</th></tr></thead>
<tbody><tr><td>Ada</td><td>Engineer</td><td style="text-align:right">12</td></tr>
<tr><td>Grace</td><td>Admiral</td><td style="text-align:right">7</td></tr>
<tr><td>Linus</td><td>Maintainer</td><td style="text-align:right">1,024</td></tr></tbody></table>
<h5>Fifth-level heading</h5>
<dl><dt>Term</dt><dd>Definition of the term.</dd><dt>Another</dt><dd>Another definition.</dd></dl>
<hr>
<h6>Sixth-level heading</h6>
<details><summary>Expandable details</summary><p>Hidden content.</p></details>
<p>{LOREM}</p>
"""

CODE = f"""
<p>A technical post mixing prose with code.</p>
<pre><code class="language-js">const entries = await fetch('/api/entries.json?perPage=30')
  .then((r) => r.json())
  .then(({{ _embedded }}) => _embedded.items.filter((e) => !e.is_archived));</code></pre>
<p>Shell, with a very long unbroken token:</p>
<pre>docker exec Wallabag php bin/console -e prod wallabag:import --importer=v2 --disableContentUpdate wallabag /tmp/seed.json</pre>
<p>A long inline token: <code>SYMFONY__ENV__TWOFACTOR_SENDER_AND_SOME_MORE_VERY_LONG_IDENTIFIER_WITHOUT_BREAKS</code>.</p>
<pre><code class="language-css">:root {{
  --accent: oklch(0.72 0.14 65);
}}</code></pre>
<p>{LOREM}</p>
"""

GREEK = """
<p>Το ποτάμι κυλούσε αργά και καφετί δίπλα στον μύλο, κουβαλώντας φύλλα από
τους οπωρώνες. Κανείς στο χωριό δεν θυμόταν πότε γύρισε τελευταία φορά ο
τροχός.</p>
<h2>Δεύτερη ενότητα</h2>
<p><em>Πλάγια γράμματα</em> και <strong>έντονα</strong>. Άλφα, Βήτα, Γάμμα, Δέλτα,
Ωμέγα — ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ αβγδεζηθικλμνξοπρστυφχψω.</p>
"""

CYRILLIC = """
<p>Река медленно текла мимо мельницы, унося листья из садов выше по течению.
Никто в деревне не помнил, когда колесо в последний раз поворачивалось.</p>
<h2>Второй раздел</h2>
<p><em>Курсив</em> и <strong>полужирный</strong>. Съешь же ещё этих мягких
французских булок, да выпей чаю. АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ.</p>
"""

ARABIC = """
<p dir="rtl">كان النهر يجري ببطء بجانب الطاحونة، حاملاً أوراق الشجر من البساتين.
لم يتذكر أحد في القرية متى دارت العجلة آخر مرة.</p>
<blockquote dir="rtl"><p>اقتباس طويل بما يكفي ليلتف على عدة أسطر في وضع القراءة.</p></blockquote>
"""

JAPANESE = """
<p>川は水車小屋のそばをゆっくりと流れ、上流の果樹園から葉を運んでいた。村の誰も、
水車が最後に回ったのがいつだったか覚えていなかった。</p>
<h2>第二節</h2>
<p>漢字、ひらがな、カタカナが混在する段落。句読点の扱いと行間を確認する。</p>
"""

IMAGES = "".join(
    f'<p>{LOREM}</p><img src="{img(f"gallery{i}", w, h)}" alt="Image {i}">'
    for i, (w, h) in enumerate([(1600, 900), (600, 1200), (300, 200), (2400, 600)])
)

LONG = "".join(
    f"<h2>Chapter {n}</h2>" + f"<p>{LOREM}</p>" * 12 for n in range(1, 16)
)

ENTRIES = [
    entry("kitchen-sink", "Kitchen sink: every element the reader can hit",
          KITCHEN_SINK, tags=["typography", "reference"], starred=True,
          picture=img("sink"), created="2026-10-29T08:00:00+00:00"),
    entry("code", "Shipping a Wallabag import pipeline in an afternoon",
          CODE, tags=["dev"], picture=img("code"),
          created="2026-10-28T08:00:00+00:00"),
    entry("long-title",
          "An extraordinarily long headline that keeps going well past the point "
          "where any reasonable editor would have cut it, just to see how cards, "
          "the reading view and the page title cope with wrapping",
          f"<p>{LOREM}</p>", tags=["edge-case"], created="2026-10-27T08:00:00+00:00"),
    entry("unbreakable", "Supercalifragilisticexpialidocious_and_then_some_more_unbreakable_title_text",
          '<p>A URL with no break points: <a href="https://example.com/'
          + "a" * 160 + '">https://example.com/' + "a" * 160 + "</a></p>",
          tags=["edge-case"], created="2026-10-26T08:00:00+00:00"),
    entry("many-tags", "An article with far too many tags", f"<p>{LOREM}</p>",
          tags=["design", "typography", "colour", "reading", "longform",
                "wallabag", "self-hosted", "rss", "fonts", "accessibility",
                "dark-mode", "a-rather-long-tag-name-for-testing"],
          picture=img("tags"), created="2026-10-25T08:00:00+00:00"),
    entry("greek", "Ο μύλος στο ποτάμι", GREEK, language="el",
          tags=["greek"], picture=img("greek"), created="2026-10-24T08:00:00+00:00"),
    entry("cyrillic", "Мельница у реки", CYRILLIC, language="ru",
          tags=["cyrillic"], picture=img("cyrillic"), created="2026-10-23T08:00:00+00:00"),
    entry("arabic", "الطاحونة على النهر", ARABIC, language="ar",
          tags=["rtl"], created="2026-10-22T08:00:00+00:00"),
    entry("japanese", "川辺の水車小屋", JAPANESE, language="ja",
          tags=["cjk"], picture=img("japan"), created="2026-10-21T08:00:00+00:00"),
    entry("images", "A gallery of oddly sized images", IMAGES,
          tags=["images"], picture=img("gallery0", 1600, 900),
          created="2026-10-20T08:00:00+00:00"),
    entry("long-read", "The longest read: fifteen chapters", LONG,
          tags=["longform"], starred=True, picture=img("long"),
          created="2026-10-19T08:00:00+00:00"),
    entry("short", "Short", "<p>One line.</p>", created="2026-10-18T08:00:00+00:00"),
    entry("empty", "Untitled entry with no content", "",
          created="2026-10-17T08:00:00+00:00"),
    entry("emoji", "🦘 Emoji in the title — and an em dash", f"<p>🎉 {LOREM} 🚀</p>",
          created="2026-10-16T08:00:00+00:00"),
    entry("archived", "An archived article", f"<p>{LOREM}</p>",
          archived=True, picture=img("archived"), created="2026-10-15T08:00:00+00:00"),
    entry("archived-starred", "Archived and starred", f"<p>{LOREM}</p>",
          archived=True, starred=True, tags=["reference"],
          created="2026-10-14T08:00:00+00:00"),
]

# Filler so the list paginates (Wallabag shows 12 per page by default).
ENTRIES += [
    entry(f"filler-{i}", f"Filler article number {i}", f"<p>{LOREM}</p>" * (i % 5 + 1),
          tags=["filler"], picture=img(f"filler{i}") if i % 3 else None,
          created=f"2026-09-{i:02d}T08:00:00+00:00")
    for i in range(1, 21)
]

print(json.dumps(ENTRIES, ensure_ascii=False, indent=1))
