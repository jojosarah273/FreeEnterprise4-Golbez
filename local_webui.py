#!/usr/bin/env python3
"""Local FreeEnterprise/Golbez generator web UI.

No MongoDB, CherryPy, or React required. Serves a small flagset tester and
runs the normal FreeEnt generator as a subprocess.
"""
import html
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse
import zipfile
import mimetypes
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path

from flag_picker import controls_html as flag_controls_html
from flag_picker import _allowed_flags, _sanitize_flags

import jinja2
import FreeEnt

ROOT = Path(__file__).resolve().parent
ROM = ROOT / "ff2.smc"
OUTPUT = ROOT / "local_webui_output"
TEMPLATES = ROOT / "FreeEnt" / "server"

GOLBEZ_DISPLAY_VERSION = "4.6.0-Golbez"

DEFAULT_FLAGS = (
    "Onone Kmain Pnone Crelaxed/only:cecil,golbez/Cstart:golbez "
    "Tvanilla Svanilla Bvanilla Evanilla Gnone/-vanilla:fashion"
)

JINJA = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(TEMPLATES / "template")),
    autoescape=jinja2.select_autoescape(["html", "xml"]),
)

def _allowed_flags():
    text = (ROOT / "FreeEnt" / "flagspec.txt").read_text()
    return set(re.split(r"[\s/]+", text.strip()))

def _sanitize_flags(flags, allowed):
    """Drop flags that are not in the current flagspec."""
    kept = []
    for token in flags.split():
        parts = []
        for part in token.split("/"):
            if not part:
                continue
            if part in allowed or (part.endswith(":*") and any(x.startswith(part[:-1]) for x in allowed)):
                parts.append(part)
        if parts:
            kept.append("/".join(parts))
    return " ".join(kept)

def _sanitize_category_presets():
    allowed = _allowed_flags()
    try:
        data = json.loads((TEMPLATES / "presets.json").read_text())
    except Exception:
        return []

    def clean_flags(flags):
        return _sanitize_flags(str(flags).replace("fusoya", "golbez"), allowed)

    output = []
    for group in data:
        if not isinstance(group, dict):
            continue
        if "presets" in group:
            presets = []
            for item in group.get("presets", []):
                if not isinstance(item, dict) or "flags" not in item:
                    continue
                flags = clean_flags(item["flags"])
                if not flags:
                    continue
                item = dict(item)
                item["flags"] = flags
                item["name"] = str(item.get("name", "Untitled preset")).replace("FuSoYa", "Golbez").replace("Fusoya", "Golbez")
                presets.append(item)
            if presets:
                group = dict(group)
                group["presets"] = presets
                output.append(group)
        else:
            output.append(group)
    return output

