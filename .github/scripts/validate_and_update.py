#!/usr/bin/env python3
"""
Validates frontmatter in /distill and /output, then rebuilds STATUS.md.

Exit code 1 if any validation error is found.
STATUS.md is always rebuilt (even on error), so partial state is visible.
"""

import os
import re
import sys
import subprocess
from datetime import date
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent.parent
DISTILL_DIR = REPO_ROOT / "distill"
OUTPUT_DIR = REPO_ROOT / "output"
STATUS_FILE = REPO_ROOT / "STATUS.md"

REQUIRED_FIELDS = {"topic_id", "state", "contributors", "refs", "next_step"}
VALID_STATES = {"intake", "distilling", "finalized"}

COMMIT_RE = re.compile(
    r"\[(?P<topics>[^\]]+)\]\s+(?P<state>\w+)\s*\|\s*rung\s+(?P<rung>\d+)\s*\|(?P<desc>.+)"
)


# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------

def parse_frontmatter(path: Path) -> tuple[dict | None, list[str]]:
    """Return (frontmatter_dict, list_of_errors)."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None, [f"{path.relative_to(REPO_ROOT)}: missing frontmatter (file must start with '---')"]

    end = text.find("\n---", 3)
    if end == -1:
        return None, [f"{path.relative_to(REPO_ROOT)}: frontmatter block never closed"]

    raw_yaml = text[3:end].strip()
    try:
        fm = yaml.safe_load(raw_yaml)
    except yaml.YAMLError as exc:
        return None, [f"{path.relative_to(REPO_ROOT)}: YAML parse error — {exc}"]

    if not isinstance(fm, dict):
        return None, [f"{path.relative_to(REPO_ROOT)}: frontmatter is not a YAML mapping"]

    return fm, []


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_file(path: Path, all_repo_files: set[str]) -> list[str]:
    errors = []
    rel = path.relative_to(REPO_ROOT)

    fm, parse_errors = parse_frontmatter(path)
    if parse_errors:
        return parse_errors
    assert fm is not None

    # Required fields
    missing = REQUIRED_FIELDS - fm.keys()
    if missing:
        errors.append(f"{rel}: missing required fields: {sorted(missing)}")

    # State value
    state = fm.get("state")
    if state and state not in VALID_STATES:
        errors.append(f"{rel}: invalid state '{state}' (must be one of {sorted(VALID_STATES)})")

    # refs exist
    refs = fm.get("refs", [])
    if refs is None:
        refs = []
    if isinstance(refs, str):
        refs = [refs]
    for ref in refs:
        if ref not in all_repo_files:
            errors.append(f"{rel}: refs points to non-existent file '{ref}'")

    return errors


def collect_all_md_files() -> set[str]:
    """Return all .md paths relative to repo root (as forward-slash strings)."""
    result = set()
    for p in REPO_ROOT.rglob("*.md"):
        if ".git" in p.parts:
            continue
        result.add(str(p.relative_to(REPO_ROOT)))
    return result


# ---------------------------------------------------------------------------
# STATUS.md generation
# ---------------------------------------------------------------------------

def parse_git_log() -> list[dict]:
    """Parse structured commit messages into records."""
    try:
        log = subprocess.check_output(
            ["git", "log", "--pretty=format:%H %ai %s", "--", "."],
            cwd=REPO_ROOT,
            text=True,
        )
    except subprocess.CalledProcessError:
        return []

    records = []
    for line in log.splitlines():
        parts = line.split(" ", 2)
        if len(parts) < 3:
            continue
        sha, timestamp, subject = parts[0], parts[1], parts[2]
        m = COMMIT_RE.match(subject)
        if not m:
            continue
        records.append(
            {
                "sha": sha,
                "date": timestamp[:10],
                "topics": [t.strip() for t in m.group("topics").split(":")],
                "state": m.group("state"),
                "rung": int(m.group("rung")),
                "desc": m.group("desc").strip(),
            }
        )
    return records


def collect_topic_data() -> dict[str, dict]:
    """
    Build a dict of topic_id -> topic info by reading frontmatter from
    distill/ and output/ files.
    """
    topics: dict[str, dict] = {}

    def process_dir(directory: Path):
        if not directory.exists():
            return
        for path in sorted(directory.glob("*.md")):
            if path.name == ".gitkeep":
                continue
            fm, errors = parse_frontmatter(path)
            if errors or fm is None:
                continue
            tid = fm.get("topic_id")
            if not tid:
                continue

            rel = str(path.relative_to(REPO_ROOT))
            if tid not in topics:
                topics[tid] = {
                    "id": tid,
                    "state": fm.get("state", "intake"),
                    "rungs": 0,
                    "last_updated": str(date.today()),
                    "latest": rel,
                    "contributors": [],
                    "linked_topics": [],
                    "output": None,
                }

            t = topics[tid]
            # Track latest file (last alphabetically = highest rung)
            t["latest"] = rel

            # Merge contributors
            contribs = fm.get("contributors", [])
            if isinstance(contribs, str):
                contribs = [contribs]
            for c in contribs:
                if c not in t["contributors"]:
                    t["contributors"].append(c)

            # Track cross-topic links from refs
            refs = fm.get("refs") or []
            if isinstance(refs, str):
                refs = [refs]
            for ref in refs:
                m = re.match(r"distill/([a-z0-9-]+)-\d+", ref)
                if m:
                    linked = m.group(1)
                    if linked != tid and linked not in t["linked_topics"]:
                        t["linked_topics"].append(linked)

            # Update state to most recent
            t["state"] = fm.get("state", t["state"])

            if directory == OUTPUT_DIR:
                t["output"] = rel

    process_dir(DISTILL_DIR)
    process_dir(OUTPUT_DIR)

    # Count rungs per topic from filenames
    if DISTILL_DIR.exists():
        for path in DISTILL_DIR.glob("*.md"):
            m = re.match(r"([a-z0-9-]+)-(\d+)-", path.name)
            if m:
                tid = m.group(1)
                rung = int(m.group(2))
                if tid in topics:
                    topics[tid]["rungs"] = max(topics[tid]["rungs"], rung)

    return topics


def build_status_md(topics: dict[str, dict]) -> str:
    lines = [
        "# STATUS",
        "",
        "> Auto-generated. Do not edit manually.",
        "> Rebuilt on every push to `main` by `.github/workflows/validate.yml`.",
        "",
    ]

    if not topics:
        lines += ["```yaml", "topics: []", "```", ""]
        return "\n".join(lines)

    lines += ["```yaml", "topics:"]
    for t in sorted(topics.values(), key=lambda x: x["id"]):
        lines.append(f"  - id: {t['id']}")
        lines.append(f"    state: {t['state']}")
        if t["state"] != "finalized":
            lines.append(f"    rungs: {t['rungs']}")
            lines.append(f"    last_updated: {t['last_updated']}")
            lines.append(f"    latest: {t['latest']}")
            if t["contributors"]:
                lines.append(f"    contributors: {t['contributors']}")
            if t["linked_topics"]:
                lines.append(f"    linked_topics: {t['linked_topics']}")
        else:
            lines.append(f"    output: {t['output']}")
    lines += ["```", ""]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    all_md = collect_all_md_files()
    errors: list[str] = []

    for directory in (DISTILL_DIR, OUTPUT_DIR):
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.md")):
            if path.name == ".gitkeep":
                continue
            errors.extend(validate_file(path, all_md))

    topics = collect_topic_data()
    STATUS_FILE.write_text(build_status_md(topics), encoding="utf-8")
    print(f"STATUS.md rebuilt ({len(topics)} topic(s)).")

    if errors:
        print("\nValidation errors:")
        for e in errors:
            print(f"  ✗ {e}")
        return 1

    print("All files valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
