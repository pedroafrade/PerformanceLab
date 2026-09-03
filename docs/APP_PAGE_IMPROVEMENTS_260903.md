# PerformanceLab — Plano de melhorias das páginas

**Criado em:** 3 de setembro de 2026  
**Estado:** alterações planeadas — implementação pendente  
**Destino no repositório:** `docs/APP_PAGE_IMPROVEMENTS_260903.md`

## 1. Objetivo e âmbito

Registar as alterações funcionais e visuais a efetuar nas páginas da aplicação,
com tarefas identificáveis e critérios de aceitação.

Este documento complementa, mas não substitui nem atualiza,
`ROADMAP_PUBLIC_UI_260825.md`. Não altera os requisitos de segurança,
privacidade, deployment ou convite da alpha.

Todos os itens abaixo estão pendentes. A sua descrição representa o resultado
pretendido, não uma confirmação do comportamento atual do código.

## 2. Regras comuns

- Evitar scroll da página no desktop nas dimensões de referência usadas na
  validação. Registar resolução, zoom e dimensões da janela nessa validação.
- Usar scroll interno nas listas extensas; não esconder conteúdo para cumprir
  o objetivo de uma página compacta.
- Não impor alturas que provoquem sobreposição, corte de texto ou perda de
  botões com conteúdos maiores, zoom ou ecrãs pequenos.
- Interpretar os alinhamentos e posições fixas como posições estáveis no
  layout desktop, não como sobreposições absolutas ao conteúdo.
- No dispositivo móvel, permitir empilhamento e scroll normal da página.
- Manter contraste nos modos claro e escuro. Cores não devem ser a única forma
  de identificar modalidades, tipos de treino ou estados.
- Alterações de apresentação não devem modificar os dados guardados nem as
  fórmulas de cálculo, exceto quando isso for explicitamente definido.
- Preservar autorização, consentimentos, exportação, eliminação e isolamento
  dos dados do atleta.

## 3. Plan

### PLN-01 — Transferir Export Calendar

- [ ] Retirar o botão **Export Calendar** da página Plan.
- [ ] Disponibilizar a mesma funcionalidade na página Calendar, conforme CAL-01.

**Aceitação:** a exportação continua acessível e funcional em Calendar, sem
regressões no conteúdo exportado. Não existe uma segunda cópia do botão em Plan.

### PLN-02 — Plan Weeks num contentor com scroll interno

- [ ] Criar um contentor para as linhas semanais de **Plan Weeks**.
- [ ] Colocar todas as linhas semanais no seu interior.
- [ ] Limitar a altura no desktop e permitir scroll dentro do contentor.
- [ ] Manter acessíveis as semanas, os expansores e os respetivos detalhes.

**Aceitação:** planos mais longos ou semanas expandidas não aumentam
indefinidamente a altura da página; o conteúdo permanece acessível por scroll
interno, rato, toque e teclado.

### PLN-03 — Compactar e alinhar a coluna direita

- [ ] Após remover Export Calendar, reorganizar **Current Phase**, **Current
  Week** e **Latest Adaptation**.
- [ ] Reduzir espaços verticais desnecessários sem comprometer a leitura.
- [ ] Alinhar o limite inferior de Latest Adaptation com o limite inferior do
  contentor Plan Weeks.

**Aceitação:** a composição desktop não gera scroll desnecessário da página.
Validar também ausência de adaptação, textos longos e diferentes fases do plano.

## 4. Activities

### ACT-01 — RPE sem casas decimais

- [ ] Mostrar RPE apenas em unidades inteiras na página Activities.
- [ ] Aplicar a mesma formatação na lista e nos detalhes que apresentem RPE.
- [ ] Preservar a precisão do valor guardado e usado nos cálculos.

**Aceitação:** nenhum RPE visível nesta página apresenta casas decimais;
valores ausentes não são convertidos em zero. Usar arredondamento para
apresentação, com regra consistente e testada, não truncagem silenciosa.

### ACT-02 — Frequência cardíaca a vermelho

- [ ] Alterar para vermelho a linha de frequência cardíaca, em BPM.
- [ ] Manter coerência entre linha, legenda e informação apresentada no hover.

**Aceitação:** a série é legível em ambos os temas e distingue-se das restantes.

### ACT-03 — Posição de Activities Summary

- [ ] Posicionar **Activities Summary** no canto inferior direito do layout
  desktop.
- [ ] Alinhar o seu limite inferior com o limite inferior do contentor de
  atividades.
- [ ] Manter a posição estável perante alterações nos filtros ou na seleção,
  sem sobrepor a lista ou os detalhes.

**Aceitação:** o resumo e a lista mantêm o alinhamento; no móvel, o resumo é
reposicionado no fluxo normal da página.

### ACT-04 — Resumos globais e por modalidade

- [ ] Substituir o conteúdo atual de Activities Summary.
- [ ] Disponibilizar os períodos **Desde sempre**, **1 ano**, **6 meses** e
  **1 mês**.
