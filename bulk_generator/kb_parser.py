"""
kb_parser.py — Knowledge Base Parser
Reads all kb/*.md files and returns structured Python dicts for use by the rule engine and LLM adapter.
"""

import re
from pathlib import Path

KB_DIR = Path(__file__).parent.parent / "kb"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_kb() -> dict:
    """Load and parse all KB files. Returns a single unified knowledge base dict."""
    return {
        "skills":      parse_skills(),
        "projects":    parse_projects(),
        "certifs":     parse_certifs(),
        "formation":   parse_formation(),
        "experience":  parse_experience(),
        "langues":     parse_langues(),
        "awards":      parse_awards(),
    }


# ---------------------------------------------------------------------------
# skills.md  (merged competences + logiciels)
# ---------------------------------------------------------------------------

def parse_skills() -> list[dict]:
    """
    Returns a list of skill categories, each with:
      { cv_category, title, domains, keywords, items: [str] }
    """
    text = _read("skills.md")
    categories = []
    current = None

    for line in text.splitlines():
        # New top-level CV category
        m = re.match(r"^## \[CV: (.+?)\]", line)
        if m:
            if current:
                categories.append(current)
            current = {
                "title":       m.group(1).strip(),
                "cv_category": _slugify(m.group(1)),
                "domains":     [],
                "keywords":    [],
                "items":       [],
                "subsections": [],
            }
            continue

        if current is None:
            continue

        # domain / keyword meta-tags
        dm = re.match(r"^>\s*domains:\s*\[(.+?)\]", line)
        if dm:
            current["domains"] = [t.strip() for t in dm.group(1).split(",")]
            continue

        km = re.match(r"^>\s*keywords:\s*\[(.+?)\]", line)
        if km:
            current["keywords"] = [t.strip() for t in km.group(1).split(",")]
            continue

        # Sub-section heading (### ...)
        sm = re.match(r"^### (.+)", line)
        if sm:
            current["subsections"].append(sm.group(1).strip())
            continue

        # Skill item (- ...)
        im = re.match(r"^- (.+)", line)
        if im:
            # Strip the " — description" part, keep just the tool name
            item_full = im.group(1).strip()
            name = item_full.split(" —")[0].split(" \u2014")[0].strip()
            current["items"].append({
                "name":    name,
                "full":    item_full,
                "section": current["subsections"][-1] if current["subsections"] else "",
            })

    if current:
        categories.append(current)

    return categories


# ---------------------------------------------------------------------------
# projects.md
# ---------------------------------------------------------------------------

def parse_projects() -> list[dict]:
    """
    Returns a list of projects:
      { title, role, timeline, domains: [str], tools: [str], description, achievements: [str] }
    """
    text = _read("projects.md")
    projects = []
    current = None

    for line in text.splitlines():
        h2 = re.match(r"^## (.+)", line)
        if h2:
            if current:
                projects.append(current)
            current = {
                "title":        h2.group(1).strip(),
                "role":         "",
                "timeline":     "",
                "domains":      [],
                "tools":        [],
                "description":  "",
                "achievements": [],
            }
            continue

        if current is None:
            continue

        _field(line, "Role", current, "role")
        _field(line, "Timeline", current, "timeline")
        _field(line, "Description", current, "description")

        dm = re.match(r"^- Domain: \[(.+?)\]", line)
        if dm:
            current["domains"] = [t.strip() for t in dm.group(1).split(",")]

        tm = re.match(r"^- Tools used: \[(.+?)\]", line)
        if tm:
            current["tools"] = [t.strip() for t in tm.group(1).split(",")]

        am = re.match(r"^\s{2}-\s+(.+)", line)
        if am and current.get("_in_achievements"):
            current["achievements"].append(am.group(1).strip())

        if re.match(r"^- Key achievements:", line):
            current["_in_achievements"] = True
        elif re.match(r"^- ", line):
            current["_in_achievements"] = False

    if current:
        projects.append(current)

    # Clean up private flags
    for p in projects:
        p.pop("_in_achievements", None)

    return projects


# ---------------------------------------------------------------------------
# certif.md
# ---------------------------------------------------------------------------

def parse_certifs() -> list[dict]:
    """
    Returns a list of certifications:
      { title, issuer, year, keywords: [str] }
    """
    text = _read("certif.md")
    certifs = []
    current = None

    for line in text.splitlines():
        h2 = re.match(r"^## (.+)", line)
        if h2:
            if current:
                certifs.append(current)
            current = {
                "title":    h2.group(1).strip(),
                "issuer":   "",
                "year":     "",
                "keywords": [],
            }
            continue

        if current is None:
            continue

        _field(line, "Issuer", current, "issuer")
        _field(line, "Year", current, "year")

        km = re.match(r"^- Relevant for: (.+)", line)
        if km:
            current["keywords"] = [t.strip() for t in km.group(1).split(",")]

    if current:
        certifs.append(current)

    return certifs


