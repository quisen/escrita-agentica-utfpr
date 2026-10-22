# Figuras

Instruções para o agente: execute a inclusão e confira o PDF. A pessoa autora fornece o material e decide sobre o conteúdo.

Guarde imagens, gráficos e fluxogramas usados no texto (`.png`, `.jpg` ou `.pdf`). Use nomes descritivos, como `fluxo-selecao.pdf`. Prefira PDF para gráficos vetoriais e imagem com texto legível no tamanho final.

No capítulo, apresente a figura e faça referência pelo rótulo:

```tex
O percurso está representado na Figura~\ref{fig:fluxo-selecao}.

\begin{figure}[htb]
  \centering
  \caption{Fluxo de seleção do material}
  \label{fig:fluxo-selecao}
  \includegraphics[width=0.85\textwidth]{fluxo-selecao.pdf}
  \fonte{elaboração própria}
\end{figure}
```

O exemplo pressupõe que você adicionou a imagem. `configuracoes.tex` já define `figuras/` como caminho de busca. Título acima e fonte abaixo seguem a configuração do template. Para adaptações, substitua a fonte pela atribuição real e inclua a referência da obra.

Não numere manualmente nem grave a legenda na própria imagem. Evite `[H]` como padrão: deixe o LaTeX posicionar e só fixe quando necessário. Confira resolução, margens e legibilidade no PDF. Para exibir a lista de figuras, ative `\incluirlistadeilustracoes` no pré-texto de `main.tex`.
