# Styles & Couleurs — CVTeX

## Thème actuel : Navy Professional

Utilisé dans `cv_ats.tex` et `lettre_model.tex`.

```latex
\definecolor{Navy}{HTML}{0A2540}
\definecolor{SlateGrey}{HTML}{2E2E2E}
\definecolor{LightGrey}{HTML}{666666}
\colorlet{heading}{Navy}
\colorlet{accent}{Navy}
\colorlet{emphasis}{SlateGrey}
\colorlet{body}{LightGrey}
```

## Thèmes alternatifs disponibles

### Vert Ingénierie (pour candidatures environnement/énergie)
```latex
\definecolor{ForestGreen}{HTML}{1B4332}
\colorlet{heading}{ForestGreen}
\colorlet{accent}{ForestGreen}
```

### Bordeaux Premium (pour candidatures grands groupes)
```latex
\definecolor{Burgundy}{HTML}{6B2737}
\colorlet{heading}{Burgundy}
\colorlet{accent}{Burgundy}
```

### Anthracite Neutre (universel, très ATS-safe)
```latex
\definecolor{Anthracite}{HTML}{1C1C1C}
\colorlet{heading}{Anthracite}
\colorlet{accent}{Anthracite}
```

---

## Typographie

- **cv_ats.tex + lettre_model.tex** : Lato (via `\usepackage[default]{lato}`)
- **cv_plush.tex + cv_a_propos.tex** : Inter/SourceSansPro (via `fontspec` + `assets/fonts/`)

---

## Section `\cvsection` — Style inline (cv_ats.tex)

Le titre et la ligne horizontale sont sur la même ligne pour économiser de l'espace :

```latex
\renewcommand{\cvsection}[2][]{%
  \medskip%
  {\color{heading}\LARGE\bfseries #2 \hspace{0.2em}\leaders\vrule height 4pt depth -2pt\hfill\mbox{}}\par\smallskip
}
```

> Ne pas remettre `\MakeUppercase` — ça casse l'alignement et gaspille une ligne.
