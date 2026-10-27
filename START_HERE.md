# START HERE

Golbez fork of FreeEnterprise4.

## Read

1. `README.md` — setup, build, local web UI.
2. `GOLBEZ_LOCKED_SPEC.md` — authoritative locked graphics/data rules.
3. `ROADMAP.md` — remaining randomizer naming cleanup.
4. `LOCAL_WEBUI.md` — local flag tester.

## Canonical build

`golbez_exact_playable.sfc`

- SHA-1: `a8ae9f5d1a5d8ca4d437c4478c1318352db4f1d0`
- SHA-256: `838dcf0f0ec7fc8c4ff57106d1ea3585172dfd52fc6b45cfa0c8513ce1a633be`
- Quickstart, playable Golbez.

## Verify

```sh
python3 verify_golbez_lock.py
python3 verify_golbez_lock.py path/to/generated.sfc
```

Generation fails if a locked region changes.

## Local web UI

```sh
python3 local_webui.py
# http://127.0.0.1:8099/make
```
