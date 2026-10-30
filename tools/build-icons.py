#!/usr/bin/env python3
# Builds fonts/lucide-wallabag.woff2: Lucide glyphs behind Wallabag's Material Icons ligature names,
# so <i class="material-icons">star</i> renders Lucide's star without template changes.
# Needs fonttools, brotli and skia-pathops. Usage: tools/build-icons.py path/to/lucide-static
# (the unpacked npm package: `npm pack lucide-static` and extract it).
import json
import os
import re
import sys

import pathops
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.svgLib.path import parse_path
from fontTools.ttLib import TTFont

# Material ligature name -> Lucide icon. Covers every name in Wallabag 2.6 templates and JS.
LIGATURES = {
	"account_circle": "circle-user",
	"account_circle_filled": "circle-user",
	"add": "plus",
	"arrow_back": "arrow-left",
	"assistant_photo": "rocket",
	"brightness_auto": "contrast",
	"brightness_high": "sun",
	"brightness_low": "moon",
	"brightness_medium": "sun-moon",
	"build": "wrench",
	"casino": "dices",
	"clear": "x",
	"close": "x",
	"comment": "message-square",
	"create": "pencil",
	"delete": "trash-2",
	"delete_outline": "trash-2",
	"done": "archive",
	"download": "download",
	"edit": "pencil",
	"email": "mail",
	"error": "circle-alert",
	"error_circle_rounded": "circle-alert",
	"error_outline": "circle-alert",
	"file_download": "download",
	"filter_list": "list-filter",
	"flag": "flag",
	"flag_filled": "flag",
	"get_app": "download",
	"grade": "star-filled",
	"group": "users",
	"import_export": "arrow-down-up",
	"input": "log-out",
	"insert_comment": "message-square",
	"insert_link": "link",
	"label": "tag",
	"label_outline": "tag",
	"language": "globe",
	"launch": "external-link",
	"library_add_check": "list-checks",
	"link": "link",
	"live_help": "circle-help",
	"local_printshop": "printer",
	"mail": "mail",
	"mail_outline": "mail",
	"markunread": "mail",
	"menu": "menu",
	"mobile": "smartphone",
	"mode": "pencil",
	"mode_edit": "pencil",
	"mode_edit_outline": "pencil",
	"more_vert": "ellipsis-vertical",
	"open_in_new": "external-link",
	"outlined_flag": "flag",
	"people": "users",
	"people_alt": "users",
	"people_outline": "users",
	"perm_identity": "user",
	"person": "user",
	"person_filled": "user",
	"person_outline": "user",
	"print": "printer",
	"refresh": "refresh-cw",
	"rss_feed": "rss",
	"save_alt": "download",
	"search": "search",
	"send": "send",
	"settings": "settings",
	"share": "share-2",
	"smartphone": "smartphone",
	"star": "star-filled",
	"star_border": "star",
	"star_outline": "star",
	"stay_current_portrait": "smartphone",
	"swap_vert": "arrow-down-up",
	"timer": "clock",
	"today": "calendar",
	"tools_wrench": "wrench",
	"unarchive": "archive-restore",
	"view_list": "list",
	"view_module": "layout-grid",
	"vpn_key": "key-round",
}
# Reachable by codepoint only, for Wallabag's icomoon classes (.icon-eye etc.)
EXTRA = ["eye", "eye-off", "calendar", "mail", "clock", "link"]

# Lucide's font maps its 24-unit SVG grid onto a 1000-unit em, y flipped
SVG_TO_FONT = (1000 / 24, 0, 0, -1000 / 24, 0, 1000)

pkg = sys.argv[1]
src = TTFont(os.path.join(pkg, "font", "lucide.ttf"))
codepoints = json.load(open(os.path.join(pkg, "font", "codepoints.json")))
src_cmap = src.getBestCmap()
src_glyphs = src.getGlyphSet()

icons = sorted(set(LIGATURES.values()) | set(EXTRA))
glyphs = {".notdef": TTGlyphPen(None).glyph()}
widths = {".notdef": 0}

for name in icons:
	pen = TTGlyphPen(None)
	if name == "star-filled":
		# Lucide has no filled star: union the stroked outline with the star's own fill
		path = pathops.Path()
		src_glyphs[src_cmap[codepoints["star"]]].draw(path.getPen())
		svg = open(os.path.join(pkg, "icons", "star.svg")).read()
		fill = pathops.Path()
		parse_path(re.search(r' d="([^"]+)"', svg).group(1), TransformPen(fill.getPen(), SVG_TO_FONT))
		pathops.union([path, fill], Cu2QuPen(pen, 1, reverse_direction=True))
	else:
		src_glyphs[src_cmap[codepoints[name]]].draw(pen)
	glyphs[name] = pen.glyph()
	widths[name] = 1000

# Letters exist only to feed the ligatures; unmatched text renders blank instead of as a word
letters = {c: f"uni{ord(c):04X}" for c in "abcdefghijklmnopqrstuvwxyz_"}
for glyph in letters.values():
	glyphs[glyph] = TTGlyphPen(None).glyph()
	widths[glyph] = 0

cmap = {ord(c): glyph for c, glyph in letters.items()}
cmap.update({codepoints[name]: name for name in icons if name in codepoints})

fb = FontBuilder(1000, isTTF=True)
fb.setupGlyphOrder(list(glyphs))
fb.setupCharacterMap(cmap)
fb.setupGlyf(glyphs)
glyf = fb.font["glyf"]
fb.setupHorizontalMetrics({name: (width, getattr(glyf[name], "xMin", 0)) for name, width in widths.items()})
fb.setupHorizontalHeader(ascent=1000, descent=0)
fb.setupOS2(sTypoAscender=1000, sTypoDescender=0, sTypoLineGap=0, usWinAscent=1000, usWinDescent=0)
fb.setupNameTable({"familyName": "Lucide Wallabag", "styleName": "Regular"})
fb.setupPost()

# Longest names first, so "star_border" wins over "star"
rules = "\n".join(
	f"\tsub {' '.join(letters[c] for c in material)} by {lucide};"
	for material, lucide in sorted(LIGATURES.items(), key=lambda item: -len(item[0]))
)
addOpenTypeFeaturesFromString(fb.font, f"feature liga {{\n{rules}\n}} liga;")

out = os.path.join(os.path.dirname(__file__), "..", "fonts", "lucide-wallabag.woff2")
os.makedirs(os.path.dirname(out), exist_ok=True)
fb.font.flavor = "woff2"
fb.font.save(out)
print(f"{out}: {len(LIGATURES)} ligatures, {len(icons)} icons, {os.path.getsize(out) // 1024} KB")
