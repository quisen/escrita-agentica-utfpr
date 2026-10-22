# Quadros

Instruções para o agente: execute a inclusão e confira o PDF. A pessoa autora fornece o material e decide sobre o conteúdo.

Use para organizar conteúdo textual: categorias, critérios, sínteses de leituras e cronogramas. Dados predominantemente numéricos ficam em `tabelas/`.

Um quadro curto pode ficar no capítulo. Se dificultar a leitura do código, salve o bloco em `quadros/quadro-criterios.tex` e inclua no capítulo com `\input{quadros/quadro-criterios}`. Caminhos são relativos à pasta `latex/`.

```tex
\begin{tabframed}[htb]
  \centering
  \caption{Critérios de seleção}
  \label{quad:criterios}
  \begin{tabular}{|p{0.25\textwidth}|p{0.60\textwidth}|}
    \hline
    \textbf{Critério} & \textbf{Definição} \\
    \hline
    Disponibilidade & Texto integral disponível para leitura. \\
    \hline
  \end{tabular}
  \fonte{elaboração própria}
\end{tabframed}
```

A classe usa `tabframed` para quadros. Cite no texto com `Quadro~\ref{quad:criterios}` e não escreva o número manualmente. A fonte deve identificar a origem real da síntese.

Para quadros de várias páginas, use `longtable` com `\renewcommand{\LTcaptype}{tabframed}`. Nesse caso, agrupe a configuração entre `\begingroup` e `\endgroup`, repita o cabeçalho com `\endfirsthead` e `\endhead`, e não envolva a tabela longa em `tabframed`. Coloque a fonte após o ambiente. Evite reduzir todo o quadro com `\resizebox` se isso prejudicar a leitura.

Confira quebras e margens no PDF. Se precisar de lista de quadros, inclua `\incluirlistadequadros` antes do sumário em `main.tex`.
