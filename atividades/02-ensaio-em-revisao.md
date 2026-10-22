# Atividade 2 · Escrever, revisar e comparar versões

Vamos transformar a comparação da atividade 1 em um texto no template UTFPR. Depois, você vai pedir uma revisão e comparar o que mudou. O agente cuida dos arquivos, da geração do PDF e do Git.

Use o mesmo projeto da [atividade 1](01-mapa-de-evidencias.md), com a posição escolhida registrada no mapa.

## 1. Peça o primeiro texto

Copie e envie ao agente:

```text
Leia AGENTS.md e corpus_md/mapa-evidencias.md.

Use a “Posição escolhida para o ensaio” para preparar um texto de
600 a 900 palavras no corpo, com introdução, discussão e considerações
finais. Resumos, quadro e referências ficam fora dessa contagem.
Use somente os dois artigos trabalhados e respeite os limites das fontes.

Substitua os textos de exemplo no template UTFPR. Ajuste título,
resumo, abstract e referências, mantendo a formatação. Deixe sem
preenchimento os dados pessoais ou institucionais que não fornecemos.
Inclua um quadro curto comparando as contribuições dos dois artigos.

Gere e confira o PDF. Abra o resultado para leitura e informe pendências.
Não faça commit nem publique nada ainda.
```

**Leia o PDF:** o texto expressa a ideia que você queria desenvolver? Se não, explique ao agente o que precisa mudar e peça uma nova versão.

Quando estiver satisfeito com esse primeiro rascunho, envie:

```text
Registre esta primeira versão em um commit local.
Guarde também uma cópia local do PDF para compararmos depois.
Não inclua PDFs de terceiros nem extrações integrais no commit.
Não envie nada ao GitHub.
```

Esse registro permite acompanhar as mudanças. Você não precisa executar comandos de Git.

## 2. Peça uma revisão concreta

Escolha um trecho que queira melhorar. Pode ser uma conclusão exagerada, uma comparação pouco clara ou uma ideia diferente da que você pretendia expressar.

Envie:

```text
Quero rever este trecho:
[cole o trecho]

O problema que vejo é:
[explique com suas palavras o que precisa mudar]

Confira as fontes e proponha uma revisão. Se meu pedido não tiver
apoio nos artigos, explique o limite em vez de inventar uma justificativa.
Ajuste os outros trechos que dependerem dessa mudança, incluindo
resumo, conclusão e quadro quando necessário.

Gere e confira o novo PDF. Mostre o trecho anterior e o revisado,
explicando o que mudou. Não faça outro commit ainda.
```

**Compare:** a revisão resolveu o problema sem mudar indevidamente sua ideia?

Se não souber o que revisar, peça ao agente que aponte uma afirmação que mereça maior cuidado e mostre a passagem da fonte usada para sustentá-la. Avalie a sugestão antes de pedir a mudança.

## 3. Decida e registre a nova versão

Você pode aceitar a revisão ou pedir outro ajuste. Por exemplo: **“Gostei da nova conclusão, mas quero manter a explicação anterior neste parágrafo.”**

Quando aceitar o resultado, envie:

```text
Registre a versão aceita em um segundo commit local, com uma mensagem
que explique a revisão. Não envie nada ao GitHub.

Mostre uma comparação curta entre as duas versões: o que mudou no
argumento e quais partes do documento acompanharam essa mudança.
Abra o PDF atual e a cópia da primeira versão para comparação.
```

**Pronto:** você tem um texto no template UTFPR e duas versões registradas. Observe o que foi decisão sua e o que foi execução do agente.

Se a geração do PDF falhar, peça ao agente que resolva o problema técnico. Você não precisa instalar pacotes nem editar comandos para continuar.