- [ ] Mostrar resumos globais e resumos por modalidade para o período escolhido.
- [ ] Identificar claramente o período e a modalidade ativos.

**A definir antes da implementação:** conjunto exato de métricas; período
predefinido; significado das janelas temporais; interação com os filtros da
lista; tratamento de atividades sem modalidade ou sem determinados dados.

**Aceitação:** totais verificáveis a partir das atividades do período; estados
vazios explícitos; ausência de dupla contagem. Não somar ou comparar métricas
entre modalidades quando isso não fizer sentido.

### ACT-05 — Melhorar a apresentação do mapa

- [ ] Rever o estilo visual do mapa e do percurso.
- [ ] Apresentar uma proposta visual antes de escolher o estilo final.
- [ ] Melhorar contraste, enquadramento e legibilidade em desktop e móvel.

**A definir:** estilo cartográfico, tratamento da rota e controlos visíveis.
Qualquer mudança de fornecedor deve ser avaliada quanto a privacidade,
atribuição, credenciais e custos antes de ser adotada.

**Aceitação:** mapa mais legível e coerente com a aplicação, preservando a
informação geográfica e o comportamento de atividades sem rota.

## 5. Calendar

### CAL-01 — Receber Export Calendar

- [ ] Integrar o botão transferido de Plan num local coerente com os controlos
  de Calendar.
- [ ] Tornar claro o âmbito da exportação existente. Não alterar silenciosamente
  o conteúdo exportado para apenas o mês visível.

**Aceitação:** navegação mensal, seleção de dia, gestão de eventos e exportação
funcionam em conjunto, sem criar scroll ou desalinhamentos desnecessários.

### CAL-02 — Fundo das sessões de treino

- [ ] Aplicar um fundo cinzento claro às sessões de treino, à semelhança do
  destaque de fundo já usado nas provas.
- [ ] Preservar o fundo vermelho das provas.
- [ ] Adaptar o tom de cinzento ao tema para manter texto e conteúdo legíveis.

### CAL-03 — Cor da linha lateral por tipo de treino

- [ ] Aplicar a seguinte correspondência à linha vertical esquerda de cada treino:

| Tipo de treino | Cor pretendida |
|---|---|
| Easy run e Shakeouts | Verde claro |
| Tempo runs e Intervals | Amarelo |
| Hills | Verde escuro |
| Long runs | Violeta |

- [ ] Manter o nome do tipo de treino visível, sem depender apenas da cor.
- [ ] Definir um estilo neutro para tipos não incluídos nesta lista.

**Aceitação:** classificação consistente, preferencialmente baseada no tipo
estruturado do treino, não apenas em correspondências frágeis do título.
Validar contraste, seleção de dia e coexistência de treino e prova no mesmo dia.

## 6. Development

### DEV-01 — Distância total em vez de Running Pace

- [ ] Substituir **Running Pace**, na primeira linha, por **Total Running Distance**.
- [ ] Adicionar um menu de três pontos no canto superior direito do contentor.
- [ ] Permitir alternar entre distância de corrida e distância de ciclismo.
- [ ] Atualizar título, valor e unidade de acordo com a modalidade escolhida.

**A definir:** persistência da escolha entre sessões e inclusão de trail no
total de corrida. O período deve ser explícito e coerente com o resumo da página.

**Aceitação:** total correto, sem mistura acidental de modalidades; zero e
ausência de dados apresentados de forma inequívoca.

### DEV-02 — Legenda completa de Load and form

- [ ] Verificar no código qual a métrica representada pela terceira linha roxa.
- [ ] Corrigir a legenda para identificar todas as séries visíveis, não apenas
  Fatigue e Fitness.
- [ ] Explicar as siglas, unidades e correspondência com os eixos.

**Aceitação:** cada linha tem nome, cor e significado identificáveis. Se a série
roxa corresponder a Form/TSB, confirmar essa relação no código antes de a
documentar. Não modificar o cálculo apenas para corrigir a legenda.

### DEV-03 — Distinguir barras e linha em Daily training load

- [ ] Usar cores diferentes para as barras e para a linha.
- [ ] Manter as cores coerentes com a legenda e o hover.

**Aceitação:** ambas as séries são distinguíveis nos dois temas e em ecrãs móveis.

## 7. Dashboard

### DSH-01 — Aumentar Weekly Plan

- [ ] Aumentar a largura de **Weekly Plan**.
- [ ] Compactar em largura **Latest Activity** e **Next Event**.

**Aceitação:** o plano semanal ganha espaço sem cortar os dados essenciais dos
outros dois contentores; o layout móvel mantém-se funcional.

### DSH-02 — Training Summary dos últimos 30 dias

- [ ] Limitar Training Summary aos últimos 30 dias, em coerência com Development.
- [ ] Indicar visivelmente o período.

