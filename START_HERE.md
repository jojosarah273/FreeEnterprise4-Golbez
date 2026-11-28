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

- SHA-1: `b85c57cec0259c56ee80f89d386528602752bfe4`
- SHA-256: `b0b0f3a83298db895e9f8b1747d136eefcf4f7643c560d8211d180c5c0ebbe25`
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
