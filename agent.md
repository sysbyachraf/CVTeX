# Agent Workflow Instructions

## 1. Proposition avant exécution
L'agent ne doit jamais créer ou modifier de fichiers finaux (CV, Lettre de motivation) sans l'accord préalable de l'utilisateur.
Pour chaque nouvelle offre ou demande d'adaptation :
- L'agent doit d'abord générer une proposition (brouillon) des modifications qu'il souhaite apporter au texte (ex: rubriques modifiées, nouveaux paragraphes de la lettre).
- L'agent soumet cette proposition à l'utilisateur pour validation.

## 2. Création dans un dossier séparé
- Une fois que l'utilisateur a approuvé la proposition (ou apporté ses corrections), l'agent doit générer les fichiers définitifs (`.tex`) dans un dossier séparé et dédié à cette offre (ex: `Nom_Entreprise_Application/`).

## 3. Rigueur et respect du modèle
- L'agent ne doit pas modifier la structure de base ni les intitulés des catégories du modèle original (`cv_ats.tex` ou de l'image de référence) à moins que cela ne soit explicitement demandé.

## 4. Single Source of Truth (/kb)
- Toutes les informations (compétences, expériences, formations, projets) doivent être puisées UNIQUEMENT dans les fichiers du dossier `/kb/`. L'agent n'a pas le droit d'inventer ou de modifier les faits sans que le fichier source dans `/kb/` ne soit mis à jour en premier.

## 5. Rendu Final et Organisation
- **Isolation et nommage** : Tout nouveau projet de candidature (ex: Santerne, Citeos) doit être créé dans son propre sous-dossier au sein de `CVTeX` (ex: `Citeos_Application`). Les fichiers finaux à l'intérieur de ces dossiers doivent obligatoirement être nommés `CV_Achraf_Izelmadene.tex` et `Lettre_Achraf_Izelmadene.tex` pour un rendu PDF professionnel et constant.
- **Propreté du dossier** : L'agent doit veiller à garder le dossier propre. Tous les fichiers de compilation auxiliaires générés (ex: `.aux`, `.log`, `.out`, `.fls`) doivent être supprimés ou déplacés dans un dossier `out/` après une compilation réussie, afin de ne laisser que le `.tex` et le `.pdf` visibles à la racine du sous-dossier.
- L'agent doit toujours s'assurer que les dates, l'année d'étude et le type de stage (ex: 5ème année, PFE) sont corrects et cohérents dans tous les documents.
- **Convention des dates** : Les lettres et les CV étant rédigés en français, l'agent doit explicitement s'assurer que les dates générées sont en français (par exemple, écrire "août" et non "August"). Il faut éviter d'utiliser `\today` si l'environnement LaTeX par défaut génère la date en anglais.
