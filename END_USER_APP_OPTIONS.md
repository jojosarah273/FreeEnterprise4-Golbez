# End-user app options

**Status: options documented, nothing implemented.**

The goal: a small app a casual user can install on a major platform, point at
their own FF2 US ROM, pick settings, and get a playable Golbez seed — with no
web server, no Python install, and no terminal.

Two codebases are relevant:

- **This repo** — the Golbez engine (`FreeEnt/` + `f4c/` + locked reference
  data). Pure Python (stdlib + `pyaes`), no ROMs included, verified builds.
- **FREEENTERPRISE_APP** (`github.com/jojosarah273/…`, see
  `DEV/FREEENTERPRISE_APP`) — an existing offline front-end for Free
  Enterprise: FF4-native menu interface, on-device engine, bundled Snes9x
  playback, seed library, in-place updates. Its
  `MULTI_ENGINE_OPTIONS.md` already specifies and *measures* a
  multi-engine design in which the Golbez engine from this repo ran through
  the app's own bridge: generation in ~4 s, ROM boots in the app's Snes9x
  core, spoiler reads "Lunar Palace character … Golbez", tracker WRAM
  address identical to the bundled engine, and all verification words
  covered by the app's existing checksum icon set.

No option below requires hosting anything. In every case the ROM is supplied
by the user at runtime and never distributed.

---

## Option A — Golbez as an engine inside FREEENTERPRISE_APP (recommended)

The app already is the "pump ROM in, choose settings, go" product; the Golbez
engine becomes a second, opt-in engine selected at seed-design time. This is
the design already chosen in that repo's `MULTI_ENGINE_OPTIONS.md`, and the
riskiest claims were tested there rather than assumed:

