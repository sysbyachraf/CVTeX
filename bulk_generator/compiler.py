"""
compiler.py — pdflatex compilation wrapper
Compiles .tex files into PDFs and writes 4 files into offres/[Company]/ folder.
Checks CV is exactly 1 page.
"""

import subprocess
import shutil
import tempfile
import re
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).parent.parent
OFFRES_DIR     = WORKSPACE_ROOT / "offres"
PDFLATEX       = "pdflatex"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compile_offer(job_id: str, company: str, cv_tex: str, lettre_tex: str) -> dict:
    """
    Compile CV and letter .tex strings to PDFs.
    Writes 4 files into offres/[company_slug]/:
      CV_Achraf_Izelmadene.tex / .pdf
      Lettre_Achraf_Izelmadene.tex / .pdf

    Returns:
      { success: bool, folder: str, cv_pages: int, overflow: bool, error: str }
    """
    company_slug = _slugify(company)
    out_dir = OFFRES_DIR / company_slug
    out_dir.mkdir(parents=True, exist_ok=True)

    cv_tex_path     = out_dir / "CV_Achraf_Izelmadene.tex"
    lettre_tex_path = out_dir / "Lettre_Achraf_Izelmadene.tex"
    cv_pdf_path     = out_dir / "CV_Achraf_Izelmadene.pdf"
    lettre_pdf_path = out_dir / "Lettre_Achraf_Izelmadene.pdf"

    # Write .tex source files
    cv_tex_path.write_text(cv_tex, encoding="utf-8")
    lettre_tex_path.write_text(lettre_tex, encoding="utf-8")

    # Compile in temp dir (avoids polluting output folder with aux files)
    cv_ok,     cv_err     = _compile(cv_tex_path,     cv_pdf_path)
    lettre_ok, lettre_err = _compile(lettre_tex_path, lettre_pdf_path)

    if not cv_ok:
        return {"success": False, "folder": str(out_dir), "error": cv_err}
    if not lettre_ok:
        return {"success": False, "folder": str(out_dir), "error": lettre_err}

    # Check page count
    cv_pages = _count_pages(cv_pdf_path)
    overflow = cv_pages > 1

    return {
        "success":  True,
        "folder":   str(out_dir),
        "cv_pages": cv_pages,
        "overflow": overflow,
        "error":    "",
    }


# ---------------------------------------------------------------------------
# Internal
# ---------------------------------------------------------------------------

def _compile(tex_path: Path, pdf_dest: Path) -> tuple[bool, str]:
    """Compile a single .tex file → .pdf using a temp directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        # Copy .tex + workspace .cls and assets into temp dir
        shutil.copy(tex_path, tmp / tex_path.name)

        # Copy required class files
        for cls in ["altacv.cls", "PlushCV.cls"]:
            src = WORKSPACE_ROOT / cls
            if src.exists():
                shutil.copy(src, tmp / cls)

        # Copy assets folder (photo)
        assets_src = WORKSPACE_ROOT / "assets"
        if assets_src.exists():
            shutil.copytree(assets_src, tmp / "assets", dirs_exist_ok=True)

        # Copy icons folder
        icons_src = WORKSPACE_ROOT / "icons"
        if icons_src.exists():
            shutil.copytree(icons_src, tmp / "icons", dirs_exist_ok=True)

        # Run pdflatex twice (for cross-refs)
        for _ in range(2):
            result = subprocess.run(
                [PDFLATEX, "-interaction=nonstopmode", tex_path.name],
                cwd=tmp,
                capture_output=True,
                text=True,
                timeout=60,
            )

        compiled_pdf = tmp / tex_path.with_suffix(".pdf").name
        if compiled_pdf.exists():
            shutil.copy(compiled_pdf, pdf_dest)
            return True, ""
        else:
            # Return last 30 lines of log for debugging
            log_file = tmp / tex_path.with_suffix(".log").name
            error_text = ""
            if log_file.exists():
                lines = log_file.read_text(encoding="utf-8", errors="replace").splitlines()
                error_text = "\n".join(lines[-30:])
            return False, error_text or result.stderr


def _count_pages(pdf_path: Path) -> int:
    """Count PDF pages using pypdf (no external dependency on pdfinfo)."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(pdf_path))
        return len(reader.pages)
    except Exception:
        return -1  # unknown


def _slugify(text: str) -> str:
    """Convert company name to a safe folder name."""
    slug = re.sub(r"[^\w\s-]", "", text).strip()
    slug = re.sub(r"[\s_-]+", "_", slug)
    return slug
