# Anexos

Instruções para o agente: execute a inclusão e confira o PDF. A pessoa autora fornece o material e decide sobre o conteúdo.

Guarde documentos de terceiros necessários à compreensão do trabalho: formulário institucional, documento normativo ou outro material consultado. Material elaborado pela pessoa autora pertence aos apêndices. Os PDFs de leitura continuam em `pdfs/` na raiz: nem toda fonte precisa virar anexo.

Crie `PosTexto/anexos/documento.tex`, começando com:

```tex
\chapter{Documento de referência}
\label{an:documento}

% Identifique a origem e insira o conteúdo pertinente.
```

Em `main.tex`, após referências e apêndices, antes de `\end{document}`, acrescente:

```tex
\begin{arquivosdeanexos}
  \include{PosTexto/anexos/documento}
\end{arquivosdeanexos}
```

A classe fornece as letras. Cite no texto com `Anexo~\ref{an:documento}`. Não digite “Anexo A” no título. Somente arquivos chamados em `main.tex` entram no PDF.

Para incorporar um PDF, `pdfpages` já está carregado. Após o título e a identificação da origem, use no arquivo do anexo:

```tex
\includepdf[pages=-]{PosTexto/anexos/documento-original.pdf}
```

Esse comando insere o documento inteiro em páginas adicionais. Confira se a página de abertura separada é adequada, se a paginação deve ser mantida e se as páginas inseridas estão legíveis. Preserve o original, atribua a fonte e verifique se o material pode ser reproduzido. Compile duas vezes e confira letras, chamadas e sumário.
