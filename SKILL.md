---
name: cvtex_izelmadene
description: Self-contained CV workspace for Achraf Izelmadene. Contains 3 CV templates, a letter template, a knowledge base, and offer-specific output folders. Read this skill before any edit.
---

# CVTeX — Achraf Izelmadene

Self-contained, portable workspace for all CV and cover letter production.
Move this folder anywhere — all paths are relative to this root.

---

## Structure

```
CVTeX/
├── cv_ats.tex          ← CV ATS 1-page (pdflatex + altacv.cls) ★ PRIMARY
├── cv_plush.tex        ← CV visuel PlushCV (xelatex + PlushCV.cls)
├── cv_a_propos.tex     ← CV "À propos" (xelatex + PlushCV.cls)
├── lettre_model.tex    ← Template lettre de motivation (pdflatex + altacv.cls)
├── altacv.cls          ← Classe pour cv_ats + lettre
├── PlushCV.cls         ← Classe pour cv_plush + cv_a_propos
├── assets/
│   ├── photo.jpg       ← Photo officielle (portrait/imageee_small.jpg)
│   └── fonts/          ← Polices pour PlushCV (XeLaTeX)
├── fonts -> assets/fonts  ← Lien symbolique (requis par PlushCV.cls)
├── icons/
│   └── main/           ← Icônes PNG requis par PlushCV (linkedin, mail, phone)
├── kb/                 ← Knowledge Base — SOURCE DE VÉRITÉ
│   ├── projects.md
│   ├── experience.md
│   ├── formation.md
│   ├── certif.md
│   ├── awards.md
│   └── langues.md
├── styles/             ← Configurations couleurs / thèmes réutilisables
│   └── colors.md
├── offres/             ← PDFs finaux uniquement, un dossier par candidature
│   ├── Vinci_Construction_PFE/
│   │   ├── CV_Izelmadene_Achraf.pdf
│   │   └── Lettre_Izelmadene_Achraf.pdf
│   └── [Entreprise_Offre]/
│       └── ...
└── SKILL.md            ← Ce fichier
```

---

## ⚠️ MANDATORY — Before Modifying Any CV or Letter for a Job Offer

**STOP. Before making any changes to adapt the CV or letter for a specific offer, you MUST read and apply these three optimization guides:**

| Guide | Path | Purpose |
|---|---|---|
| CV Optimization | `CVTeX/optimisation_cv.md` | Rules for CV structure, wording, skills section, experiences |
| Letter Optimization | `CVTeX/optimisation_lettre.md` | VOUS-MOI-NOUS framework, signature, linguistic alignment |
| Photo Guidance | `CVTeX/optimisation_photo.md` | Impact of the photo, posture, tone |

### Pre-Edit Checklist (run before every offer-specific modification)
- [ ] Read `optimisation_cv.md` → identify which sections need tailoring to the offer keywords
- [ ] Read `optimisation_lettre.md` → verify the letter follows VOUS → MOI → NOUS structure
- [ ] Check vocabulary alignment between offer text and CV/letter language
- [ ] Select between **2 (minimum) and 3 (maximum)** projects based on relevance and available space.
- [ ] Verify the CV compiles to exactly **1 page** after any edits
- [ ] Place both output PDFs AND their source `.tex` files in `offres/[Entreprise_Offre]/`. **IMPORTANT: Name the files strictly `CV_Achraf_Izelmadene` and `Lettre_Achraf_Izelmadene` (do NOT append the company name).**

