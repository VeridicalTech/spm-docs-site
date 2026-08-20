# SPM-Polaris Documentation Site (docs.spmos.ai)

Static documentation builder: Markdown content + a shared page shell, rendered
to `dist/` by `build.py`. No JS framework.

## Layout

- `content/*.md` — the documentation pages (front-matter `title`)
- `templates/page.html` + `assets/site.css` / `site.js` — page shell
- `assets/logo/` — brand images copied into `dist/assets/` at build time
- `build.py` — renders every `content/*.md` page into `dist/`

## Build

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python build.py      # outputs dist/
```

Deploy target: Cloudflare Pages project `spmos-docs` (custom domain
`docs.spmos.ai`), production branch `main`.
