"""
llm_adapter.py — LLM generation via Antigravity SDK
Generates the Profil (accroche) and Lettre de motivation body
using google-antigravity, grounded in the KB data and optimization guides.
"""

import asyncio
import os
import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

# Optimization guide texts (located in docs/)
_GUIDES_DIR = Path(__file__).parent.parent
_DOCS_DIR   = _GUIDES_DIR / "docs"
_CV_FILE    = (_DOCS_DIR / "optimisation_cv.md") if (_DOCS_DIR / "optimisation_cv.md").exists() else (_GUIDES_DIR / "optimisation_cv.md")
_LTR_FILE   = (_DOCS_DIR / "optimisation_lettre.md") if (_DOCS_DIR / "optimisation_lettre.md").exists() else (_GUIDES_DIR / "optimisation_lettre.md")
_OPT_CV     = _CV_FILE.read_text(encoding="utf-8") if _CV_FILE.exists() else ""
_OPT_LTR    = _LTR_FILE.read_text(encoding="utf-8") if _LTR_FILE.exists() else ""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_profil(offer: dict, cv_data: dict) -> str:
    """
    Generate the CV Profil (accroche) paragraph.
    Returns plain text (no LaTeX), max ~4 lines.
    """
    prompt = _profil_prompt(offer, cv_data)
    return _run_async(_ask(prompt))


def generate_lettre(offer: dict, cv_data: dict) -> str:
    """
    Generate the cover letter body (3 paragraphs: VOUS / MOI / NOUS).
    Returns plain text (no LaTeX markup).
    """
    prompt = _lettre_prompt(offer, cv_data)
    return _run_async(_ask(prompt))


def current_french_date() -> str:
    """Return today's date in French, e.g. '27 août 2026'."""
    months = {
        1: "janvier", 2: "février", 3: "mars", 4: "avril",
        5: "mai", 6: "juin", 7: "juillet", 8: "août",
        9: "septembre", 10: "octobre", 11: "novembre", 12: "décembre",
    }
    today = datetime.date.today()
    return f"{today.day} {months[today.month]} {today.year}"


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

def _profil_prompt(offer: dict, cv_data: dict) -> str:
    projects_titles = ", ".join(p["title"] for p in cv_data.get("projects", []))
    skills_flat = "; ".join(
        ", ".join(i["name"] for i in cat["items"])
        for cat in cv_data.get("skills", [])
    )

    return f"""Tu es un expert en rédaction de CV pour ingénieurs.
Tu dois rédiger le paragraphe PROFIL (accroche) du CV d'Achraf Izelmadene pour l'offre suivante.

RÈGLES ABSOLUES:
- Maximum 4 lignes (60-70 mots max)
- Langue: français professionnel
- Mentionner "stage de fin d'études dès le 1er février 2027"
- Si l'entreprise est hors du Maroc: ajouter "Mobile et disponible à me relocaliser"
- Ne pas utiliser d'émojis ni de puces
- Utiliser le vocabulaire exact de l'offre
- Ne jamais inventer de faits non présents dans le profil

OFFRE CIBLE:
- Entreprise: {offer.get('company', '')}
- Poste: {offer.get('job_title', '')}
- Description: {offer.get('job_description', '')[:800]}

PROFIL D'ACHRAF (faits réels uniquement):
- Élève Ingénieur en Génie Électrique et Systèmes Intelligents à l'EMSI Marrakech
- Stage récent: Bureau d'études Core Engineering Solutions — dimensionnement HTA/BT, PV autoconsommation
- Stage précédent: Menara Prefa — migration automate Siemens S7, TIA Portal
- Projets pertinents: {projects_titles}
- Compétences: {skills_flat}
- Hackathons: 1er Prix AISEC Summit 2026, 2ème Prix Vision AI Competition 2026

GUIDE CV (extrait):
{_OPT_CV[:600]}

Réponds UNIQUEMENT avec le texte du paragraphe, sans titre ni balise LaTeX.
"""


def _lettre_prompt(offer: dict, cv_data: dict) -> str:
    projects_str = "\n".join(
        f"- {p['title']}: {p.get('description', '')[:200]}"
        for p in cv_data.get("projects", [])[:3]
    )

    return f"""Tu es un expert en rédaction de lettres de motivation pour ingénieurs.
Tu dois rédiger le CORPS de la lettre de motivation d'Achraf Izelmadene pour l'offre suivante.

STRUCTURE OBLIGATOIRE — 3 paragraphes:
1. VOUS: Montrer que tu comprends les besoins/enjeux de l'entreprise (recherche sur l'entreprise)
2. MOI: Expliquer comment ton profil répond exactement à ces besoins (réalisations concrètes)
3. NOUS: Conclure en sollicitant un entretien de façon proactive

RÈGLES ABSOLUES:
- Langue: français professionnel, soutenu mais naturel
- Toujours mentionner "stage dès le 1er février 2027 pour une durée de 4 à 6 mois"
- Utiliser le vocabulaire exact de l'offre
- Ne jamais inventer de faits
- Ne pas inclure "Madame, Monsieur," ni la formule de politesse finale (déjà dans le template)
- Ne pas utiliser d'émojis
- Chaque paragraphe: 3-4 phrases

OFFRE CIBLE:
- Entreprise: {offer.get('company', '')}
- Poste: {offer.get('job_title', '')}
- Description: {offer.get('job_description', '')[:1200]}

PROFIL D'ACHRAF (faits réels uniquement):
- Élève Ingénieur en Génie Électrique et Systèmes Intelligents, EMSI Marrakech
- Stage Core Engineering Solutions (juil.-août 2026): dimensionnement HTA/BT, schémas unifilaires, PVsyst, AutoCAD, Caneco BT
- Stage Menara Prefa (juil. 2024): migration automate Siemens S7 sous TIA Portal
- Projets sélectionnés:
{projects_str}
- Prix: 1er Hack The Intelligence (AISEC 2026), 2ème Vision AI Competition (EMSI 2026)

GUIDE LETTRE:
{_OPT_LTR}

Réponds UNIQUEMENT avec les 3 paragraphes (séparés par une ligne vide), sans titre ni balise LaTeX.
"""


# ---------------------------------------------------------------------------
# Antigravity SDK async runner
# ---------------------------------------------------------------------------

async def _ask(prompt: str) -> str:
    try:
        from google.antigravity import Agent, LocalAgentConfig
        config = LocalAgentConfig(
            system_instructions="Tu es un expert en rédaction de candidatures professionnelles pour ingénieurs francophones.",
        )
        async with Agent(config) as agent:
            response = await agent.chat(prompt)
            tokens = []
            async for token in response:
                tokens.append(token)
            return "".join(tokens).strip()
    except ImportError:
        # Fallback: if SDK not available, return a placeholder
        return f"[LLM generation unavailable — install google-antigravity and set GEMINI_API_KEY]"
    except Exception as e:
        return f"[LLM error: {e}]"


def _run_async(coro) -> str:
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, coro)
                return future.result()
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)
