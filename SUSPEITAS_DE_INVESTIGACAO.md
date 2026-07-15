# Suspeitas de Investigacao

Este documento define como o Motor de Investigacao do TCRIA deve identificar,
organizar e explicar sinais encontrados em um conjunto de documentos.

Apesar do nome historico deste documento, o termo usado pelo TCRIA nas saidas
para o cliente deve ser **sinal de investigacao**.

Uma suspeita pode soar como acusacao. Um sinal descreve algo que merece
atencao, verificacao ou contexto adicional, sem concluir antecipadamente que
existe erro, culpa, fraude ou descumprimento.

## Principio central

O Motor de Investigacao nao deve sair procurando culpados.

Ele deve procurar:

- fatos;
- relacoes;
- contradicoes;
- diferencas relevantes;
- ausencias;
- quebras de padrao;
- mudancas ao longo do tempo;
- excecoes;
- informacoes sem prova suficiente;
- provas que ainda nao permitem uma conclusao.

A pergunta central do modulo e:

> Quais sinais este conjunto de documentos emite?

Esses sinais orientam o profissional sobre onde olhar primeiro. Eles nao
substituem a verificacao humana nem autorizam uma conclusao que as provas ainda
nao sustentam.

## O que e um sinal de investigacao

Um sinal de investigacao e uma observacao verificavel que indica uma possivel
incoerencia, lacuna, excecao ou mudanca relevante no conjunto analisado.

Um sinal deve sempre explicar:

1. o que foi observado;
2. em quais documentos foi observado;
3. por que isso merece atencao;
4. o que ainda nao pode ser afirmado;
5. qual verificacao deve acontecer em seguida.

O TCRIA deve separar claramente:

- **fato:** informacao diretamente encontrada nos documentos;
- **sinal:** relacao, diferenca, ausencia ou comportamento que merece analise;
- **hipotese:** explicacao possivel para o sinal;
- **conclusao:** afirmacao sustentada por evidencia suficiente;
- **recomendacao:** proximo passo sugerido para reduzir a incerteza.

## Tipos de sinais

### 1. Contradicao

Existe quando duas ou mais fontes apresentam afirmacoes que nao podem ser
verdadeiras ao mesmo tempo dentro do mesmo contexto.

Exemplos:

- um contrato estabelece prazo de 90 dias e um aditivo informa 120 dias;
- um documento registra `aprovado` e outro registra `pendente`;
- duas fontes atribuem a mesma responsabilidade a pessoas diferentes.

O TCRIA deve verificar se os documentos tratam do mesmo objeto, periodo e
versao antes de registrar uma contradicao.

### 2. Diferenca relevante

Existe quando documentos comparaveis apresentam diferencas importantes, mesmo
que nao exista contradicao direta.

Exemplo:

- cinco procedimentos seguem um fluxo e um sexto utiliza uma sequencia
  diferente.

A diferenca deve ser apresentada como um ponto para verificacao, e nao como
prova automatica de irregularidade.

### 3. Ausencia

Existe quando uma informacao ou documento esperado nao foi encontrado no
material analisado.

A pergunta obrigatoria e:

> O que era esperado encontrar e nao foi encontrado?

Uma ausencia so deve ser registrada quando o TCRIA puder explicar por que o
item era esperado. A falta de um arquivo no lote nao prova que ele nao exista
fora do lote.

### 4. Quebra de padrao

Existe quando a maior parte de um grupo comparavel segue um padrao e um ou mais
itens fogem desse comportamento.

Exemplo:

- nove contratos possuem assinatura, data e responsavel identificado;
- um contrato nao possui um desses elementos.

O padrao de comparacao e a excecao encontrada devem ficar visiveis no sinal.

### 5. Mudanca de procedimento

Existe quando setores, equipes, periodos ou documentos equivalentes registram
formas diferentes de executar o mesmo processo.

Exemplo:

- Setor A: `aprovacao -> juridico -> assinatura`;
- Setor B: `assinatura -> aprovacao`.

Esse sinal nao significa, por si so, que alguem errou. Ele indica que a empresa
pode nao estar trabalhando de forma uniforme e que a diferenca precisa ser
explicada.

### 6. Evolucao temporal

Existe quando uma regra, informacao, responsabilidade ou procedimento muda ao
longo do tempo.

O TCRIA deve ordenar os registros por data e perguntar:

> O que mudou entre os periodos e qual documento explica essa mudanca?

Uma mudanca temporal pode representar evolucao legitima, correcao, nova regra
ou inconsistencia. O motor nao deve escolher uma dessas explicacoes sem prova.

### 7. Excecao ou documento isolado

Existe quando um item nao acompanha a regra ou o comportamento observado no
restante do lote.

