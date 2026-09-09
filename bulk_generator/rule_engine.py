"""
rule_engine.py — Keyword-based selection engine
Scores and selects CV sections (projects, certifs, skills, formation modules)
based on overlap between offer keywords and KB item metadata.
"""

import re
from typing import Any


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_cv_data(offer: dict, kb: dict) -> dict:
    """
    Given a parsed offer dict and the full KB, returns a dict of all
    CV sections ready to be fed into tex_generator.py.

    offer keys: company, job_title, job_description, keywords (optional)
    """
    offer_kws = _extract_keywords(offer)

    return {
        "tagline":      _select_tagline(offer),
        "projects":     _select_projects(offer_kws, kb["projects"], max_count=4),
        "certifs":      _select_certifs(offer_kws, kb["certifs"], max_count=4),
        "skills":       _select_skills(offer_kws, kb["skills"]),
        "formation":    _select_formation(offer_kws, kb["formation"]),
        "experience":   kb["experience"],   # always both — no filtering
        "langues":      kb["langues"],
        "awards":       kb["awards"],
        "offer":        offer,
        "offer_kws":    offer_kws,
    }


# ---------------------------------------------------------------------------
# Tagline
# ---------------------------------------------------------------------------

def _select_tagline(offer: dict) -> str:
    """Use the offer job_title as the CV tagline if available."""
    title = offer.get("job_title", "").strip()
    if title:
        # Prefix with standard student marker
        return f"Élève Ingénieur — {title}"
    return "Élève Ingénieur en Génie Électrique et Systèmes Intelligents"


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

def _select_projects(offer_kws: set[str], projects: list[dict], max_count: int = 4) -> list[dict]:
    scored = []
    for p in projects:
        score = _score(offer_kws, _project_terms(p))
        scored.append((score, p))

    scored.sort(key=lambda x: x[0], reverse=True)

    # Always include at least 2, at most max_count
    count = max(2, min(max_count, sum(1 for s, _ in scored if s > 0)))
    # If nothing matches, take the first 2
    if count == 0:
        count = 2

    return [p for _, p in scored[:count]]


def _project_terms(p: dict) -> set[str]:
    terms = set()
    terms.update(_tokenize(p.get("title", "")))
    terms.update(_tokenize(p.get("description", "")))
    for d in p.get("domains", []):
        terms.update(_tokenize(d))
    for t in p.get("tools", []):
        terms.update(_tokenize(t))
    return terms


# ---------------------------------------------------------------------------
# Certifications
# ---------------------------------------------------------------------------

def _select_certifs(offer_kws: set[str], certifs: list[dict], max_count: int = 4) -> list[dict]:
    scored = []
    for c in certifs:
        terms = _tokenize(c.get("title", ""))
        for kw in c.get("keywords", []):
            terms.update(_tokenize(kw))
        score = _score(offer_kws, terms)
        scored.append((score, c))

    scored.sort(key=lambda x: x[0], reverse=True)
    # Take at least 2, at most max_count relevant ones
    count = max(2, min(max_count, sum(1 for s, _ in scored if s > 0)))
    return [c for _, c in scored[:count]]


# ---------------------------------------------------------------------------
# Skills
# ---------------------------------------------------------------------------

def _select_skills(offer_kws: set[str], skill_categories: list[dict]) -> list[dict]:
    """
    For each fixed category, score every item against offer keywords.
    Return up to N most relevant items per category, always keeping at least a minimum.
    """
    result = []
    for cat in skill_categories:
        scored_items = []
        for item in cat.get("items", []):
            item_terms = _tokenize(item["name"]) | _tokenize(item.get("full", ""))
            score = _score(offer_kws, item_terms)
            scored_items.append((score, item))

        # Also score the category's domain/keyword tags
        cat_terms = set()
        for d in cat.get("domains", []):
            cat_terms.update(_tokenize(d))
        for k in cat.get("keywords", []):
            cat_terms.update(_tokenize(k))
        cat_score = _score(offer_kws, cat_terms)

        # Sort items: scored ones first, then remainder
        scored_items.sort(key=lambda x: x[0], reverse=True)

        # Minimum 2 items per category, max 6
        min_items = 2
        max_items = 6
        n = max(min_items, min(max_items, len([s for s, _ in scored_items if s > 0])))
        if n < min_items:
            n = min(min_items, len(scored_items))

        selected = [item for _, item in scored_items[:n]]

        result.append({
            "title":      cat["title"],
            "cv_category": cat["cv_category"],
            "items":      selected,
            "cat_score":  cat_score,
        })

    return result


# ---------------------------------------------------------------------------
# Formation
# ---------------------------------------------------------------------------

def _select_formation(offer_kws: set[str], degrees: list[dict]) -> list[dict]:
    """
    For each degree, select the most relevant modules based on offer keywords.
    The degree list itself is fixed (all degrees shown), only module selection varies.
    """
    result = []
    for deg in degrees:
        # Score each module
        scored_modules = []
        for mod in deg.get("modules", []):
            score = _score(offer_kws, _tokenize(mod))
            scored_modules.append((score, mod))

        scored_modules.sort(key=lambda x: x[0], reverse=True)

        # Pick top modules — target a compact display (max 6 modules shown)
        top_modules = [m for _, m in scored_modules[:6]]

        result.append({
            "title":   deg["title"],
            "school":  deg["school"],
            "years":   deg["years"],
            "field":   deg["field"],
            "modules": top_modules,
            "note_cv": deg.get("note_cv", ""),
        })

    return result


# ---------------------------------------------------------------------------
# Keyword utilities
# ---------------------------------------------------------------------------

def _extract_keywords(offer: dict) -> set[str]:
    """
    Build offer keyword set from the 'keywords' column (if provided)
    plus tokens extracted from job_title and job_description.
    """
    kws: set[str] = set()

    raw_kws = offer.get("keywords", "")
    if raw_kws:
        for kw in raw_kws.split(","):
            kws.update(_tokenize(kw))

    kws.update(_tokenize(offer.get("job_title", "")))
    kws.update(_tokenize(offer.get("job_description", "")))

    # Remove very short / stop words
    stop = {"de", "du", "des", "le", "la", "les", "et", "en", "un", "une",
            "pour", "par", "sur", "avec", "the", "of", "and", "in", "for",
            "to", "a", "an", "is", "are", "at", "on"}
    kws -= stop
    kws = {k for k in kws if len(k) >= 3}
    return kws


def _tokenize(text: str) -> set[str]:
    """Lowercase and split text into word tokens."""
    return set(re.findall(r"[a-zA-ZÀ-ÿ0-9+/#]{2,}", text.lower()))


def _score(offer_kws: set[str], item_terms: set[str]) -> float:
    """Jaccard-like overlap score between offer keywords and item terms."""
    if not offer_kws or not item_terms:
        return 0.0
    intersection = offer_kws & item_terms
    return len(intersection) / len(offer_kws | item_terms)