| Measured (via the app's `fe_bridge.py --ext`) | Result |
|---|---|
| Engine version reporting | `4.6.0.open` (Golbez fork) |
| Generation time (host) | ~4 s |
| ROM boots in the app's Snes9x core | yes |
| Spoiler shows Golbez content | yes |
| Tracker flag address | `$7e1500` — identical to bundled engine |
| Bridge changes required | none (`--ext` isolation already suffices) |

Remaining work (already enumerated in that repo; repeated here for
completeness):

1. `EngineStore` — list/select per-engine directories; parse each engine's
   `manifest.json` (`id`, display name, version, upstream URL).
2. An `Engine` row in the generate flow; the flag editor loads the selected
   engine's own compiled `ui_spec.json`, presets, and checks — each engine
   ships its own spec compiled by **its own** `compile_uispec.py`, so no
   cross-engine flag translation is ever authored by hand.
3. Seed rows labelled with their engine; "new seed with these flags" silently
   re-selects the recorded engine.
4. Packaging: an engine bundle zip containing `FreeEnt/`, `f4c/`, `pyaes/`,
   `golbez_reference/`, plus `assets/ui_spec.json` compiled by this repo's
   spec tooling (`cd FreeEnt && bash compile_all_specs.sh`), the engine's
   `presets.json`, and `checks.json`.

This repo's engine is already in the shape the bundle format expects:
self-contained, ROM-free, with its locked data applied by
`FreeEnt/golbez_lock.py` from `golbez_reference/LOCKED_MANIFEST.json`, and its
UI spec already trimmed to the Golbez flag surface (`Cstart:golbez`,
`only:cecil,golbez`, `O1:char_golbez`, …; no FuSoYa-era flags).

**Doc refresh needed in the app repo:** its `GOLBEZ_MODE_FEASIBILITY.md`
describes the earlier IPS-patch-based fork (three `.ips` files, free-space
pointer edits, `golbez_final_test.sfc`). The current engine has **no IPS
dependency at all** — locked blobs are applied directly by the generator and
verified at build time — so the engine bundle is simpler than that document
implies. Re-run its offset/compatibility notes against the current `main`
before the app-side integration is built.

**Platform story:** Android ships today (Chaquopy embeds the engine,
Snes9x plays the result in-app). Windows/Linux are the app's own
`MENU_PORTABILITY.md` plan — the emulator core and engine are already
portable; the remaining work is the menu-shell backends. Golbez rides along
for free once it is an engine in the store, because engines are isolated by
design.

**Trade-offs:** the most polished result and the only one that also *plays*
the seed; but it depends on the app repo's desktop-menu work for the
"major platforms" part, and the Golbez engine becomes a guest of another
project's release cadence.

---

## Option B — small standalone app from this repo (webview shell)

A dedicated, minimal Golbez app built directly on what this repo already
contains:

- the existing stdlib HTTP server (`local_webui.py`) serving the real React
  flag editor, bound to `127.0.0.1` on a random port inside the app;
- a native window via **pywebview** (OS webview — no bundled Chromium) that
  just displays that page, with a JS→Python bridge so "Generate" writes the
  `.sfc` and shows a native save dialog instead of a browser download;
- packaged with **PyInstaller** (one-folder) including the engine data files
  (`f4c/*.lark`, `FreeEnt/scripts`, `FreeEnt/assets`, `flagspec.pickle`,
  `golbez_reference/`);
- Linux buildable and fully testable on this machine; Windows builds via
  GitHub Actions; webview-missing fallback: open the default browser at the
  same local URL, so the shell is a presentation choice, not a dependency.

**Trade-offs:** roughly a day of work and zero coupling to the app repo — but
it is a second product to maintain, has no playback, no seed library, and no
in-app updates, and its UI is the web flag editor rather than the FF4-native
interface. Reasonable as a quick stopgap; hard to justify if Option A is
already on the roadmap.

---

## Option C — "Golbez-lite": a stripped build of FREEENTERPRISE_APP

A reduced configuration of the existing app: engine picker collapsed to one
engine, generate screen only, output handed to the user's own emulator.
Smaller surface to publish, but it discards the app's differentiators
(in-app play, library, tracker, updates) while still carrying the menu
portability work. It forks the maintenance story without buying anything
Option A doesn't. **Not recommended** — Option A's opt-in engine download
already gives casual users the simple path without a second app.

---

## Option D — fully in-browser (Pyodide/WASM)

Ship a static web page that runs the engine client-side in WASM; the user's
ROM never leaves their machine and there is nothing to install at all.
Attractive in principle, but: CPython-in-WASM packaging for this engine is
unproven (the ~4 s native generation could become tens of seconds), the
PyInstaller-grade data-file plumbing would have to be redone for the wasm
filesystem, and every engine update re-triggers that work. **Future option
only** — worth revisiting once the engine is selectable inside the app, not
as the first delivery vehicle.

---

## Recommendation

**Option A.** The app repo's own measurements show the Golbez engine already
runs through its bridge unchanged, its tracker and verification icons already
cover this engine's output, and its flag editor already compiles per-engine
specs. Bending in the Golbez engine is mostly *packaging work in this repo*
(produce the engine bundle zip: `FreeEnt/`, `f4c/`, `pyaes/`,
`golbez_reference/`, `ui_spec.json`, `presets.json`, `checks.json`,
`manifest.json`), plus the already-specified `EngineStore` work in the app
repo. Option B remains the fallback if a standalone Golbez-branded app is
wanted quickly.

### If initiated, the first concrete steps would be

1. In this repo: script the engine-bundle zip (data only — no ROMs, no
   generated seeds) and verify a seed generated *from the bundle* passes
   `verify_golbez_lock.py`.
2. In the app repo: re-run the bridge compatibility numbers against the
   current `main` of this repo, and refresh `GOLBEZ_MODE_FEASIBILITY.md`
   (it predates the lock/manifest refactor).
3. Then the app-side `EngineStore` + engine row, per its
   `MULTI_ENGINE_OPTIONS.md`.
