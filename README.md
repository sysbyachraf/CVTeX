# CVTeX — Achraf Izelmadene

> Automated LaTeX CV & Cover Letter Generation Workspace, Knowledge Base, and Web Bulk Generator.

---

## 📌 Project Overview

**CVTeX** is a self-contained, portable workspace designed for generating highly tailored, ATS-compliant Curriculum Vitae (CV) and Cover Letters (Lettres de Motivation) in French.

The repository includes:
- **LaTeX Templates**: ATS 1-page CV template, modern visual template, and cover letter models based on `altacv.cls`.
- **Knowledge Base (`kb/`)**: The authoritative Single Source of Truth (SSOT) detailing verified projects, skills, formations, internships, and certifications.
- **Bulk Generator Web App (`bulk_generator/`)**: A Flask web application integrating with Gemini AI to automate offer parsing, candidate-job matching, and `.tex` generation.
- **AI Agent Directives (`SKILL.md`, `agent.md`, `optimisation_*.md`)**: Strict guidelines for AI coding assistants working in this repository.

---

## 🚀 First-Time Setup on a New Machine

Follow these steps when checking out or cloning this repository on a fresh PC.

### Prerequisites

1. **Git**: [git-scm.com](https://git-scm.com/)
2. **Python 3.10+**: [python.org](https://www.python.org/)
3. **LaTeX Distribution** (supports `pdflatex` and `xelatex`):
   - **Windows**: [MiKTeX](https://miktex.org/) or [TeX Live](https://tug.org/texlive/)
     > *Note for MiKTeX*: Enable "Always install missing packages on-the-fly" in MiKTeX Console.
   - **Ubuntu/Debian**:
     ```bash
     sudo apt update && sudo apt install texlive-latex-extra texlive-fonts-recommended texlive-xetex latexmk
     ```
   - **macOS**: [MacTeX](https://www.tug.org/mactex/)

---

### Step 1: Clone the Repository

```bash
git clone https://github.com/sysbyachraf/CVTeX.git
cd CVTeX
```

---

### Step 2: Setup Python Virtual Environment for `bulk_generator`

The `bulk_generator` application requires Python dependencies:

```bash
cd bulk_generator

# Create virtual environment
python -m venv .venv

# Activate environment
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### Step 3: Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Edit `.env` to insert your Gemini API Key:
   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   ```

---

### Step 4: Run the Bulk Generator App (Optional / Web UI)

From within the `bulk_generator/` folder (with `.venv` active):

```bash
python app.py
```

Open your browser and navigate to: `http://127.0.0.1:5000`

---

### Step 5: Verify LaTeX Compilation

Test that your local LaTeX engine compiles documents properly:

```bash
# Return to repository root if inside bulk_generator
cd ..

# Test compiling the ATS CV (must compile to exactly 1 page)
pdflatex -interaction=nonstopmode cv_ats.tex

# Test compiling the cover letter
pdflatex -interaction=nonstopmode lettre_model.tex
```

Clean up auxiliary files after testing:
```powershell
# Windows PowerShell
Remove-Item *.aux, *.log, *.out, *.bcf, *.run.xml, *.synctex.gz -ErrorAction SilentlyContinue
```

---

## 🤖 Instructions for AI Assistants (Agent Onboarding)

When an AI agent (Gemini, Antigravity, Claude, ChatGPT, etc.) operates in this repository, it **MUST** adhere to the following rules:

### 1. The Single Source of Truth (`kb/`)
- All candidate data (projects, tech stack, dates, formations, awards, languages) **MUST strictly come from `/kb/`**.
- **HALLUCINATION IS STRICTLY FORBIDDEN**: Never invent projects, frameworks, past companies, or claims not present in `kb/`.

### 2. Mandatory Reading Before Any Edit
Before tailoring a CV or letter for a specific job offer, you **MUST** read:
1. `SKILL.md`: Main instructions and LaTeX rules.
2. `agent.md`: Workflow protocol (propose before applying).
3. `optimisation_cv.md`: ATS formatting, keyword placement, project selection rules.
4. `optimisation_lettre.md`: Cover letter VOUS → MOI → NOUS structure.

### 3. Application Workflow Protocol
1. **Proposal First**: Present proposed modifications (which projects to highlight, letter paragraphs) to the user before writing final files.
2. **Dedicated Folder**: Once approved, create the application in `offres/[Entreprise]_[Poste]_Application/`.
3. **Strict Naming**:
   - CV file: `CV_Achraf_Izelmadene.tex` & `CV_Achraf_Izelmadene.pdf`
   - Cover Letter file: `Lettre_Achraf_Izelmadene.tex` & `Lettre_Achraf_Izelmadene.pdf`
   - *Do not append the company name to the file names.*
4. **1-Page Rule**: `cv_ats.tex` **MUST strictly fit on 1 page**. If the compiled PDF has 2 pages, adjust vertical spacing, margins, or bullet points.
5. **French Formatting**: All letters and CVs are in French. Dates must be in French (e.g., "août 2026", not "August"). Avoid `\today` if it generates English.
6. **Clean Workspace**: Remove auxiliary compilation artifacts (`.aux`, `.log`, `.bcf`, etc.).

---

## 📂 Repository Directory Layout

```
CVTeX/
├── README.md               ← This onboarding & setup guide
├── SKILL.md                ← AI Agent skill specification & LaTeX guide
├── agent.md                ← Behavioral rules & workflow for AI agents
├── optimisation_cv.md      ← ATS optimization guidelines for the CV
├── optimisation_lettre.md  ← Linguistic and structural guide for cover letters
├── optimisation_photo.md   ← Recommendations regarding photo usage
├── cv_ats.tex              ← Primary ATS 1-page CV template (pdflatex)
├── cv_ats.pdf              ← Pre-compiled reference ATS CV
├── lettre_model.tex        ← Cover letter template (pdflatex)
├── altacv.cls              ← LaTeX class for CV and cover letters
├── PlushCV.cls             ← Alternative visual LaTeX CV class (xelatex)
├── assets/                 ← Candidate official photo and fonts
├── icons/                  ← Social icons (LinkedIn, mail, phone)
│
├── kb/                     ← Knowledge Base (SINGLE SOURCE OF TRUTH)
│   ├── README.md           ← Overview of candidate profile
│   ├── projects.md         ← Verified technical projects
│   ├── skills.md           ← Validated technical skills & tools
│   ├── experience.md       ← Professional internships & roles
│   ├── formation.md        ← Academic background & degrees
│   ├── certif.md           ← Certifications & accreditations
│   ├── awards.md           ← Hackathons & honors
│   ├── academic.md         ← Academic coursework details
│   └── langues.md          ← Language proficiency levels
│
├── bulk_generator/         ← Python/Flask Web Application
│   ├── app.py              ← Main Flask application entrypoint
│   ├── compiler.py         ← Automates pdflatex background compilation
│   ├── rule_engine.py      ← Matchmaking rules & project selection
│   ├── kb_parser.py        ← Markdown parser for kb/
│   ├── llm_adapter.py      ← Gemini LLM integration for tailoring
│   ├── requirements.txt    ← Python package dependencies
│   ├── .env.example        ← Template for environment variables
│   ├── templates/          ← HTML UI and Jinja-LaTeX templates
│   └── static/             ← Frontend assets (CSS, JS)
│
└── offres/                 ← Generated applications per company/role
    ├── Alstom_LiDAR_Application/
    ├── Amplitude_Industrialisation_Application/
    ├── Analog_Way_Embarque_Application/
    └── Assystem_SII_Application/
```

---

## 🛠️ Quick Commands Reference

| Task | Command |
|---|---|
| Compile CV | `pdflatex -interaction=nonstopmode cv_ats.tex` |
| Compile Letter | `pdflatex -interaction=nonstopmode lettre_model.tex` |
| Activate Python venv (Windows) | `bulk_generator\.venv\Scripts\Activate.ps1` |
| Run Bulk Generator App | `python bulk_generator/app.py` |
| Check Git status | `git status` |
| Push to GitHub | `git push origin main` |

---

## 👤 Candidate Profile

- **Name**: Achraf Izelmadene
- **Field**: Electrical Engineering & Embedded Intelligent Systems (Génie Électrique et Systèmes Intelligents)
- **School**: EMSI Marrakech (Final Year / PFE) & FSSM (Licence)

- **À propos de moi (Profil) Guidelines**:
  La rubrique « À propos de moi » doit être conçue comme une accroche et doit donner envie à la personne qui lira votre CV de se pencher sur le reste de votre candidature et d'aller voir plus en détail vos compétences et expériences.
  La rubrique « À propos de moi » de votre CV doit permettre au recruteur de se faire une idée de votre profil en quelques secondes.
  La rubrique « À propos de moi » de votre CV peut vous aider à y parvenir.
