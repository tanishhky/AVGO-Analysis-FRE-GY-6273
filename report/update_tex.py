import re

with open('AVGO_Equity_Research_Report.tex', 'r') as f:
    content = f.read()

header_replacement = r'''\begin{tikzpicture}[remember picture,overlay]

% --- Top firm header band (white) ---
\node[anchor=north west,inner sep=0pt]
  at ([xshift=0.6in,yshift=-0.30in]current page.north west) {\includegraphics[height=0.40in]{logo_big.png}};
\node[anchor=north west,text=nyudark,font=\fontsize{10}{12}\itshape,inner sep=0pt]
  at ([xshift=0.6in,yshift=-0.75in]current page.north west) {NYU MSFE Equity Research \textbar{} Initiation of Coverage};

% Date/identifier right
\node[anchor=north east,text=nyugrey,font=\fontsize{10}{12}\sffamily,inner sep=0pt]
  at ([xshift=-0.6in,yshift=-0.30in]current page.north east) {25 April 2026};
\node[anchor=north east,text=nyugrey,font=\fontsize{9}{11}\sffamily,inner sep=0pt]
  at ([xshift=-0.6in,yshift=-0.48in]current page.north east) {Sector: Technology};
\node[anchor=north east,text=nyugrey,font=\fontsize{9}{11}\sffamily,inner sep=0pt]
  at ([xshift=-0.6in,yshift=-0.62in]current page.north east) {Industry: Semiconductors \& Software};

% --- Violet accent stripe ---
\fill[nyuviolet] ([yshift=-1.0in]current page.north west) rectangle ([yshift=-1.05in]current page.north east);

% --- Black band with ticker (Bloomberg-style) ---
\fill[tickerblack] ([yshift=-1.05in]current page.north west) rectangle ([yshift=-1.95in]current page.north east);

% Ticker block left
\node[anchor=north west,inner sep=0pt]
  at ([xshift=0.6in,yshift=-1.25in]current page.north west) {\includegraphics[height=0.45in]{broadcom_logo.png}};
\node[anchor=north west,text=white,font=\fontsize{28}{34}\bfseries,inner sep=0pt]
  at ([xshift=2.1in,yshift=-1.25in]current page.north west) {AVGO};
\node[anchor=north west,text=white!70,font=\fontsize{10}{12}\sffamily,inner sep=0pt]
  at ([xshift=2.1in,yshift=-1.65in]current page.north west) {NASDAQ \textbar{} BROADCOM INC \textbar{} USD};

% Ticker block right - price + change
\node[anchor=north east,text=white,font=\fontsize{28}{34}\bfseries,inner sep=0pt]
  at ([xshift=-0.6in,yshift=-1.25in]current page.north east) {\$422.76};
\node[anchor=north east,text=accentgreen!70!white,font=\fontsize{12}{14}\bfseries\sffamily,inner sep=0pt]
  at ([xshift=-0.6in,yshift=-1.65in]current page.north east) {\(\blacktriangle\) +32.6\% (30D) \quad +121.6\% (12M)};

% --- Headline ---'''

content = re.sub(r'\\begin\{tikzpicture\}\[remember picture,overlay\].*?% --- Headline ---', header_replacement, content, flags=re.DOTALL)

fancyhead_replacement = r'\\fancyhead\[L\]\{\\raisebox{-0.2\\height\}\{\\includegraphics\[height=12pt\]\{logo_small.png\}\} \\hspace\{4pt\} \\color\{nyuviolet\}\\bfseries\\small Broadcom Inc. (AVGO) \\textbar\{\} Equity Research\}'
content = re.sub(r'\\fancyhead\[L\]\{.*?\}', fancyhead_replacement, content)

with open('AVGO_Equity_Research_Report.tex', 'w') as f:
    f.write(content)