### Rédiger la Lettre de Motivation
- [ ] L'Objet doit indiquer le titre du poste SANS les suffixes génériques comme "H/F", "F/H" ou "M/F".
- [ ] Structurer la lettre en 3 parties (MOI, VOUS, NOUS).
  1. **MOI** : Doit OBLIGATOIREMENT commencer par "Actuellement étudiant en dernière année à l'EMSI [de Marrakech] en Génie Électrique et Systèmes Intelligents" (vous pouvez varier légèrement la phrase ou omettre Marrakech). Mentionnez ici *vos* projets (issus de la KB) et liez-les explicitement aux besoins de l'offre.
  2. **VOUS** : L'entreprise et l'offre (pourquoi elle m'intéresse, le lien avec mes compétences).
  3. **NOUS** : Ce que nous allons accomplir ensemble, la valeur ajoutée apportée au poste.

---


## Compilation

### cv_ats.tex (★ CV principal)
```bash
pdflatex -interaction=nonstopmode cv_ats.tex
```
- Engine: `pdflatex`
- Font: Lato (package)
- **MUST compile to 1 page.** If 2 pages → fix overflow before finishing.

### cv_plush.tex / cv_a_propos.tex
```bash
xelatex -interaction=nonstopmode cv_plush.tex
```
- Engine: `xelatex`
- Fonts loaded from `assets/fonts/`

### lettre_model.tex
```bash
pdflatex -interaction=nonstopmode lettre_model.tex
```

---

## Workflow — Nouvelle candidature

1. **Lire l'offre** et identifier les compétences clés demandées
2. **Ouvrir `cv_ats.tex`** (ou le CV approprié selon la cible)
3. **Adapter le contenu** en consultant `kb/` pour les données exactes
4. **Compiler** et vérifier 1 page
5. **Copier le PDF** dans `offres/[Entreprise_Offre]/CV_Izelmadene_Achraf.pdf`
6. **Adapter `lettre_model.tex`**, compiler
7. **Copier le PDF** dans `offres/[Entreprise_Offre]/Lettre_Izelmadene_Achraf.pdf`

> **JAMAIS** de `.tex` dans les dossiers `offres/` — seulement des PDFs.

---

## Règles de contenu (Knowledge Base)

Toute information ajoutée au CV **DOIT** venir de `kb/`. Ne jamais inventer.

| Fichier KB       | Contient                                  |
|------------------|-------------------------------------------|
| `projects.md`    | 6 projets avec outils et résultats        |
| `experience.md`  | 2 stages (Core Engineering + Menara Prefa)|
| `formation.md`   | EMSI ingénieur + Licence FSSM             |
| `certif.md`      | Certifications (DeepLearning.AI, 3DS...) |
| `awards.md`      | Prix hackathons                           |
| `langues.md`     | Niveaux de langue                         |

---

## Compétences validées (cv_ats.tex)

```
Programmation : C/C++, Python, JavaScript, HTML/CSS
Logiciels & CAO : AutoCAD, Caneco BT, PVsyst, Dialux EVO, MATLAB, TIA PORTAL, SolidWorks
Outils & Plateformes : Git, Docker, PyBullet, Arduino, Supabase, 3DEXPERIENCE, Pack Office
IA & MLOps : Scikit-learn, OpenCV, MediaPipe, AutoML, MLOps, GenAIOps
```

> Ne modifier cette liste qu'avec confirmation explicite du candidat.

---

## Design — Couleurs (cv_ats.tex + lettre_model.tex)

| Rôle      | Couleur   | Hex       |
|-----------|-----------|-----------|
| `heading` | Navy      | `#0A2540` |
| `accent`  | Navy      | `#0A2540` |
| `emphasis`| SlateGrey | `#2E2E2E` |
| `body`    | LightGrey | `#666666` |

---

## Projets disponibles (4 actifs dans cv_ats.tex)

1. Smart Agriculture IoT Ecosystem
2. Maintenance Prédictive 4.0 par AutoML
3. Bras Robotique 3 DOF — Jeu d'Échecs
4. Traduction ASL par Vision Artificielle

Projets disponibles en remplacement (dans `kb/projects.md`) :
- Détection d'anomalies Smartgrid (clustering)
- Voiture Télécommandée Arduino

---

## Erreurs à éviter

| Erreur | Conséquence |
|--------|-------------|
| Utiliser `xelatex` pour `cv_ats.tex` | Ne compile pas, mauvaise police |
| Chemin photo `imageee.png` | Fichier absent dans CVTeX, utiliser `assets/photo.jpg` |
| Dépasser 1 page dans `cv_ats.tex` | CV rejeté par ATS |
| Ajouter `.tex` dans `offres/` | Pollue le dossier de sortie |
| Inventer des outils non présents dans `kb/` | Information incorrecte sur le CV |
