# Tabelas

Instruções para o agente: execute a inclusão e confira o PDF. A pessoa autora fornece o material e decide sobre o conteúdo.

Use para dados predominantemente numéricos. Para categorias e sínteses textuais, veja `quadros/`. Mantenha a unidade no cabeçalho e identifique a origem dos dados.

Salve, por exemplo, `tabelas/tabela-distribuicao.tex` e inclua no capítulo com `\input{tabelas/tabela-distribuicao}`:

```tex
\begin{table}[htb]
  \centering
  \caption{Distribuição do material por grupo}
  \label{tab:distribuicao}
  \begin{tabular}{lr}
    \toprule
    Grupo & Quantidade \\
    \midrule
    A & 12 \\
    B & 8 \\
    \midrule
    Total & 20 \\
    \bottomrule
  \end{tabular}
  \fonte{dados fictícios para demonstração}
\end{table}
```

Substitua os números de exemplo e a fonte antes de usar em um trabalho. `booktabs` já está carregado. Apresente a tabela no texto com `Tabela~\ref{tab:distribuicao}`. Não digite a numeração manualmente.

Confira totais, unidades e correspondência com o texto. Quando houver geração por script, corrija a fonte de dados ou o script e regenere a saída. Para várias páginas, use `longtable` sem o ambiente flutuante `table`, com cabeçalho repetido. Confira legibilidade e quebras no PDF. Para exibir a lista, ative `\incluirlistadetabelas` em `main.tex`.
