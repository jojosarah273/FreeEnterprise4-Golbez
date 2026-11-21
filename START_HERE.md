# START HERE

Golbez fork of FreeEnterprise4.

## Read

1. `README.md` — setup, build, local web UI.
2. `GOLBEZ_LOCKED_SPEC.md` — authoritative locked graphics/data rules.
3. `ROADMAP.md` — remaining randomizer naming cleanup.
4. `LOCAL_WEBUI.md` — local flag tester.
5. `END_USER_APP_OPTIONS.md` — options for a small end-user app.

## Canonical build

`golbez_exact_playable.sfc`

- SHA-1: `8aa201aac361236ce9e9080c79752b41c6359014`
- SHA-256: `6e3433d8aa42f0e4b9c40434410c0a403721429f1f6966f14064513c59c16268`
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