**Aceitação:** a mesma janela temporal e os mesmos dados produzem totais
consistentes nas duas páginas; testar limites de datas e ausência de atividades.

### DSH-03 — Estimated Recovery coerente com Today

- [ ] Substituir o Recovery atual por **Estimated Recovery**, reutilizando a
  lógica e a apresentação de Today.
- [ ] Evitar duplicação de fórmulas entre páginas.

**Aceitação:** para o mesmo atleta, dados e instante de referência, Today e
Dashboard apresentam o mesmo valor e estado de recuperação.

### DSH-04 — Barras de estado com cor significativa

- [ ] Manter a barra de Estimated Recovery e a barra de Training Load.
- [ ] Fazer a cor corresponder à condição atual de cada indicador.
- [ ] Preservar um rótulo textual do estado.

**Aceitação:** cores coerentes com os estados efetivamente calculados; não
inventar novos limiares clínicos ou fisiológicos como parte de uma alteração
visual. Estados sem dados têm representação própria.

### DSH-05 — Retirar o gráfico Performance

- [ ] Retirar o gráfico **Performance** do Dashboard.

**Aceitação:** remover apenas este gráfico, sem confundir com o contentor
Performance Status nem eliminar métricas usadas noutras páginas.

### DSH-06 — Retirar Monthly Summary

- [ ] Retirar **Monthly Summary** do fundo do Dashboard.
- [ ] Eliminar o espaço vazio que possa ficar após a remoção.

## 8. Nova página — Guia de métricas e planos

**Nome proposto na interface inglesa:** Metrics & Plans Guide.  
**Nome descritivo em português:** Guia de métricas e planos.

### GUI-01 — Acesso e organização

- [ ] Criar uma página acessível através da barra lateral.
- [ ] Organizar o conteúdo por temas, com pesquisa ou índice que permita
  encontrar rapidamente um conceito.
- [ ] Usar linguagem simples, apresentando os detalhes técnicos progressivamente.

### GUI-02 — Inventário dos conceitos e fórmulas

- [ ] Inventariar todas as métricas, coeficientes e regras efetivamente usados
  na aplicação, incluindo criação e adaptação de planos.
- [ ] Cobrir carga, forma, recuperação, RPE, zonas de frequência cardíaca,
  distâncias, durações, desnível e outras métricas presentes na interface.
- [ ] Explicar como objetivos, disponibilidade, histórico, fases, tipos de
  sessão e eventos influenciam a criação e adaptação de planos.
- [ ] Distinguir cálculos determinísticos de interpretações do Training Coach.

### GUI-03 — Estrutura de cada explicação

Para cada conceito, documentar:

1. Nome e sigla apresentados na aplicação.
2. Significado em linguagem simples e finalidade.
3. Dados de entrada, unidades, origem e período considerado.
4. Fórmula ou regra efetivamente implementada.
5. Coeficientes, valores predefinidos, limiares e eventual personalização.
6. Exemplo numérico simples com dados fictícios, quando aplicável.
7. Interpretação do resultado, limitações e comportamento sem dados suficientes.
8. Origem: referência externa, heurística do produto ou configuração do utilizador.

**Aceitação:** explicações verificadas contra o código e testes; referências
externas verificadas antes de publicação. Não apresentar heurísticas como
verdades científicas nem resultados estimados como medições clínicas.

### GUI-04 — Manutenção e transparência

- [ ] Definir como manter o guia atualizado quando fórmulas ou coeficientes mudam.
- [ ] Testar exemplos e coerência com as funções reais, evitando apenas testes
  de presença de frases.
- [ ] Não divulgar segredos nem dados de atletas nos exemplos.

## 9. Sequência de execução proposta

1. Plan e Calendar em conjunto para transferir a exportação e ajustar os layouts.
2. Cores e identificação dos treinos em Calendar.
3. Activities: RPE e BPM; depois resumo e proposta visual do mapa.
4. Development: métricas e legibilidade dos gráficos.
5. Dashboard: redistribuição, remoções e uniformização dos indicadores.
6. Guia de métricas e planos, com inventário técnico iniciado durante as etapas
   anteriores para não deixar fórmulas por documentar.

Esta sequência é uma proposta de implementação, não altera a ordem das fases
da roadmap da alpha e não autoriza mudanças adicionais fora deste âmbito.

## 10. Regra de conclusão

Concluir um conjunto lógico de alterações de cada vez, identificando os seus IDs.
Para marcar um item como concluído:

- testes específicos e pytest completo sem erros;
- verificação de apresentação em desktop e móvel, nos modos claro e escuro;
- verificação de dados vazios, textos longos e volumes de dados elevados;
- confirmação visual pelo utilizador quando aplicável;
- commit e push confirmados, com referência registada neste documento.

A criação deste documento não conclui nenhum item e não exige alterações na
roadmap existente. As opções assinaladas como «A definir» devem ser resolvidas
antes de implementar o respetivo comportamento.
