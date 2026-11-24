# Strings de busca no Scopus, IEEE Xplore e SciELO

Este guia mostra como montar uma string de busca bibliográfica e adaptá-la a três bases: Scopus, IEEE Xplore e SciELO. O agente pode montar, revisar e traduzir as strings entre as bases. **A busca é executada por você na interface de cada base**, porque o acesso costuma depender de login institucional (CAFe ou rede da universidade). Depois, informe ao agente os totais e exporte os registros.

## 1. Comece pelos blocos, não pela sintaxe

Antes de escrever operadores, separe os termos da pesquisa em blocos de conceitos. Uma estrutura que funciona bem tem três blocos:

| Bloco | Função | Exemplo |
| --- | --- | --- |
| A · objeto empírico | Delimita onde o fenômeno acontece | Instagram |
| B · tecnologia ou fenômeno central | Nomeia o que está sendo estudado | IA generativa, LLMs |
| C · conceitos e atores | Traz a lente teórica e os sujeitos | trabalho em plataforma, criadores de conteúdo, mediação algorítmica |

A lógica geral é:

```text
(A) AND (B1 OR B2 OR B3 ...) AND (C1 OR C2 OR C3 ...)
```

- **Dentro de um bloco, use OR**: sinônimos, variações em português e inglês, singular e plural.
- **Entre blocos, use AND**: um registro só aparece se tratar de todos os blocos ao mesmo tempo.
- **Mantenha a mesma lógica em todas as bases.** Mude só a sintaxe. Se uma base exigir outra estrutura (por exemplo, `A AND (B OR C)` em vez de `A AND B AND C`), registre a diferença: os totais deixam de ser comparáveis entre as bases.
- Para cada termo, liste antes os equivalentes de busca em uma tabela (palavra-chave, motivo da escolha, equivalentes em inglês). Essa tabela costuma entrar na metodologia.

## 2. Regras que valem nas três bases

- Escreva os operadores em **MAIÚSCULAS**: `AND`, `OR`, `NOT` ou `AND NOT`.
- **Use parênteses em todo bloco.** As bases não seguem a mesma ordem de precedência entre operadores, e o Scopus anunciou mudanças nessa ordem. Com parênteses, a string não depende dessas regras.
- **Coloque termos compostos entre aspas** (`"generative AI"`). Sem aspas, a base pode procurar as palavras soltas em qualquer lugar do registro, e não a expressão.
- Use aspas retas (`"`), não aspas curvas (`“ ”`). Ao copiar de um editor de texto, confira: o Scopus pode acusar erro com aspas curvas.
- **Curingas** (`*`) precisam de pelo menos três letras antes: `influencer*` funciona, `in*` não funciona.
- Inclua termos em português se a base indexa produção brasileira. Inclua grafias britânica e americana quando a base não as trate automaticamente (`platformization`, `platformisation`).

## 3. Scopus

