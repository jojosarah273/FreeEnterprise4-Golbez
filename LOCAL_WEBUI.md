# Local Golbez generator web UI

A local service that serves the original FreeEnterprise React flag editor, restricted to the flags that exist in this codebase.

The UI version label is overridden to **`4.6.0-Golbez`** without changing the internal FreeEnt version/flag compatibility.

## Run

```sh
cd /home/jojosarah273/DEV/FE_GOLBEZ
python3 local_webui.py
```

Open:

```text
http://127.0.0.1:8099/
```

This redirects to `/make`, which uses the actual `make_react.html`, `make_react.js`, `uispec.js`, `flags.js`, and `make_react.css` from `FreeEnt/server/`. The flag editor expands/collapses nested options exactly like the upstream React UI.

A simple fallback form remains at:

```text
http://127.0.0.1:8099/simple
```

Set `LOCAL_WEBUI_PORT` to change the port.

## What it does

- Serves the real React flag editor and generated `uispec.js`.
- `/presets` serves the upstream preset categories, sanitized so only current flags remain.
- Legacy `fusoya` names are converted to `golbez` for preset testing.
- `/generate` accepts the React form POST and returns the generated `.sfc`.
- Local builds use `-q`/quickstart by default.
- Generated files are also written to `local_webui_output/` and listed at `/outputs`.
- Every generated ROM still goes through the exact Golbez reference blobs and the build-time lock guard.

## Current Golbez flags

```text
Cstart:golbez
Conly:golbez
Cno:golbez
Crestrict:golbez
O1:char_golbez
O1:boss_golbez
```

The picker is filtered against the current `FreeEnt/flagspec.txt`. It intentionally omits FuSoYa flags and any other flags unsupported by this source tree.

## Rebuilding the UI data

If flags or UI text change:

```sh
cd FreeEnt
bash compile_all_specs.sh
```

Then restart `local_webui.py`.

## Verification

```sh
python3 verify_golbez_lock.py local_webui_output/<build>.sfc
```

Expected:

```text
PASS: reference blobs match LOCKED_MANIFEST.json
PASS: <build> contains every locked Golbez region
```
