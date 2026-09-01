import subprocess

tex = r"""\documentclass{article}
\usepackage{fontspec}
\usepackage{xcolor}
\usepackage{stackengine}
\definecolor{SwaraRed}{HTML}{c62828}
\definecolor{ModifierDarkBlue}{HTML}{002171}

\newfontfamily\malayalamfont[Scale=1.0, Script=Malayalam, Path=fonts/]{NotoSerifMalayalam-Regular.ttf}
\newfontfamily\swarafont[Scale=0.68, Script=Grantha, Path=fonts/]{JaimineeyaSwara.ttf}

\newcommand{\swarastack}[2]{%
  \stackengine{5.8pt}{\vphantom{\malayalamfont തീ}#1}{\raisebox{0pt}[\height][0pt]{#2}}{O}{c}{F}{T}{S}%
}

\begin{document}
\large

\noindent \textbf{Mantrakshara Modifiers (Dark Blue) + Swara Markers (Red Bold):}

\vspace{1.5em}
1. Subsection 3: \texttt{Ruhaa(Paa)(A) Aa-i-sho(Pha-II)(G)}\\
\swarastack{\malayalamfont ൠഹാ\rlap{\swarafont \textcolor{ModifierDarkBlue}{\raisebox{1.5ex}{\hspace{-0.8em}\char"E004}}}}{\swarafont \bfseries \textcolor{SwaraRed}{𑌪𑌾}} \quad
\swarastack{\malayalamfont ആഇഷോ\rlap{\swarafont \textcolor{ModifierDarkBlue}{\raisebox{-0.3ex}{\char"E003}}}}{\swarafont \bfseries \textcolor{SwaraRed}{}}

\vspace{1.5em}
2. Subsection 1: \texttt{O(Ta)(C) Taa(Ca)(H) Saa(Tta)\_ Tsaa(Tta).}\\
\swarastack{\malayalamfont ഓ\rlap{\swarafont \textcolor{ModifierDarkBlue}{\raisebox{0.30ex}{\hspace{0.05em}\char"E001}}}}{\swarafont \bfseries \textcolor{SwaraRed}{𑌤}} \quad
\swarastack{\malayalamfont താ\rlap{\swarafont \textcolor{ModifierDarkBlue}{\raisebox{1.5ex}{\char"E002}}}}{\swarafont \bfseries \textcolor{SwaraRed}{𑌚}} \quad
\swarastack{\malayalamfont സാ\_}{\swarafont \bfseries \textcolor{SwaraRed}{𑌟}} \quad
\swarastack{\malayalamfont ത്സാ.}{\swarafont \bfseries \textcolor{SwaraRed}{𑌟}}

\vspace{1.5em}
3. Subsection 4: \texttt{Ho(Kha)(A) Baa(Bha-II)(G) Ho(Bha-II)(D)}\\
\swarastack{\malayalamfont ഹോ\rlap{\swarafont \textcolor{ModifierDarkBlue}{\raisebox{1.5ex}{\char"E004}}}}{\swarafont \bfseries \textcolor{SwaraRed}{𑌖}} \quad
\swarastack{\malayalamfont ബാ\rlap{\swarafont \textcolor{ModifierDarkBlue}{\raisebox{-0.3ex}{\char"E003}}}}{\swarafont \bfseries \textcolor{SwaraRed}{}} \quad
\swarastack{\malayalamfont ഹോ\rlap{\swarafont \textcolor{ModifierDarkBlue}{\raisebox{1.5ex}{\char"E006}}}}{\swarafont \bfseries \textcolor{SwaraRed}{}}

\end{document}
"""

with open('test_mantrakshara_modifiers.tex', 'w', encoding='utf-8') as f:
    f.write(tex)

subprocess.run(['xelatex', '-interaction=nonstopmode', 'test_mantrakshara_modifiers.tex'])
subprocess.run(['pdftoppm', '-png', '-r', '250', 'test_mantrakshara_modifiers.pdf', 'test_mantrakshara_modifiers_out'])
print('Rendered test_mantrakshara_modifiers_out!')
