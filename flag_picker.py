"""Build a restricted flag picker from the current FreeEnt uispec/flagspec.

Only flags present in FreeEnt/flagspec.txt are offered. This keeps the local
web UI from exposing stale FuSoYa-era or otherwise unsupported flags.
"""
from __future__ import annotations
import html
import re
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent
UISPEC = ROOT / "FreeEnt" / "server" / "uispec.txt"
FLAGSPEC = ROOT / "FreeEnt" / "flagspec.txt"


@dataclass
class Item:
    flag: str
    text: str
    kind: str  # checkbox, radio, select, group
    hard: bool = False
    hide: bool = True
    children: list["Item"] = field(default_factory=list)
    valid: bool = True


def _allowed_flags() -> set[str]:
    allowed: set[str] = set()
    for line in FLAGSPEC.read_text().splitlines():
        for token in re.split(r"[\s/]+", line.strip()):
            token = token.strip()
            if token:
                allowed.add(token)
    return allowed


def _flag_is_allowed(flag: str, allowed: set[str]) -> bool:
    if not flag or flag.startswith("@"):
        return True
    if flag.endswith(":*"):
        prefix = flag[:-1]
        return any(x.startswith(prefix) for x in allowed)
    return flag in allowed


def parse() -> list[Item]:
    allowed = _allowed_flags()
    sections: list[Item] = []
    stack: list[Item] = []
    section_re = re.compile(r"^\s*==\s*(.*?)\s*$")
    widget_re = re.compile(
        r"""^\s*
        (?P<depth>\.*)
        (?P<widget>\[([^\]]*)\]|\(([^)]*)\)|<([^>]*)>)
        (?P<nohide>@?)
        (?P<hard>!?)
        \s*(?P<text>.*?)\s*$
        """,
        re.VERBOSE,
    )
    for raw in UISPEC.read_text().splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = section_re.match(line)
        if m:
            section = Item("", m.group(1), "group")
            sections.append(section)
            stack = [section]
            continue
        m = widget_re.match(line)
        if not m:
            continue
        depth = len(m.group("depth"))
        widget = m.group("widget")
        flag = widget[1:-1].strip()
        text = m.group("text").strip()
        kind = {"[": "checkbox", "(": "radio", "<": "select"}[widget[0]]
        item = Item(flag, text, kind, bool(m.group("hard")), not bool(m.group("nohide")))
        item.valid = _flag_is_allowed(flag, allowed)
        # Clamp malformed indentation rather than crashing.
        if depth >= len(stack):
            parent = stack[-1]
        else:
            stack = stack[:depth + 1]
            parent = stack[depth]
        parent.children.append(item)
        stack = stack[:depth + 1] + [item]
    # Drop invalid leaves; keep valid descendants.
    def prune(items: list[Item]) -> list[Item]:
        out = []
        for it in items:
            it.children = prune(it.children)
            if it.valid or it.kind == "group" or it.children:
                out.append(it)
        return out
    for sec in sections:
        sec.children = prune(sec.children)
    return sections


def _render_items(items: list[Item], group: str, counter: list[int]) -> str:
    out = []
    for it in items:
        if it.kind == "group" or not it.flag or it.flag.startswith("@"):
            label = html.escape(it.text) if it.text else ""
            out.append('<div class="flag-group">')
            if label:
                out.append(f'<div class="flag-group-title">{label}</div>')
            out.append(_render_items(it.children, group + "-" + str(counter[0]), counter))
            out.append("</div>")
            continue
        if not it.valid:
            # Invalid parent: still expose any valid descendants.
            out.append(_render_items(it.children, group + "-" + str(counter[0]), counter))
            continue
        counter[0] += 1
        uid = f"flag-{counter[0]}"
        flag = html.escape(it.flag)
        label = html.escape(it.text) if it.text else flag
        if it.kind == "radio":
            out.append(
                f'<label class="flag-option{" hard" if it.hard else ""}">'
                f'<input type="radio" name="{group}" id="{uid}" value="{flag}" data-flag="1"> '
                f"<span>{label}</span></label>"
            )
        elif it.kind == "select" and not it.children:
            out.append(
                f'<label class="flag-option{" hard" if it.hard else ""}">'
                f'<input type="checkbox" id="{uid}" value="{flag}" data-flag="1"> '
                f"<span>{label}</span></label>"
            )
        else:
            out.append(
                f'<label class="flag-option{" hard" if it.hard else ""}">'
                f'<input type="checkbox" id="{uid}" value="{flag}" data-flag="1"> '
                f"<span>{label}</span></label>"
            )
        if it.children:
            out.append('<div class="flag-children">')
            out.append(_render_items(it.children, group + "-" + str(counter[0]), counter))
            out.append("</div>")
    return "\n".join(out)


def controls_html() -> str:
    sections = parse()
    out = ['<div id="flagPicker">']
    counter = [0]
    for i, sec in enumerate(sections):
        title = html.escape(sec.text)
        out.append('<details class="flag-section">')
        out.append(f"<summary>{title}</summary>")
        out.append(_render_items(sec.children, f"group-{i}", counter))
        out.append("</details>")
    out.append("</div>")
    return "\n".join(out)

def _sanitize_flags(flags: str, allowed: set[str]) -> str:
    """Keep only flags that exist in the current flagspec."""
    kept = []
    for token in flags.split():
        parts = []
        for part in token.split('/'):
            if not part:
                continue
            if part in allowed or (part.endswith(':*') and any(x.startswith(part[:-1]) for x in allowed)):
                parts.append(part)
        if parts:
            kept.append('/'.join(parts))
    return ' '.join(kept)
