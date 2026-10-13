# Orbis

Static map-stories site (see README.md). No build step.

## Licensing rule (two tiers)
- **Base data** (map geometry, basemap imagery, borders, libraries, fonts — anything every story depends on) must allow **commercial use**. Copyleft/share-alike (GPL, CC BY-SA, ODbL) in the base needs explicit sign-off.
- **Story layers** (optional data shown in a story or as a switchable overlay) may use **any licence, including non-commercial or permission-based**, as long as the files may be **published in a public open-source repository**.
- Never use data whose terms forbid redistribution, are unclear, or say "ask us" without a written grant on file.
- Every source: register it in `js/sources.js`, add a row to `docs/LICENSING.md`, make sure the UI shows it (story `sources:` / scene `sources:`), and run `node tools/check-licences.js` before committing.