**Acesso:** pelo [Portal de Periódicos da CAPES](https://www.periodicos.capes.gov.br/).

1. Faça login no portal (acesso CAFe, com a conta da sua instituição).
2. Clique em **Lista de bases e coleções**.
3. Pesquise `scopus` e selecione **Scopus (Elsevier)**.
4. Clique em **Acesse**.

**Onde:** *Advanced document search*. A busca avançada aceita a string inteira, incluindo os limites.

| Recurso | Sintaxe |
| --- | --- |
| Título, resumo e palavras-chave | `TITLE-ABS-KEY( ... )` |
| Só título, só resumo, só palavras-chave | `TITLE( )`, `ABS( )`, `KEY( )` |
| Frase aproximada (ignora pontuação, inclui plurais) | `"content creator"` |
| Frase exata (pontuação e espaços contam) | `{content creator}` |
| Zero ou mais caracteres | `influencer*` |
| Exatamente um caractere | `platformi?ation` (`platformization` e `platformisation`) |
| Proximidade | `W/n` (qualquer ordem), `PRE/n` (na ordem) |
| Ano | `PUBYEAR > 2017 AND PUBYEAR < 2027` |
| Tipo de documento e de fonte | `DOCTYPE(ar)` (artigo), `SRCTYPE(j)` (periódico) |
| Idioma | `LANGUAGE(english) OR LANGUAGE(portuguese)` |

Observações:

- O Scopus já inclui plurais e variações britânicas e americanas em termos sem chaves. Curingas são úteis para outras derivações (`empreendedor* digit*`).
- Curingas funcionam dentro de aspas (`"large language model*"`). Dentro de chaves, são lidos como caracteres literais.
- `KEY()` busca palavras-chave dos autores e termos indexados, não só as palavras escolhidas pelos autores.
- Prefira colocar os limites (ano, tipo, idioma) na própria string. Assim, o registro guarda a busca completa. Se usar os filtros da barra lateral, anote quais foram aplicados.
- **Acentos:** a documentação oficial não informa como o Scopus trata acentos. Teste a mesma expressão com e sem acento (`plataformização` e `plataformizacao`) e compare os totais antes de fixar a string.

## 4. IEEE Xplore

**Acesso:** [Command Search do IEEE Xplore](https://ieeexplore.ieee.org/search/advanced/command).

**Onde:** *Advanced Search* (formulário com campos) ou *Command Search* (string livre). Para colar uma string pronta, use *Command Search*, no link acima.

| Recurso | Sintaxe |
| --- | --- |
| Todos os metadados (padrão sem campo) | `"generative AI"` |
| Campo específico | `"Document Title":Instagram`, `"Abstract":"platform labor"` |
| Frase | `"platform labor"` |
| Zero ou mais caracteres | `influencer*` |
| Um caractere | `platformi?ation` |
| Proximidade | `NEAR/n` (qualquer ordem), `ONEAR/n` (na ordem). Não funciona no formulário *Advanced Search*. |
| Ano | Filtro *Publication Year* na interface |

Observações:

- Sem campo, a busca cobre *All Metadata*: título, resumo, termos indexados e dados bibliográficos. O texto completo é uma opção separada e amplia muito os resultados.
- O IEEE aplica *stemming* (plurais, tempos verbais, grafias britânica e americana) em termos soltos. **As aspas desligam essa expansão**, então `"content creator"` não encontra `content creators`. Use curinga dentro das aspas: `"content creator*"`.
- **Há limite de termos por busca e de curingas por busca**, e esses limites mudaram ao longo dos anos. Strings longas com muitas variações em português podem ultrapassar o limite. Se aparecer erro, reduza variações redundantes (o *stemming* já cobre parte delas) ou divida a busca e registre as partes.
- O IEEE indexa pouca produção em português. Termos em português raramente alteram o total, mas mantê-los não prejudica a busca, desde que caibam no limite.

## 5. SciELO

**Acesso:** [search.scielo.org](https://search.scielo.org/). O acesso é aberto e não exige login.

**Onde:** caixa de busca da página inicial, com os filtros da coluna lateral na página de resultados.

| Recurso | Sintaxe |
| --- | --- |
| Operadores | `AND`, `OR`, `AND NOT` (o formulário oferece os três) |
| Frase | `"inteligência artificial generativa"` |
| Título, resumo e palavras-chave | `subject:( ... )` |
| Só título, resumo, palavras-chave | `ti:`, `ab:`, `kw:` |
| Outros campos | `au:` (autor), `la:` (idioma), `type:`, `publication_year:`, `journal_title:` |

Filtros na interface: Coleções, Periódico, Idioma, Ano de publicação, Áreas temáticas (SciELO e WoS), Citáveis e não citáveis, e Tipo de literatura (por exemplo, `research-article`).

Observações:

- **Use aspas em todo termo composto.** A ajuda da SciELO não informa como palavras soltas são combinadas. `(generative AI)` sem aspas não é garantia de que se busque a expressão.
- A ajuda também não documenta curingas nem o tratamento de acentos. Até testar, escreva explicitamente as variações de singular e plural (`"criador de conteúdo" OR "criadores de conteúdo"`) e compare os totais com e sem acento.
- Sem prefixo de campo, a busca pode abranger mais do que título, resumo e palavras-chave. Para aproximar o recorte do Scopus, envolva os blocos em `subject:( ... )` e confira se o total muda de forma coerente.
- A SciELO tem menos registros que o Scopus. Se a busca em três blocos retornar pouco ou nada, não afrouxe a lógica sem registrar a mudança. Uma estratégia mais ampla é legítima, mas precisa ser declarada na metodologia, porque os totais deixam de ser comparáveis.

## 6. Exemplo resolvido: uma dissertação sobre LLMs e Instagram

Estas strings vêm de uma pesquisa de mestrado sobre o uso de IA generativa por empreendedores digitais no Instagram. As buscas foram feitas em 27/06/2026, com o período limitado a 2018 a 2026.

**Scopus** (18 registros):

```text
TITLE-ABS-KEY(
  Instagram
  AND ( "generative AI" OR "generative artificial intelligence"
        OR "large language model*" OR LLM*
        OR "inteligência artificial generativa"
        OR "modelos de linguagem de grande porte" )
  AND ( "platform labor" OR "creator labor" OR "platform work"
        OR platformi?ation OR "algorithmic mediation"
        OR "algorithmic visibility" OR "sociotechnical dependence"
        OR "platform dependence" OR "platform dependency"
        OR "algorithmic dependence" OR "dependency on platforms"
        OR "digital entrepreneur*" OR "content creator*" OR influencer*
        OR "creator economy" OR "empreendedor* digit*"
        OR "criador* de conteúdo" OR influenciador*
        OR "dependência sociotécnica" OR "trabalho em plataforma"
        OR plataformização OR "mediação algorítmica"
        OR "visibilidade algorítmica" )
)
AND PUBYEAR > 2017 AND PUBYEAR < 2027
AND DOCTYPE(ar) AND SRCTYPE(j)
AND (LANGUAGE(english) OR LANGUAGE(portuguese))
```

**IEEE Xplore** (8 registros, filtro *Publication Year* 2018 a 2026):

```text
("Instagram")
AND ("generative AI" OR "generative artificial intelligence"
     OR "large language model*" OR LLM*)
AND ("platform labor" OR "creator labor" OR "platform work"
     OR platformization OR platformisation OR "algorithmic mediation"
     OR "algorithmic visibility" OR "sociotechnical dependence"
     OR "platform dependence" OR "platform dependency"
     OR "algorithmic dependence" OR "dependency on platforms"
     OR "digital entrepreneur*" OR "content creator*" OR influencer*
     OR "creator economy")
```

**SciELO** (36 registros, filtros: português e inglês, 2018 a 2026, `research-article`, citáveis):

```text
(Instagram) AND (
  ((inteligência artificial generativa) OR (generative AI) OR ... OR (LLMs))
  OR ((empreendedores digitais) OR (content creators) OR ... OR (influenciador))
  OR ((trabalho em plataforma) OR (platform labor) OR ... OR (platform dependency))
)
```

O que este exemplo ensina:

- O Scopus e o IEEE usam a mesma lógica `A AND B AND C`. A diferença entre eles é só de sintaxe: o IEEE dispensa os termos em português e usa o filtro de ano da interface.
- **Na SciELO, a lógica mudou para `A AND (B OR C)`.** A busca recupera estudos sobre criadores e Instagram mesmo sem menção a IA. Por isso, os 36 registros não podem ser comparados com os 18 do Scopus, e a dissertação declara essa diferença na metodologia.
- Na SciELO, os termos compostos ficaram entre parênteses sem aspas. Em uma nova rodada, a versão mais segura seria `"generative AI"`, `"content creators"` e assim por diante, mantendo a estrutura em três blocos sempre que o total permitir.

## 7. Registre cada busca

A metodologia precisa permitir que outra pessoa repita a busca. Para cada base, registre:

| Campo | Exemplo |
| --- | --- |
| Base e interface | Scopus · *Advanced document search* |
| Data da busca | 27/06/2026 |
| String exata, copiada da interface | (texto completo) |
| Filtros aplicados fora da string | Idioma, ano, tipo de documento |
| Total recuperado e total exportado | 18 · 18 |
| Formato de exportação | CSV, RIS ou BibTeX |

Peça ao agente que mantenha esse registro em `corpus_md/registro-buscas.md`. Ao repetir a busca para atualização, registre uma nova rodada com data própria, sem sobrescrever a anterior.

## Pedidos prontos para o agente

```text
Leia AGENTS.md e guias/strings-de-busca.md. Com base nestas palavras-chave
[cole a tabela ou a lista], monte os blocos e proponha strings para Scopus,
IEEE Xplore e SciELO com a mesma lógica. Aponte onde a sintaxe de cada base
pode mudar o resultado. Não execute buscas.
```

```text
Fiz as buscas. Seguem as strings copiadas das interfaces, os filtros e os
totais [cole]. Registre em corpus_md/registro-buscas.md e confira se a
lógica ficou equivalente entre as bases.
```

## Documentação oficial

- Scopus: [uso da busca avançada](https://www.elsevier.support/scopus/answer/how-can-i-best-use-the-advanced-search) e [guia de sintaxe](https://dev.elsevier.com/sc_search_tips.html).
- IEEE Xplore: [dicas de busca](https://ieeexplore.ieee.org/Xplorehelp/searching-ieee-xplore/search-tips) e [Command Search](https://ieeexplore.ieee.org/Xplorehelp/searching-ieee-xplore/command-search).
- SciELO: caixa "Glossário e ajuda para busca" em [search.scielo.org](https://search.scielo.org/).

Regras de sintaxe e limites mudam. Se uma base rejeitar a string ou retornar um total inesperado, confira a ajuda atual antes de alterar a lógica.