O documento isolado merece verificacao prioritaria, mas nao deve ser tratado
automaticamente como incorreto.

### 8. Informacao sem prova

Existe quando um documento apresenta uma afirmacao relevante, mas o lote nao
contem suporte suficiente para confirma-la.

Exemplos:

- o texto afirma que houve aprovacao, mas nao ha registro da aprovacao;
- o documento menciona uma entrega, mas nao ha comprovante correspondente.

O TCRIA deve dizer qual prova seria necessaria para confirmar a informacao.

### 9. Prova sem conclusao

Existe quando ha documentos ou registros relevantes, mas eles nao permitem
entender com seguranca o que aconteceu ou qual resultado deve ser adotado.

Esse sinal evita que a existencia de muitos arquivos seja confundida com
evidencia suficiente para concluir.

## Estrutura minima de um sinal

Cada sinal produzido pelo Motor de Investigacao deve conter:

| Campo | O que deve informar |
| --- | --- |
| Identificacao | Codigo unico do sinal no relatorio. |
| Tipo | Contradicao, ausencia, quebra de padrao ou outro tipo previsto neste documento. |
| Titulo | Descricao curta em portugues simples. |
| O que foi observado | Fatos encontrados sem interpretacao excessiva. |
| Documentos relacionados | Fontes que deram origem ao sinal. |
| Comparacao realizada | Elementos, periodos ou padroes comparados. |
| Por que merece atencao | Consequencia pratica da observacao. |
| O que ainda nao sabemos | Limite da analise e incerteza restante. |
| Quanto confiamos | Confianca na identificacao do sinal, e nao na culpa de alguem. |
| Prioridade de verificacao | Ordem sugerida para revisao profissional. |
| Proximo passo | Documento, contexto ou confirmacao que deve ser buscado. |

Um sinal sem fonte identificavel ou sem explicacao do que falta nao deve ser
apresentado como um achado confiavel.

## Fluxo operacional

O Motor de Investigacao deve trabalhar nesta ordem:

1. inventariar o que chegou;
2. registrar o que conseguiu e o que nao conseguiu ler;
3. agrupar documentos comparaveis;
4. identificar fatos, datas, pessoas, responsabilidades e procedimentos;
5. procurar os tipos de sinais definidos neste documento;
6. vincular cada sinal aos documentos que o sustentam;
7. testar explicacoes alternativas;
8. registrar contradicoes, lacunas e limites;
9. definir o que pode e o que ainda nao pode ser afirmado;
10. recomendar a proxima verificacao.

O motor nao deve pular da leitura diretamente para a conclusao.

## Regras de seguranca

O TCRIA deve obedecer a estas regras:

1. nao transformar diferenca em erro automaticamente;
2. nao transformar ausencia no lote em prova de inexistencia;
3. nao chamar mudanca de contradicao sem verificar datas e versoes;
4. nao atribuir intencao, culpa ou fraude com base apenas em um sinal;
5. nao esconder documentos que enfraquecam uma hipotese;
6. considerar explicacoes alternativas antes de concluir;
7. dizer `nao foi possivel confirmar` quando a evidencia for insuficiente;
8. pedir mais documentos quando uma lacuna impedir a verificacao;
9. manter cada conclusao ligada as fontes que a sustentam;
10. deixar claro quando a revisao profissional ainda for necessaria.

## Linguagem para o cliente

O relatorio deve apresentar sinais como perguntas e observacoes compreensiveis.

Preferir:

- `Os documentos apresentam informacoes diferentes sobre o prazo.`
- `Este item nao segue o padrao encontrado nos demais contratos.`
- `Nao encontramos, neste lote, o documento que comprova a aprovacao.`
- `O procedimento mudou entre 2025 e 2026, mas a causa nao esta documentada.`
- `Este sinal merece verificacao antes de qualquer conclusao.`

Evitar:

- `Erro detectado.`
- `Fraude provavel.`
- `Culpado identificado.`
- `Nao conformidade comprovada.`
- qualquer afirmacao definitiva que ultrapasse a evidencia disponivel.

## Resultado esperado

O Motor de Investigacao nao deve produzir apenas uma lista de conclusoes.

Ele deve entregar um mapa de sinais que mostre:

- onde os documentos convergem;
- onde nao combinam;
- o que foge do padrao;
- o que mudou;
- o que esta faltando;
- o que possui prova;
- o que ainda depende de confirmacao;
- onde o profissional deve olhar primeiro.

O principio de comunicacao e:

> Aqui existem sinais que merecem sua atencao.

Essa formulacao preserva a utilidade investigativa do TCRIA sem antecipar
acusacoes ou conclusoes que o conjunto documental ainda nao permite sustentar.
