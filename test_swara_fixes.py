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

1. Grantha consonant clusters (no dotted circles):\\
{\swarafont \bfseries \textcolor{SwaraRed}{𑌥𑌾𑌚𑍍}} \quad {\swarafont \bfseries \textcolor{SwaraRed}{𑌟𑌾}} \quad {\swarafont \bfseries \textcolor{SwaraRed}{𑌟𑌿}}

\vspace{1em}
2. Swarita top-aligned to bottom of swara letter baseline:\\
\swarastack{\malayalamfont ദാ}{\swarafont \bfseries \textcolor{SwaraRed}{𑌚𑌿}\textcolor{ModifierGreen}{\raisebox{-1.0ex}{|}}} \quad
\swarastack{\malayalamfont താ}{\swarafont \bfseries \textcolor{SwaraRed}{𑌚}\textcolor{ModifierGreen}{\raisebox{-1.0ex}{|}}} \quad
\swarastack{\malayalamfont താ}{\swarafont \bfseries \textcolor{SwaraRed}{𑌚}\textcolor{ModifierGreen}{\char"E002}}

\vspace{1em}
3. Wide underbar underneath akshara:\\
\swarastack{\malayalamfont യാ\rlap{\swarafont \bfseries \textcolor{ModifierGreen}{\raisebox{-0.2ex}{\char"E007}}}}{\swarafont \bfseries \textcolor{SwaraRed}{𑌟𑌾}} \quad
\swarastack{\malayalamfont യാ\rlap{\swarafont \bfseries \textcolor{ModifierGreen}{\char"E007}}}{\swarafont \bfseries \textcolor{SwaraRed}{𑌟𑌾}}

\end{document}
"""

with open('test_swara_fixes.tex', 'w', encoding='utf-8') as f:
    f.write(tex)

subprocess.run(['xelatex', '-interaction=nonstopmode', 'test_swara_fixes.tex'])
subprocess.run(['pdftoppm', '-png', '-r', '250', 'test_swara_fixes.pdf', 'test_swara_fixes_out'])
print('Rendered test_swara_fixes_out!')
