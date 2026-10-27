# START HERE

Golbez fork of FreeEnterprise4.

## Read

1. `README.md` — setup, build, local web UI.
2. `GOLBEZ_LOCKED_SPEC.md` — authoritative locked graphics/data rules.
3. `ROADMAP.md` — remaining randomizer naming cleanup.
4. `LOCAL_WEBUI.md` — local flag tester.

## Canonical build

`golbez_exact_playable.sfc`

- SHA-1: `640e63b5cfbf23439adf33aefaf978687781c295`
- SHA-256: `357b25a5103c08cf9675fa97677647877a93f98daf94988d1e30630062cb153c`
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
