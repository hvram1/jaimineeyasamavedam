import subprocess

tex = r"""\documentclass{article}
\usepackage{fontspec}
\usepackage{xcolor}
\newfontfamily\swarawithbold[Scale=0.8, Script=Grantha, AutoFakeBold=2.0, Path=fonts/]{JaimineeyaSwara.ttf}
\newfontfamily\swaranobold[Scale=0.8, Script=Grantha, Path=fonts/]{JaimineeyaSwara.ttf}
\begin{document}
With FakeBold: {\swarawithbold \char"11325\char"1133E\char"1131A\char"1134D}

Without FakeBold: {\swaranobold \char"11325\char"1133E\char"1131A\char"1134D}
\end{document}
"""

with open('test_shaping.tex', 'w', encoding='utf-8') as f:
    f.write(tex)

res = subprocess.run(['xelatex', '-interaction=nonstopmode', 'test_shaping.tex'], capture_output=True, text=True)
print(res.stdout[-400:])
subprocess.run(['pdftoppm', '-png', '-r', '200', 'test_shaping.pdf', 'test_shaping_out'])
print('Generated test_shaping_out!')
