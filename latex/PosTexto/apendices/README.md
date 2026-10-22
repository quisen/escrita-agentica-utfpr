# Apêndices

Instruções para o agente: execute a inclusão e confira o PDF. A pessoa autora fornece o material e decide sobre o conteúdo.

Guarde materiais elaborados pela pessoa autora que complementam a pesquisa: instrumento de coleta, livro de códigos ou protocolo detalhado. Documentos de terceiros pertencem aos anexos. Rascunhos e registros internos não precisam entrar no PDF final.

Crie `PosTexto/apendices/instrumento.tex`, começando com:

```tex
\chapter{Instrumento de coleta}
\label{ap:instrumento}

% Insira aqui o instrumento efetivamente elaborado.
```

Em `main.tex`, após as referências (`\endgroup`) e antes de `\end{document}`, acrescente:

```tex
\begin{arquivosdeapendices}
  \include{PosTexto/apendices/instrumento}
\end{arquivosdeapendices}
```

Inclua os demais arquivos dentro do mesmo ambiente. A classe fornece a identificação por letras. No corpo do trabalho, use `Apêndice~\ref{ap:instrumento}`. Não escreva “Apêndice A” dentro de `\chapter`.

A pasta não é incluída automaticamente: somente os arquivos chamados em `main.tex` entram no documento. Descreva instrumentos previstos como previstos, sem sugerir aplicação já realizada. Compile duas vezes e confira títulos, letras, sumário e chamadas no PDF.
