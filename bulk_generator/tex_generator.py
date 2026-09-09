r"""
tex_generator.py — LaTeX file generator via Jinja2
Fills CV and letter templates with data from the rule engine and LLM adapter.

CV template uses << >> delimiters to avoid conflicts with LaTeX { } braces.

Sections generated dynamically (everything else is hardcoded in the template):
  - tagline          : offer job title
  - profil           : LLM accroche paragraph
  - projects         : 2-4 selected project blocks
  - formation_emsi   : comma-separated EMSI modules (selected per offer)
  - formation_fssm   : comma-separated FSSM modules (selected per offer)
  - skills_table     : tabular block — 3 fixed category titles, dynamic item lists
  - certifs          : certification \item lines

Sections hardcoded in template (never generated):
  - EXPÉRIENCE       : both stages verbatim
  - LANGUES & DIVERS : languages, prizes, hobbies
"""

import re
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = Path(__file__).parent / "templates"

# Use << >> as delimiters to avoid clashing with LaTeX { } and \commands
_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=False,
    variable_start_string="<<",
    variable_end_string=">>",
    block_start_string="<%",
    block_end_string="%>",
    comment_start_string="<#",
    comment_end_string="#>",
    keep_trailing_newline=True,
)

# Fixed CV skill category titles — never changes
_SKILL_CATEGORIES = [
    ("Ingénierie & Outils",        "ingenierie_outils"),
    ("Code & Intelligence",         ["programmation", "ia_data"]),   # merged
    ("Compétences Transversales",   "competences_transversales"),
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def render_cv(cv_data: dict, profil: str) -> str:
    """Render the CV .tex content from the template."""
    tpl = _env.get_template("cv_template.tex")
    return tpl.render(
        tagline         = tex_escape(cv_data["tagline"]),
        profil          = tex_escape(profil),
        projects        = _render_projects(cv_data["projects"]),
        formation_emsi  = _render_formation_modules(cv_data["formation"], school_key="emsi"),
        formation_fssm  = _render_formation_modules(cv_data["formation"], school_key="fssm"),
        skills_table    = _render_skills_table(cv_data["skills"]),
        certifs         = _render_certifs(cv_data["certifs"]),
    )


def render_lettre(cv_data: dict, lettre_body: str, issue_date: str) -> str:
    """Render the cover letter .tex content from the template."""
    tpl = _env.get_template("lettre_template.tex")
    return tpl.render(
        company     = tex_escape(cv_data["offer"].get("company", "")),
        job_title   = tex_escape(cv_data["offer"].get("job_title", "")),
        issue_date  = tex_escape(issue_date),
        lettre_body = _format_lettre_body(lettre_body),
    )


# ---------------------------------------------------------------------------
# Section renderers
# ---------------------------------------------------------------------------

def _render_projects(projects: list) -> str:
    r"""
    Render 2-4 project blocks as raw LaTeX.
    Format mirrors cv_ats.tex exactly:
      {\large\bfseries\color{accent} TITLE}\\[0.05cm]
      \begin{itemize}
        \item bullet1
        \item bullet2
      \end{itemize}
    """
    parts = []
    for p in projects:
        title = tex_escape(p["title"])

        # Use achievements; fall back to splitting description into sentences
        bullets = [a for a in p.get("achievements", []) if a]
        if not bullets and p.get("description"):
            sents = re.split(r"(?<=[.!?])\s+", p["description"].strip())
            bullets = sents[:2]

        bullet_lines = "\n".join(f"  \\item {tex_escape(b)}" for b in bullets[:2])

        parts.append(
            "{\\large\\bfseries\\color{accent} " + title + "}\\\\[0.05cm]\n"
            "\\begin{itemize}\n" +
            bullet_lines + "\n"
            "\\end{itemize}"
        )

    return "\n\n".join(parts)


def _render_formation_modules(degrees: list, school_key: str) -> str:
    """
    Return a comma-separated string of selected modules for one degree.
    school_key: 'emsi' matches EMSI degree; 'fssm' matches FSSM/Licence degree.
    """
    keyword = "Marocaine" if school_key == "emsi" else "Semlalia"
    for deg in degrees:
        if keyword.lower() in deg.get("school", "").lower():
            mods = deg.get("modules", [])
            if mods:
                return tex_escape(", ".join(mods[:6]) + "...")
    return ""


def _render_skills_table(skill_categories: list) -> str:
    r"""
    Render the COMPETENCES tabular block.
    Category TITLES are the 3 fixed ones defined in _SKILL_CATEGORIES.
    The items under each are selected per offer by the rule engine.

    Output format (mirrors cv_ats.tex):
      \begin{tabular}{@{}ll@{}}
      \textbf{Ingénierie & Outils :} & tool1, tool2, tool3 \\[1pt]
      \textbf{Code & Intelligence :} & Python, C/C++, Scikit-learn, Arduino \\[1pt]
      \textbf{Compétences Transversales :} & Gestion de projets, Travail en équipe \\
      \end{tabular}
    """
    # Build a lookup: cv_category_slug → list of item names
    cat_lookup: dict[str, list[str]] = {}
    for cat in skill_categories:
        slug = cat.get("cv_category", "")
        cat_lookup[slug] = [item["name"] for item in cat.get("items", [])]

    rows = []
    for i, (title, slugs) in enumerate(_SKILL_CATEGORIES):
        # Collect items from one or multiple source categories
        items: list[str] = []
        if isinstance(slugs, str):
            items = cat_lookup.get(slugs, [])
        else:
            for s in slugs:
                items += cat_lookup.get(s, [])

        items_str = tex_escape(", ".join(items))
        title_tex = tex_escape(title)
        suffix = r"\\[1pt]" if i < len(_SKILL_CATEGORIES) - 1 else r"\\"
        rows.append(f"\\textbf{{{title_tex} :}} & {items_str} {suffix}")

    return (
        "\\begin{tabular}{@{}ll@{}}\n" +
        "\n".join(rows) + "\n"
        "\\end{tabular}"
    )


def _render_certifs(certifs: list) -> str:
    r"""
    Render certification \item lines — goes inside the \begin{itemize} block
    already present in the template.
    Format mirrors cv_ats.tex:
      \item \textbf{Title} \hfill {\color{emphasis}Issuer}
    """
    lines = []
    for c in certifs:
        title  = tex_escape(c["title"])
        issuer = tex_escape(c.get("issuer", ""))
        year   = c.get("year", "")
        issuer_full = f"{issuer} ({year})" if year else issuer
        lines.append(
            f"  \\item \\textbf{{{title}}} \\hfill {{\\color{{emphasis}}{tex_escape(issuer_full)}}}"
        )
    return "\n".join(lines)


def _format_lettre_body(body: str) -> str:
    """Convert plain-text paragraphs into LaTeX paragraph breaks."""
    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
    return "\n\n\\vspace{0.4cm}\n\n".join(tex_escape(p) for p in paragraphs)


# ---------------------------------------------------------------------------
# LaTeX special character escaping
# ---------------------------------------------------------------------------

_LATEX_SPECIAL = [
    ("&",  r"\&"),
    ("%",  r"\%"),
    ("$",  r"\$"),
    ("#",  r"\#"),
    ("_",  r"\_"),
    ("{",  r"\{"),
    ("}",  r"\}"),
    ("~",  r"\textasciitilde{}"),
    ("^",  r"\textasciicircum{}"),
    ("\\", r"\textbackslash{}"),
]

def tex_escape(text: str) -> str:
    """Escape LaTeX special characters. Safe to call multiple times (idempotent)."""
    if not text:
        return ""
    # Process backslash last to avoid double-escaping \commands already in text
    result = text
    for char, escaped in _LATEX_SPECIAL[:-1]:   # skip backslash for now
        result = result.replace(char, escaped)
    # Backslash: only escape literal backslashes that aren't already LaTeX commands
    # (heuristic: skip sequences already starting with \)
    result = re.sub(r"\\(?![a-zA-Z{])", r"\\textbackslash{}", result)
    return result
