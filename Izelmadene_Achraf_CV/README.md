# Modèles de CV par Profil — Achraf Izelmadene

Ce dossier regroupe les 6 profils cibles d'ingénierie GESI. Chaque sous-dossier contient un CV prêt à l'emploi nommé `Izelmadene_Achraf_CV.tex` et son PDF compilé `Izelmadene_Achraf_CV.pdf` (strictement 1 page A4).

## Architecture & Système de Style

- **`cv_style.tex`** : Fichier de style unique centralisant la mise en page, les couleurs, les marges, l'en-tête, les coordonnées, les langues et les activités. Toute modification de design faite ici s'applique automatiquement à tous les profils.
- **`altacv.cls`** : Classe LaTeX AltaCV commune.

## Les 7 Profils

| N° | Dossier | Profil Cible | Projets & Compétences Phares |
|---|---|---|---|
| **1** | [`1_Generaliste/`](1_Generaliste/) | **Généraliste GESI** (candidatures spontanées, offres mixtes) | Agriculture IoT (5★), AutoML (4★), Smartgrid (4★) |
| **2** | [`2_Energie_Electrotechnique/`](2_Energie_Electrotechnique/) | **Énergie & Électrotechnique** (bureau d'études, HTA/BT, PV) | Smartgrid (4★), SmartStruct COCIA'26 (2★), Gradateur HIL (3★) |
| **3** | [`3_Automatisme_Info_Industrielle/`](3_Automatisme_Info_Industrielle/) | **Automatisme & Informatique Industrielle** (API, supervision, SCADA) | Gradateur HIL Simulink (3★), Agriculture IoT (5★), Bras PyBullet (3★) |
| **4** | [`4_Maintenance_Fiabilite/`](4_Maintenance_Fiabilite/) | **Maintenance & Fiabilité** (maintenance prédictive, CND, Industrie 4.0) | AutoML TPOT vs Auto-WEKA (4★), Smartgrid (4★), Contrôle Qualité YOLOv8 (2★) |
| **5** | [`5_Embarque_IoT_IIoT/`](5_Embarque_IoT_IIoT/) | **Systèmes Embarqués & IoT / IIoT** (firmware, LoRa, ESP32, capteurs) | Agriculture IoT (5★), Gradateur HIL (3★), SmartStruct IoT (2★) |
| **6** | [`6_Data_IA_EdgeAI/`](6_Data_IA_EdgeAI/) | **Data Science, IA & Edge AI** (séries temporelles, TFLite, MLOps) | AutoML (4★), Smartgrid Clustering (4★), Traduction ASL TFLite (2★) |
| **7** | [`7_Industrie40_TransitionDigitale/`](7_Industrie40_TransitionDigitale/) | **Industrie 4.0 & Transition Digitale** (innovation, maintenance prédictive, digital twin) | AutoML Prédictif (4★), Contrôle Qualité YOLOv8 (2★), Agriculture IoT (5★) |

## Comment postuler à une nouvelle offre ?

1. Choisissez le sous-dossier correspondant le mieux à l'offre.
2. Copiez le sous-dossier dans `offres/<Nom_Entreprise>_Application/`.
3. Ajustez uniquement les 2 lignes `\target{...}` (l'intitulé du poste) et `\apropos{...}` (votre pitch ciblé).
4. Compilez : `/Library/TeX/texbin/pdflatex Izelmadene_Achraf_CV.tex`.
