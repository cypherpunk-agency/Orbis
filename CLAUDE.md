# Orbis

Static map-stories site (see README.md). No build step.

## Licensing rule (two tiers)
- **Base data** (map geometry, basemap imagery, borders, libraries, fonts — anything every story depends on) must allow **commercial use**. Copyleft/share-alike (GPL, CC BY-SA, ODbL) in the base needs explicit sign-off.
- **Story layers** (optional data shown in a story or as a switchable overlay) may use **any licence, including non-commercial or permission-based**, as long as the files may be **published in a public open-source repository**.
- Never use data whose terms forbid redistribution, are unclear, or say "ask us" without a written grant on file.
- Every source: register it in `js/sources.js`, add a row to `docs/LICENSING.md`, make sure the UI shows it (story `sources:` / scene `sources:`), and run `node tools/check-licences.js` before committing.

## Deploy
- Live at https://orbis.cypherpunk.agency/. **Only a push to `production` deploys** (`.github/workflows/deploy.yml`); `master` never does. Push `production` only when Tommi says so.
- Served: `index.html editor.html css js data stories`. `tools/` and `docs/` are not shipped. Paths are served as-is (no SPA fallback, no build).
- The server's CSP allows only `'self'`, cdnjs.cloudflare.com, cdn.jsdelivr.net, Google Fonts and `https:` images; `connect-src` is `'self'`. A new external script, stylesheet, font or fetch/XHR origin is **blocked silently** until infra adds it. Ask the infra (server-setup) session first; it owns the VM, Caddy and monitoring. Embedding (`?embed=1` in third-party iframes) must keep working.
- Uptime monitoring probes `/data/world50.json`; don't move or rename it without telling infra.
