# Guide d'Optimisation ATS & Audit de Lisibilité Machine

Ce document résume l'audit de lisibilité par les systèmes de suivi des candidatures (ATS - *Applicant Tracking Systems* : Workday, Taleo, Greenhouse, Lever, etc.) réalisé sur le modèle `cv_v2.pdf`, ainsi que les recommandations techniques pour maximiser le score de parsing.

---

## 1. Résumé de l'Évaluation ATS

- **Score Global :** **88 / 100** (Mention : *Très Bon*)
- **Potentiel après micro-optimisations :** **96+ / 100**
- **Structure :** Monocolonne (idéale pour la lecture séquentielle par les algorithmes).
- **Format :** Strictement 1 page A4 compilée via pdfLaTeX.

| Critère | Note | Évaluation |
| :--- | :---: | :--- |
| **Structure & Flux de lecture** | 19 / 20 | Excellente hiérarchie linéaire de haut en bas sans interférences de colonnes. |
| **Mots-clés Métier (GESI)** | 23 / 25 | Couverture complète : génie électrique (HTA/BT, Caneco, PVsyst, TIA Portal) et IA/IoT (LoRa, ESP32, TFLite, AutoML). |
| **Encodage & Extraction Machine** | 21 / 25 | Texte vectoriel sélectionnable ; quelques artefacts d'espacement et de glyphes à corriger. |
| **Impact & Quantifications** | 25 / 30 | Réalisations techniques claires, pouvant être enrichies d'ordres de grandeur chiffrés. |

---

## 2. Analyse du Flux de Texte Extrait (Simulation Robot)

Lors de l'extraction automatisée par un parser ATS (testé via `pypdf`), le texte brut est lu séquentiellement :

```text
IZELMADENE ACHRAF
Élève Ingénieur en Génie Électrique et Systèmes Intelligents (GESI)
À la recherche d’un stage de fin d’études (PFE) de 6 mois dès février 2027...
Double compétence en génie électrique et en systèmes intelligents...
/ne+212699098736achraf.izelmadene@gmail.com/♀nednachraf-izelmadeneMarrakech, Maroc
FORMATION
École Marocaine des Sciences de l’Ingénieur - Marrakech2025 - Présent
EXPÉRIENCE
Core Engineering Solutions - Berrchid, Casablancajuil. - août 2026
...
```

---

## 3. Les 3 Recommandations Majeures d'Optimisation

### 1. Séparation explicite sur les commandes `\hfill`
* **Problème :** En LaTeX, `\hfill` crée un espacement élastique visuel, mais n'ajoute aucun caractère d'espace dans le flux de caractères PDF. Plusieurs mots se retrouvent ainsi collés dans les parsers basiques :
  - `Marrakech2025` au lieu de `Marrakech 2025`
  - `Casablancajuil.` au lieu de `Casablanca juil.`
  - `maternelleFrançais` au lieu de `maternelle Français`
  - `AutomationLearnQuest` au lieu de `Automation LearnQuest`
  - `BLoisirs` au lieu de `B Loisirs`
* **Solution :** Insérer systématiquement une espace insécable `~` ou un espace `\ ` juste avant chaque `\hfill` :
  ```latex
  % Avant :
  \textbf{Arabe :} Langue maternelle \hfill \textbf{Français :} DELF B2
  % Optimisé ATS :
  \textbf{Arabe :} Langue maternelle~\hfill \textbf{Français :} DELF B2
  ```

### 2. Nettoyage de la Ligne de Contact & Icônes FontAwesome
* **Problème :** 
  - Les glyphes d'icônes `\faPhone` et `\faLinkedin` produisent des artefacts textuels au parsing (`/ne`, `/♀nedn`).
  - L'absence d'espace réel entre le numéro et l'email les fusionne : `+212699098736achraf.izelmadene@gmail.com`.
* **Solution :** 
  - Ajouter des séparateurs textuels réels (ex. `~|~`) ou des espaces insécables entre les champs de contact pour garantir que les regex d'extraction téléphonique et email isolent chaque entité sans ambiguïté.

### 3. Intégration de Mesures d'Impact Chiffrées
* **Problème :** Les modèles d'évaluation ATS les plus récents (et les recruteurs humains) attribuent des points supplémentaires aux puces contenant des données quantitatives.
* **Solution :** Ajouter des ordres de grandeur dès que possible :
  - *Puissance / Dimensionnement :* Indiquer la puissance du transformateur (ex. `poste HTA/BT 630 kVA`) ou de l'installation solaire (`XX kWc`).
  - *Temps / Performance :* Indiquer les gains de latence ou de précision (ex. `précision de 94 %`, `temps de réponse < 50 ms`).

---

## 4. Checklist de Conformité ATS pour CVTeX

- [x] **Mise en page monocolonne** : lecture linéaire naturelle garantie.
- [x] **Titres de sections standardisés** : `FORMATION`, `EXPÉRIENCE`, `PROJETS`, `COMPÉTENCES`, `CERTIFICATIONS`, `LANGUES & DIVERS`.
- [x] **Désactivation des ligatures** : `\DisableLigatures{encoding=*, family=*}` active pour éviter les bugs sur "fi", "fl", "ffi".
- [x] **Format 1 page stricte** : aucun débordement de page.
- [x] **Police compatible unicode** : Lato avec encodage T1.
- [ ] **Espaces de sécurité avant `\hfill`** : à appliquer pour éviter la fusion de mots-clés limitrophes.
- [ ] **Séparateur clair sur les coordonnées** : à appliquer pour une détection infaillible du téléphone et de l'email.