# ---------------------------------------------------------------------------
# formation.md
# ---------------------------------------------------------------------------

def parse_formation() -> list[dict]:
    """
    Returns a list of degrees:
      { title, school, years, field, modules: [str], note_cv }
    """
    text = _read("formation.md")
    degrees = []
    current = None

    for line in text.splitlines():
        h2 = re.match(r"^## (.+?) — (.+?) \((.+?)\)", line)
        if h2:
            if current:
                degrees.append(current)
            current = {
                "title":    h2.group(1).strip(),
                "school":   h2.group(2).strip(),
                "years":    h2.group(3).strip(),
                "field":    "",
                "modules":  [],
                "note_cv":  "",
            }
            continue

        if current is None:
            continue

        fm = re.match(r"^- Field: (.+)", line)
        if fm:
            current["field"] = fm.group(1).strip()

        nm = re.match(r"^- Note CV : (.+)", line)
        if nm:
            current["note_cv"] = nm.group(1).strip()

        # Modules are listed as "  - Module name"
        mm = re.match(r"^\s{4}-\s+(.+)", line)
        if mm:
            current["modules"].append(mm.group(1).strip())

    if current:
        degrees.append(current)

    return degrees


# ---------------------------------------------------------------------------
# experience.md
# ---------------------------------------------------------------------------

def parse_experience() -> list[dict]:
    text = _read("experience.md")
    experiences = []
    current = None

    for line in text.splitlines():
        h2 = re.match(r"^## (.+)", line)
        if h2:
            if current:
                experiences.append(current)
            current = {
                "title":            h2.group(1).strip(),
                "location":         "",
                "domains":          [],
                "responsibilities": [],
                "tools":            [],
                "subject":          "",
            }
            continue

        if current is None:
            continue

        lm = re.match(r"^- Location: (.+)", line)
        if lm:
            current["location"] = lm.group(1).strip()

        dm = re.match(r"^- Domain: \[(.+?)\]", line)
        if dm:
            current["domains"] = [t.strip() for t in dm.group(1).split(",")]

        sm = re.match(r"^- Subject: (.+)", line)
        if sm:
            current["subject"] = sm.group(1).strip()

        rm = re.match(r"^\s{2}-\s+(.+)", line)
        if rm and current.get("_in_resp"):
            current["responsibilities"].append(rm.group(1).strip())

        tm = re.match(r"^- Tools used: \[(.+?)\]", line)
        if tm:
            current["tools"] = [t.strip() for t in tm.group(1).split(",")]
            current["_in_resp"] = False

        if re.match(r"^- Responsibilities:", line):
            current["_in_resp"] = True
        elif re.match(r"^- (?!Responsibilities)", line):
            current["_in_resp"] = False

    if current:
        experiences.append(current)

    for e in experiences:
        e.pop("_in_resp", None)

    return experiences


# ---------------------------------------------------------------------------
# langues.md
# ---------------------------------------------------------------------------

def parse_langues() -> list[dict]:
    text = _read("langues.md")
    langues = []
    current = None

    for line in text.splitlines():
        h2 = re.match(r"^## (.+)", line)
        if h2:
            if current:
                langues.append(current)
            current = {"language": h2.group(1).strip(), "level": "", "certif": ""}
            continue

        if current is None:
            continue

        lm = re.match(r"^- Level: (.+)", line)
        if lm:
            current["level"] = lm.group(1).strip()

        cm = re.match(r"^- Certifications: (.+)", line)
        if cm:
            current["certif"] = cm.group(1).strip()

    if current:
        langues.append(current)

    return langues


# ---------------------------------------------------------------------------
# awards.md
# ---------------------------------------------------------------------------

def parse_awards() -> list[dict]:
    text = _read("awards.md")
    awards = []
    current = None

    for line in text.splitlines():
        h2 = re.match(r"^## (.+)", line)
        if h2:
            if current:
                awards.append(current)
            current = {"title": h2.group(1).strip(), "organizer": "", "year": "", "description": ""}
            continue

        if current is None:
            continue

        _field(line, "Organizer", current, "organizer")
        _field(line, "Year", current, "year")
        _field(line, "Description", current, "description")

    if current:
        awards.append(current)

    return awards


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read(filename: str) -> str:
    path = KB_DIR / filename
    return path.read_text(encoding="utf-8")


def _field(line: str, key: str, target: dict, field: str):
    m = re.match(rf"^- {re.escape(key)}: (.+)", line)
    if m:
        target[field] = m.group(1).strip()


def _slugify(text: str) -> str:
    import unicodedata
    # Normalize accents (e.g. é -> e)
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    # Replace & with nothing or just let it be stripped
    text = re.sub(r"[^a-z0-9_]", "_", text.lower().strip()).strip("_")
    # Collapse multiple underscores
    text = re.sub(r"_+", "_", text)
    return text
