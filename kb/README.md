# Knowledge Base (KB) — Profile Single Source of Truth

This directory acts as the centralized **Single Source of Truth (SSOT)** for all background details, experiences, certifications, projects, awards, and academic history of **Achraf Izelmadene**.

---

## 📁 File Structure

1. **`formation.md`**  
   Academic degrees (EMSI, FSSM, Baccalaureat), major subjects, and notes on degree inclusion guidelines.

2. **`experience.md`**  
   Professional engineering internships (Production Unit at Ménara Préfa, Engineering Office at Core Engineering Solutions) detailing locations, domains, responsibilities, tools, and achievements.

3. **`projects.md`**  
   Technical engineering projects (Predictive Maintenance 4.0, Robotic Arm Simulation, Smart Agriculture, ASL Translation, Smartgrid Anomaly Detection, Remote-Controlled Car) with roles, tools, and technical highlights.

4. **`certif.md`**  
   Complete repository of professional certifications (Dassault Systèmes 3DEXPERIENCE, Coursera/DeepLearning.AI, Colorado Boulder, etc.).

5. **`awards.md`**  
   Honors and hackathon achievements (Hack The Intelligence, Vision AI Competition).

6. **`skills.md`** ← *replaces the former `competences.md` + `logiciels.md`*  
   Single source for ALL skills and tools, organized into the **4 fixed CV categories**:
   - `[CV: Ingénierie & Outils]` — CAO tools, automatisme, robotique, platforms
   - `[CV: Programmation]` — languages (C/C++, Python, JS, HTML/CSS, SQL)
   - `[CV: IA & Data]` — ML/AI libraries, embedded & IoT hardware
   - `[CV: Compétences Transversales]` — domain know-how + management/soft skills  
   Each section has `cv_category` and `domains/keywords` tags for automated rule-engine matching.

---

## 🎯 Usage Protocol

Any automated agent or human contributor generating or tailoring CVs, cover letters (`Lettre_motivation`), or application portfolios **MUST**:

1. Consult this `kb/` folder as the ground truth before editing any LaTeX document (`cv.tex`, `Lettre_motivation_*.tex`).
2. Use `skills.md` (not the deleted `competences.md`/`logiciels.md`) for all skill selection.
3. Selectively filter and highlight relevant experiences, tools, and projects based on the target job offer profile (e.g., Automatisme vs. Bureau d'Études vs. AI/IoT).
4. Update these Markdown files whenever a new certification, project, or professional milestone is completed.