def page(title, body):
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{html.escape(title)}</title>
<style>
body{{font-family:system-ui,sans-serif;max-width:1100px;margin:2rem auto;padding:0 1rem;background:#101820;color:#e8eef4}}
h1,h2{{color:#7fd7ff}} a{{color:#7fd7ff}} textarea,input{{width:100%;box-sizing:border-box;background:#182630;color:#e8eef4;border:1px solid #35576b;padding:.55rem;border-radius:5px}}
textarea{{min-height:8rem;font-family:monospace}} button{{background:#1f6f8b;color:white;border:0;padding:.7rem 1.2rem;border-radius:5px;cursor:pointer}}
button:hover{{background:#2a8cab}} .row{{display:flex;gap:1rem;align-items:end;flex-wrap:wrap}} .row>div{{flex:1;min-width:220px}}
pre{{background:#0b1116;padding:1rem;overflow:auto;border:1px solid #263b49}} .muted{{color:#9fb3c2}} .ok{{color:#8ee6a1}} .err{{color:#ff8787}}
select{{width:100%;padding:.55rem;background:#182630;color:#e8eef4;border:1px solid #35576b;border-radius:5px}}
code{{background:#182630;padding:.15rem .3rem;border-radius:3px}}
#flagPicker details{{margin:.2rem 0 .45rem}} #flagPicker summary{{cursor:pointer;color:#9fe3ff;font-weight:600;margin:.35rem 0}}
.flag-group-title{{margin:.45rem 0 .2rem;color:#c8d8e4;font-weight:600}} .flag-children{{margin-left:1.1rem;padding-left:.7rem;border-left:1px solid #2b4656}}
.flag-option{{display:block;margin:.16rem 0;font-size:.94rem}} .flag-option input{{width:auto;margin-right:.35rem}}
.flag-option.hard span{{color:#ffcf7a}}</style></head><body><h1>{html.escape(title)}</h1>{body}</body></html>"""

class Handler(BaseHTTPRequestHandler):
    presets = []

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, code, body, content_type="text/html; charset=utf-8", extra=None):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def _real_make(self, flags=None, seed=None):
        page_html = JINJA.get_template("make_react.html").render(
            version=GOLBEZ_DISPLAY_VERSION,
            production=False,
            initial_flags=flags or DEFAULT_FLAGS,
            initial_seed=seed or "",
            beta_changelog=None,
        )
        return self._send(200, page_html)

    def _serve_tree(self, prefix, path):
        rel = urllib.parse.unquote(path[len(prefix):])
        base = (ROOT / "FreeEnt" / "server" / prefix.strip("/")).resolve()
        target = (base / rel).resolve()
        try:
            target.relative_to(base)
        except ValueError:
            return self._send(403, "forbidden", "text/plain")
        if not target.is_file():
            return self._send(404, "not found", "text/plain")
        data = target.read_bytes()
        ctype = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        return self._send(200, data, ctype)

    def _presets_json(self):
        body = json.dumps(_sanitize_category_presets())
        return self._send(200, body, "application/json")

    def _index(self):
        options = ['<option value="">— choose a preset —</option>']
        for i, p in enumerate(self.presets):
            options.append(f'<option value="{i}">{html.escape(p["name"])}</option>')
        body = f"""
<p>Local flagset tester for the Golbez FreeEnterprise build. Generation uses the normal FreeEnt generator from this repo.</p>
<p class="muted">Current character flag is <code>Cstart:golbez</code> / <code>only:cecil,golbez</code>. Legacy <code>fusoya</code> flags are not valid in this source version.</p>
<div class="row"><div><label>Preset (fusoya names are converted to golbez for testing)</label><select id="preset" onchange="pickPreset(this.value)">{''.join(options)}</select></div></div>
<h2>Pick flags</h2>
<p class="muted">Only flags present in the current <code>FreeEnt/flagspec.txt</code> are shown. Use the textarea below for manual edits.</p>
{flag_controls_html()}
<form method="post" action="/generate">
<div class="row"><div><label>Flags</label><textarea name="flags">{html.escape(DEFAULT_FLAGS)}</textarea></div></div>
<div class="row"><div><label>Seed (optional)</label><input name="seed" placeholder="random if empty"></div><div><label><input type="checkbox" name="quickstart" value="1" checked style="width:auto"> Quickstart (skip intro)</label></div></div>
<p><button type="submit">Generate ROM</button></p>
</form>
<h2>Current Golbez flags</h2>
<pre>Cstart:golbez          start as Golbez
Conly:golbez           only Golbez is eligible to join
Cno:golbez             exclude Golbez
Crestrict:golbez       mark Golbez as restricted
O1:char_golbez         objective: Get Golbez
O1:boss_golbez         objective: Defeat Golbez</pre>
<h2>Changed from upstream</h2>
<p>The current source uses <strong>Golbez</strong> where upstream FreeEnterprise used FuSoYa.</p>
<ul>
<li>Use <code>Cstart:golbez</code>, <code>Conly:golbez</code>, <code>Cno:golbez</code>, <code>Crestrict:golbez</code>.</li>
<li>Omitted legacy flags: <code>Cstart:fusoya</code>, <code>Conly:fusoya</code>, <code>Cno:fusoya</code>, <code>Crestrict:fusoya</code>, <code>char_fusoya</code>, <code>boss_fusoya</code>.</li>
<li>Objectives are <code>char_golbez</code> and <code>boss_golbez</code>.</li>
<li>Preset text is converted from <code>fusoya</code> to <code>golbez</code> where needed for testing.</li>
</ul>
<h2>Useful commands</h2>
<pre>python3 local_webui.py
# then open http://127.0.0.1:8099/</pre>
<p class="muted">Generated files are also written under <code>local_webui_output/</code>.</p>
<script>
const presets = {json.dumps(self.presets)};
const DEFAULT_FLAGS = {json.dumps(DEFAULT_FLAGS)};
function flagInputs() {{ return Array.from(document.querySelectorAll('#flagPicker input')); }}
function collectFlags() {{
  const parts = flagInputs().filter(i => i.checked).map(i => i.value).filter(Boolean);
  document.querySelector('textarea[name=flags]').value = Array.from(new Set(parts)).join(' ');
}}
function setFlags(text) {{
  const tokens = (text || '').trim().split(/\s+/).filter(Boolean);
  for (const input of flagInputs()) input.checked = false;
  for (const token of tokens) {{
    const matches = flagInputs().filter(i => i.value === token);
    if (matches.length) matches[0].checked = true;
  }}
  document.querySelector('textarea[name=flags]').value = text || '';
}}
function pickPreset(i) {{
  if (i === '') return;
  const p = presets[Number(i)];
  if (p) setFlags(p.flags);
}}
document.addEventListener('change', (e) => {{
  if (e.target.closest('#flagPicker')) collectFlags();
}});
document.getElementById('flagPicker').addEventListener('click', (e) => {{
  if (e.target.tagName === 'INPUT') collectFlags();
}});
window.addEventListener('load', () => setFlags(DEFAULT_FLAGS));
</script>"""
        self._send(200, page("Golbez FreeEnterprise Local Generator", body))

    def _outputs(self):
        OUTPUT.mkdir(exist_ok=True)
        files = sorted(OUTPUT.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)
        rows = "".join(
            f'<li><a href="/outputs/{html.escape(p.name)}">{html.escape(p.name)}</a> '
            f'<span class="muted">({p.stat().st_size} bytes)</span></li>' for p in files[:100]
        ) or '<li class="muted">No files yet.</li>'
        body = f'<p><a href="/">Back</a></p><ul>{rows}</ul>'
        self._send(200, page("Generated Files", body))

    def _generate(self, form):
        flags = form.get("flags", [""])[0].strip()
        seed = form.get("seed", [""])[0].strip()
        quickstart = bool(form.get("quickstart")) or True  # local UI builds skip intro by default
        if not flags:
            return self._send(400, page("Error", "<p class='err'>Flags are required.</p><p><a href='/make'>Back</a></p>"))

        OUTPUT.mkdir(exist_ok=True)
        safe_seed = re.sub(r"[^A-Za-z0-9_.-]", "_", seed)[:32] or "random"
        stem = f"golbez_{safe_seed}_{int(time.time())}"
        out = OUTPUT / f"{stem}.sfc"
        cmd = [sys.executable, "-m", "FreeEnt", str(ROM), "make", "-r", "-f", flags, "-o", str(out)]
        if seed:
            cmd += ["-s", seed]
        if quickstart:
            cmd += ["-q"]
        try:
            proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=600)
        except subprocess.TimeoutExpired:
            return self._send(500, page("Generation Timeout", "<p class='err'>Generator timed out after 10 minutes.</p>"))
        if proc.returncode != 0 or not out.is_file():
            detail = html.escape((proc.stderr or proc.stdout or "No output")[-12000:])
            return self._send(500, page("Generation Failed", f"<p class='err'>Flag or generator error.</p><pre>{detail}</pre><p><a href='/make'>Back</a></p>"))
        data = out.read_bytes()
        return self._send(200, data, "application/octet-stream", {"Content-Disposition": f'attachment; filename="{out.name}"'})

    def _serve_output(self, name):
        p = OUTPUT / Path(name).name
        if not p.is_file():
            return self._send(404, page("Not Found", "<p>File not found.</p>"))
        data = p.read_bytes()
        self._send(200, data, "application/octet-stream", {"Content-Disposition": f'attachment; filename="{p.name}"'})

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            return self._send(302, "", extra={"Location": "/make"})
        if parsed.path in ("/make", "/make_react.html"):
            qs = urllib.parse.parse_qs(parsed.query)
            return self._real_make(qs.get("flags", [None])[0], qs.get("seed", [None])[0])
        if parsed.path == "/simple":
            return self._index()
        if parsed.path == "/presets":
            return self._presets_json()
        if parsed.path.startswith("/script/"):
            return self._serve_tree("/script/", parsed.path)
        if parsed.path.startswith("/static/"):
            return self._serve_tree("/static/", parsed.path)
        if parsed.path == "/health":
            return self._send(200, "ok", "text/plain")
        if parsed.path == "/outputs":
            return self._outputs()
        if parsed.path.startswith("/outputs/"):
            return self._serve_output(urllib.parse.unquote(parsed.path[len("/outputs/"):]))
        return self._send(404, page("Not Found", "<p>Not found.</p>"))

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/generate":
            return self._send(404, page("Not Found", "<p>Not found.</p>"))
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8", "replace")
        form = urllib.parse.parse_qs(raw, keep_blank_values=True)
        self._generate(form)

def main():
    Handler.presets = _sanitize_category_presets()
    port = int(os.environ.get("LOCAL_WEBUI_PORT", "8099"))
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Serving Golbez local generator at http://127.0.0.1:{port}/")
    print(f"Output directory: {OUTPUT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
