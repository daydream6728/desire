#!/usr/bin/env python3
"""What the prompts promise about themselves, checked rather than trusted: the
links resolve, the deny lists name real tools, the loaded prompts fit their
budget, and with `--memory` a MEMORY_REPO clone matches the seed it came from
and its board fits under 200 lines.

Run: python3 .github/lint.py [--memory <path to MEMORY_REPO clone>]
"""
import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SEED = ROOT / "template" / "memory"

# Bytes a session loads, 20% above their size on 2026-10-21.
BUDGET = {"CLAUDE.md": 22_840, "BIRDSONG.md": 2_412, "EVENING.md": 3_508}

# The MCP servers a deny list may name: a wrong server name denies nothing.
SERVERS = {"claude-code-remote"}

# Files a MEMORY_REPO clone carries verbatim from the seed.
COPIES = [".claude/settings.json", ".claude/hooks/session-start.sh",
          ".agents/skills/sweep/sweep.py", ".agents/skills/sweep/test_sweep.py"]

LINK = re.compile(r"\]\(([^)\s]+)\)")
IMPORT = re.compile(r"^@(\S+)$", re.MULTILINE)


def slug(heading):
    """GitHub's anchor for a heading: lowercase, punctuation dropped, spaces
    to hyphens."""
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def anchors(path):
    return {slug(line.lstrip("#")) for line in path.read_text().splitlines()
            if line.startswith("#")}


def links(root, skip=("CHANGELOG.md",)):
    """Every relative link in a Markdown file that points nowhere. The
    changelog is history and may name files that are gone."""
    for path in sorted(root.rglob("*.md")):
        if ".git" in path.parts or path.name in skip:
            continue
        for target in LINK.findall(path.read_text()):
            if re.match(r"[a-z]+:", target):
                continue
            name, _, anchor = target.partition("#")
            where = (path.parent / name).resolve() if name else path
            if not where.exists():
                yield f"{path.relative_to(root)}: no such file {target}"
            elif anchor and where.suffix == ".md" and anchor not in anchors(
                    where):
                yield f"{path.relative_to(root)}: no such heading {target}"


def loaded(path):
    """The bytes a file puts in context with every `@` import it pulls in."""
    text = path.read_text()
    return len(text.encode()) + sum(
        loaded(path.parent / name) for name in IMPORT.findall(text)
        if (path.parent / name).exists())


def budget():
    for name, cap in BUDGET.items():
        if (size := loaded(ROOT / name)) > cap:
            yield f"{name} loads {size} bytes, over its budget of {cap}"


def denied():
    """The tools the seed denies, from the settings file and from the hook
    that writes the same list into the workspace settings."""
    settings = json.loads((SEED / ".claude/settings.json").read_text())
    hook = (SEED / ".claude/hooks/session-start.sh").read_text()
    written = json.loads(re.search(r"^deny='(.*)'$", hook, re.M).group(1))
    return set(settings["permissions"]["deny"]), set(written)


def deny():
    settings, written = denied()
    if settings != written:
        yield f"the hook denies {sorted(written ^ settings)} and the" \
              " settings do not, or the other way round"
    for tool in settings | written:
        server = re.match(r"mcp__(.+?)__", tool)
        if server and server.group(1) not in SERVERS:
            yield f"deny names {tool}, on no server in {sorted(SERVERS)}"


def memory(clone):
    for name in COPIES:
        if not (clone / name).exists():
            yield f"{clone.name}/{name} is missing, the seed carries it"
        elif (clone / name).read_bytes() != (SEED / name).read_bytes():
            yield f"{clone.name}/{name} differs from template/memory/{name}"
    if (lines := len((clone / "README.md").read_text().splitlines())) > 200:
        yield f"the board is {lines} lines, over 200"
    yield from (f"{clone.name}/{finding}" for finding in links(clone))


def main(arguments):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--memory", type=pathlib.Path)
    options = parser.parse_args(arguments)
    findings = [*links(ROOT), *budget(), *deny()]
    if options.memory:
        findings += memory(options.memory.resolve())
    print("\n".join(findings) or "clean")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
