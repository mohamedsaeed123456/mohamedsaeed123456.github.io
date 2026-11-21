# Mohamed Saeed portfolio

Static site for GitHub Pages. English at `/`, Arabic (right-to-left) at `/ar/`.

## Structure

```
index.html, ar/index.html   generated pages (upload these)
assets/                     generated site.css and site.js, config.js, favicon
cv/, Mohamed_Saeed.pdf      CV files
src/                        the source you edit
  layout.html               page skeleton
  sections/*.html           one file per section
  i18n/en.json, ar.json     all text, per language
  data/site.json            links, numbers, project tags (shared by both languages)
  styles/                   CSS split by component and section (rtl.css for Arabic)
  scripts/                  JS modules (theme, reveal, roles, filter, analytics)
build.py                    builds everything
```

## Change something

1. Edit the text in `src/i18n/en.json` and `ar.json` (keep both files with the same structure), or a section in `src/sections/`, or CSS/JS in `src/`.
2. Run `python3 build.py` (Python 3, no packages needed).
3. Upload the changed files to the repository.

The build fails with a clear message if a placeholder is missing or the two languages differ in structure.

## Visit counts (optional)

Create a free site on goatcounter.com and write its code in `assets/config.js`. Counts are anonymous: no cookies, no personal data.

## Publish

Upload the contents of this folder to the `mohamedsaeed123456.github.io` repository (`index.html` at the root, keep `ar/`, `assets/`, `cv/`). The `src/` folder and `build.py` are optional on the server.
