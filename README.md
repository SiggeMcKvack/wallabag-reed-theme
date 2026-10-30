# wallabag-reed-theme

A calm, warm theme for [Wallabag](https://wallabag.org): warm paper by day, warm brown by night, with an amber accent.

It ports the palette and type of [Reed](https://github.com/SiggeMcKvack/reed-theme) (a FreshRSS theme) onto the Wallabag structure of [wallabag-material-theme](../wallabag-material-theme).

- Reed's light and dark palettes, following Wallabag's theme toggle (Auto follows the OS)
- Bundled [Inter](https://rsms.me/inter/) for the interface and [Literata](https://github.com/googlefonts/literata) for articles, split by script so Greek and Cyrillic only load when needed
- [Lucide](https://lucide.dev) icons everywhere, with no template changes
- Quiet chrome: flat sentence-case buttons, outlined fields with an accent glow on focus, cards that lift on hover
- Serif reading view directly on the page, with no card around it

Tuned against Wallabag 2.6.14.

## Installation

Wallabag loads `web/custom.css` after its own CSS. Make `custom.css` and `fonts/` available there.

Docker:

```yaml
volumes:
  - ./wallabag-reed-theme/custom.css:/var/www/wallabag/web/custom.css:ro
  - ./wallabag-reed-theme/fonts:/var/www/wallabag/web/fonts:ro
```

Then hard-refresh (Cmd/Ctrl+Shift+R) the page.

Editing `custom.css` while it's bind-mounted: most editors save by replacing the file, and a single-file mount keeps pointing at the old one, so Wallabag serves nothing. Restart the container (`docker restart <container>`) after each edit.

## How the icons work

Wallabag writes icons as Material ligatures, for example `<i class="material-icons">star</i>`. `fonts/lucide-wallabag.woff2` is a Lucide font with those same ligature names, so each word is drawn as the matching Lucide glyph. Lucide has no filled star, so the build makes one for starred entries (`star`, compared with `star_border`). A word the font doesn't know renders blank instead of as text.

The mapping lives in `tools/build-icons.py`. To change an icon or update Lucide:

```sh
npm pack lucide-static && tar xzf lucide-static-*.tgz   # unpacks to ./package
pip install fonttools brotli skia-pathops
tools/build-icons.py package
```

## License

[AGPL-3.0](LICENSE), inherited from Reed. Lucide icons are [ISC licensed](LICENSE-lucide). Inter and Literata are OFL-1.1 licensed ([Inter](LICENSE-inter), [Literata](LICENSE-literata)).
