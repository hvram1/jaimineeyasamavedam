import subprocess

tex = r"""\documentclass{article}
\usepackage{fontspec}
\usepackage{xcolor}
\usepackage{stackengine}
\definecolor{SwaraRed}{HTML}{c62828}
\definecolor{ModifierGreen}{HTML}{2e7d32}

\newfontfamily\malayalamfont[Scale=1.0, Script=Malayalam, Path=fonts/]{NotoSerifMalayalam-Regular.ttf}
\newfontfamily\swarafont[Scale=0.68, Script=Grantha, Path=fonts/]{JaimineeyaSwara.ttf}

\newcommand{\swarastack}[2]{%
  \stackengine{5.8pt}{\vphantom{തീ}#1}{\raisebox{0pt}[\height][0pt]{#2}}{O}{c}{F}{T}{S}%
}

\begin{document}
\large

Comparison of Swarita top-alignment to swara letter baseline:

1. Using raisebox{-\height}:\\
\swarastack{\malayalamfont ദാ}{\swarafont \bfseries \textcolor{SwaraRed}{𑌚𑌿}\textcolor{ModifierGreen}{\raisebox{-\height}{|}}} \quad
\swarastack{\malayalamfont താ}{\swarafont \bfseries \textcolor{SwaraRed}{𑌚}\textcolor{ModifierGreen}{\raisebox{-\height}{|}}}

\vspace{1.5em}
2. Using phrasing danda \uE002:\\
\swarastack{\malayalamfont ദാ}{\swarafont \bfseries \textcolor{SwaraRed}{𑌚𑌿}\textcolor{ModifierGreen}{\char"E002}} \quad
\swarastack{\malayalamfont താ}{\swarafont \bfseries \textcolor{SwaraRed}{𑌚}\textcolor{ModifierGreen}{\char"E002}}

\vspace{1.5em}
3. Using raisebox{-1.4ex}:\\
\swarastack{\malayalamfont ദാ}{\swarafont \bfseries \textcolor{SwaraRed}{𑌚𑌿}\textcolor{ModifierGreen}{\raisebox{-1.4ex}{|}}} \quad
\swarastack{\malayalamfont താ}{\swarafont \bfseries \textcolor{SwaraRed}{𑌚}\textcolor{ModifierGreen}{\raisebox{-1.4ex}{|}}}

\end{document}
"""

with open('test_swarita_align.tex', 'w', encoding='utf-8') as f:
    f.write(tex)

subprocess.run(['xelatex', '-interaction=nonstopmode', 'test_swarita_align.tex'])
subprocess.run(['pdftoppm', '-png', '-r', '250', 'test_swarita_align.pdf', 'test_swarita_align_out'])
print('Rendered test_swarita_align_out!')
