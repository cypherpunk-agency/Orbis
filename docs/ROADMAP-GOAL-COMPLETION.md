# M1–M8 goal completion audit

Independent final audit, 14 October 2026. The finite **M1–M8 goal passes locally**: 59 unique required stories, 285 scenes and seven complete campaigns. M2a is satisfied by the completed Turkey sequence. M9 and M10 remain outside this goal and are not complete; this is not completion of the entire M1–M10 release.

The accepted checkout is main `78c1fd6` plus the authorized local source/story corrections. Current `js/app.js` SHA256 is `fa99ebd08a627c194eee1892ea54944e30b8aab6964655566788b78a6242bce4`.

| Independently checked evidence | Result |
| --- | --- |
| [Acceptance ledger](ROADMAP-ACCEPTANCE.md), compared with frozen scope IDs | All 59 required story rows and M1–M8/M2a passed; M9/M10 not started. Superseded unresolved-tooltip checkpoint text removed. |
| `node tools/check-roadmap-regression.mjs .cache/roadmap-review/current-regression-final` | Current hashes, 139 registered stories, 278 viewport results, 1,434 scene views, 274 option views and 1,708 screenshot files; no errors. |
| `current-controls/suite-final.json` and every referenced chapter report | 59 chapters, 570 actual scene-control views, two viewports per chapter and exact current scene counts; no errors. The stopped fame child is explicitly superseded by the passing full two-viewport diagnostic report. |
| All seven referenced current campaign reports, compared with frozen manifest | Exact orders, chapter boundaries, deep links and embeds pass at both sizes. |
| `current-play/chunk-{0,1}.json`, compared with an independently derived expected timeline-case set | Exactly 108 cases, no missing, extra or duplicate cases; first-observation advancement and paused state recorded, no errors. |
| Current country, UI and normal/embed navigation reports | Eight actual country-pointer checks, two UI viewports and three motion configurations per navigation mode pass, with no errors. Navigation provenance is documented by the frozen current-renderer run; its raw report does not embed a renderer hash. |
| `current-builder-reproduction.json` | All 33 emitted US/Ukraine JSON files semantically match the current checkout. |

Report paths above are under `.cache/roadmap-review/`. These checks complement the completed source/content and screenshot inspections linked in the milestone audits and [current regression evidence](ROADMAP-EVIDENCE-REGRESSION.md). They do not imply a new upstream retrieval or clearance. The recorded BHHT reused-artifact licence renewal limitation, bounded observation coverage, historical geometry approximations and other disclosed source limitations remain in force. No concrete unresolved implementation or acceptance blocker was found in this final audit.

The latest corrections remain local and have not been committed or deployed by this goal. Previously hosted-release evidence is separately versioned.
